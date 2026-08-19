from src.pages.base_page import BasePage


class ConnectivitySettingsPage(BasePage):
    def connect_known_wifi(self) -> None:
        self.tap("wifi_connect_known_network")

    def disconnect_wifi(self) -> None:
        self.tap("wifi_disconnect")

    def toggle_hotspot(self) -> None:
        self.tap("hotspot_toggle")

    def toggle_cellular(self) -> None:
        self.tap("cellular_toggle")

    def is_wifi_connected(self) -> bool:
        return self.is_displayed("wifi_connected_indicator")

    def is_hotspot_enabled(self) -> bool:
        return self.is_displayed("hotspot_enabled_indicator")

    def is_cellular_active(self) -> bool:
        return self.is_displayed("cellular_active_indicator")
