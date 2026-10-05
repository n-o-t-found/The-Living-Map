"""Robustness check: run many seeds, count how often the Writer completes the mission cleanly."""
import sys, math
from sim_world import World, SimHAL
from writer import Writer, WriterConfig
def run(seed, **kw):
    w = World(kw.pop('debris', False)); hal = SimHAL(w, seed=seed, **kw); wr = Writer(hal, WriterConfig(), dt=0.1)
    while not wr.finished and not hal.dead and hal.t < 1000:
        wr.tick(); hal.step()
    types = {b['type'] for b in w.beacons}
    return wr, hal, w, types
if __name__ == '__main__':
    ok = 0; N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    for s in range(N):
        wr, hal, w, types = run(s)
        good = wr.status == 'returned' and not hal.fell and {'HAZARD','HOLE','JUNCTION'} <= types
        ok += good
        print(f"seed {s:2d}: {wr.status:10s} t={hal.t:5.0f}s path={wr.path_len:5.1f}m beacons={len(w.beacons)} types={sorted(types)} reason={wr.return_reason} {'OK' if good else '<<< PROBLEM'}")
    print(f"\n{ok}/{N} clean runs")
