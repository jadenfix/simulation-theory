"""Exact experiment-subset interaction geometry on a finite model lattice.

This module isolates a static subproblem of active experiment design.  A finite
set of globally fixed models induces source laws on one declared zero-error
confusion graph.  Each deterministic experiment reveals one finite label of the
model.  Observing a subset of experiments partitions the model family by their
joint label signatures.  Inside each resulting observation cell, the controller
chooses a zero-error prefix code, either deterministically or using an explicit
independent public seed.

Every subset is evaluated against one fixed model-informed oracle vector: for
model m, O_m is the minimum expected code length when m is known.  This removes
moving-benchmark effects.  The full set function over experiment subsets can
then be transformed by the Boolean-lattice Möbius transform.  Nonzero higher-
order coefficients expose genuine interactions among revealed latent facts.

A k-bit parity construction gives a particularly sharp result.  Models are all
k-bit strings, experiment j reveals bit j, and the downstream source symbol is
the parity bit.  Every strict subset of experiments leaves both parities possible
inside every observation cell, while all k bits determine parity.  On complete
confusion K3, the deterministic benchmark gap is one for every strict subset
and zero for the full set; after public-seed convexification it is one-half for
every strict subset and zero for the full set.  Consequently every nonempty
proper Möbius coefficient vanishes and the unique top-order coefficient is -1
(deterministic) or -1/2 (mixed).

All probabilities and game calculations use exact rational arithmetic.  Search
spaces are bounded explicitly.  These are internal finite decision results, not
empirical evidence for simulation.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Mapping, Sequence

from .confusion_graphs import ConfusionGraph
from .prior_weighted_codes import RationalInput
from .robust_prior_codes import (
    ExactZeroSumGameCertificate,
    RobustCandidateEnumeration,
    enumerate_robust_code_candidates,
    solve_exact_zero_sum_game,
)


@dataclass(frozen=True)
class DeterministicModelExperiment:
    name: str
    labels: tuple[int, ...]

    @property
    def valid(self) -> bool:
        return bool(self.name) and bool(self.labels) and all(label >= 0 for label in self.labels)


def deterministic_model_experiment(
    name: str,
    labels: Sequence[int],
) -> DeterministicModelExperiment:
    result = DeterministicModelExperiment(str(name), tuple(int(label) for label in labels))
    if not result.valid:
        raise ValueError("invalid deterministic model experiment")
    return result


@dataclass(frozen=True)
class ObservationCellValue:
    models: tuple[int, ...]
    deterministic_gap: Fraction
    mixed_gap: Fraction
    deterministic_candidate: int
    mixed_game: ExactZeroSumGameCertificate

    @property
    def valid(self) -> bool:
        return (
            bool(self.models)
            and tuple(sorted(set(self.models))) == self.models
            and self.deterministic_gap >= 0
            and self.mixed_gap >= 0
            and self.mixed_gap <= self.deterministic_gap
            and self.deterministic_candidate >= 0
            and self.mixed_game.valid
            and self.mixed_gap == self.mixed_game.value
        )


@dataclass(frozen=True)
class ExperimentSubsetValue:
    subset_mask: int
    experiment_indices: tuple[int, ...]
    cells: tuple[ObservationCellValue, ...]
    deterministic_gap: Fraction
    mixed_gap: Fraction

    @property
    def valid(self) -> bool:
        return (
            self.subset_mask >= 0
            and tuple(sorted(set(self.experiment_indices))) == self.experiment_indices
            and bool(self.cells)
            and all(cell.valid for cell in self.cells)
            and self.deterministic_gap == max(cell.deterministic_gap for cell in self.cells)
            and self.mixed_gap == max(cell.mixed_gap for cell in self.cells)
        )


@dataclass(frozen=True)
class ObservationLatticeCertificate:
    graph: ConfusionGraph
    model_laws: tuple[tuple[Fraction, ...], ...]
    experiments: tuple[DeterministicModelExperiment, ...]
    enumeration: RobustCandidateEnumeration
    oracle_values: tuple[Fraction, ...]
    subset_values: tuple[ExperimentSubsetValue, ...]
    deterministic_mobius: tuple[Fraction, ...]
    mixed_mobius: tuple[Fraction, ...]
    max_experiments: int
    max_subsets: int
    max_game_bases: int

    @property
    def experiment_count(self) -> int:
        return len(self.experiments)

    @property
    def subset_count(self) -> int:
        return 1 << self.experiment_count

    @property
    def valid(self) -> bool:
        if (
            not self.model_laws
            or not self.experiments
            or len(self.oracle_values) != len(self.model_laws)
            or len(self.subset_values) != self.subset_count
            or len(self.deterministic_mobius) != self.subset_count
            or len(self.mixed_mobius) != self.subset_count
            or any(not experiment.valid for experiment in self.experiments)
            or any(len(experiment.labels) != len(self.model_laws) for experiment in self.experiments)
            or any(not value.valid for value in self.subset_values)
            or tuple(value.subset_mask for value in self.subset_values) != tuple(range(self.subset_count))
            or self.experiment_count > self.max_experiments
            or self.subset_count > self.max_subsets
        ):
            return False
        det_values = tuple(value.deterministic_gap for value in self.subset_values)
        mix_values = tuple(value.mixed_gap for value in self.subset_values)
        return (
            self.deterministic_mobius == boolean_mobius_transform(det_values)
            and self.mixed_mobius == boolean_mobius_transform(mix_values)
            and all(
                richer.deterministic_gap <= poorer.deterministic_gap
                and richer.mixed_gap <= poorer.mixed_gap
                for poorer in self.subset_values
                for richer in self.subset_values
                if poorer.subset_mask & richer.subset_mask == poorer.subset_mask
            )
        )


def _validate_law(
    law: Sequence[RationalInput],
    size: int,
) -> tuple[Fraction, ...]:
    values = tuple(Fraction(value) for value in law)
    if len(values) != size or any(value < 0 for value in values) or sum(values, Fraction(0)) != 1:
        raise ValueError("model source law must be a rational probability vector matching graph size")
    return values


def _subset_indices(mask: int, count: int) -> tuple[int, ...]:
    return tuple(index for index in range(count) if mask & (1 << index))


def _observation_cells(
    experiments: Sequence[DeterministicModelExperiment],
    subset: Sequence[int],
    model_count: int,
) -> tuple[tuple[int, ...], ...]:
    by_signature: dict[tuple[int, ...], list[int]] = {}
    for model in range(model_count):
        signature = tuple(experiments[index].labels[model] for index in subset)
        by_signature.setdefault(signature, []).append(model)
    return tuple(
        tuple(models)
        for _, models in sorted(by_signature.items(), key=lambda item: (item[0], tuple(item[1])))
    )


def boolean_mobius_transform(values: Sequence[Fraction]) -> tuple[Fraction, ...]:
    """Return Möbius coefficients on the Boolean subset lattice.

    ``values[mask] = sum_{submask subset mask} mu[submask]``.
    """
    supplied = tuple(Fraction(value) for value in values)
    if not supplied or len(supplied) & (len(supplied) - 1):
        raise ValueError("Boolean-lattice value vector length must be a power of two")
    result = list(supplied)
    bits = (len(supplied) - 1).bit_length()
    for bit in range(bits):
        step = 1 << bit
        for mask in range(len(result)):
            if mask & step:
                result[mask] -= result[mask ^ step]
    return tuple(result)


def boolean_zeta_transform(coefficients: Sequence[Fraction]) -> tuple[Fraction, ...]:
    supplied = tuple(Fraction(value) for value in coefficients)
    if not supplied or len(supplied) & (len(supplied) - 1):
        raise ValueError("Boolean-lattice coefficient vector length must be a power of two")
    result = list(supplied)
    bits = (len(supplied) - 1).bit_length()
    for bit in range(bits):
        step = 1 << bit
        for mask in range(len(result)):
            if mask & step:
                result[mask] += result[mask ^ step]
    return tuple(result)


def exact_observation_lattice_values(
    graph: ConfusionGraph,
    model_laws: Sequence[Sequence[RationalInput]],
    experiments: Sequence[DeterministicModelExperiment],
    *,
    max_experiments: int = 12,
    max_subsets: int = 4096,
    max_game_bases: int = 2_000_000,
    max_vertices: int = 8,
    max_partitions: int = 10000,
    max_candidates: int = 10000,
    max_prefix_assignments: int = 100000,
    max_prefix_shapes: int = 10000,
    max_dominance_pairs: int = 1000000,
) -> ObservationLatticeCertificate:
    laws = tuple(_validate_law(law, graph.vertex_count) for law in model_laws)
    if not laws:
        raise ValueError("at least one model law is required")
    experiment_tuple = tuple(experiments)
    if not experiment_tuple or any(not experiment.valid for experiment in experiment_tuple):
        raise ValueError("at least one valid experiment is required")
    if len({experiment.name for experiment in experiment_tuple}) != len(experiment_tuple):
        raise ValueError("experiment names must be unique")
    if any(len(experiment.labels) != len(laws) for experiment in experiment_tuple):
        raise ValueError("every experiment requires one label per model")
    if len(experiment_tuple) > int(max_experiments):
        raise ValueError("experiment count exceeds configured cap")
    subset_count = 1 << len(experiment_tuple)
    if subset_count > int(max_subsets):
        raise ValueError("experiment subset space exceeds configured cap")

    enumeration = enumerate_robust_code_candidates(
        graph,
        laws,
        max_vertices=max_vertices,
        max_partitions=max_partitions,
        max_candidates=max_candidates,
        max_prefix_assignments=max_prefix_assignments,
        max_prefix_shapes=max_prefix_shapes,
        max_dominance_pairs=max_dominance_pairs,
    )
    candidates = enumeration.candidates
    if not candidates:
        raise AssertionError("zero-error code universe is empty")
    oracle_values = tuple(
        min(candidate.scenario_costs[model] for candidate in candidates)
        for model in range(len(laws))
    )

    cell_cache: dict[tuple[int, ...], ObservationCellValue] = {}

    def cell_value(models: tuple[int, ...]) -> ObservationCellValue:
        cached = cell_cache.get(models)
        if cached is not None:
            return cached
        gaps = tuple(
            tuple(candidate.scenario_costs[model] - oracle_values[model] for model in models)
            for candidate in candidates
        )
        if any(value < 0 for row in gaps for value in row):
            raise AssertionError("model-informed oracle was not minimal")
        best_index = min(
            range(len(candidates)),
            key=lambda index: (max(gaps[index]), gaps[index], index),
        )
        matrix = tuple(
            tuple(gaps[candidate][position] for candidate in range(len(candidates)))
            for position in range(len(models))
        )
        game = solve_exact_zero_sum_game(matrix, max_bases=max_game_bases)
        result = ObservationCellValue(
            models,
            max(gaps[best_index]),
            game.value,
            best_index,
            game,
        )
        if not result.valid:
            raise AssertionError("observation-cell value failed validation")
        cell_cache[models] = result
        return result

    subset_values: list[ExperimentSubsetValue] = []
    for mask in range(subset_count):
        indices = _subset_indices(mask, len(experiment_tuple))
        cells = tuple(
            cell_value(models)
            for models in _observation_cells(experiment_tuple, indices, len(laws))
        )
        value = ExperimentSubsetValue(
            mask,
            indices,
            cells,
            max(cell.deterministic_gap for cell in cells),
            max(cell.mixed_gap for cell in cells),
        )
        if not value.valid:
            raise AssertionError("experiment-subset value failed validation")
        subset_values.append(value)

    det = tuple(value.deterministic_gap for value in subset_values)
    mix = tuple(value.mixed_gap for value in subset_values)
    certificate = ObservationLatticeCertificate(
        graph,
        laws,
        experiment_tuple,
        enumeration,
        oracle_values,
        tuple(subset_values),
        boolean_mobius_transform(det),
        boolean_mobius_transform(mix),
        int(max_experiments),
        int(max_subsets),
        int(max_game_bases),
    )
    if not certificate.valid:
        raise AssertionError("observation-lattice certificate failed validation")
    return certificate


def parity_observation_lattice(
    bit_count: int,
    *,
    max_game_bases: int = 2_000_000,
) -> ObservationLatticeCertificate:
    """Construct the exact k-bit parity interaction family on complete K3."""
    k = int(bit_count)
    if k < 1 or k > 10:
        raise ValueError("bit_count must lie in [1,10]")
    graph = ConfusionGraph.from_edges((0, 1, 2), ((0, 1), (0, 2), (1, 2)))
    model_count = 1 << k
    laws = tuple(
        tuple(
            Fraction(1) if symbol == (model.bit_count() & 1) else Fraction(0)
            for symbol in range(3)
        )
        for model in range(model_count)
    )
    experiments = tuple(
        deterministic_model_experiment(
            f"bit-{bit}",
            tuple((model >> bit) & 1 for model in range(model_count)),
        )
        for bit in range(k)
    )
    return exact_observation_lattice_values(
        graph,
        laws,
        experiments,
        max_experiments=max(12, k),
        max_subsets=1 << k,
        max_game_bases=max_game_bases,
    )
