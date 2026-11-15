import math
from orbital_engine.calculator import OrbitalCalculator, R_EARTH, MU_EARTH

calc = OrbitalCalculator()

def test_orbital_energy_conservation():
    """Verifies that vis-viva velocity preserves specific mechanical energy."""
    r = R_EARTH + 500000.0  # 500 km
    a = r
    v = calc.orbital_velocity(r, a, MU_EARTH)
    specific_energy = (v**2) / 2.0 - (MU_EARTH / r)
    expected_energy = -MU_EARTH / (2.0 * a)
    assert math.isclose(specific_energy, expected_energy, rel_tol=1e-6)

def test_sun_synchronous_precession_accuracy():
    """Verifies SSO inclination matches standard NASA Goddard tables within 0.05 deg."""
    altitude_m = 600000.0
    inc_deg = calc.sun_synchronous_inclination(altitude_m)
    assert math.isclose(inc_deg, 97.79, abs_tol=0.05)

def test_eclipse_geometry_bounds():
    """Verifies eclipse duration fraction is within physical bounds (35% to 40% for LEO)."""
    altitude_m = 400000.0
    duration_s, pct = calc.eclipse_duration(altitude_m)
    assert 35.0 <= pct <= 40.0
    assert 2000.0 <= duration_s <= 2300.0

def test_rf_link_margin_threshold():
    """Verifies that an under-powered RF link fails the 3.0 dB threshold."""
    # 0.1 Watt transmitter attempting 120 Mbps at 2000 km
    eb_n0 = calc.link_budget_snr_db(
        tx_power_w=0.1, tx_gain_dbi=2.0, rx_gain_dbi=30.0,
        freq_ghz=8.2, range_km=2000.0, data_rate_bps=120e6
    )
    assert eb_n0 < 3.0  # Must fail link margin check

if __name__ == "__main__":
    test_orbital_energy_conservation()
    test_sun_synchronous_precession_accuracy()
    test_eclipse_geometry_bounds()
    test_rf_link_margin_threshold()
    print("All core physics test cases passed successfully.")
