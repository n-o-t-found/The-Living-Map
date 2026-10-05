# The Living Map — Spatial Memory for Emergency Robots

TSYP14 Technical Challenge · IEEE RAS × IEEE AESS, Tunisia Section Chapters

> **Phase 1 status:** the Writer robot simulation is implemented and tested.
> Beacon, Outside Network, Command Post and Executor remain design-level components.
> No physical hardware has been tested yet.

## 1. What The Living Map is

The Living Map gives a GPS-denied and disconnected environment a persistent memory.

A first robot, the **Writer**, enters and explores the environment. It detects important
events and leaves information behind in radio beacons.

A later **Executor** robot can use this inherited information to continue the mission
without starting from zero.

The architecture contains four main roles:

1. Writer Robot
2. Beacon Network
3. Outside Network Area
4. Executor Robot

## 2. Challenge scenario

Our proposed environment is a **Fire / Hazardous Building**.

The Writer enters first without a pre-existing map. It explores autonomously and can detect:

- HAZARD — heat / fire hotspot
- HOLE — collapsed or missing floor
- JUNCTION — navigation landmark

The challenge requires at least two event types. The current Writer simulation implements all three.

The Outside Network is the required bridge between the disconnected interior and the outside
world. Direct robot-to-command-post communication is not used in the architecture.

## 3. System architecture

```text
              INSIDE / DISCONNECTED
              
        ┌──────────────┐
        │ Writer Robot │
        └──────┬───────┘
               │
          drops beacons
               │
        ┌──────▼───────┐
        │    Beacons   │
        └──────┬───────┘
               │
               │
        OUTSIDE NETWORK AREA
               │
        ┌──────▼────────────┐
        │ Outside Network   │
        │ RECEIVE           │
        │ TRANSLATE         │
        │ CARRY             │
        │ BRIEF             │
        └──────┬────────────┘
               │
        ┌──────▼───────┐
        │ Command Post │
        └──────┬───────┘
               │ mission briefing
        ┌──────▼───────┐
        │   Executor   │
        └──────────────┘
