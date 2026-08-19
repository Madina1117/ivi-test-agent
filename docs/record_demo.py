"""Drives the real MockUIDriver/page-object stack through a short narrative
and screenshots the HMI mockup after each step, so the demo GIF shows actual
framework state changes rather than a hand-animated mockup.

Not part of the test suite - a one-off asset generator for docs/README.
Usage: python docs/record_demo.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.device.mock_driver import MockUIDriver  # noqa: E402
from src.pages.home_screen import HomeScreen  # noqa: E402
from src.vehicle.vehicle_bus_simulator import VehicleBusSimulator  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DOCS_DIR = Path(__file__).resolve().parent
TEMPLATE = DOCS_DIR / "hmi" / "template.html"
FRAMES_DIR = DOCS_DIR / "hmi" / "frames"
OUT_GIF = DOCS_DIR / "hmi-demo.gif"

vehicle_bus = VehicleBusSimulator()
driver = MockUIDriver(vehicle_bus=vehicle_bus)
home = HomeScreen(driver)
frame_i = 0


def snapshot(step_label: str, dwell_frames: int = 1) -> None:
    global frame_i
    s = driver.state
    state = {
        "screen": s.screen,
        "step_label": step_label,
        "bt_connected_device": s.bt_connected_device,
        "bt_call_active": s.bt_call_active,
        "media_source": s.media_source,
        "media_playing": s.media_playing,
        "media_track": s.media_track,
        "media_volume": s.media_volume,
        "gps_locked": s.gps_locked,
        "route_active": s.route_active,
        "nav_destination": s.nav_destination,
        "projection_active": s.projection_active,
        "voice_listening": s.voice_listening,
        "voice_last_command": s.last_voice_command,
        "climate_temp_c": s.climate_temp_c,
        "day_night_mode": "night" if vehicle_bus.headlights_on else "day",
        "wifi_connected": s.wifi_connected,
        "hotspot_enabled": s.hotspot_enabled,
        "cellular_active": s.cellular_active,
        "ota_status": s.ota_status,
    }
    html = TEMPLATE.read_text().replace("__STATE_JSON__", json.dumps(state))
    frame_html = FRAMES_DIR / "frame.html"
    frame_html.write_text(html)

    for _ in range(dwell_frames):
        out_png = FRAMES_DIR / f"frame_{frame_i:03d}.png"
        subprocess.run(
            [
                CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                f"--screenshot={out_png}", "--window-size=1000,660",
                frame_html.as_uri(),
            ],
            check=True, capture_output=True,
        )
        frame_i += 1


def main() -> None:
    if FRAMES_DIR.exists():
        shutil.rmtree(FRAMES_DIR)
    FRAMES_DIR.mkdir(parents=True)

    home.driver.launch_app("com.oem.ivi.launcher")
    snapshot("System boot complete", dwell_frames=2)

    bt = home.open_bluetooth()
    snapshot("Opening Bluetooth settings")
    bt.pair_new_device()
    bt.connect_known_device()
    snapshot("Paired + connected known device", dwell_frames=2)

    media = home.open_media()
    snapshot("Opening Media")
    media.select_source("bluetooth")
    media.play_pause()
    snapshot("Streaming over A2DP", dwell_frames=2)

    nav = home.open_navigation()
    snapshot("Opening Navigation")
    nav.acquire_gps()
    nav.set_destination("221B Baker Street")
    nav.start_route()
    snapshot("GPS locked, route active", dwell_frames=2)

    voice = home.open_voice_assistant()
    snapshot("Opening Voice Assistant")
    voice.wake()
    snapshot("Wake word detected, command recognized", dwell_frames=2)

    climate = home.open_climate()
    snapshot("Opening Climate")
    climate.increase_temp(degrees=2)
    vehicle_bus.set_headlights(True)
    snapshot("Headlights on -> night mode engaged", dwell_frames=2)

    conn = home.open_connectivity()
    snapshot("Opening Connectivity")
    conn.connect_known_wifi()
    snapshot("WiFi connected", dwell_frames=2)

    diag = home.open_diagnostics()
    snapshot("Opening Diagnostics")
    diag.start_ota_update()
    snapshot("OTA update downloading", dwell_frames=3)

    subprocess.run(
        [
            "ffmpeg", "-y", "-framerate", "1",
            "-i", str(FRAMES_DIR / "frame_%03d.png"),
            "-vf", "fps=8,scale=1000:-1:flags=lanczos,split[s0][s1];"
                   "[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=bayer",
            str(OUT_GIF),
        ],
        check=True, capture_output=True,
    )
    print(f"wrote {OUT_GIF} ({frame_i} frames)")


if __name__ == "__main__":
    main()
