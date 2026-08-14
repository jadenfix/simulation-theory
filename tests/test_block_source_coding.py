from fractions import Fraction

from simtheory.block_source_coding import exact_iid_block_prefix_code, product_distribution


def test_product_distribution_is_exact():
    p = (Fraction(3, 4), Fraction(1, 4))
    block = product_distribution(p, 2)
    assert block == (
        Fraction(9, 16),
        Fraction(3, 16),
        Fraction(3, 16),
        Fraction(1, 16),
    )


def test_block_huffman_respects_entropy_redundancy_bound():
    p = (Fraction(4, 5), Fraction(1, 10), Fraction(1, 10))
    for m in range(1, 5):
        certificate = exact_iid_block_prefix_code(p, m)
        assert certificate.valid
        assert certificate.redundancy_per_symbol_bits < 1 / m + 1e-12


def test_dyadic_source_has_zero_redundancy_for_every_block():
    p = (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4))
    for m in range(1, 5):
        certificate = exact_iid_block_prefix_code(p, m)
        assert certificate.valid
        assert certificate.redundancy_per_symbol_bits < 1e-12


def test_sequence_cap_fails_closed():
    try:
        product_distribution((Fraction(1, 3),) * 3, 8, max_sequences=100)
    except ValueError as error:
        assert "sequence cap" in str(error)
    else:
        raise AssertionError("block enumeration must fail closed above cap")
