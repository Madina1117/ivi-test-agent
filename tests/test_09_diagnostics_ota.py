"""Suite 09 - diagnostics logcat triage and OTA update flow."""
from pathlib import Path

import pytest

from src.analysis.failure_analyzer import FailureAnalyzer
from src.utils.logcat import write_logcat_artifact

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


@pytest.mark.regression
@pytest.mark.mock_only
def test_logcat_triage_flags_injected_crash(driver, device_bridge, failure_analyzer: FailureAnalyzer):
    driver.inject_crash("com.oem.ivi.media")
    result = failure_analyzer.analyze(device_bridge.pull_logcat())

    assert not result.is_clean
    assert result.counts["crash"] == 1


@pytest.mark.regression
@pytest.mark.mock_only
def test_logcat_triage_flags_injected_anr(driver, device_bridge, failure_analyzer: FailureAnalyzer):
    driver.inject_anr("com.oem.ivi.navigation")
    result = failure_analyzer.analyze(device_bridge.pull_logcat())

    assert not result.is_clean
    assert result.counts["anr"] == 1


@pytest.mark.smoke
def test_diagnostic_logcat_artifact_is_written(device_bridge):
    logs = device_bridge.pull_logcat()
    out_path = write_logcat_artifact(logs, RESULTS_DIR, "sample_diagnostic_capture")

    assert out_path.exists()
    assert out_path.read_text().strip() != ""


@pytest.mark.smoke
def test_ota_update_starts_and_reports_progress(home_screen):
    diag = home_screen.open_diagnostics()
    assert diag.ota_status() == "idle"

    diag.start_ota_update()
    assert diag.ota_status() == "downloading"


@pytest.mark.regression
@pytest.mark.mock_only
def test_ota_rollback_on_failed_update(home_screen):
    diag = home_screen.open_diagnostics()
    diag.start_ota_update()

    home_screen.driver.set_ota_status("failed")
    assert diag.ota_status() == "failed"

    home_screen.driver.set_ota_status("rolled_back")
    assert diag.ota_status() == "rolled_back"
