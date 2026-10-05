"""Run the Writer in the simulated building.   python run_demo.py --help"""
import argparse
import json
import os
from sim_world import World, SimHAL
from writer import Writer, WriterConfig, State


def main():
    ap = argparse.ArgumentParser(description="Writer robot simulation (Phase 1)")
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--stock', type=int, default=8, help='beacons in the magazine')
    ap.add_argument('--drop-fail-prob', type=float, default=0.0, help='servo/radio failure probability per attempt')
    ap.add_argument('--battery-drain', type=float, default=0.0003, help='raise to force a low-battery return')
    ap.add_argument('--kill-at', type=float, default=None, help='Writer dies at this sim time (s) - failure case')
    ap.add_argument('--debris', action='store_true', help='add low debris the LiDAR cannot see - failure case')
    ap.add_argument('--out', default='out', help='output folder')
    ap.add_argument('--gif', action='store_true', help='also render an animated GIF')
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    world = World(with_debris=a.debris)
    hal = SimHAL(world, seed=a.seed, drop_fail_prob=a.drop_fail_prob, battery_drain=a.battery_drain, kill_at=a.kill_at)
    cfg = WriterConfig(capacity=a.stock)
    writer = Writer(hal, cfg, dt=hal.dt)

    last_state = None
    while not writer.finished and not hal.dead and hal.t < cfg.max_time_s + 60:
        writer.tick()
        hal.step()
        if writer.state != last_state:
            print(f"[{hal.t:6.1f}s] {writer.state.name}" + (f"  ({writer.return_reason})" if writer.state in (State.RETURN, State.UPLOAD) else ''))
            last_state = writer.state

    lost = hal.dead and not writer.finished
    if lost:
        writer.status = 'lost' + (' (fell into hole)' if hal.fell else '')
    elif not writer.finished:
        writer.status = 'timeout'

    # ---- outputs
    if hal.uploaded:
        with open(f'{a.out}/writer_log.json', 'w') as f:
            json.dump(hal.uploaded, f, indent=1)
    with open(f'{a.out}/beacons_on_ground.json', 'w') as f:
        json.dump(world.beacons, f, indent=1)

    print('\n=== RESULT ===')
    print(f"status            : {writer.status}")
    print(f"sim time          : {hal.t:.0f} s   path: {writer.path_len:.1f} m   battery left: {hal.battery():.0%}")
    print(f"beacons on ground : {len(world.beacons)}   (stock left {writer.stock}/{cfg.capacity})")
    print(f"log uploaded      : {'yes' if hal.uploaded else 'NO - knowledge lives only in the beacons'}")
    ex, ey = hal.ex, hal.ey
    print(f"final drift       : {((hal.x - world.entrance[0] - ex) ** 2 + (hal.y - world.entrance[1] - ey) ** 2) ** 0.5:.2f} m   "
          f"heading corrections applied: {writer.heading_corrections}")
    print('\nBeacons:')
    for b in world.beacons:
        print(f"  #{b['id']:<2} {b['type']:<9} dir={b['dir_deg']:>3}deg dist={b['dist_m']}m  "
              f"at ({b['true_x']:.1f},{b['true_y']:.1f})" + (f" exits={b['exits']:04b}" if 'exits' in b else ''))
    print('\nDecisions:')
    for d in writer.decisions:
        print(f"  t={d['t']:>6}s {d['action']:<4} {d['type']:<9} {d['reason']}")

    import viz
    viz.plot_run(world, hal, writer, f'{a.out}/writer_demo.png')
    if a.gif:
        viz.make_gif(world, hal, f'{a.out}/writer_demo.gif')
    print(f"\nFiles written to ./{a.out}/")


if __name__ == '__main__':
    main()
