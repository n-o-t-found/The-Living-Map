"""
Writer robot - decision logic (hardware independent: talks only to WriterHAL).

State machine:
  CALIBRATE -> EXPLORE <-> DROP
                 |  \\-> RECOVER (stuck) -> EXPLORE
                 v
              RETURN -> UPLOAD -> DONE          (any state -> SAFE_STOP on tip-over)
"""
import math
from dataclasses import dataclass, field
from enum import Enum, auto
import numpy as np
from hal import WriterHAL


def wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi
def clip(v, lo, hi): return max(lo, min(hi, v))
def dist(a, b): return math.hypot(a[0] - b[0], a[1] - b[1])


class State(Enum):
    CALIBRATE = auto(); EXPLORE = auto(); DROP = auto(); RECOVER = auto()
    RETURN = auto(); UPLOAD = auto(); DONE = auto(); SAFE_STOP = auto()


@dataclass
class WriterConfig:
    # motion
    cruise_v: float = 0.30
    curve_v: float = 0.12
    curve_w: float = 0.8
    turn_w: float = 1.0
    wall_target: float = 0.40       # m from the right wall
    lost_wall: float = 1.0          # right range above this = opening on the right
    front_stop: float = 0.50
    kd: float = 1.2                 # wall-distance gain
    kphi: float = 2.0               # wall-angle gain
    calib_s: float = 3.0
    # events
    open_range: float = 1.5         # a direction is "open" if free for more than this
    junc_debounce: int = 2
    heat_thresh: float = 45.0       # deg C
    heat_ref: float = 85.0          # deg C that maps to severity 1.0
    heat_model_tsrc: float = 80.0   # assumed source temp for range estimate (approximate!)
    hole_mm: float = 150.0          # floor reading above this = no floor ahead
    floor_lookahead: float = 0.30
    # beacon policy
    capacity: int = 8
    rf_spacing: float = 3.5         # ASSUMPTION: reliable beacon-to-beacon radio range ~ 3.5 m (measure on hardware)
    min_beacon_gap: float = 0.6
    novelty_r: dict = field(default_factory=lambda: {'HAZARD': 2.0, 'HOLE': 1.5, 'JUNCTION': 2.0, 'WAYPOINT': 2.0})
    thr_min: float = 0.2
    thr_slope: float = 0.7          # threshold rises as the magazine empties
    drop_time_s: float = 1.0
    drop_retries: int = 2
    # return / safety
    battery_reserve: float = 0.30
    max_time_s: float = 900.0
    loop_erase_r: float = 0.32
    stuck_s: float = 2.0
    stuck_max: int = 2
    tilt_limit_deg: float = 35.0


class Writer:
    def __init__(self, hal: WriterHAL, cfg: WriterConfig = None, dt: float = 0.1):
        self.hal, self.cfg, self.dt = hal, cfg or WriterConfig(), dt
        self.t0 = hal.now()
        self.state = State.CALIBRATE
        self.t_state = hal.now()
        self.stock = self.cfg.capacity
        self.next_id = 1
        self.beacons, self.decisions, self.path = [], [], []
        self.crumbs = [(0.0, 0.0)]          # loop-erased breadcrumb trail (shortest known way out)
        self.route = []
        self.path_len, self._last_pose, self._last_path_t = 0.0, (0.0, 0.0), -1.0
        self.last_beacon_xy, self.last_wp_try = (0.0, 0.0), (0.0, 0.0)
        self.left_start = False
        self.junc_count = 0
        self.heat_peak = None
        self.skip_memory = []
        self.pending = None
        self.drop_msg, self.drop_ok, self.drop_attempts = None, False, 0
        self.drop_failures = 0
        self.heading_corrections = 0
        self.last_w, self.stuck_t, self.stuck_count = 0.0, 0.0, 0
        self.upload_tries = 0
        self.return_reason, self.status = None, 'running'

    # ------------------------------------------------------------------ main tick
    def tick(self):
        if self.state not in (State.SAFE_STOP, State.DONE) and abs(self.hal.tilt_deg()) > self.cfg.tilt_limit_deg:
            self.status = 'safe_stop: tip-over'
            self._enter(State.SAFE_STOP)
        pose = self.hal.get_pose()
        {State.CALIBRATE: self._calibrate, State.EXPLORE: self._explore, State.DROP: self._drop,
         State.RECOVER: self._recover, State.RETURN: self._return, State.UPLOAD: self._upload,
         State.DONE: self._halt, State.SAFE_STOP: self._halt}[self.state](pose)

    @property
    def finished(self):
        return self.state in (State.DONE, State.SAFE_STOP)

    def _enter(self, s):
        self.state, self.t_state = s, self.hal.now()

    def _elapsed(self):
        return self.hal.now() - self.t_state

    def _halt(self, pose):
        self.hal.drive(0, 0)

    # ------------------------------------------------------------------ CALIBRATE
    def _calibrate(self, pose):
        self.hal.drive(0, 0)
        if self._elapsed() >= self.cfg.calib_s:
            self.hal.calibrate_imu()
            self._enter(State.EXPLORE)

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _sector(ang, rng, center_deg, half_deg):
        d = np.abs(np.degrees(np.angle(np.exp(1j * (ang - math.radians(center_deg))))))
        m = d <= half_deg
        return float(rng[m].min()) if m.any() else 6.0

    @staticmethod
    def _fit_wall(ang, rng, lo=-150, hi=-30):
        """Fit a line to the right-side LiDAR points -> (angle of wall in robot frame, residual, length)."""
        deg = np.degrees(ang)
        m = (deg >= lo) & (deg <= hi) & (rng < 1.5)
        if m.sum() < 8:
            return None
        pts = np.stack([rng[m] * np.cos(ang[m]), rng[m] * np.sin(ang[m])], 1)
        c = pts.mean(0)
        _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
        d, n = vt[0], vt[1]
        phi = math.atan2(d[1], d[0])
        if phi > math.pi / 2: phi -= math.pi
        elif phi <= -math.pi / 2: phi += math.pi
        proj = (pts - c) @ d
        return phi, float(np.abs((pts - c) @ n).max()), float(proj.max() - proj.min())

    def _heading_snap(self, pose, fit):
        """Simplified stand-in for LiDAR scan matching: in a building, walls are parallel to the
        x/y axes, so a straight wall seen by the LiDAR tells us the true heading modulo 90 deg."""
        if fit is None or abs(self.last_w) > 0.3:
            return
        phi, resid, length = fit
        if resid > 0.04 or length < 0.7:
            return
        k = round((pose[2] + phi) / (math.pi / 2))
        err = wrap(k * math.pi / 2 - phi - pose[2])
        if abs(err) > math.radians(20):
            return                                   # implausible -> ignore (not a wall we understand)
        self.hal.correct_heading(wrap(pose[2] + 0.3 * err))
        self.heading_corrections += 1

    def _log_path(self, pose):
        self.path_len += dist(pose, self._last_pose)
        self._last_pose = pose
        t = self.hal.now() - self.t0
        if t - self._last_path_t >= 0.5:
            self.path.append([round(pose[0], 2), round(pose[1], 2), round(pose[2], 3), round(t, 1)])
            self._last_path_t = t
        if dist(pose, (0, 0)) > 3.0:
            self.left_start = True

    def _update_crumbs(self, pose):
        """Breadcrumb trail with loop erasure: going into a dead end and coming back leaves no trace,
        so the trail is always the shortest known way back to the entrance."""
        p = (pose[0], pose[1])
        if dist(p, self.crumbs[-1]) < 0.25:
            return
        for i in range(max(0, len(self.crumbs) - 12)):
            if dist(p, self.crumbs[i]) < self.cfg.loop_erase_r:
                del self.crumbs[i + 1:]
                break
        self.crumbs.append(p)

    # ------------------------------------------------------------------ EXPLORE
    def _explore(self, pose):
        cfg, h = self.cfg, self.hal
        ang, rng = h.scan()
        fit = self._fit_wall(ang, rng)
        self._heading_snap(pose, fit)
        pose = h.get_pose()
        self._log_path(pose)
        self._update_crumbs(pose)

        reason = self._return_reason(pose)
        if reason == 'exploration complete':
            self.return_reason = reason
            self._enter(State.UPLOAD)
            return
        if reason:
            self.return_reason = reason
            self._enter(State.RETURN)
            return

        d_front = self._sector(ang, rng, 0, 20)
        d_right = self._sector(ang, rng, -90, 6)
        hole_ahead = h.floor_distance_mm() > cfg.hole_mm

        events = self._detect_events(pose, ang, rng, hole_ahead)
        for ev in sorted(events, key=self._score, reverse=True):
            if self._decide(ev, pose):
                self.pending = ev
                self._start_drop(pose)
                return

        good = fit is not None and fit[1] < 0.05 and fit[2] >= 0.7
        v, w = self._wall_follow(d_front, d_right, fit[0] if good else None, hole_ahead)   # ignore polluted fits (e.g. door frames)
        h.drive(v, w)
        self.last_w = w
        if v > 0.1 and h.measured_speed() < 0.03:
            self.stuck_t += self.dt
        else:
            self.stuck_t = 0.0
        if self.stuck_t >= cfg.stuck_s:
            self.stuck_count += 1
            self.stuck_t = 0.0
            if self.stuck_count >= cfg.stuck_max:
                self.return_reason = 'stuck: path blocked by obstacle the LiDAR cannot see'
                self._enter(State.RETURN)
            else:
                self._enter(State.RECOVER)

    def _wall_follow(self, d_front, d_right, wall_angle, hole_ahead):
        c = self.cfg
        if d_front < c.front_stop or hole_ahead:
            return 0.0, c.turn_w                              # blocked (wall or no floor): turn left
        if d_right > c.lost_wall:
            return c.curve_v, -c.curve_w                      # opening on the right: follow it
        w = -c.kd * (d_right - c.wall_target)
        if wall_angle is not None:
            w += c.kphi * clip(wall_angle, -0.9, 0.9)        # large angles happen when leaving a branch
        w = clip(w, -1.2, 1.2)
        return c.cruise_v * (1 - 0.6 * min(1.0, abs(w))), w   # slow down while turning

    def _return_reason(self, pose):
        c = self.cfg
        if self.stock <= 0: return 'magazine empty'
        if self.hal.battery() <= c.battery_reserve: return 'battery reserve reached'
        if self.hal.now() - self.t0 > c.max_time_s: return 'time limit'
        if self.left_start and dist(pose, (0, 0)) < 0.6: return 'exploration complete'
        return None

    # ------------------------------------------------------------------ RECOVER (stuck)
    def _recover(self, pose):
        t = self._elapsed()
        if t < 1.0: self.hal.drive(-0.15, 0.0)
        elif t < 2.0: self.hal.drive(0.0, 1.0)
        else:
            self.stuck_t = 0.0
            self._enter(State.EXPLORE)

    # ------------------------------------------------------------------ events
    def _detect_events(self, pose, ang, rng, hole_ahead):
        c, evs = self.cfg, []
        x, y, th = pose
        if hole_ahead:
            evs.append(dict(type='HOLE', sev=0.9, dir=th, dist=c.floor_lookahead))
        ev = self._track_heat(*self.hal.read_thermal(), pose)
        if ev: evs.append(ev)
        # right side uses the same opening test as the wall follower (the robot hugs that wall at ~0.4 m)
        opens = [self._sector(ang, rng, 0, 8) > c.open_range, self._sector(ang, rng, 90, 8) > c.open_range,
                 self._sector(ang, rng, -90, 6) > c.lost_wall, self._sector(ang, rng, 180, 8) > c.open_range]
        self.junc_count = self.junc_count + 1 if sum(opens) >= 3 else 0
        if self.junc_count == c.junc_debounce:
            mask = 0
            for o, a in zip(opens, (0, 90, -90, 180)):
                if o: mask |= 1 << (round((th + math.radians(a)) / (math.pi / 2)) % 4)   # bit0=E bit1=N bit2=W bit3=S
            evs.append(dict(type='JUNCTION', sev=0.5, dir=th, dist=c.rf_spacing, exits=mask))
        if dist((x, y), self.last_beacon_xy) > c.rf_spacing and dist((x, y), self.last_wp_try) > 1.5:
            evs.append(dict(type='WAYPOINT', sev=0.3, dir=th, dist=c.rf_spacing,
                            gap=dist((x, y), self.last_beacon_xy)))
        return evs

    def _track_heat(self, temp, bearing, pose):
        """Follow a heat reading up to its peak, then emit ONE hazard event (peak severity)."""
        c, now = self.cfg, self.hal.now()
        pk = self.heat_peak
        if temp >= c.heat_thresh:
            if pk is None or temp > pk['T']:
                self.heat_peak = pk = dict(T=temp, dir=pose[2] + bearing, t0=pk['t0'] if pk else now)
            if temp < pk['T'] - 4.0 or now - pk['t0'] > 4.0:
                return self._finish_heat()
        elif pk is not None:
            return self._finish_heat()
        return None

    def _finish_heat(self):
        c, pk = self.cfg, self.heat_peak
        self.heat_peak = None
        sev = clip((pk['T'] - c.heat_thresh) / (c.heat_ref - c.heat_thresh), 0.0, 1.0)
        rng_est = clip(2.5 * (1 - (pk['T'] - 25) / (c.heat_model_tsrc - 25)), 0.2, 2.5)
        return dict(type='HAZARD', sev=sev, dir=pk['dir'], dist=rng_est, peak_c=round(pk['T'], 1))

    # ------------------------------------------------------------------ beacon policy
    def _score(self, ev):
        if ev['type'] == 'WAYPOINT':      # the longer the silent gap, the more urgent a relay beacon becomes
            return 0.3 + 0.4 * clip((ev['gap'] - self.cfg.rf_spacing) / self.cfg.rf_spacing, 0.0, 1.0)
        return {'HAZARD': 0.6 + 0.4 * ev['sev'], 'HOLE': 0.9, 'JUNCTION': 0.5}[ev['type']]

    def _threshold(self):
        c = self.cfg
        return c.thr_min + c.thr_slope * (1 - self.stock / c.capacity)

    def _decide(self, ev, pose):
        c, x, y = self.cfg, pose[0], pose[1]
        score, thr = self._score(ev), self._threshold()
        ev['score'] = round(score, 2)
        if self.stock <= 0:
            return False
        for b in self.beacons:
            d = dist((x, y), (b['x'], b['y']))
            if d < c.min_beacon_gap or (b['type'] == ev['type'] and d < c.novelty_r[ev['type']]):
                return False                                   # already covered by an existing beacon
        if any(m[0] == ev['type'] and dist((x, y), m[1:]) < 1.5 for m in self.skip_memory):
            return False
        if score < thr:
            self.skip_memory.append((ev['type'], x, y))
            if ev['type'] == 'WAYPOINT':
                self.last_wp_try = (x, y)
            self._log_decision(ev, pose, 'skip', f"score {score:.2f} < threshold {thr:.2f} (stock {self.stock}/{c.capacity})")
            return False
        return True

    def _log_decision(self, ev, pose, action, reason):
        self.decisions.append(dict(t=round(self.hal.now() - self.t0, 1), type=ev['type'], action=action,
                                   score=ev.get('score'), reason=reason, x=round(pose[0], 2), y=round(pose[1], 2)))

    # ------------------------------------------------------------------ DROP
    def _start_drop(self, pose):
        ev = self.pending
        msg = {'id': self.next_id, 'type': ev['type'], 'dir_deg': int(round(math.degrees(wrap(ev['dir'])))) % 360,
               'dist_m': round(ev['dist'], 1), 't': int(self.hal.now()), 'ver': 1}
        if 'exits' in ev:
            msg['exits'] = ev['exits']
        self.drop_msg, self.drop_attempts = msg, 0
        self._enter(State.DROP)
        self.hal.drive(0, 0)
        self.drop_ok = self.hal.drop_beacon(msg)

    def _drop(self, pose):
        c = self.cfg
        self.hal.drive(0, 0)
        if self._elapsed() < c.drop_time_s:
            return
        ev = self.pending
        if self.drop_ok:
            b = dict(self.drop_msg, x=round(pose[0], 2), y=round(pose[1], 2), severity=round(ev['sev'], 2),
                     score=ev['score'], confidence=round(max(0.2, 1 - self.path_len / 200), 2))
            self.beacons.append(b)
            self.stock -= 1
            self.next_id += 1
            self.last_beacon_xy = (pose[0], pose[1])
            self._log_decision(ev, pose, 'drop', f"beacon #{b['id']} placed (stock left {self.stock})")
            self._enter(State.EXPLORE)
            return
        self.drop_attempts += 1
        self.drop_failures += 1
        if self.drop_attempts < c.drop_retries:
            self.t_state = self.hal.now()
            self.drop_ok = self.hal.drop_beacon(self.drop_msg)
            return
        self.skip_memory.append((ev['type'], pose[0], pose[1]))
        self._log_decision(ev, pose, 'fail', 'servo/radio failed after retry - beacon stays in magazine')
        self._enter(State.EXPLORE)

    # ------------------------------------------------------------------ RETURN / UPLOAD
    def _return(self, pose):
        h, c = self.hal, self.cfg
        self._log_path(pose)
        if not self.route:
            self.route = list(reversed(self.crumbs))
        p = (pose[0], pose[1])
        while len(self.route) > 1 and dist(p, self.route[0]) < 0.3:
            self.route.pop(0)
        if dist(p, (0, 0)) < 0.5 or (len(self.route) == 1 and dist(p, self.route[0]) < 0.3):
            h.drive(0, 0)
            self._enter(State.UPLOAD)
            return
        target = next((q for q in self.route[:8] if dist(p, q) >= 0.6), self.route[min(7, len(self.route) - 1)])
        err = wrap(math.atan2(target[1] - p[1], target[0] - p[0]) - pose[2])
        ang, rng = h.scan()
        d_front = self._sector(ang, rng, 0, 20)
        if d_front < 0.30 or h.floor_distance_mm() > c.hole_mm:
            left, right = self._sector(ang, rng, 90, 30), self._sector(ang, rng, -90, 30)
            h.drive(0.0, 1.0 if left > right else -1.0)
        elif abs(err) > 0.9:
            h.drive(0.0, clip(2.0 * err, -1.2, 1.2))
        else:
            h.drive(c.cruise_v * max(0.3, math.cos(err)), clip(2.0 * err, -1.2, 1.2))

    def _upload(self, pose):
        self.hal.drive(0, 0)
        if self._elapsed() < 1.0:
            return
        self.upload_tries += 1
        if self.hal.upload_log(self.export_log()):
            self.status = 'returned'
            self._enter(State.DONE)
        elif self.upload_tries >= 3:
            self.status = 'upload_failed (log kept on board)'
            self._enter(State.DONE)
        else:
            self.t_state = self.hal.now()

    # ------------------------------------------------------------------ interface I3 (Writer -> Outside Network Area)
    def export_log(self):
        return {
            'robot': 'writer', 'frame': 'private', 'origin': 'entrance',
            'axes': 'x = direction of entry, y = left, angles CCW from +x (degrees)',
            'start_time': int(self.t0), 'end_time': int(self.hal.now()),
            'status': 'returned', 'return_reason': self.return_reason,
            'path': self.path, 'beacons': self.beacons, 'decisions': self.decisions,
            'stats': {'path_length_m': round(self.path_len, 1), 'heading_corrections': self.heading_corrections,
                      'drop_failures': self.drop_failures, 'stock_left': self.stock,
                      'battery_end': round(self.hal.battery(), 2), 'stuck_events': self.stuck_count},
        }
