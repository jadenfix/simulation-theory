from simtheory.algorithmic import kraft_admissible, multiplicity_inflation, normalized_observational_prior


def test_multiple_descriptions_change_raw_program_mass():
    inflation = multiplicity_inflation([(3, "A"), (4, "A"), (5, "A"), (3, "B")])
    assert inflation["A"] > inflation["B"]


def test_kraft_and_observational_normalization():
    assert kraft_admissible([1, 2, 2])
    assert not kraft_admissible([1, 1, 1])
    prior = normalized_observational_prior([(2, "A"), (3, "A"), (3, "B")])
    assert abs(sum(prior.values()) - 1.0) < 1e-12
    assert prior["A"] > prior["B"]
