from simtheory.physics import (
    bekenstein_information_bits,
    landauer_erasure_energy,
    margolus_levitin_rate,
    mass_energy_joules,
    mass_limited_operation_rate,
    schwarzschild_radius_meters,
    required_parent_resource,
    state_identity_bits,
)


def test_local_physical_bounds_are_monotone():
    assert landauer_erasure_energy(2.0, 300.0) == 2.0 * landauer_erasure_energy(1.0, 300.0)
    assert margolus_levitin_rate(2.0) == 2.0 * margolus_levitin_rate(1.0)
    assert bekenstein_information_bits(2.0, 3.0) > bekenstein_information_bits(1.0, 3.0)


def test_cross_level_cost_requires_explicit_coefficient():
    assert required_parent_resource(10.0, 0.2) == 2.0
    assert state_identity_bits(8) == 3.0


def test_mass_based_local_envelope():
    assert mass_energy_joules(2.0) == 2.0 * mass_energy_joules(1.0)
    assert mass_limited_operation_rate(2.0) == 2.0 * mass_limited_operation_rate(1.0)
    assert schwarzschild_radius_meters(2.0) == 2.0 * schwarzschild_radius_meters(1.0)
