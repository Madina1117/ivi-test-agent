"""Suite 08 - WiFi, hotspot, and cellular data connectivity."""
import pytest


@pytest.mark.smoke
def test_connect_to_known_wifi_network(home_screen):
    conn = home_screen.open_connectivity()
    assert not conn.is_wifi_connected()

    conn.connect_known_wifi()
    assert conn.is_wifi_connected()


@pytest.mark.regression
def test_hotspot_tethering_toggle(home_screen):
    conn = home_screen.open_connectivity()
    assert not conn.is_hotspot_enabled()

    conn.toggle_hotspot()
    assert conn.is_hotspot_enabled()

    conn.toggle_hotspot()
    assert not conn.is_hotspot_enabled()


@pytest.mark.regression
def test_cellular_fallback_when_wifi_drops(home_screen):
    conn = home_screen.open_connectivity()
    conn.connect_known_wifi()
    assert conn.is_wifi_connected()
    assert not conn.is_cellular_active()

    conn.disconnect_wifi()
    assert not conn.is_wifi_connected()
    assert conn.is_cellular_active()
