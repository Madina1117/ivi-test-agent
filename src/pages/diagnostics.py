from src.pages.base_page import BasePage


class DiagnosticsPage(BasePage):
    def start_ota_update(self) -> None:
        self.tap("ota_start_update")

    def ota_status(self) -> str:
        return self.text_of("ota_status_label")
