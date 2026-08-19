"""Suite 03 - media playback across sources, volume, and track metadata."""
import pytest


@pytest.mark.smoke
def test_play_pause_toggles_playing_state(home_screen):
    media = home_screen.open_media()
    assert not media.is_playing()

    media.play_pause()
    assert media.is_playing()

    media.play_pause()
    assert not media.is_playing()


@pytest.mark.regression
@pytest.mark.parametrize("source", ["usb", "bluetooth", "streaming"])
def test_switch_media_source_updates_track_metadata(home_screen, source):
    media = home_screen.open_media()
    media.select_source(source)
    assert source.capitalize() in media.track_title()


@pytest.mark.regression
def test_selecting_unknown_source_raises(home_screen):
    media = home_screen.open_media()
    with pytest.raises(ValueError):
        media.select_source("cassette")


@pytest.mark.smoke
def test_volume_respects_upper_and_lower_bounds(home_screen):
    media = home_screen.open_media()

    media.volume_up(times=50)
    assert media.volume_level() == 20

    media.volume_down(times=50)
    assert media.volume_level() == 0
