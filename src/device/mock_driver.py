"""In-memory virtual head unit used when tests run without real hardware.

`MockUIDriver` implements the same `UIDriverBase` contract as the real
Appium driver, backed by `VirtualHeadUnitState` - a small state machine that
models the handful of IVI screens this suite covers (home, bluetooth,
media, navigation, voice, climate, connectivity, diagnostics). Page objects
are written once against `UIDriverBase` and run unmodified against either
implementation, which is what lets ``pytest`` pass in CI with zero hardware
while the exact same test/page-object code also drives a real head unit
locally with ``--real-device``.
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass, field

from src.device.ui_driver import Locator, UIDriverBase
from src.vehicle.vehicle_bus_simulator import VehicleBusSimulator


@dataclass
class VirtualHeadUnitState:
    screen: str = "home"
    boot_time_s: float = 0.0
    logcat: list[str] = field(default_factory=list)

    bt_known_devices: set[str] = field(default_factory=set)
    bt_connected_device: str | None = None
    bt_call_active: bool = False

    media_source: str = "usb"
    media_playing: bool = False
    media_volume: int = 8
    media_track: str = "Track 01 - Unknown Artist"

    gps_locked: bool = False
    route_active: bool = False
    voice_guidance_on: bool = True

    projection_active: bool = False

    voice_listening: bool = False
    last_voice_command: str | None = None
    tts_played: bool = False

    climate_temp_c: int = 21

    wifi_connected: bool = False
    hotspot_enabled: bool = False
    cellular_active: bool = False

    ota_status: str = "idle"


class MockUIDriver(UIDriverBase):
    """A deterministic, fast fake of the head unit UI, driven by simple
    tap-triggered transitions rather than real rendering."""

    #: elements considered "text input" and therefore locked while driving
    _INPUT_ELEMENTS = {"nav_destination_input", "bt_pin_input", "wifi_password_input"}

    #: real screenshots are PNGs; the mock writes a plain-text stand-in
    SCREENSHOT_EXT = ".txt"

    def __init__(self, vehicle_bus: VehicleBusSimulator | None = None, boot_time_s: float | None = None):
        self.state = VirtualHeadUnitState()
        self.vehicle_bus = vehicle_bus or VehicleBusSimulator()
        self.state.boot_time_s = (
            boot_time_s if boot_time_s is not None else round(random.uniform(9.0, 13.5), 2)
        )
        self._log(f"BOOT_COMPLETE in {self.state.boot_time_s}s")

    # -- UIDriverBase -----------------------------------------------------
    def launch_app(self, package: str) -> None:
        screen = package.rsplit(".", 1)[-1]
        self.state.screen = screen
        self._log(f"ActivityManager: START {package}")

    def tap(self, locator: Locator) -> None:
        if self._is_locked(locator):
            self._log(f"UI_LOCKOUT: blocked tap on {locator.element_id} while driving")
            raise PermissionError(f"'{locator.element_id}' is locked while the vehicle is in motion")
        self._transition(locator.element_id)

    def input_text(self, locator: Locator, text: str) -> None:
        if self._is_locked(locator):
            raise PermissionError(f"'{locator.element_id}' is locked while the vehicle is in motion")
        if locator.element_id == "nav_destination_input":
            self.state.route_active = bool(text)
            self._log(f"NAV: destination set to '{text}'")

    def get_text(self, locator: Locator) -> str:
        mapping = {
            "current_screen_label": self.state.screen,
            "media_track_title": self.state.media_track,
            "media_volume_level": str(self.state.media_volume),
            "climate_temp_label": f"{self.state.climate_temp_c}C",
            "bt_connected_device_label": self.state.bt_connected_device or "",
            "voice_last_command_label": self.state.last_voice_command or "",
            "day_night_mode_label": "night" if self.vehicle_bus.headlights_on else "day",
            "ota_status_label": self.state.ota_status,
        }
        return mapping.get(locator.element_id, "")

    def is_displayed(self, locator: Locator) -> bool:
        s = self.state
        indicators = {
            "voice_listening_indicator": s.voice_listening,
            "voice_tts_played_indicator": s.tts_played,
            "bt_call_active_indicator": s.bt_call_active,
            "media_playing_indicator": s.media_playing,
            "nav_gps_locked_indicator": s.gps_locked,
            "nav_route_active_indicator": s.route_active,
            "nav_voice_guidance_enabled_indicator": s.voice_guidance_on,
            "auto_projection_active_indicator": s.projection_active,
            "wifi_connected_indicator": s.wifi_connected,
            "hotspot_enabled_indicator": s.hotspot_enabled,
            "cellular_active_indicator": s.cellular_active,
        }
        return indicators.get(locator.element_id, True)

    def is_enabled(self, locator: Locator) -> bool:
        return not self._is_locked(locator)

    def wait_for(self, locator: Locator, timeout: float = 5.0) -> bool:
        return True

    def current_screen(self) -> str:
        return self.state.screen

    def take_screenshot(self, out_path: str) -> None:
        with open(out_path, "w") as fh:
            fh.write(f"[mock screenshot] screen={self.state.screen} at t={time.time()}\n")

    def quit(self) -> None:
        self._log("SESSION_END")

    # -- state machine ------------------------------------------------------
    def _is_locked(self, locator: Locator) -> bool:
        return locator.element_id in self._INPUT_ELEMENTS and self.vehicle_bus.is_driving()

    def _transition(self, element_id: str) -> None:
        s = self.state
        handlers = {
            "nav_bluetooth": lambda: setattr(s, "screen", "bluetooth"),
            "nav_media": lambda: setattr(s, "screen", "media"),
            "nav_navigation": lambda: setattr(s, "screen", "navigation"),
            "nav_voice": lambda: setattr(s, "screen", "voice"),
            "nav_climate": lambda: setattr(s, "screen", "climate"),
            "nav_connectivity": lambda: setattr(s, "screen", "connectivity"),
            "nav_diagnostics": lambda: setattr(s, "screen", "diagnostics"),
            "nav_home": lambda: setattr(s, "screen", "home"),
            "bt_pair_new_device": lambda: s.bt_known_devices.add("Pixel-8-Pro"),
            "bt_connect_known_device": self._bt_connect,
            "bt_accept_call": lambda: setattr(s, "bt_call_active", True),
            "bt_end_call": lambda: setattr(s, "bt_call_active", False),
            "media_play_pause": lambda: setattr(s, "media_playing", not s.media_playing),
            "media_volume_up": lambda: setattr(s, "media_volume", min(20, s.media_volume + 1)),
            "media_volume_down": lambda: setattr(s, "media_volume", max(0, s.media_volume - 1)),
            "media_source_usb": lambda: self._set_media_source("usb"),
            "media_source_bluetooth": lambda: self._set_media_source("bluetooth"),
            "media_source_streaming": lambda: self._set_media_source("streaming"),
            "nav_acquire_gps": lambda: setattr(s, "gps_locked", True),
            "nav_start_route": lambda: setattr(s, "route_active", True),
            "nav_cancel_route": lambda: setattr(s, "route_active", False),
            "nav_toggle_voice_guidance": lambda: setattr(s, "voice_guidance_on", not s.voice_guidance_on),
            "auto_connect_projection": lambda: setattr(s, "projection_active", True),
            "auto_disconnect_projection": lambda: setattr(s, "projection_active", False),
            "voice_wake": self._voice_wake,
            "climate_temp_up": lambda: setattr(s, "climate_temp_c", min(28, s.climate_temp_c + 1)),
            "climate_temp_down": lambda: setattr(s, "climate_temp_c", max(16, s.climate_temp_c - 1)),
            "wifi_connect_known_network": lambda: setattr(s, "wifi_connected", True),
            "wifi_disconnect": self._wifi_disconnect,
            "hotspot_toggle": lambda: setattr(s, "hotspot_enabled", not s.hotspot_enabled),
            "cellular_toggle": lambda: setattr(s, "cellular_active", not s.cellular_active),
            "ota_start_update": self._ota_start,
        }
        handler = handlers.get(element_id)
        if handler is None:
            raise ValueError(f"unknown element_id '{element_id}' on virtual head unit")
        handler()
        self._log(f"TAP {element_id} -> screen={s.screen}")

    def _wifi_disconnect(self) -> None:
        """Losing wifi triggers automatic cellular data fallback."""
        self.state.wifi_connected = False
        self.state.cellular_active = True

    def _bt_connect(self) -> None:
        if not self.state.bt_known_devices:
            raise RuntimeError("no known bluetooth devices to connect to")
        self.state.bt_connected_device = next(iter(self.state.bt_known_devices))

    def _set_media_source(self, source: str) -> None:
        self.state.media_source = source
        self.state.media_track = f"Track 01 - {source.capitalize()} Source"

    def _voice_wake(self) -> None:
        self.state.voice_listening = True
        self.state.last_voice_command = "navigate home"
        self.state.tts_played = True

    def _ota_start(self) -> None:
        self.state.ota_status = "downloading"

    def set_ota_status(self, status: str) -> None:
        self.state.ota_status = status
        self._log(f"OTA_STATUS {status}")

    def inject_anr(self, component: str) -> None:
        self._log(f"ActivityManager: ANR in {component}")

    def inject_crash(self, component: str) -> None:
        self._log(f"FATAL EXCEPTION: {component} java.lang.RuntimeException")

    def _log(self, line: str) -> None:
        self.state.logcat.append(f"{time.strftime('%H:%M:%S')} {line}")
