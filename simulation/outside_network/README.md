# simulation/outside_network/ — NOT IMPLEMENTED

There is **no Outside Network code** in this project (no receive, translate, carry, brief, no live map).

What exists elsewhere:
- Full design brief: `../../docs/The_Living_Map_Outside_Network_Area.pdf` (roles, sequence, interfaces I3–I5,
  frame-translation formulas with a worked example, six proposed tests T1–T6). All **PROPOSED / DESIGN ONLY**.
- Its only input that exists today is the Writer's log (`../../results/sample_run_seed0/writer_log.json`, interface I3 draft).
- Report: `../../report/rapport-phase1.pdf` (sections 12–13).

Open decisions: building-bearing source, who builds the beacon chain, link technology, clock synchronisation,
meaning of a "live" map when the Writer only reports on return.
