"""
Coverage check for the Writer simulation (normal scenario, seeds 0-13).

HISTORY: this logic was originally run inline in a shell during debugging and was only saved as a file
when the repository was packaged (2026-10-04). The logic is unchanged.

It compares the Writer's TRUE path with five zones of the simulated building and reports which zones
were never visited. This is the check that exposed the known exploration bug (see PROJECT_STATUS.md,
section 10). test_robust.py does NOT check coverage.

Run from this folder:   python coverage_check.py

NOTE: the zone 'east end' (x >= 12.8) is probably tighter than the distance at which the Writer stops
before the wall, so a "missed east end" on seeds 0 and 7 is probably a test artefact (NOT verified).
"""
import numpy as np
from test_robust import run

zones = {'R1 room': (3, 6, 0.5, 2), 'R2 room': (10, 13, 0.5, 2), 'R3 room': (1.5, 4.5, 6, 7.5),
         'B hole edge': (8, 9, 5.4, 6.0), 'east end': (12.8, 13.5, 3.5, 4.5)}

if __name__ == '__main__':
    for s in range(14):
        wr, hal, w, types = run(s)
        tp = np.array(hal.true_path)
        cov = {k: bool(((tp[:, 0] >= a) & (tp[:, 0] <= b) & (tp[:, 1] >= c) & (tp[:, 1] <= d)).any())
               for k, (a, b, c, d) in zones.items()}
        miss = [k for k, v in cov.items() if not v]
        hz = [b for b in w.beacons if b['type'] == 'HAZARD']
        print(f"seed {s:2d} t={hal.t:4.0f}s path={wr.path_len:5.1f} stuck={wr.stuck_count} "
              f"missed={miss or '-'} hazards={len(hz)} fell={hal.fell}")
