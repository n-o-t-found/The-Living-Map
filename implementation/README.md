# implementation/ — Phase 1 implementation plan

## 1. Purpose

This document defines the proposed implementation path from the end of Phase 1
to the final challenge submission on 01/12/2026.

The project is currently software/design dominated. The Writer simulation is
implemented and tested. Physical hardware has not yet been tested.

This plan separates:
- IMPLEMENTED simulation work
- PROPOSED hardware and architecture
- OPEN engineering decisions
- validation activities required before the final phase

---

## 2. Current implementation status

| Subsystem | Current state | Next action | Owner |
|---|---|---|---|
| Writer software simulation | IMPLEMENTED | Stabilize and integrate with hardware | Writer team |
| Writer hardware | PROPOSED / partly CONFIRMED | Hardware bring-up and sensor tests | Writer team |
| Beacon | DESIGN ONLY | Freeze architecture and build prototype | Beacon team |
| Outside Network | DESIGN ONLY | Implement gateway, translation and communication | Outside Network team |
| Command Post | DESIGN ONLY | Build map/dashboard interface | Command Post team |
| Executor | DESIGN ONLY | Implement navigation and mission behavior | Executor team |
| End-to-end integration | NOT IMPLEMENTED | Integrate all interfaces | Whole team |

---

## 3. Hardware plan

### Writer Robot

| Hardware | Status | Validation | Owner |
|---|---|---|---|
| Arduino UNO Q | CONFIRMED by user | Board bring-up | Writer team |
| RPLIDAR | CONFIRMED; exact model OPEN | USB / powered hub / scan test | Writer team |
| Modulino Movement (LSM6DSOX) | CONFIRMED; owned | IMU and heading test | Writer team |
| Modulino Distance (VL53L4CD) | CONFIRMED; owned | Floor-distance / hole detection test | Writer team |
| Servo | CONFIRMED | Release/repeatability test | Writer team |
| Beacon dispenser / magazine | OPEN | Mechanical drop test | Writer team |
| Thermal sensor | OPEN: MLX90640 / AMG8833 candidates | Select and test hotspot detection | Writer team |
| Drive base | PROPOSED | Motion test | Writer team |
| Wheel encoders | PROPOSED | Odometry test | Writer team |
| Motor driver | PROPOSED | Motor-control test | Writer team |
| Battery / power system | PROPOSED | Runtime and protection test | Writer team |
| Emergency stop | PROPOSED | Safety test | Writer team |

### Beacon

| Hardware | Status | Validation | Owner |
|---|---|---|---|
| ESP32-class MCU | PROPOSED | Firmware bring-up | Beacon team |
| SX1276/RFM95-class LoRa | PROPOSED | RF communication/range test | Beacon team |
| Non-volatile memory | PROPOSED | Message storage/retrieval test | Beacon team |
| LiPo + regulator | PROPOSED | Power/runtime test | Beacon team |
| Deployment switch | PROPOSED | Activation test after release | Beacon team |
| LED / status indicator | PROPOSED | State indication test | Beacon team |
| Antenna | PROPOSED | RF performance test | Beacon team |

### Outside Network / Command Post

| Hardware | Status | Validation | Owner |
|---|---|---|---|
| Raspberry Pi gateway | PROPOSED | Gateway software test | Outside Network team |
| GPS receiver | PROPOSED | Position/coordinate test | Outside Network team |
| Local network interface | PROPOSED | Data transfer test | Outside Network team |
| PC/browser | PROPOSED | Map/dashboard test | Command Post team |
| Wireless/satellite backhaul | OPEN | Select and validate | Outside Network team |

### Executor

Proposed reuse of the Writer architecture where practical:

UNO Q, RPLIDAR, IMU, floor-distance sensing, selected thermal sensor,
beacon-compatible RF receiver, drive base, encoders, motor driver and battery.

Exact Executor hardware remains OPEN until the architecture and beacon
interface are frozen.

---

## 4. Proposed timeline

The following schedule is PROPOSED and must be adapted with the team.

| Period | Main work | Deliverable |
|---|---|---|
| 05–07 Oct | Freeze I1–I5, event set and beacon message | Agreed interfaces |
| 06–12 Oct | Writer hardware bring-up; RPLIDAR, IMU, distance sensor | Basic Writer hardware test |
| 08–15 Oct | Thermal sensor selection + hotspot test | Selected thermal sensor |
| 10–18 Oct | Beacon mechanical dispenser + prototype beacon | First beacon prototype |
| 15–22 Oct | Beacon RF communication and range testing | RF test results |
| 18–27 Oct | Outside Network RECEIVE / TRANSLATE / CARRY / BRIEF | Gateway prototype |
| 22–31 Oct | Frame translation + command-post map | GPS-referenced map |
| 01–10 Nov | Executor software and beacon-following logic | Executor simulation/prototype |
| 08–17 Nov | Executor hardware bring-up | Executor basic navigation |
| 15–23 Nov | Writer + Beacon + Outside Network + Executor integration | End-to-end demonstration |
| 20–26 Nov | Failure cases and robustness testing | Test report/logs |
| 24–28 Nov | RF, GPS, navigation and safety validation | Validation evidence |
| 28–30 Nov | Final documentation, figures, GitHub and user manual | Final package |
| 01 Dec | Final submission | Final challenge submission |

---

## 5. Mandatory hardware validation tests

### T1 — RPLIDAR / USB

Verify:
- board connection
- USB interface / powered USB-C hub if required
- stable scan rate
- detection of walls and obstacles

### T2 — IMU

Verify:
- calibration
- heading stability
- residual drift
- safe behavior after abnormal tilt

### T3 — Floor-distance sensor

Verify:
- normal floor distance
- missing-floor threshold
- detection reliability at the planned look-ahead distance

### T4 — Thermal sensor

Compare candidate sensors and validate:
- hotspot detection
- useful temperature range
- detection distance
- response time
- false detections

### T5 — Beacon dispenser

Verify:
- reliable servo movement
- one beacon released per command
- release confirmation
- no double release
- behavior after failed release

### T6 — Beacon RF

Verify:
- transmission
- reception
- usable range
- packet loss
- battery impact
- behavior around walls/obstacles

### T7 — Outside Network

Verify:
- Writer log reception
- validation
- private-to-GPS translation
- command-post delivery
- store-and-forward behavior

### T8 — Executor

Verify:
- beacon detection
- trust/aging interpretation
- local navigation
- obstacle avoidance
- target mission
- safe exit

---

## 6. Main risks and mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| Writer navigation not robust enough | High | Keep simulation tests and improve coverage before integration |
| RPLIDAR USB/power issues | Medium | Test early with powered hub if required |
| Thermal sensor unsuitable | High | Compare candidates before mechanical integration |
| Beacon RF range too short | High | Perform range test early; evaluate relay architecture |
| Beacon dispenser jams | High | Mechanical prototype and repeated drop test |
| GPS/frame translation errors | High | Test with known reference points |
| Interface disagreements | High | Freeze I1–I5 before integration |
| Executor cannot trust stale beacons | High | Define aging rules and sensor cross-check |
| Integration delays | High | Test interfaces independently before full integration |
| Power/runtime insufficient | Medium | Measure actual consumption and battery autonomy |
| Physical hardware unavailable | Medium | Maintain simulation as fallback for development |

---

## 7. Simulation versus physical implementation

### Already implemented in simulation

- Writer exploration
- LiDAR-based navigation model
- IMU/odometry error model
- thermal event detection
- hole detection
- junction detection
- beacon decision policy
- beacon deposition model
- return behavior
- battery reserve behavior
- recovery behavior
- Writer log generation
- upload behavior
- Writer failure scenarios

### Design only / not yet physically implemented

- Physical Writer integration
- Physical beacon
- Beacon RF communication
- Beacon relay / chain
- Outside Network gateway
- GPS frame translation software
- Command-post live map
- Executor robot
- End-to-end physical communication
- Trust/aging implementation

---

## 8. Interface freeze

Before hardware integration, the team must agree on:

- I1 Writer → Beacon
- I2 Beacon → Executor
- I3 Writer → Outside Network
- I4 Outside Network → Command Post
- I5 Outside Network → Executor
- event types
- beacon message format
- timestamp/clock policy
- beacon-chain construction
- RF technology and frequency
- trust/aging thresholds

No hardware integration should be considered final until these interfaces are frozen.

---

## 9. Final validation target

Before the final submission, the complete system should demonstrate:

Writer
→ detects and records events
→ deploys persistent beacons
→ returns or fails while preserving knowledge
→ Outside Network receives/translates information
→ Command Post generates the mission
→ Executor receives the briefing
→ Executor uses the beacon information to reach the target
→ system exits safely.

The physical prototype and final integrated validation belong to the final phase.
