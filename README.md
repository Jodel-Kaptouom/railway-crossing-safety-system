# Railway Crossing Safety System
## Repository Structure

```
railway-crossing-safety-system/
├── README.md
├── docs/
│   └── requirements.md       # Full requirements specification
├── simulation/
│   └── crossing_sim.py       # Python FSM simulation with logging
└── validation/
    └── test_cases.md         # Test scenarios mapped to requirements
```
### Model-Based Specification of a Safety-Critical Railway Crossing Control System

![Status](https://img.shields.io/badge/status-in%20progress-yellow)
![Language](https://img.shields.io/badge/language-Python%20%7C%20Markdown-blue)
![Method](https://img.shields.io/badge/method-V--Model-green)

---

## Motivation

This project was initiated as a self-directed learning exercise to develop a systems engineering mindset in the context of **safety-critical railway automation** — a field where the cost of failure is measured not in data loss but in human lives.

The goal is not to build a full production system, but to practice the **V-Model development process** from requirements specification through architecture design to simulated validation — the core workflow of a Systems Engineer in railway automation.

---

## System Description

A **level crossing safety system** controls the sequence of events when a train approaches and passes through a road-rail intersection. The system must guarantee:

- **No road traffic** is present when a train enters the crossing zone
- **Barrier state** is always known and consistent with train position
- **Faults** are detected and the system transitions to a defined safe state
- **Timing constraints** are respected (barrier closing time ≤ T_close_max)

---

## Development Approach — V-Model
Each left-side artifact (requirements, architecture, design) has a corresponding
right-side verification artifact (test cases, integration scenarios, validation results).

---

## System States

| State | Description |
|---|---|
| `IDLE` | No train detected — crossing open for road traffic |
| `TRAIN_DETECTED` | Train sensor triggered — initiate closing sequence |
| `BARRIER_CLOSING` | Barrier motor active — road traffic warned |
| `BARRIER_CLOSED` | Barrier fully closed — confirmed by end-stop sensor |
| `TRAIN_PASSING` | Train occupying crossing zone |
| `BARRIER_OPENING` | Train cleared — barrier opening |
| `FAULT` | Sensor failure or timing violation detected |
| `SAFE_STATE` | Emergency stop — barrier down, signals red, alert triggered |

---

## Key Safety Requirements (excerpt)

| ID | Requirement | Type |
|---|---|---|
| SR-01 | Barrier SHALL be fully closed before any train enters the crossing zone | Safety |
| SR-02 | System SHALL detect barrier motor timeout (> 30s) and transition to FAULT | Safety |
| SR-03 | In FAULT or SAFE_STATE, ROAD_SIGNAL_RED SHALL remain active | Safety |
| SR-04 | Transition to TRAIN_PASSING SHALL only occur after BARRIER_END_STOP_DOWN confirmed | Safety |
| SR-05 | System SHALL NOT open the barrier while TRAIN_PASSING is active | Safety |
| SR-06 | Any undefined input SHALL transition the system to SAFE_STATE | Safety |

---

## Repository Structure
---

## Tools & Methods

- **Development process:** V-Model
- **Modeling approach:** Finite State Machine (FSM)
- **Simulation:** Python 3 (no external dependencies)
- **Documentation:** Markdown with structured requirement IDs

---

## Status

| Artifact | Status |
|---|---|
| Requirements specification | ✅ Complete |
| FSM state diagram | ✅ Complete |
| Python simulation | ✅ Complete |
| Test cases / validation | ✅ Complete |

---

## Author

**Baurel Kaptouom**  
M.Eng. Elektrotechnik & Informationstechnik — HAWK Göttingen  
[GitHub](https://github.com/Jodel-Kaptouom)

*This project is part of a self-directed learning path toward
safety-critical systems engineering in railway automation.*