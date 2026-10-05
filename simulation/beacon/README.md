# simulation/beacon/ — NOT IMPLEMENTED

There is **no Beacon code** in this project. No radio model, no beacon firmware, no packet format in bytes.

What exists elsewhere:
- The beacon message **fields** (id, type, dir_deg, dist_m, t, ver, exits) exist only as a Python dict created inside
  `../writer/writer.py` (`_start_drop`). Meaning of each field: `../../PROJECT_STATUS.md`, section 6.
- Design ideas: `../../docs/The_Living_Map_Phase1_Status_and_Handover.pdf` (section 8) and the report
  `../../report/rapport-phase1.pdf` (sections 9–11: ESP32 + LoRa reference architecture, direct/relay modes,
  beacon chain with previous_id/next_id, hop_count, TTL). All **PROPOSED**; none agreed with the Beacon teammate.

Open decisions: how a beacon receives its message (D3), RF technology/band/range, byte layout, who computes
the message age, who builds the beacon-to-beacon chain.
