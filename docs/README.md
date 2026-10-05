# docs/

| Path | Content |
|---|---|
| `The_Living_Map_Phase1_Status_and_Handover.pdf` | 16-page handover: challenge, Phase 1 requirements, concept, Writer, simulation, limitations, open decisions, beacons, failure cases, repo and report plans, checklist (written 2026-10-03) |
| `The_Living_Map_Outside_Network_Area.pdf` | 6-page brief for the Outside Network Area: roles, sequence, interfaces, frame translation with worked example, tests, failure cases, open decisions |
| `The_Living_Map_Executor_Robot.pdf` | 7-page brief for the Executor: state flow, trust by age, navigation, hardware, tests E1–E7, failure cases, open decisions |
| `figures/` | PNG figures used in the PDFs (architecture, Writer state machine, building layout, Outside Network internals, Executor state flow, trust timeline) — **drafts** |
| `official/` | The organizers' documents: the cahier des charges and the presentation. They are the source of truth. Remove them before making the repository public if you are unsure about sharing them |
| `build_scripts/` | The Python scripts that generated the figures and PDFs |

There is **no separate Beacon design document**; beacon design is in the handover PDF (section 8) and the report (sections 9–11).

## build_scripts/ — read before using
They are included unchanged so that nothing is lost. They contain **hard-coded paths from the original sandbox**
(`/home/claude/...`) and need the DejaVu fonts at `/usr/share/fonts/truetype/dejavu/`; edit the paths first.
Libraries: `requirements-docs.txt`. They are not needed to run the simulation.
`handover_make_figs.py` imports `sim_world` / `viz` from the original `writer_sim` folder (now `simulation/writer/`).
