"""Suite 04 - GPS lock, route planning, and voice guidance."""
import pytest


@pytest.mark.smoke
def test_gps_lock_acquired(home_screen):
    nav = home_screen.open_navigation()
    assert not nav.gps_locked()

    nav.acquire_gps()
    assert nav.gps_locked()


@pytest.mark.smoke
def test_start_and_cancel_route(home_screen):
    nav = home_screen.open_navigation()
    nav.set_destination("221B Baker Street")
    nav.start_route()
    assert nav.route_is_active()

    nav.cancel_route()
    assert not nav.route_is_active()


@pytest.mark.regression
def test_voice_guidance_toggle(home_screen):
    nav = home_screen.open_navigation()
    assert nav.voice_guidance_enabled() is True  # on by default per spec

    nav.toggle_voice_guidance()
    assert nav.voice_guidance_enabled() is False


@pytest.mark.regression
def test_destination_input_locked_while_driving(home_screen, vehicle_bus):
    from src.vehicle.vehicle_bus_simulator import Gear, Ignition

    nav = home_screen.open_navigation()
    vehicle_bus.set_ignition(Ignition.ON)
    vehicle_bus.set_gear(Gear.DRIVE)
    vehicle_bus.set_speed(40)

    assert not nav.destination_input_enabled()
    with pytest.raises(PermissionError):
        nav.set_destination("New destination while driving")
