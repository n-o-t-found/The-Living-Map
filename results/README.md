# results/ — Phase 1 simulation evidence

These files are real outputs generated from the Writer simulation in
`simulation/writer/`.

No physical hardware was involved. These results represent the simulation only.

## Normal demonstration

| Folder | What it shows |
|---|---|
| `demo_seed2/` | Clean Writer demonstration using seed 2 |
| `demo_seed2/writer_log.json` | Writer log produced after successful return/upload |
| `demo_seed2/beacons_on_ground.json` | Beacons deposited in the simulated environment |
| `demo_seed2/writer_demo.png` | Final map with trajectory and beacons |
| `demo_seed2/writer_demo.gif` | Animated Writer exploration and beacon deposition |

### Normal run result

- Status: returned
- Simulation time: 247 s
- Path length: 56.0 m
- Battery remaining: 92%
- Beacons deposited: 5
- Events: 2 JUNCTION, 2 HAZARD, 1 HOLE
- Log uploaded: yes
- Final drift: 0.03 m

## Failure-case evidence

| Folder | Scenario | Result |
|---|---|---|
| `failure_writer_lost/` | Writer killed at 120 s | Writer is lost; no log is uploaded; deployed beacons remain |
| `failure_beacon_drop/` | Beacon drop failure probability = 1 | All drop attempts fail; retries occur; no beacon is deposited; Writer still returns and uploads |
| `failure_debris/` | Hidden debris | Writer enters RECOVER, resumes exploration, returns and uploads |
| `failure_low_battery_v2/` | Low battery | Battery reserve is reached; Writer returns, uploads and finishes |
| `failure_upload/` | Forced upload failure | Three upload attempts fail; mission ends with `upload_failed (log kept on board)` |

### Low-battery development test

`failure_low_battery_timeout/` contains an earlier aggressive battery-drain test.

The battery trigger worked, but the return did not complete before the simulation timeout.
It is kept as development evidence and is not presented as a successful test.

## Robustness evidence

| File | Description |
|---|---|
| `coverage_check_14seeds_output.txt` | Coverage-oriented check showing known exploration limitations |
| `test_robust_14seeds_output.txt` | 14-seed execution test using a lenient criterion |
| `sample_run_seed0/` | Earlier seed-0 evidence retained for reference |

The 14/14 result does **not** mean full building coverage. Separate coverage checking identified:

- seed 3 missed room R1
- seed 10 missed room R3 and produced a false stuck event
- seeds 1 and 9 produced unusually long trajectories
- some junctions were not consistently recorded

These are known Phase 1 simulation limitations.

## Important scope

The current repository contains an implemented Writer simulation.

Beacon, Outside Network, Command Post and Executor are currently design-level components
and do not yet have corresponding simulation code in this repository.

The results in this folder therefore provide evidence primarily for the Writer and its
failure-handling behavior.
