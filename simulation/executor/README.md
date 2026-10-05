# simulation/executor/ — NOT IMPLEMENTED

There is **no Executor code** in this project (no beacon reception, no trust module, no navigation).

What exists elsewhere:
- Full design brief: `../../docs/The_Living_Map_Executor_Robot.pdf` (state flow, trust-by-age rules,
  contradiction checks per event type, navigation options, proposed tests E1–E7). All **PROPOSED / DESIGN ONLY**.
- Report: `../../report/rapport-phase1.pdf` (sections 14–15).
- Warning for whoever builds it: `../../results/sample_run_seed0/beacons_on_ground.json` contains `true_x`/`true_y`
  (simulation ground truth, for plotting). A simulated Executor must **not** read them.

Open decisions: aging thresholds and who computes the age, beacons-only vs briefing-assisted navigation, proximity
method / receiver radio, heading consistency, whether the Executor rewrites beacons, mission stand-in, whether it must exit.
