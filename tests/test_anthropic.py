from simtheory.anthropic import WorldModel, full_evidence_presence, observer_number_weighted, reference_sampling


def test_conditioning_rules_can_disagree():
    worlds = [
        WorldModel("small", 0.5, 10.0, 1.0, 0.8),
        WorldModel("large", 0.5, 1000.0, 10.0, 0.2),
    ]
    a = reference_sampling(worlds)
    b = observer_number_weighted(worlds)
    c = full_evidence_presence(worlds)
    assert a != b
    assert b != c
    assert c != a
