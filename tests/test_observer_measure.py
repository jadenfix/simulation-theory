from simtheory.observer_measure import descendant_resource_bound, finite_descendant_resource


def test_resource_bound():
    assert finite_descendant_resource(1.0, 0.5, 8) < descendant_resource_bound(1.0, 0.5)
