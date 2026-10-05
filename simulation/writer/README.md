# simulation/writer/ — Writer robot simulation (IMPLEMENTED, simulation only)

Run **from this folder** (the files import each other with plain `import` statements):

```bash
python run_demo.py --seed 0 --out out
```

| File | Role |
|---|---|
| `hal.py` | The contract: abstract class `WriterHAL` (drive, get_pose, correct_heading, measured_speed, calibrate_imu, tilt_deg, battery, scan, read_thermal, floor_distance_mm, drop_beacon, upload_log, now, step). The Writer logic only uses this interface, so a real-robot version could replace the simulation. |
| `sim_world.py` | `World` (14 m × 8 m tree-like building: main corridor, branches A–D, rooms R1–R3, 2 heat sources, 1 collapsed-floor hole, optional low debris) and `SimHAL` (simulated robot and noisy sensors). |
| `writer.py` | `WriterConfig` (all tunable numbers, all ASSUMED), `State`, `Writer` (state machine, wall following, heading correction, event detection, beacon policy, drop sequence, breadcrumb return, upload, log export). |
| `run_demo.py` | Command-line runner. Options: `--seed --stock --drop-fail-prob --battery-drain --kill-at --debris --out --gif`. |
| `viz.py` | `plot_run` (PNG) and `make_gif` (GIF — never run). |
| `test_robust.py` | `python test_robust.py 14` — runs seeds, prints a verdict per seed. **Lenient: does not check coverage.** |
| `coverage_check.py` | `python coverage_check.py` — checks which building zones were never visited. Saved at packaging time from a check that was originally run inline; logic unchanged. |

Outputs of `run_demo.py` (in the folder given by `--out`): `writer_log.json` (only if the upload succeeded),
`beacons_on_ground.json`, `writer_demo.png`, and `writer_demo.gif` with `--gif`.

Status of the options: normal run **TESTED**; `--kill-at`, `--drop-fail-prob`, `--battery-drain`, `--debris`, `--gif`
**UNTESTED**. Code of the six original files is unchanged from the snapshot made on 2026-10-03.
