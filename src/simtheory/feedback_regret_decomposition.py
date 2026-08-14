"""Exact additive decomposition of deterministic feedback-regret values.

For the declared information timing hierarchy

    0 = R_clairvoyant <= R_current <= R_delayed <= R_open,

the total open-loop regret decomposes exactly into three nonnegative pieces:

    R_open
      = (R_open - R_delayed)
      + (R_delayed - R_current)
      + R_current.

The terms respectively quantify the value of one-period-delayed law feedback,
the incremental value of observing the current law before choosing the current
codebook, and the residual value of complete future path foresight beyond
current-law feedback.

A source-independent shared open-loop mixture supplies a fourth resource with
benefit ``R_open - R_shared``.  That benefit is recorded separately rather than
inserted into the deterministic information telescope: public randomization and
source-law information are not generally ordered and a hybrid extensive-form
game would need to be specified before their values could be added.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .feedback_regret import DriftInformationRegretCertificate


@dataclass(frozen=True)
class FeedbackRegretDecomposition:
    certificate: DriftInformationRegretCertificate
    delayed_feedback_value: Fraction
    current_law_timing_value: Fraction
    future_foresight_value: Fraction
    shared_open_loop_randomization_value: Fraction

    @property
    def deterministic_total(self) -> Fraction:
        return (
            self.delayed_feedback_value
            + self.current_law_timing_value
            + self.future_foresight_value
        )

    @property
    def valid(self) -> bool:
        certificate = self.certificate
        return (
            certificate.valid
            and self.delayed_feedback_value
            == certificate.open_loop_value - certificate.delayed_value
            and self.current_law_timing_value
            == certificate.delayed_value - certificate.current_value
            and self.future_foresight_value == certificate.current_value
            and self.shared_open_loop_randomization_value
            == certificate.open_loop_value - certificate.shared_open_loop_value
            and self.deterministic_total == certificate.open_loop_value
            and self.delayed_feedback_value >= 0
            and self.current_law_timing_value >= 0
            and self.future_foresight_value >= 0
            and self.shared_open_loop_randomization_value >= 0
        )


def decompose_feedback_regret(
    certificate: DriftInformationRegretCertificate,
) -> FeedbackRegretDecomposition:
    """Return the exact deterministic information telescope and shared gain."""

    if not certificate.valid:
        raise ValueError("feedback-regret certificate must be valid")
    result = FeedbackRegretDecomposition(
        certificate,
        certificate.open_loop_value - certificate.delayed_value,
        certificate.delayed_value - certificate.current_value,
        certificate.current_value,
        certificate.open_loop_value - certificate.shared_open_loop_value,
    )
    if not result.valid:
        raise AssertionError("feedback-regret decomposition failed validation")
    return result
