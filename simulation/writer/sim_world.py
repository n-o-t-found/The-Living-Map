"""Simulated hazardous building + SimHAL (implements WriterHAL with realistic imperfections)."""
import math
import random
from typing import Tuple
import numpy as np
from hal import WriterHAL

CELL = 0.25          # grid resolution (m)
ROBOT_R = 0.14       # robot radius (m)
LIDAR_MAX = 6.0
N_RAYS = 120         # 3 degree resolution


def wrap(a: float) -> float:
    return (a + math.pi) % (2 * math.pi) - math.pi


class World:
    """Tree-like building: main corridor + 4 branches, 2 heat sources, 1 collapsed floor.
    World frame: origin bottom-left, entrance at (1,4) facing +x (so private frame = world - entrance)."""

    def __init__(self, with_debris: bool = False):
        self.w, self.h = 14.0, 8.0
        self.nx, self.ny = int(self.w / CELL), int(self.h / CELL)
        self.wall = np.ones((self.ny, self.nx), dtype=bool)
        self.hole = np.zeros_like(self.wall)
        self.debris = np.zeros_like(self.wall)      # low debris: invisible to LiDAR, blocks wheels
        self.entrance = (1.0, 4.0)
        self.heat = [(5.3, 1.1, 90.0), (12.4, 1.0, 90.0)]   # (x, y, source temp C)
        self.beacons = []                           # messages physically lying on the ground
        for rect in [
            (0.5, 3.5, 13.5, 4.5),    # main corridor
            (4.0, 1.0, 5.0, 3.5),     # branch A (south) ...
            (3.0, 0.5, 6.0, 2.0),     # ... room R1 (heat source)
            (8.0, 4.5, 9.0, 7.5),     # branch B (north) - floor collapsed inside
            (11.0, 1.0, 12.0, 3.5),   # branch C (south) ...
            (10.0, 0.5, 13.0, 2.0),   # ... room R2 (heat source)
            (2.0, 4.5, 3.0, 6.5),     # branch D (north) ...
            (1.5, 6.0, 4.5, 7.5),     # ... room R3 (empty)
        ]:
            self._fill(self.wall, *rect, value=False)
        self._fill(self.hole, 8.0, 6.0, 9.0, 6.5, value=True)
        if with_debris:
            self._fill(self.debris, 6.0, 3.5, 6.5, 4.0, value=True)

    def _fill(self, grid, x0, y0, x1, y1, value):
        grid[int(y0 / CELL):int(y1 / CELL), int(x0 / CELL):int(x1 / CELL)] = value

    def _cell(self, grid, x, y, oob):
        iy, ix = int(math.floor(y / CELL)), int(math.floor(x / CELL))
        if 0 <= iy < self.ny and 0 <= ix < self.nx:
            return bool(grid[iy, ix])
        return oob

    def hole_at(self, x, y):
        return self._cell(self.hole, x, y, False)

    def blocked(self, x, y, r=ROBOT_R):
        pts = [(x, y)] + [(x + r * math.cos(a), y + r * math.sin(a))
                          for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
        return any(self._cell(self.wall, px, py, True) or self._cell(self.debris, px, py, False)
                   for px, py in pts)

    def line_of_sight(self, x0, y0, x1, y1):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 0.05))
        for i in range(n + 1):
            f = i / n
            if self._cell(self.wall, x0 + f * (x1 - x0), y0 + f * (y1 - y0), True):
                return False
        return True


class SimHAL(WriterHAL):
    def __init__(self, world: World, seed: int = 1, dt: float = 0.1, epoch0: float = 1_790_000_000.0,
                 drop_fail_prob: float = 0.0, battery_drain: float = 0.0003, kill_at=None,
                 gyro_bias_dps: float = 0.3, scale_err: float = 0.015):
        self.world, self.dt, self.epoch0 = world, dt, epoch0
        self.rng = random.Random(seed)
        self.t = 0.0
        self.x, self.y = world.entrance            # TRUE pose (world frame) - never visible to the Writer
        self.th = 0.0
        self.ex = self.ey = self.eth = 0.0         # ESTIMATED pose (private frame) - what the Writer sees
        self.cmd_v = self.cmd_w = 0.0
        self.meas_v = 0.0
        self.bias = math.radians(gyro_bias_dps) * self.rng.choice([-1, 1])
        self.cal_bias = 0.0
        self.scale = 1 + scale_err * self.rng.choice([-1, 1])
        self.batt, self.drain = 1.0, battery_drain
        self.drop_fail_prob, self.kill_at = drop_fail_prob, kill_at
        self.dead, self.fell = False, False
        self.true_path, self.est_path, self.beacon_log = [], [], []   # for plots
        self.drop_calls = 0
        self.uploaded = None

    # ---- time ----
    def now(self):
        return self.epoch0 + self.t

    def step(self, dt=None):
        dt = dt or self.dt
        self.t += dt
        if self.kill_at is not None and self.t >= self.kill_at:
            self.dead = True
        if self.dead:
            self.meas_v = 0.0
            return
        v, w = self.cmd_v, self.cmd_w
        dth = w * dt * (1 + self.rng.gauss(0, 0.01))                 # wheel slip on turns
        mid = self.th + dth / 2
        moved = 0.0
        if abs(v) > 1e-6:
            nx, ny = self.x + v * dt * math.cos(mid), self.y + v * dt * math.sin(mid)
            if not self.world.blocked(nx, ny):
                self.x, self.y, moved = nx, ny, v * dt
        self.th = wrap(self.th + dth)
        if self.world.hole_at(self.x, self.y):                       # fell into the collapsed floor
            self.fell = self.dead = True
        # odometry: encoders (scale error + noise) and gyro (residual bias + noise)
        d_meas = moved * self.scale + (self.rng.gauss(0, 0.0004) if moved else 0.0)
        self.eth = wrap(self.eth + dth + (self.bias - self.cal_bias) * dt + self.rng.gauss(0, 0.0004))
        self.ex += d_meas * math.cos(self.eth)
        self.ey += d_meas * math.sin(self.eth)
        self.meas_v = d_meas / dt
        self.batt = max(0.0, self.batt - self.drain * (0.3 + abs(v) / 0.3) * dt)
        self.true_path.append((self.x, self.y))
        self.est_path.append((self.world.entrance[0] + self.ex, self.world.entrance[1] + self.ey))

    # ---- actuation / proprioception ----
    def drive(self, v, w):
        self.cmd_v = max(-0.35, min(0.35, v))
        self.cmd_w = max(-1.5, min(1.5, w))

    def get_pose(self):
        return (self.ex, self.ey, self.eth)

    def correct_heading(self, theta):
        self.eth = wrap(theta)

    def measured_speed(self):
        return self.meas_v

    def calibrate_imu(self):
        self.cal_bias = self.bias + self.rng.gauss(0, math.radians(0.03))   # ~0.03 deg/s left over

    def tilt_deg(self):
        return 0.0

    def battery(self):
        return self.batt

    # ---- exteroception ----
    def scan(self) -> Tuple[np.ndarray, np.ndarray]:
        ang = np.linspace(-math.pi, math.pi, N_RAYS, endpoint=False)
        steps = np.arange(0.05, LIDAR_MAX, 0.05)
        wa = self.th + ang
        px = self.x + np.cos(wa)[:, None] * steps[None, :]
        py = self.y + np.sin(wa)[:, None] * steps[None, :]
        ix, iy = np.floor(px / CELL).astype(int), np.floor(py / CELL).astype(int)
        oob = (ix < 0) | (ix >= self.world.nx) | (iy < 0) | (iy >= self.world.ny)
        hit = self.world.wall[np.clip(iy, 0, self.world.ny - 1), np.clip(ix, 0, self.world.nx - 1)] | oob
        first = hit.argmax(axis=1)
        rng = np.where(hit.any(axis=1), steps[first], LIDAR_MAX)
        rng = rng + np.array([self.rng.gauss(0, 0.02) for _ in range(N_RAYS)])
        return ang, np.clip(rng, 0.05, LIDAR_MAX)

    def read_thermal(self):
        best_t, best_b = 25.0, 0.0
        for sx, sy, ts in self.world.heat:
            d = math.hypot(sx - self.x, sy - self.y)
            b = wrap(math.atan2(sy - self.y, sx - self.x) - self.th)
            if d > 3.0 or abs(b) > math.radians(70) or not self.world.line_of_sight(self.x, self.y, sx, sy):
                continue
            temp = 25.0 + (ts - 25.0) * max(0.0, 1 - d / 2.5)
            if temp > best_t:
                best_t, best_b = temp, b
        return best_t + self.rng.gauss(0, 0.8), best_b + self.rng.gauss(0, 0.03)

    def floor_distance_mm(self):
        px, py = self.x + 0.30 * math.cos(self.th), self.y + 0.30 * math.sin(self.th)
        base = 240.0 if self.world.hole_at(px, py) else 60.0
        return base + self.rng.gauss(0, 2.0)

    # ---- beacons / comms ----
    def drop_beacon(self, message):
        self.drop_calls += 1
        if self.rng.random() < self.drop_fail_prob:
            return False
        b = dict(message, true_x=round(self.x, 2), true_y=round(self.y, 2))
        self.world.beacons.append(b)
        self.beacon_log.append((len(self.true_path), b))
        return True

    def upload_log(self, log):
        if self.dead:
            return False
        ex, ey = self.world.entrance
        if math.hypot(self.x - ex, self.y - ey) > 1.5:
            return False                       # out of range of the Outside Network Area
        self.uploaded = log
        return True
