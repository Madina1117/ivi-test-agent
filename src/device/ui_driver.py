"""Driver abstraction for talking to an Android Automotive / IVI head unit.

`UIDriverBase` is the contract every page object codes against. Two
implementations exist:

- `AppiumUIDriver`  -> drives a real head unit or emulator via Appium +
  UiAutomator2 (used when tests are run with ``--real-device``).
- `MockUIDriver`    -> drives an in-memory virtual head unit (see
  ``mock_driver.py``) so the whole suite is runnable in CI without any
  hardware, emulator, or Appium server.

Page objects never import Appium or the mock directly - they only see this
interface, which keeps the test layer honest to what a real HMI exposes.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Locator:
    """A single, named UI element on the head unit."""

    element_id: str
    by: str = "id"  # id | text | content-desc | xpath


class UIDriverBase(ABC):
    @abstractmethod
    def launch_app(self, package: str) -> None: ...

    @abstractmethod
    def tap(self, locator: Locator) -> None: ...

    @abstractmethod
    def input_text(self, locator: Locator, text: str) -> None: ...

    @abstractmethod
    def get_text(self, locator: Locator) -> str: ...

    @abstractmethod
    def is_displayed(self, locator: Locator) -> bool: ...

    @abstractmethod
    def is_enabled(self, locator: Locator) -> bool: ...

    @abstractmethod
    def wait_for(self, locator: Locator, timeout: float = 5.0) -> bool: ...

    @abstractmethod
    def current_screen(self) -> str: ...

    @abstractmethod
    def take_screenshot(self, out_path: str) -> None: ...

    @abstractmethod
    def quit(self) -> None: ...


class AppiumUIDriver(UIDriverBase):
    """Thin wrapper around Appium's UiAutomator2 driver for real hardware.

    Imports appium lazily so the mock-mode CI path never needs the
    Appium/Selenium dependency chain installed.
    """

    SCREENSHOT_EXT = ".png"

    def __init__(self, udid: str | None = None, app_package: str = "com.oem.ivi.launcher"):
        from appium import webdriver  # noqa: WPS433 - deliberate lazy import
        from appium.options.android import UiAutomator2Options

        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.automation_name = "UiAutomator2"
        options.app_package = app_package
        if udid:
            options.udid = udid
        options.new_command_timeout = 120

        self._driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

    def launch_app(self, package: str) -> None:
        self._driver.activate_app(package)

    def tap(self, locator: Locator) -> None:
        self._find(locator).click()

    def input_text(self, locator: Locator, text: str) -> None:
        el = self._find(locator)
        el.clear()
        el.send_keys(text)

    def get_text(self, locator: Locator) -> str:
        return self._find(locator).text

    def is_displayed(self, locator: Locator) -> bool:
        try:
            return self._find(locator).is_displayed()
        except Exception:
            return False

    def is_enabled(self, locator: Locator) -> bool:
        return self._find(locator).is_enabled()

    def wait_for(self, locator: Locator, timeout: float = 5.0) -> bool:
        from selenium.webdriver.support.ui import WebDriverWait

        try:
            WebDriverWait(self._driver, timeout).until(lambda _: self.is_displayed(locator))
            return True
        except Exception:
            return False

    def current_screen(self) -> str:
        return self._driver.current_activity or "unknown"

    def take_screenshot(self, out_path: str) -> None:
        self._driver.save_screenshot(out_path)

    def quit(self) -> None:
        self._driver.quit()

    def _find(self, locator: Locator):
        from appium.webdriver.common.appiumby import AppiumBy

        by_map = {
            "id": AppiumBy.ID,
            "text": AppiumBy.ANDROID_UIAUTOMATOR,
            "content-desc": AppiumBy.ACCESSIBILITY_ID,
            "xpath": AppiumBy.XPATH,
        }
        return self._driver.find_element(by_map[locator.by], locator.element_id)
