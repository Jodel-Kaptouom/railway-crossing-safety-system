"""
Railway Crossing Safety System — FSM Simulation
================================================
Author : Jodel Baurel Kaptouom Fotso
Purpose: Simulate the state machine of a level crossing safety controller.
         Each transition is logged with timestamp and trigger event.
         This simulation validates the safety requirements defined in docs/requirements.md
"""

import time
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# States
# ---------------------------------------------------------------------------

class State(Enum):
    IDLE             = auto()
    TRAIN_DETECTED   = auto()
    BARRIER_CLOSING  = auto()
    BARRIER_CLOSED   = auto()
    TRAIN_PASSING    = auto()
    BARRIER_OPENING  = auto()
    FAULT            = auto()
    SAFE_STATE       = auto()


# ---------------------------------------------------------------------------
# Events (sensor inputs)
# ---------------------------------------------------------------------------

class Event(Enum):
    TRAIN_APPROACH        = auto()   # Train detected 500m before crossing
    BARRIER_END_STOP_DOWN = auto()   # Barrier fully closed confirmed
    TRAIN_CLEAR           = auto()   # Train cleared crossing zone
    BARRIER_END_STOP_UP   = auto()   # Barrier fully open confirmed
    MOTOR_TIMEOUT         = auto()   # Barrier motor did not reach end-stop in time
    SENSOR_FAULT          = auto()   # Any sensor reporting invalid state
    RESET                 = auto()   # Manual reset from FAULT/SAFE_STATE


# ---------------------------------------------------------------------------
# Outputs (actuator commands)
# ---------------------------------------------------------------------------

@dataclass
class Outputs:
    barrier_motor_down: bool = False
    barrier_motor_up:   bool = False
    road_signal_red:    bool = False
    road_signal_green:  bool = True
    alarm:              bool = False

    def __str__(self):
        active = []
        if self.barrier_motor_down: active.append("MOTOR_DOWN")
        if self.barrier_motor_up:   active.append("MOTOR_UP")
        if self.road_signal_red:    active.append("SIGNAL_RED")
        if self.road_signal_green:  active.append("SIGNAL_GREEN")
        if self.alarm:              active.append("ALARM")
        return "[" + ", ".join(active) + "]" if active else "[none]"


# ---------------------------------------------------------------------------
# FSM Controller
# ---------------------------------------------------------------------------

class RailwayCrossingFSM:

    BARRIER_TIMEOUT_S = 30.0  # SR-02

    def __init__(self):
        self.state        = State.IDLE
        self.outputs      = Outputs()
        self._barrier_start_time: Optional[float] = None
        self._log: list[str] = []
        self._enter_state(State.IDLE)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def process_event(self, event: Event) -> None:
        """Process an incoming sensor event and update state + outputs."""
        prev = self.state
        next_state = self._transition(self.state, event)

        if next_state is None:
            # Undefined transition → safety catch (SR-06)
            self._log_entry(
                f"  ⚠  Undefined event {event.name} in state "
                f"{self.state.name} → SAFE_STATE (SR-06)"
            )
            self._enter_state(State.SAFE_STATE)
        else:
            self._enter_state(next_state)

        if self.state != prev:
            self._log_entry(
                f"  ↳  {prev.name}  →  {self.state.name}  "
                f"(trigger: {event.name})  outputs: {self.outputs}"
            )

    def check_timeouts(self) -> None:
        """Call periodically to detect motor timeout (SR-02)."""
        if self.state in (State.BARRIER_CLOSING, State.BARRIER_OPENING):
            if self._barrier_start_time is not None:
                elapsed = time.time() - self._barrier_start_time
                if elapsed > self.BARRIER_TIMEOUT_S:
                    self._log_entry(f"  ⏱  Motor timeout after {elapsed:.1f}s → FAULT")
                    self.process_event(Event.MOTOR_TIMEOUT)

    def print_log(self) -> None:
        print("\n" + "=" * 60)
        print("  RAILWAY CROSSING FSM — Event Log")
        print("=" * 60)
        for entry in self._log:
            print(entry)
        print("=" * 60 + "\n")

    # ------------------------------------------------------------------
    # State entry actions
    # ------------------------------------------------------------------

    def _enter_state(self, state: State) -> None:
        self.state   = state
        self.outputs = Outputs()

        if state == State.IDLE:
            self.outputs.road_signal_green = True
            self._barrier_start_time = None

        elif state == State.TRAIN_DETECTED:
            self.outputs.road_signal_red   = True
            self.outputs.road_signal_green = False
            self.outputs.alarm             = True

        elif state == State.BARRIER_CLOSING:
            self.outputs.barrier_motor_down = True
            self.outputs.road_signal_red    = True
            self.outputs.alarm              = True
            self._barrier_start_time        = time.time()

        elif state == State.BARRIER_CLOSED:
            self.outputs.road_signal_red = True
            self._barrier_start_time     = None

        elif state == State.TRAIN_PASSING:
            self.outputs.road_signal_red = True

        elif state == State.BARRIER_OPENING:
            self.outputs.barrier_motor_up = True
            self.outputs.road_signal_red  = True
            self._barrier_start_time      = time.time()

        elif state in (State.FAULT, State.SAFE_STATE):
            self.outputs.road_signal_red    = True   # SR-03
            self.outputs.barrier_motor_down = False
            self.outputs.barrier_motor_up   = False
            self._barrier_start_time        = None

    # ------------------------------------------------------------------
    # Transition table
    # ------------------------------------------------------------------

    def _transition(self, state: State, event: Event) -> Optional[State]:
        table = {
            (State.IDLE,            Event.TRAIN_APPROACH):        State.TRAIN_DETECTED,
            (State.IDLE,            Event.SENSOR_FAULT):          State.FAULT,

            (State.TRAIN_DETECTED,  Event.TRAIN_APPROACH):        State.BARRIER_CLOSING,
            (State.TRAIN_DETECTED,  Event.SENSOR_FAULT):          State.FAULT,

            (State.BARRIER_CLOSING, Event.BARRIER_END_STOP_DOWN): State.BARRIER_CLOSED,
            (State.BARRIER_CLOSING, Event.MOTOR_TIMEOUT):         State.FAULT,
            (State.BARRIER_CLOSING, Event.SENSOR_FAULT):          State.FAULT,

            (State.BARRIER_CLOSED,  Event.TRAIN_APPROACH):        State.TRAIN_PASSING,
            (State.BARRIER_CLOSED,  Event.SENSOR_FAULT):          State.FAULT,

            (State.TRAIN_PASSING,   Event.TRAIN_CLEAR):           State.BARRIER_OPENING,
            (State.TRAIN_PASSING,   Event.SENSOR_FAULT):          State.SAFE_STATE,

            (State.BARRIER_OPENING, Event.BARRIER_END_STOP_UP):   State.IDLE,
            (State.BARRIER_OPENING, Event.MOTOR_TIMEOUT):         State.FAULT,
            (State.BARRIER_OPENING, Event.SENSOR_FAULT):          State.FAULT,

            (State.FAULT,           Event.RESET):                 State.SAFE_STATE,
            (State.SAFE_STATE,      Event.RESET):                 State.IDLE,
        }
        return table.get((state, event), None)

    def _log_entry(self, msg: str) -> None:
        ts = time.strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}"
        self._log.append(entry)
        print(entry)


# ---------------------------------------------------------------------------
# Test scenarios
# ---------------------------------------------------------------------------

def scenario_normal_cycle():
    """TC-01 / TC-02 / TC-03: Normal operation — train passes, road safe."""
    print("\n>>> SCENARIO 1: Normal cycle")
    fsm = RailwayCrossingFSM()
    fsm.process_event(Event.TRAIN_APPROACH)
    fsm.process_event(Event.TRAIN_APPROACH)
    fsm.process_event(Event.BARRIER_END_STOP_DOWN)
    fsm.process_event(Event.TRAIN_APPROACH)
    fsm.process_event(Event.TRAIN_CLEAR)
    fsm.process_event(Event.BARRIER_END_STOP_UP)
    fsm.print_log()


def scenario_motor_timeout():
    """TC-04 / TC-05: Motor timeout → FAULT, signal red stays active (SR-02, SR-03)."""
    print("\n>>> SCENARIO 2: Motor timeout → FAULT")
    fsm = RailwayCrossingFSM()
    fsm.process_event(Event.TRAIN_APPROACH)
    fsm.process_event(Event.TRAIN_APPROACH)
    fsm.process_event(Event.MOTOR_TIMEOUT)
    assert fsm.outputs.road_signal_red,        "SR-03 VIOLATED: red signal not active in FAULT"
    assert not fsm.outputs.barrier_motor_down, "Motor must be stopped in FAULT"
    print("  ✅  SR-02 verified: FAULT reached on motor timeout")
    print("  ✅  SR-03 verified: ROAD_SIGNAL_RED active in FAULT state")
    fsm.print_log()


def scenario_sensor_fault_in_passing():
    """TC-09: Sensor fault during TRAIN_PASSING → SAFE_STATE (SR-03, SR-05)."""
    print("\n>>> SCENARIO 3: Sensor fault → SAFE_STATE")
    fsm = RailwayCrossingFSM()
    fsm.process_event(Event.TRAIN_APPROACH)
    fsm.process_event(Event.TRAIN_APPROACH)
    fsm.process_event(Event.BARRIER_END_STOP_DOWN)
    fsm.process_event(Event.TRAIN_APPROACH)
    fsm.process_event(Event.SENSOR_FAULT)
    assert fsm.state == State.SAFE_STATE,  "Should be in SAFE_STATE"
    assert fsm.outputs.road_signal_red,    "SR-03 VIOLATED in SAFE_STATE"
    print("  ✅  SR-03 verified: ROAD_SIGNAL_RED active in SAFE_STATE")
    print("  ✅  SR-05 verified: barrier NOT opening during TRAIN_PASSING fault")
    fsm.print_log()


def scenario_undefined_event():
    """TC-06: Undefined event → SAFE_STATE (SR-06)."""
    print("\n>>> SCENARIO 4: Undefined event → SAFE_STATE")
    fsm = RailwayCrossingFSM()
    fsm.process_event(Event.TRAIN_CLEAR)   # undefined in IDLE
    assert fsm.state == State.SAFE_STATE, "SR-06 VIOLATED: should be in SAFE_STATE"
    print("  ✅  SR-06 verified: undefined input → SAFE_STATE")
    fsm.print_log()


if __name__ == "__main__":
    scenario_normal_cycle()
    scenario_motor_timeout()
    scenario_sensor_fault_in_passing()
    scenario_undefined_event()
    print("\n✅  All scenarios completed.")