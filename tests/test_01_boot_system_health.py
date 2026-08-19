"""Suite 01 - boot performance and system health of the head unit."""
import pytest

from src.analysis.failure_analyzer import FailureAnalyzer

BOOT_TIME_BUDGET_S = 15.0
MEMORY_BUDGET_MB = {
    "com.oem.ivi.launcher": 300,
    "com.oem.ivi.media": 400,
    "com.oem.ivi.navigation": 600,
}


@pytest.mark.smoke
def test_boot_completes_within_budget(device_bridge):
    boot_time = device_bridge.wait_for_boot_complete(timeout=60)
    assert boot_time <= BOOT_TIME_BUDGET_S, f"boot took {boot_time}s, budget is {BOOT_TIME_BUDGET_S}s"


@pytest.mark.smoke
def test_launcher_starts_after_boot(home_screen):
    assert home_screen.current_screen_name() == "launcher"


@pytest.mark.regression
def test_no_anr_or_crash_during_boot(device_bridge, failure_analyzer: FailureAnalyzer):
    logs = device_bridge.pull_logcat()
    result = failure_analyzer.analyze(logs)
    assert result.is_clean, result.summary()


@pytest.mark.regression
@pytest.mark.parametrize("package", list(MEMORY_BUDGET_MB))
def test_app_memory_within_budget(device_bridge, package):
    used_mb = device_bridge.get_memory_usage_mb(package)
    budget = MEMORY_BUDGET_MB[package]
    assert used_mb <= budget, f"{package} used {used_mb}MB, budget is {budget}MB"


@pytest.mark.smoke
def test_battery_level_reported(device_bridge):
    level = device_bridge.get_battery_level()
    assert 0 <= level <= 100
