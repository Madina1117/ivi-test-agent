"""Suite 05 - phone projection (Android Auto / CarPlay-style mirroring)."""
import pytest

from src.pages.android_auto import AndroidAutoPage


@pytest.mark.smoke
def test_connect_and_disconnect_projection(home_screen):
    auto = AndroidAutoPage(home_screen.driver)
    assert not auto.is_projection_active()

    auto.connect_projection()
    assert auto.is_projection_active()

    auto.disconnect_projection()
    assert not auto.is_projection_active()


@pytest.mark.regression
def test_disconnecting_projection_returns_to_native_home(home_screen):
    auto = AndroidAutoPage(home_screen.driver)
    auto.connect_projection()
    auto.disconnect_projection()

    home_screen.tap("nav_home")
    assert home_screen.current_screen_name() == "home"
