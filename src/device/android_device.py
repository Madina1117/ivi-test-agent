"""ADB-level device operations, separate from UI automation.

Boot timing, battery/memory stats, and logcat pulls happen at the `adb`
layer rather than through the UI driver. As with `ui_driver.py`, a real
implementation (`AndroidDeviceBridge`, shells out to `adb`) and a mock one
(`MockAndroidDeviceBridge`) share the same interface so diagnostics/boot
tests run in both modes.
"""
from __future__ import annotations

import subprocess
from abc import ABC, abstractmethod


class DeviceBridgeBase(ABC):
    @abstractmethod
    def reboot(self) -> None: ...

    @abstractmethod
    def wait_for_boot_complete(self, timeout: float = 60.0) -> float: ...

    @abstractmethod
    def get_prop(self, name: str) -> str: ...

    @abstractmethod
    def get_battery_level(self) -> int: ...

    @abstractmethod
    def get_memory_usage_mb(self, package: str) -> int: ...

    @abstractmethod
    def pull_logcat(self, lines: int = 500) -> list[str]: ...

    @abstractmethod
    def clear_logcat(self) -> None: ...


class AndroidDeviceBridge(DeviceBridgeBase):
    """Real device/emulator access via the `adb` CLI."""

    def __init__(self, serial: str | None = None):
        self._serial_args = ["-s", serial] if serial else []

    def reboot(self) -> None:
        self._adb("reboot")

    def wait_for_boot_complete(self, timeout: float = 60.0) -> float:
        import time

        self._adb("wait-for-device")
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            result = self._adb("shell", "getprop", "sys.boot_completed")
            if result.strip() == "1":
                return round(time.monotonic() - start, 2)
            time.sleep(1)
        raise TimeoutError("device did not report sys.boot_completed=1 in time")

    def get_prop(self, name: str) -> str:
        return self._adb("shell", "getprop", name).strip()

    def get_battery_level(self) -> int:
        out = self._adb("shell", "dumpsys", "battery")
        for line in out.splitlines():
            if "level" in line:
                return int(line.split(":")[-1].strip())
        raise RuntimeError("battery level not found in dumpsys output")

    def get_memory_usage_mb(self, package: str) -> int:
        out = self._adb("shell", "dumpsys", "meminfo", package)
        for line in out.splitlines():
            if "TOTAL" in line:
                return int(line.split()[1]) // 1024
        raise RuntimeError(f"no meminfo found for {package}")

    def pull_logcat(self, lines: int = 500) -> list[str]:
        out = self._adb("logcat", "-d", "-t", str(lines))
        return out.splitlines()

    def clear_logcat(self) -> None:
        self._adb("logcat", "-c")

    def _adb(self, *args: str) -> str:
        cmd = ["adb", *self._serial_args, *args]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True)
        return result.stdout


class MockAndroidDeviceBridge(DeviceBridgeBase):
    """Simulated adb layer, backed by the same virtual head unit used by
    `MockUIDriver` so logcat/boot data stays consistent across a test."""

    def __init__(self, mock_driver):
        self._driver = mock_driver

    def reboot(self) -> None:
        self._driver.state.logcat.clear()
        self._driver._log("Rebooting...")

    def wait_for_boot_complete(self, timeout: float = 60.0) -> float:
        return self._driver.state.boot_time_s

    def get_prop(self, name: str) -> str:
        return {"sys.boot_completed": "1", "ro.build.version.release": "14"}.get(name, "")

    def get_battery_level(self) -> int:
        return 87

    def get_memory_usage_mb(self, package: str) -> int:
        baseline = {"com.oem.ivi.launcher": 210, "com.oem.ivi.media": 340, "com.oem.ivi.navigation": 480}
        return baseline.get(package, 150)

    def pull_logcat(self, lines: int = 500) -> list[str]:
        return self._driver.state.logcat[-lines:]

    def clear_logcat(self) -> None:
        self._driver.state.logcat.clear()
