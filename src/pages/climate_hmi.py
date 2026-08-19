from src.pages.base_page import BasePage


class ClimateHmiPage(BasePage):
    def increase_temp(self, degrees: int = 1) -> None:
        for _ in range(degrees):
            self.tap("climate_temp_up")

    def decrease_temp(self, degrees: int = 1) -> None:
        for _ in range(degrees):
            self.tap("climate_temp_down")

    def current_temp_label(self) -> str:
        return self.text_of("climate_temp_label")

    def day_night_mode(self) -> str:
        return self.text_of("day_night_mode_label")
