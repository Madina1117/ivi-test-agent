"""Suite 06 - voice assistant wake, command recognition, and TTS response."""
import pytest


@pytest.mark.smoke
def test_wake_word_triggers_listening(home_screen):
    voice = home_screen.open_voice_assistant()
    assert not voice.is_listening()

    voice.wake()
    assert voice.is_listening()


@pytest.mark.regression
def test_recognized_command_is_recorded(home_screen):
    voice = home_screen.open_voice_assistant()
    voice.wake()
    assert voice.last_command() == "navigate home"


@pytest.mark.regression
def test_tts_response_plays_after_command(home_screen):
    voice = home_screen.open_voice_assistant()
    voice.wake()
    assert voice.tts_response_played()
