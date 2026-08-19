from src.pages.base_page import BasePage


class NavigationPage(BasePage):
    def acquire_gps(self) -> None:
        self.tap("nav_acquire_gps")

    def set_destination(self, address: str) -> None:
        self.type_text("nav_destination_input", address)

    def start_route(self) -> None:
        self.tap("nav_start_route")

    def cancel_route(self) -> None:
        self.tap("nav_cancel_route")

    def toggle_voice_guidance(self) -> None:
        self.tap("nav_toggle_voice_guidance")

    def destination_input_enabled(self) -> bool:
        return self.is_enabled("nav_destination_input")

    def gps_locked(self) -> bool:
        return self.is_displayed("nav_gps_locked_indicator")

    def route_is_active(self) -> bool:
        return self.is_displayed("nav_route_active_indicator")

    def voice_guidance_enabled(self) -> bool:
        return self.is_displayed("nav_voice_guidance_enabled_indicator")
