"""Shared fixtures and pytest configuration for the IVI test suite.

Tests run in one of two modes:

- default (mock)  -> `MockUIDriver` / `MockAndroidDeviceBridge` drive an
  in-memory virtual head unit. No Android SDK, emulator, or Appium server
  required - this is what CI runs.
- ``--real-device`` -> `AppiumUIDriver` / `AndroidDeviceBridge` drive an
  actual head unit or emulator over Appium + adb. Tests marked
  ``@pytest.mark.real_device`` only run in this mode.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from src.analysis.failure_analyzer import FailureAnalyzer
from src.device.android_device import AndroidDeviceBridge, MockAndroidDeviceBridge
from src.device.mock_driver import MockUIDriver
from src.device.ui_driver import AppiumUIDriver
from src.pages.home_screen import HomeScreen
from src.vehicle.vehicle_bus_simulator import VehicleBusSimulator

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--real-device",
        action="store_true",
        default=False,
        help="Run against a real head unit / emulator via Appium instead of the mock driver.",
    )
    parser.addoption(
        "--udid",
        action="store",
        default=None,
        help="Device UDID to target when --real-device is set (defaults to the only attached device).",
    )


def pytest_configure(config: pytest.Config) -> None:
    for marker, description in {
        "smoke": "fast, high-value checks suitable for every build",
        "regression": "full-depth coverage, run on nightly/scheduled builds",
        "real_device": "requires --real-device; skipped in mock mode",
        "mock_only": "exercises mock-only fault injection; skipped with --real-device",
        "slow": "test takes multiple seconds even in mock mode",
    }.items():
        config.addinivalue_line("markers", f"{marker}: {description}")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    real_device = config.getoption("--real-device")
    skip_real = pytest.mark.skip(reason="requires a real device: run with --real-device")
    skip_mock_only = pytest.mark.skip(reason="mock-only fault injection: not available with --real-device")
    for item in items:
        if not real_device and "real_device" in item.keywords:
            item.add_marker(skip_real)
        if real_device and "mock_only" in item.keywords:
            item.add_marker(skip_mock_only)


@pytest.fixture
def vehicle_bus() -> VehicleBusSimulator:
    return VehicleBusSimulator()


@pytest.fixture
def device_bridge(request: pytest.FixtureRequest, driver):
    if request.config.getoption("--real-device"):
        return AndroidDeviceBridge(serial=request.config.getoption("--udid"))
    return MockAndroidDeviceBridge(driver)


@pytest.fixture
def driver(request: pytest.FixtureRequest, vehicle_bus: VehicleBusSimulator):
    if request.config.getoption("--real-device"):
        real_driver = AppiumUIDriver(udid=request.config.getoption("--udid"))
        yield real_driver
        real_driver.quit()
    else:
        mock_driver = MockUIDriver(vehicle_bus=vehicle_bus)
        yield mock_driver
        mock_driver.quit()


@pytest.fixture
def home_screen(driver) -> HomeScreen:
    driver.launch_app("com.oem.ivi.launcher")
    return HomeScreen(driver)


@pytest.fixture
def failure_analyzer() -> FailureAnalyzer:
    return FailureAnalyzer()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call):
    """On failure, dump a screenshot (or its mock equivalent) into results/
    named after the failing test, so a run's artifacts are easy to triage."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver is not None:
            RESULTS_DIR.mkdir(exist_ok=True)
            safe_name = item.nodeid.replace("/", "_").replace("::", "__")
            ext = getattr(driver, "SCREENSHOT_EXT", ".png")
            driver.take_screenshot(str(RESULTS_DIR / f"{safe_name}{ext}"))
