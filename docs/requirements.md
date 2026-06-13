# Requirements Specification
## Railway Crossing Safety System

**Document ID:** RCS-REQ-001  
**Version:** 1.0  
**Author:**  Baurel Kaptouom   
**Status:** Baseline

---

## 1. System Purpose

The Railway Crossing Safety System (RCSS) shall control a level crossing
to prevent simultaneous occupation of the crossing zone by road traffic
and rail traffic.

---

## 2. Stakeholders

| Stakeholder | Interest |
|---|---|
| Railway operator | Train passes without obstruction |
| Road authority | Road users protected at all times |
| Safety authority | System meets SIL-2 requirements (reference only) |
| Maintenance team | Faults are detectable and logged |

---

## 3. Safety Requirements

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| SR-01 | The barrier SHALL be fully closed before any train enters the crossing zone | Critical | TC-01 |
| SR-02 | The system SHALL detect barrier motor timeout (> 30s) and transition to FAULT | Critical | TC-04 |
| SR-03 | In FAULT or SAFE_STATE, ROAD_SIGNAL_RED SHALL remain permanently active | Critical | TC-05 |
| SR-04 | Transition to TRAIN_PASSING SHALL only occur after BARRIER_END_STOP_DOWN confirmation | Critical | TC-02 |
| SR-05 | The system SHALL NOT open the barrier while TRAIN_PASSING is active | Critical | TC-03 |
| SR-06 | Any undefined input combination SHALL transition the system to SAFE_STATE | Critical | TC-06 |

---

## 4. Functional Requirements

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| FR-01 | The system SHALL log all state transitions with timestamp and trigger event | High | TC-07 |
| FR-02 | Normal cycle (IDLE → BARRIER_CLOSED) SHALL complete within 45 seconds | High | TC-08 |
| FR-03 | The system SHALL activate ALARM during BARRIER_CLOSING state | Medium | TC-09 |
| FR-04 | After TRAIN_CLEAR, the system SHALL automatically initiate BARRIER_OPENING | High | TC-10 |

---

## 5. Interface Requirements

| ID | Requirement |
|---|---|
| IR-01 | All sensor inputs SHALL be digital (active HIGH) |
| IR-02 | All actuator outputs SHALL be digital (active HIGH) |
| IR-03 | The system SHALL provide a serial log output for maintenance purposes |

---

## 6. Inputs / Outputs

### Sensors (Inputs)

| Signal | Description |
|---|---|
| `TRAIN_APPROACH` | Inductive loop sensor, 500m before crossing |
| `TRAIN_CLEAR` | Inductive loop sensor, 100m after crossing |
| `BARRIER_END_STOP_DOWN` | Mechanical end-stop — barrier fully closed |
| `BARRIER_END_STOP_UP` | Mechanical end-stop — barrier fully open |
| `FAULT_SENSOR` | Any sensor reporting invalid state |

### Actuators (Outputs)

| Signal | Description |
|---|---|
| `BARRIER_MOTOR_DOWN` | Drive barrier to closed position |
| `BARRIER_MOTOR_UP` | Drive barrier to open position |
| `ROAD_SIGNAL_RED` | Stop road traffic |
| `ROAD_SIGNAL_GREEN` | Allow road traffic |
| `ALARM` | Audible/visual warning during closing sequence |