from src.pages.base_page import BasePage


class BluetoothSettingsPage(BasePage):
    def pair_new_device(self) -> None:
        self.tap("bt_pair_new_device")

    def connect_known_device(self) -> None:
        self.tap("bt_connect_known_device")

    def connected_device_name(self) -> str:
        return self.text_of("bt_connected_device_label")

    def accept_incoming_call(self) -> None:
        self.tap("bt_accept_call")

    def end_call(self) -> None:
        self.tap("bt_end_call")

    def call_is_active(self) -> bool:
        return self.is_displayed("bt_call_active_indicator")
