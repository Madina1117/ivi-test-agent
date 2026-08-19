from __future__ import annotations

from typing import TYPE_CHECKING

from src.pages.base_page import BasePage

if TYPE_CHECKING:
    from src.pages.bluetooth_settings import BluetoothSettingsPage
    from src.pages.climate_hmi import ClimateHmiPage
    from src.pages.connectivity_settings import ConnectivitySettingsPage
    from src.pages.diagnostics import DiagnosticsPage
    from src.pages.media_player import MediaPlayerPage
    from src.pages.navigation import NavigationPage
    from src.pages.voice_assistant import VoiceAssistantPage


class HomeScreen(BasePage):
    def open_bluetooth(self) -> BluetoothSettingsPage:
        from src.pages.bluetooth_settings import BluetoothSettingsPage

        self.tap("nav_bluetooth")
        return BluetoothSettingsPage(self.driver)

    def open_media(self) -> MediaPlayerPage:
        from src.pages.media_player import MediaPlayerPage

        self.tap("nav_media")
        return MediaPlayerPage(self.driver)

    def open_navigation(self) -> NavigationPage:
        from src.pages.navigation import NavigationPage

        self.tap("nav_navigation")
        return NavigationPage(self.driver)

    def open_voice_assistant(self) -> VoiceAssistantPage:
        from src.pages.voice_assistant import VoiceAssistantPage

        self.tap("nav_voice")
        return VoiceAssistantPage(self.driver)

    def open_climate(self) -> ClimateHmiPage:
        from src.pages.climate_hmi import ClimateHmiPage

        self.tap("nav_climate")
        return ClimateHmiPage(self.driver)

    def open_connectivity(self) -> ConnectivitySettingsPage:
        from src.pages.connectivity_settings import ConnectivitySettingsPage

        self.tap("nav_connectivity")
        return ConnectivitySettingsPage(self.driver)

    def open_diagnostics(self) -> DiagnosticsPage:
        from src.pages.diagnostics import DiagnosticsPage

        self.tap("nav_diagnostics")
        return DiagnosticsPage(self.driver)

    def current_screen_name(self) -> str:
        return self.driver.current_screen()
