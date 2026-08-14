"""Independent exact dual certificates for rational prior polytopes.

The vertex enumerator in :mod:`simtheory.polyhedral_priors` is a primal route.
This module adds two logically independent rational certificates:

* Farkas infeasibility witnesses for an empty transformed halfspace system;
* LP dual multipliers for extremal linear expectations over a nonempty system.

If the last simplex coordinate has been eliminated, write the ambiguity set as

    C x <= d.

Farkas' alternative says this system is infeasible exactly when there is
``y >= 0`` with ``C^T y = 0`` and ``d^T y < 0``.  We normalize ``sum(y)=1``
and search rational basic witnesses.

For a fixed state-value vector ``g``, after elimination the maximization problem
is

    max  g_n + c^T x      subject to C x <= d,

where ``c_j = g_j-g_n``.  Its dual is

    min  g_n + d^T y      subject to C^T y = c, y >= 0.

Minimization is certified by applying the same construction to ``-g``.  Every
reported receipt checks exact rational primal/dual equality; CI success is not
itself used as an optimality argument.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb
from typing import Sequence

from .polyhedral_priors import (
    PolyhedralExpectationCertificate,
    RationalPriorPolytope,
    _solve_square,
    extremal_expectation,
)
from .prior_weighted_codes import RationalInput


def _fraction(value: RationalInput | Fraction | int) -> Fraction:
    if isinstance(value, float):
        raise ValueError("dual inputs must be exact rational values")
    return value if isinstance(value, Fraction) else Fraction(value)


@dataclass(frozen=True)
class FarkasInfeasibilityCertificate:
    """Normalized rational witness that ``C x <= d`` has no feasible point."""

    polytope: RationalPriorPolytope
    multipliers: tuple[Fraction, ...]
    transpose_product: tuple[Fraction, ...]
    bound_product: Fraction
    normalization: Fraction
    support: tuple[int, ...]
    candidate_bases: int
    bases_examined: int
    max_bases: int

    @property
    def valid(self) -> bool:
        rows = self.polytope.transformed_constraints
        d = self.polytope.dimension
        if (
            not self.polytope.empty
            or len(self.multipliers) != len(rows)
            or any(weight < 0 for weight in self.multipliers)
            or self.normalization != sum(self.multipliers, Fraction(0)) != 1
            or self.transpose_product != (Fraction(0),) * d
            or self.bound_product >= 0
            or self.bases_examined > self.candidate_bases
            or self.candidate_bases > self.max_bases
        ):
            return False
        transpose = tuple(
            sum(
                (
                    self.multipliers[index] * rows[index][0][coordinate]
                    for index in range(len(rows))
                ),
                Fraction(0),
            )
            for coordinate in range(d)
        )
        bound = sum(
            (
                self.multipliers[index] * rows[index][1]
                for index in range(len(rows))
            ),
            Fraction(0),
        )
        return (
            transpose == self.transpose_product
            and bound == self.bound_product
            and self.support
            == tuple(index for index, weight in enumerate(self.multipliers) if weight > 0)
        )


def exact_farkas_infeasibility_certificate(
    polytope: RationalPriorPolytope,
    *,
    max_bases: int = 2_000_000,
) -> FarkasInfeasibilityCertificate:
    """Return an exact sparse normalized Farkas witness for an empty polytope.

    The normalized witness polytope has ``d+1`` equality constraints
    (``C^T y=0`` and ``1^T y=1``), so a basic feasible witness needs at most
    ``d+1`` positive multipliers.  The search exhausts all such bases below a
    hard cap and fails closed if no certificate is reconstructed.
    """

    if not polytope.empty:
        raise ValueError("Farkas infeasibility is requested only for an empty polytope")
    rows = polytope.transformed_constraints
    d = polytope.dimension
    cap = int(max_bases)
    if cap < 1:
        raise ValueError("max_bases must be positive")
    if not rows:
        raise AssertionError("simplex transformation must contain inequalities")

    if d == 0:
        candidate_bases = len(rows)
        if candidate_bases > cap:
            raise ValueError("Farkas basis space exceeds configured cap")
        for examined, (_, bound, _) in enumerate(rows, start=1):
            if bound < 0:
                multipliers = tuple(
                    Fraction(1) if index == examined - 1 else Fraction(0)
                    for index in range(len(rows))
                )
                certificate = FarkasInfeasibilityCertificate(
                    polytope,
                    multipliers,
                    tuple(),
                    bound,
                    Fraction(1),
                    (examined - 1,),
                    candidate_bases,
                    examined,
                    cap,
                )
                if not certificate.valid:
                    raise AssertionError("zero-dimensional Farkas receipt failed")
                return certificate
        raise AssertionError("empty zero-dimensional system has no Farkas witness")

    support_size = d + 1
    candidate_bases = comb(len(rows), support_size)
    if candidate_bases > cap:
        raise ValueError("Farkas basis space exceeds configured cap")

    best: tuple[Fraction, tuple[Fraction, ...], int] | None = None
    examined = 0
    rhs = (Fraction(0),) * d + (Fraction(1),)
    for basis in combinations(range(len(rows)), support_size):
        examined += 1
        matrix = tuple(
            tuple(rows[index][0][coordinate] for index in basis)
            for coordinate in range(d)
        ) + (tuple(Fraction(1) for _ in basis),)
        solution = _solve_square(matrix, rhs)
        if solution is None or any(weight < 0 for weight in solution):
            continue
        objective = sum(
            (weight * rows[index][1] for weight, index in zip(solution, basis)),
            Fraction(0),
        )
        if objective >= 0:
            continue
        full = [Fraction(0)] * len(rows)
        for index, weight in zip(basis, solution):
            full[index] = weight
        candidate = (objective, tuple(full), examined)
        if best is None or candidate[0] < best[0]:
            best = candidate

    if best is None:
        raise AssertionError("empty rational polytope did not yield a Farkas witness")
    objective, multipliers, found_at = best
    transpose = tuple(
        sum(
            (
                multipliers[index] * rows[index][0][coordinate]
                for index in range(len(rows))
            ),
            Fraction(0),
        )
        for coordinate in range(d)
    )
    certificate = FarkasInfeasibilityCertificate(
        polytope,
        multipliers,
        transpose,
        objective,
        sum(multipliers, Fraction(0)),
        tuple(index for index, weight in enumerate(multipliers) if weight > 0),
        candidate_bases,
        examined,
        cap,
    )
    if not certificate.valid:
        raise AssertionError("Farkas infeasibility certificate failed validation")
    return certificate


@dataclass(frozen=True)
class PolyhedralExpectationDualCertificate:
    """Exact primal/dual certificate for a linear expectation extremum."""

    primal: PolyhedralExpectationCertificate
    sign: int
    transformed_constant: Fraction
    transformed_objective: tuple[Fraction, ...]
    multipliers: tuple[Fraction, ...]
    transpose_product: tuple[Fraction, ...]
    transformed_dual_value: Fraction
    original_dual_value: Fraction
    support: tuple[int, ...]
    candidate_bases: int
    bases_examined: int
    max_bases: int

    @property
    def valid(self) -> bool:
        polytope = self.primal.polytope
        rows = polytope.transformed_constraints
        d = polytope.dimension
        if (
            not self.primal.valid
            or self.sign not in (-1, 1)
            or len(self.multipliers) != len(rows)
            or any(weight < 0 for weight in self.multipliers)
            or len(self.transformed_objective) != d
            or self.transpose_product != self.transformed_objective
            or self.original_dual_value != self.primal.optimum
            or self.transformed_dual_value != self.sign * self.primal.optimum
            or self.bases_examined > self.candidate_bases
            or self.candidate_bases > self.max_bases
        ):
            return False
        transpose = tuple(
            sum(
                (
                    self.multipliers[index] * rows[index][0][coordinate]
                    for index in range(len(rows))
                ),
                Fraction(0),
            )
            for coordinate in range(d)
        )
        dual = self.transformed_constant + sum(
            (
                self.multipliers[index] * rows[index][1]
                for index in range(len(rows))
            ),
            Fraction(0),
        )
        return (
            transpose == self.transpose_product
            and dual == self.transformed_dual_value
            and self.support
            == tuple(index for index, weight in enumerate(self.multipliers) if weight > 0)
        )


def exact_expectation_primal_dual(
    polytope: RationalPriorPolytope,
    values: Sequence[RationalInput],
    *,
    maximize: bool = True,
    max_bases: int = 2_000_000,
) -> PolyhedralExpectationDualCertificate:
    """Certify an extremal expectation by independent exact LP duality."""

    if polytope.empty:
        raise ValueError("expectation dual requires a nonempty ambiguity set")
    vector = tuple(_fraction(value) for value in values)
    if len(vector) != polytope.state_count:
        raise ValueError("one state value is required per source state")
    primal = extremal_expectation(polytope, vector, maximize=maximize)
    sign = 1 if maximize else -1
    d = polytope.dimension
    rows = polytope.transformed_constraints
    constant = Fraction(sign) * vector[-1]
    objective = tuple(Fraction(sign) * (vector[j] - vector[-1]) for j in range(d))
    cap = int(max_bases)
    if cap < 1:
        raise ValueError("max_bases must be positive")

    if d == 0 or all(value == 0 for value in objective):
        multipliers = (Fraction(0),) * len(rows)
        transformed_value = constant
        certificate = PolyhedralExpectationDualCertificate(
            primal,
            sign,
            constant,
            objective,
            multipliers,
            objective,
            transformed_value,
            Fraction(sign) * transformed_value,
            tuple(),
            1,
            1,
            cap,
        )
        if not certificate.valid:
            raise AssertionError("constant-objective dual certificate failed")
        return certificate

    candidate_bases = comb(len(rows), d)
    if candidate_bases > cap:
        raise ValueError("dual basis space exceeds configured cap")
    best: tuple[Fraction, tuple[Fraction, ...]] | None = None
    examined = 0
    for basis in combinations(range(len(rows)), d):
        examined += 1
        matrix = tuple(
            tuple(rows[index][0][coordinate] for index in basis)
            for coordinate in range(d)
        )
        solution = _solve_square(matrix, objective)
        if solution is None or any(weight < 0 for weight in solution):
            continue
        full = [Fraction(0)] * len(rows)
        for index, weight in zip(basis, solution):
            full[index] = weight
        transformed_value = constant + sum(
            (full[index] * rows[index][1] for index in range(len(rows))),
            Fraction(0),
        )
        candidate = (transformed_value, tuple(full))
        if best is None or candidate[0] < best[0]:
            best = candidate

    if best is None:
        raise AssertionError("bounded nonempty primal did not yield a feasible LP dual")
    transformed_value, multipliers = best
    transpose = tuple(
        sum(
            (
                multipliers[index] * rows[index][0][coordinate]
                for index in range(len(rows))
            ),
            Fraction(0),
        )
        for coordinate in range(d)
    )
    certificate = PolyhedralExpectationDualCertificate(
        primal,
        sign,
        constant,
        objective,
        multipliers,
        transpose,
        transformed_value,
        Fraction(sign) * transformed_value,
        tuple(index for index, weight in enumerate(multipliers) if weight > 0),
        candidate_bases,
        examined,
        cap,
    )
    if not certificate.valid:
        raise AssertionError(
            "polyhedral expectation primal/dual gap is nonzero or receipt invalid"
        )
    return certificate
