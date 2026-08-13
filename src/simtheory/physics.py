"""Physical-computation bounds under known local physics.

These formulas constrain devices governed by the physical assumptions used to
derive them. They do not, without a law-transfer/implementation assumption,
constrain an unknown parent substrate.
"""

from __future__ import annotations

from math import log, log2, pi

BOLTZMANN_J_PER_K = 1.380649e-23
PLANCK_J_S = 6.62607015e-34
HBAR_J_S = PLANCK_J_S / (2.0 * pi)
SPEED_OF_LIGHT_M_PER_S = 299_792_458.0


def landauer_erasure_energy(bit_erasures: float, temperature_kelvin: float) -> float:
    """Minimum dissipated energy n k_B T ln 2 for irreversible erasure."""
    if bit_erasures < 0.0 or temperature_kelvin < 0.0:
        raise ValueError("bit erasures and temperature must be nonnegative")
    return bit_erasures * BOLTZMANN_J_PER_K * temperature_kelvin * log(2.0)


def margolus_levitin_rate(energy_above_ground_joules: float) -> float:
    """Upper rate 2E/(pi*hbar) of orthogonal-state transitions."""
    if energy_above_ground_joules < 0.0:
        raise ValueError("energy must be nonnegative")
    return 2.0 * energy_above_ground_joules / (pi * HBAR_J_S)


def bekenstein_information_bits(energy_joules: float, radius_meters: float) -> float:
    """Bekenstein entropy-bound expression converted to bits."""
    if energy_joules < 0.0 or radius_meters < 0.0:
        raise ValueError("energy and radius must be nonnegative")
    return 2.0 * pi * energy_joules * radius_meters / (
        HBAR_J_S * SPEED_OF_LIGHT_M_PER_S * log(2.0)
    )


def state_identity_bits(distinguishable_states: int) -> float:
    """Information needed to identify one of N distinguishable states."""
    if distinguishable_states < 1:
        raise ValueError("at least one state is required")
    return log2(distinguishable_states)


def required_parent_resource(
    internal_quantity: float,
    explicit_resource_per_internal_unit: float,
) -> float:
    """Apply an explicitly supplied cross-level implementation coefficient.

    The coefficient is not inferred from internal physics. Making it an input
    prevents accidental projection of internal mass/energy into parent cost.
    """
    if internal_quantity < 0.0 or explicit_resource_per_internal_unit < 0.0:
        raise ValueError("quantities must be nonnegative")
    return internal_quantity * explicit_resource_per_internal_unit

GRAVITATIONAL_CONSTANT_M3_KG_S2 = 6.67430e-11


def mass_energy_joules(mass_kg: float) -> float:
    if mass_kg < 0.0:
        raise ValueError("mass must be nonnegative")
    return mass_kg * SPEED_OF_LIGHT_M_PER_S**2


def schwarzschild_radius_meters(mass_kg: float) -> float:
    """Schwarzschild radius 2GM/c^2 for a nonrotating uncharged mass."""
    if mass_kg < 0.0:
        raise ValueError("mass must be nonnegative")
    return 2.0 * GRAVITATIONAL_CONSTANT_M3_KG_S2 * mass_kg / SPEED_OF_LIGHT_M_PER_S**2


def mass_limited_operation_rate(mass_kg: float) -> float:
    """Margolus-Levitin rate after converting an explicit mass to energy."""
    return margolus_levitin_rate(mass_energy_joules(mass_kg))
