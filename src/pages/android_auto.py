from src.pages.base_page import BasePage


class AndroidAutoPage(BasePage):
    """Covers Android Auto / CarPlay-style phone projection onto the head unit."""

    def connect_projection(self) -> None:
        self.tap("auto_connect_projection")

    def disconnect_projection(self) -> None:
        self.tap("auto_disconnect_projection")

    def is_projection_active(self) -> bool:
        return self.is_displayed("auto_projection_active_indicator")
