"""
Orbital Mechanics & Mission Astrodynamics Engine for Orbital Architect (Lucy)
Provides closed-form, scientifically defensible orbital equations and simulation models.
Standard references: Bate, Mueller, White (Fundamentals of Astrodynamics), Wertz (SMAD).
"""

import math
from typing import Dict, Any, Tuple

# Physical & Astrodynamic Constants (SI Units)
G = 6.67430e-11                      # Gravitational constant, m^3 kg^-1 s^-2
MU_EARTH = 3.986004418e14             # Earth gravitational parameter, m^3/s^2
R_EARTH = 6378137.0                   # Earth equatorial radius, m
J2_EARTH = 1.08262668e-3              # Earth second dynamic form factor (oblateness)

MU_MOON = 4.9048695e12                # Lunar gravitational parameter, m^3/s^2
R_MOON = 1737400.0                    # Moon mean radius, m

MU_MARS = 4.282837e13                 # Mars gravitational parameter, m^3/s^2
R_MARS = 3389500.0                    # Mars mean radius, m

MU_SUN = 1.32712440018e20             # Sun gravitational parameter, m^3/s^2
AU_METERS = 149597870700.0            # 1 Astronomical Unit, m
SOLAR_CONSTANT_1AU = 1361.0           # Solar flux at Earth, W/m^2


class OrbitalCalculator:
    """Computes orbital parameters, coverage geometry, and delta-v trade-offs."""

    @staticmethod
    def orbital_period(semi_major_axis_m: float, mu: float = MU_EARTH) -> float:
        """Returns orbital period in seconds: T = 2*pi * sqrt(a^3 / mu)."""
        return 2.0 * math.pi * math.sqrt((semi_major_axis_m ** 3) / mu)

    @staticmethod
    def orbital_velocity(r_m: float, semi_major_axis_m: float, mu: float = MU_EARTH) -> float:
        """Vis-viva equation: v = sqrt(mu * (2/r - 1/a))."""
        return math.sqrt(mu * (2.0 / r_m - 1.0 / semi_major_axis_m))

    @staticmethod
    def eclipse_duration(altitude_m: float, r_body: float = R_EARTH, mu: float = MU_EARTH) -> Tuple[float, float]:
        """
        Calculates eclipse duration and fraction for a circular orbit at zero beta angle.
        Returns: (eclipse_duration_seconds, eclipse_fraction_pct)
        """
        r_orbit = r_body + altitude_m
        t_period = OrbitalCalculator.orbital_period(r_orbit, mu)
        # Angular half-width of Earth shadow: alpha = arcsin(R / r)
        sin_alpha = min(1.0, max(-1.0, r_body / r_orbit))
        alpha_rad = math.asin(sin_alpha)
        # Fraction of orbit in shadow (for circular, coplanar orbit): 2*alpha / (2*pi) = alpha / pi
        eclipse_fraction = alpha_rad / math.pi
        t_eclipse = t_period * eclipse_fraction
        return t_eclipse, eclipse_fraction * 100.0

    @staticmethod
    def sun_synchronous_inclination(altitude_m: float) -> float:
        """
        Calculates required inclination (deg) for a Sun-Synchronous Orbit (SSO) around Earth:
        dOmega/dt = -3/2 * J2 * (R_E / p)^2 * sqrt(mu / a^3) * cos(i) == omega_sun (0.9856 deg/day)
        """
        r_orbit = R_EARTH + altitude_m
        omega_sun_rad_s = (360.0 / 365.2422) * (math.pi / 180.0) / 86400.0  # ~1.991e-7 rad/s

        mean_motion_n = math.sqrt(MU_EARTH / (r_orbit ** 3))
        p = r_orbit  # circular orbit: semi-latus rectum p = a

        # Solve for cos(i)
        factor = -1.5 * J2_EARTH * ((R_EARTH / p) ** 2) * mean_motion_n
        cos_i = omega_sun_rad_s / factor

        if abs(cos_i) > 1.0:
            return 98.0  # Fallback for extreme altitudes outside SSO range
        return math.degrees(math.acos(cos_i))

    @staticmethod
    def atmospheric_drag_decay_rate(altitude_km: float, ballistic_coeff: float = 50.0) -> float:
        """
        Simplified exponential atmospheric density model to compute altitude loss in meters/day.
        ballistic_coeff = mass / (Cd * Area), typical range 30-100 kg/m^2.
        """
        if altitude_km > 1000.0:
            return 0.0  # Negligible drag

        # Standard scale-height table (US Standard Atmosphere approx)
        if altitude_km < 300:
            rho_0, h_0, h_scale = 2.4e-11, 200.0, 37.5
        elif altitude_km < 500:
            rho_0, h_0, h_scale = 3.6e-12, 300.0, 53.0
        elif altitude_km < 750:
            rho_0, h_0, h_scale = 2.2e-13, 500.0, 76.0
        else:
            rho_0, h_0, h_scale = 3.8e-15, 750.0, 110.0

        rho = rho_0 * math.exp(-(altitude_km - h_0) / h_scale)
        r_m = (R_EARTH + altitude_km * 1000.0)
        v = math.sqrt(MU_EARTH / r_m)

        # Delta-a per revolution = -2 * pi * (Cd*A / m) * rho * a^2
        # Convert to altitude loss per day: (revolutions/day) * delta_a
        t_rev = 2.0 * math.pi * r_m / v
        revs_per_day = 86400.0 / t_rev
        delta_a_per_rev_m = 2.0 * math.pi * (1.0 / ballistic_coeff) * rho * (r_m ** 2)
        daily_loss_m = delta_a_per_rev_m * revs_per_day
        return daily_loss_m

    @staticmethod
    def hohmann_transfer_delta_v(r1_m: float, r2_m: float, mu: float = MU_EARTH) -> Tuple[float, float, float]:
        """
        Computes Hohmann transfer velocity increments:
        Returns: (delta_v1, delta_v2, total_delta_v) in m/s.
        """
        v1 = math.sqrt(mu / r1_m)
        v2 = math.sqrt(mu / r2_m)
        v_tx_perigee = math.sqrt(mu * (2.0 / r1_m - 2.0 / (r1_m + r2_m)))
        v_tx_apogee = math.sqrt(mu * (2.0 / r2_m - 2.0 / (r1_m + r2_m)))

        dv1 = abs(v_tx_perigee - v1)
        dv2 = abs(v2 - v_tx_apogee)
        return dv1, dv2, dv1 + dv2

    @staticmethod
    def solar_flux_at_distance(distance_au: float) -> float:
        """Computes solar irradiance in W/m^2 using inverse-square law."""
        return SOLAR_CONSTANT_1AU / (distance_au ** 2)

    @staticmethod
    def link_budget_snr_db(
        tx_power_w: float,
        tx_gain_dbi: float,
        rx_gain_dbi: float,
        freq_ghz: float,
        range_km: float,
        data_rate_bps: float
    ) -> float:
        """
        Calculates received Eb/N0 (dB) for a digital communication link.
        Standard free-space path loss (FSPL).
        """
        freq_hz = freq_ghz * 1e9
        range_m = range_km * 1e3
        c = 299792458.0
        k_boltzmann = 1.380649e-23
        t_sys_kelvin = 290.0  # Standard ground station receiver temperature

        # Free space path loss: FSPL = (4 * pi * d * f / c)^2
        fspl_linear = ((4.0 * math.pi * range_m * freq_hz) / c) ** 2
        fspl_db = 10.0 * math.log10(fspl_linear)

        tx_power_dbw = 10.0 * math.log10(tx_power_w)
        eirp_dbw = tx_power_dbw + tx_gain_dbi

        # Received power Pr (dBW) = EIRP - FSPL + Gr
        pr_dbw = eirp_dbw - fspl_db + rx_gain_dbi

        # Noise spectral density N0 (dBW/Hz) = 10*log10(k * T)
        n0_dbw_hz = 10.0 * math.log10(k_boltzmann * t_sys_kelvin)

        # Eb/N0 = Pr - N0 - 10*log10(BitRate)
        eb_n0_db = pr_dbw - n0_dbw_hz - 10.0 * math.log10(data_rate_bps)
        return eb_n0_db


# Verification Self-Test
if __name__ == "__main__":
    calc = OrbitalCalculator()
    print("--- ORBITAL CALCULATOR TEST SUITE ---")
    
    # 1. ISS / LEO test: 400 km
    leo_alt = 400000.0
    t_leo = calc.orbital_period(R_EARTH + leo_alt) / 60.0
    v_leo = calc.orbital_velocity(R_EARTH + leo_alt, R_EARTH + leo_alt)
    ecl_dur, ecl_pct = calc.eclipse_duration(leo_alt)
    print(f"LEO (400 km): Period = {t_leo:.2f} min, Velocity = {v_leo:.1f} m/s, Eclipse = {ecl_dur/60.0:.1f} min ({ecl_pct:.1f}%)")

    # 2. SSO test: 600 km
    sso_inc = calc.sun_synchronous_inclination(600000.0)
    print(f"SSO (600 km): Required Inclination = {sso_inc:.3f} deg (Expected: ~97.8 deg)")

    # 3. GEO test: 35786 km
    geo_alt = 35786000.0
    t_geo = calc.orbital_period(R_EARTH + geo_alt) / 3600.0
    print(f"GEO (35,786 km): Period = {t_geo:.2f} hours (Expected: ~24.0 hours)")

    # 4. GTO to GEO Hohmann Transfer
    r_perigee = R_EARTH + 250000.0   # 250 km LEO
    r_apogee = R_EARTH + 35786000.0  # GEO
    dv1, dv2, dv_tot = calc.hohmann_transfer_delta_v(r_perigee, r_apogee)
    print(f"Hohmann Transfer (250 km -> GEO): Δv1 = {dv1:.1f} m/s, Δv2 = {dv2:.1f} m/s, Total Δv = {dv_tot:.1f} m/s")

    # 5. Mars Solar Constant
    mars_flux = calc.solar_flux_at_distance(1.524)
    print(f"Mars Solar Irradiance at 1.524 AU: {mars_flux:.1f} W/m^2 (Expected: ~589 W/m^2)")

    # 6. LEO X-Band Link Budget Check
    eb_n0 = calc.link_budget_snr_db(tx_power_w=8.0, tx_gain_dbi=16.5, rx_gain_dbi=42.0, freq_ghz=8.2, range_km=1200.0, data_rate_bps=120e6)
    print(f"LEO 120 Mbps X-Band Link Eb/N0: {eb_n0:.2f} dB (Margin > 3 dB: {eb_n0 >= 3.0})")
