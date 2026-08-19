"""Suite 02 - Bluetooth pairing, audio/call profiles, reconnection."""
import pytest


@pytest.mark.smoke
def test_pair_new_device(home_screen):
    bt = home_screen.open_bluetooth()
    bt.pair_new_device()
    bt.connect_known_device()
    assert bt.connected_device_name() == "Pixel-8-Pro"


@pytest.mark.regression
def test_connect_fails_with_no_known_devices(home_screen):
    bt = home_screen.open_bluetooth()
    with pytest.raises(RuntimeError):
        bt.connect_known_device()


@pytest.mark.smoke
def test_hfp_incoming_call_accept_and_end(home_screen):
    bt = home_screen.open_bluetooth()
    bt.pair_new_device()
    bt.connect_known_device()

    bt.accept_incoming_call()
    assert bt.call_is_active()

    bt.end_call()
    assert not bt.call_is_active()


@pytest.mark.regression
def test_a2dp_media_source_switches_to_bluetooth(home_screen):
    bt = home_screen.open_bluetooth()
    bt.pair_new_device()
    bt.connect_known_device()

    media = home_screen.open_media()
    media.select_source("bluetooth")
    assert "Bluetooth" in media.track_title()
