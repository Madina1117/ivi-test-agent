"""Suite 07 - climate controls and drive-state-aware HMI lockouts."""
import pytest

from src.vehicle.vehicle_bus_simulator import Gear, Ignition


@pytest.mark.smoke
def test_temperature_increase_and_decrease(home_screen):
    climate = home_screen.open_climate()
    assert climate.current_temp_label() == "21C"

    climate.increase_temp(degrees=3)
    assert climate.current_temp_label() == "24C"

    climate.decrease_temp(degrees=5)
    assert climate.current_temp_label() == "19C"


@pytest.mark.smoke
def test_temperature_clamped_to_valid_range(home_screen):
    climate = home_screen.open_climate()
    climate.increase_temp(degrees=20)
    assert climate.current_temp_label() == "28C"

    climate.decrease_temp(degrees=20)
    assert climate.current_temp_label() == "16C"


@pytest.mark.regression
def test_day_night_mode_follows_headlights(home_screen, vehicle_bus):
    climate = home_screen.open_climate()
    assert climate.day_night_mode() == "day"

    vehicle_bus.set_headlights(True)
    assert climate.day_night_mode() == "night"

    vehicle_bus.set_headlights(False)
    assert climate.day_night_mode() == "day"


@pytest.mark.regression
def test_text_input_locked_above_walking_speed_in_drive(home_screen, vehicle_bus):
    """Same drive-state lockout exercised in suite 04, from the vehicle-bus side."""
    nav = home_screen.open_navigation()
    assert nav.destination_input_enabled()

    vehicle_bus.set_ignition(Ignition.ON)
    vehicle_bus.set_gear(Gear.DRIVE)
    vehicle_bus.set_speed(6)
    assert not nav.destination_input_enabled()

    vehicle_bus.set_speed(3)
    assert nav.destination_input_enabled()
