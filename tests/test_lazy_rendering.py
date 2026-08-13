from simtheory.lazy_rendering import minimum_exact_memory_bits, minimum_exact_state_count


def test_predictive_state_bound():
    laws = {(("a",),): [0.5, 0.5], (("b",),): [0.9, 0.1], (("c",),): [0.5, 0.5], (("d",),): [0.1, 0.9]}
    assert minimum_exact_state_count(laws) == 3
    assert minimum_exact_memory_bits(laws) == 2
