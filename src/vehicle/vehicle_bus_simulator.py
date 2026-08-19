"""A minimal stand-in for the vehicle CAN/LIN bus.

Real IVI test rigs drive this through a CAN interface (e.g. PCAN, Vector) to
inject signals like vehicle speed or gear position and observe how the head
unit's UI reacts (driving-mode lockouts, reverse-camera trigger, etc.).
This simulator reproduces just enough of that signal surface - speed,
gear, ignition state, park-brake - for the test suite to exercise the same
HMI behaviour deterministically, without any hardware in the loop.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Gear(StrEnum):
    PARK = "P"
    REVERSE = "R"
    NEUTRAL = "N"
    DRIVE = "D"


class Ignition(StrEnum):
    OFF = "OFF"
    ACC = "ACC"
    ON = "ON"
    START = "START"


@dataclass
class VehicleBusSimulator:
    """Emits CAN-like frames and tracks the current vehicle state."""

    speed_kmh: float = 0.0
    gear: Gear = Gear.PARK
    ignition: Ignition = Ignition.OFF
    park_brake_engaged: bool = True
    headlights_on: bool = False
    frames: list[dict] = field(default_factory=list)

    def set_speed(self, kmh: float) -> None:
        if kmh < 0:
            raise ValueError("speed cannot be negative")
        self.speed_kmh = kmh
        self._emit("VEHICLE_SPEED", kmh)

    def set_gear(self, gear: Gear) -> None:
        if gear != Gear.PARK and self.ignition == Ignition.OFF:
            raise RuntimeError("cannot shift gear with ignition off")
        self.gear = gear
        self._emit("GEAR_POSITION", gear.value)

    def set_ignition(self, state: Ignition) -> None:
        self.ignition = state
        if state == Ignition.OFF:
            self.speed_kmh = 0.0
            self.gear = Gear.PARK
        self._emit("IGNITION_STATE", state.value)

    def set_park_brake(self, engaged: bool) -> None:
        self.park_brake_engaged = engaged
        self._emit("PARK_BRAKE", engaged)

    def set_headlights(self, on: bool) -> None:
        self.headlights_on = on
        self._emit("HEADLIGHT_STATE", on)

    def is_driving(self) -> bool:
        """UI lockout rule used across the HMI test suites."""
        return self.speed_kmh > 5.0 and self.gear == Gear.DRIVE

    def is_reverse(self) -> bool:
        return self.gear == Gear.REVERSE

    def _emit(self, signal: str, value) -> None:
        self.frames.append({"signal": signal, "value": value})
