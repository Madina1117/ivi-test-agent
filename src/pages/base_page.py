"""Base class for the Page Object Model used across the HMI test suites."""
from __future__ import annotations

from src.device.ui_driver import Locator, UIDriverBase


class BasePage:
    def __init__(self, driver: UIDriverBase):
        self.driver = driver

    def _loc(self, element_id: str, by: str = "id") -> Locator:
        return Locator(element_id=element_id, by=by)

    def tap(self, element_id: str) -> None:
        self.driver.tap(self._loc(element_id))

    def text_of(self, element_id: str) -> str:
        return self.driver.get_text(self._loc(element_id))

    def is_displayed(self, element_id: str) -> bool:
        return self.driver.is_displayed(self._loc(element_id))

    def is_enabled(self, element_id: str) -> bool:
        return self.driver.is_enabled(self._loc(element_id))

    def type_text(self, element_id: str, text: str) -> None:
        self.driver.input_text(self._loc(element_id), text)
