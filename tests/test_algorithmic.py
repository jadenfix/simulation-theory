from simtheory.algorithmic import multiplicity_inflation


def test_multiple_descriptions_change_raw_program_mass():
    inflation = multiplicity_inflation([(3, "A"), (4, "A"), (5, "A"), (3, "B")])
    assert inflation["A"] > inflation["B"]
