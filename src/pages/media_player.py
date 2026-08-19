from src.pages.base_page import BasePage

_SOURCE_ELEMENTS = {
    "usb": "media_source_usb",
    "bluetooth": "media_source_bluetooth",
    "streaming": "media_source_streaming",
}


class MediaPlayerPage(BasePage):
    def play_pause(self) -> None:
        self.tap("media_play_pause")

    def select_source(self, source: str) -> None:
        if source not in _SOURCE_ELEMENTS:
            raise ValueError(f"unknown media source '{source}'")
        self.tap(_SOURCE_ELEMENTS[source])

    def volume_up(self, times: int = 1) -> None:
        for _ in range(times):
            self.tap("media_volume_up")

    def volume_down(self, times: int = 1) -> None:
        for _ in range(times):
            self.tap("media_volume_down")

    def volume_level(self) -> int:
        return int(self.text_of("media_volume_level"))

    def track_title(self) -> str:
        return self.text_of("media_track_title")

    def is_playing(self) -> bool:
        return self.is_displayed("media_playing_indicator")
