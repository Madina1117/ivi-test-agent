from src.pages.base_page import BasePage


class VoiceAssistantPage(BasePage):
    def wake(self) -> None:
        self.tap("voice_wake")

    def last_command(self) -> str:
        return self.text_of("voice_last_command_label")

    def is_listening(self) -> bool:
        return self.is_displayed("voice_listening_indicator")

    def tts_response_played(self) -> bool:
        return self.is_displayed("voice_tts_played_indicator")
