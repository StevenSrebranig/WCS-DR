"""
WCS/DR – Weighted Cohesion Score / Distributional Ratio

Minimal, general-purpose implementation.

Concept
-------

We often want to know how well a subject "fits" or "coheres" with a target
profile (group, ideal, policy, character, etc.) across multiple attributes,
each with its own importance.

Weighted Cohesion Score (WCS) compresses that comparison into a single number
in [0, 1]:

    WCS(subject, target) = sum_i w_i * sim_i(subject_i, target_i) / sum_i w_i

- w_i >= 0 is the weight (importance) of attribute i
- sim_i(...) is a similarity function for attribute i, returning a value
  in [0, 1], where 1 = perfect match and 0 = no match

Distributional Ratio (DR) compares two such fits:

    DR(subject; A, B) = WCS(subject, A) / WCS(subject, B)

Values > 1 mean the subject is more coherent with A than B; values < 1 mean
closer to B than A. The method is agnostic to the domain: it can be used for
social integration, policy alignment, character coherence, etc.
"""

from typing import Callable, Iterable, List, Optional, Sequence
import math


SimilarityFunc = Callable[[float, float], float]


def similarity_binary(a: float, b: float) -> float:
    """
    Binary / categorical similarity.

    Returns 1.0 if a == b, else 0.0.

    Suitable for attributes like:
    - religion
    - party membership
    - gender (if encoded)
    - category labels
    """
    return 1.0 if a == b else 0.0


def similarity_scalar(a: float, b: float, scale: float) -> float:
    """
    Scalar similarity on a fixed scale.

    Returns 1 - |a - b| / scale, clipped to [0, 1].

    For example:
        - age on a 0–100 scale
        - income on a normalized 0–1 scale
        - Likert scores on a 0–4 or 0–10 scale
    """
    if scale <= 0.0:
        raise ValueError("scale must be positive.")
    d = abs(a - b) / scale
    return max(0.0, min(1.0, 1.0 - d))


def weighted_cohesion_score(
    subject: Sequence[float],
    target: Sequence[float],
    weights: Optional[Sequence[float]] = None,
    similarity: Optional[Iterable[SimilarityFunc]] = None,
    scales: Optional[Sequence[float]] = None,
) -> float:
    """
    Compute the Weighted Cohesion Score (WCS) between subject and target.

    Args:
        subject: sequence of attribute values for the subject.
        target: sequence of attribute values for the target profile.
        weights: nonnegative weights w_i for each attribute. If None,
                 all attributes are weighted equally.
        similarity: iterable of similarity functions sim_i(a, b) for each
                    attribute. If None, all attributes are assumed to be
                    scalar, and 'scales' must be provided.
        scales: optional per-attribute scales used with similarity_scalar
                when 'similarity' is None.

    Returns:
        WCS in [0, 1]. If all weights are zero, returns 0.0.
    """
    s = list(subject)
    t = list(target)

    if len(s) != len(t):
        raise ValueError("subject and target must have the same length.")

    n = len(s)
    if n == 0:
        return 0.0

    # Weights
    if weights is None:
        w = [1.0] * n
    else:
        w = list(weights)
        if len(w) != n:
            raise ValueError("weights must match subject length.")

    # Similarity functions
    if similarity is not None:
        sims = list(similarity)
        if len(sims) != n:
            raise ValueError("similarity iterable must match subject length.")
    else:
        # Use scalar similarity with shared or per-attribute scales.
        if scales is None:
            raise ValueError(
                "Either 'similarity' must be provided, or 'scales' for scalar attributes."
            )
        scale_list = list(scales)
        if len(scale_list) != n:
            raise ValueError("scales must match subject length.")

        def make_scalar_sim(scale: float) -> SimilarityFunc:
            return lambda a, b, s=scale: similarity_scalar(a, b, s)

        sims = [make_scalar_sim(scale_list[i]) for i in range(n)]

    weighted_sum = 0.0
    weight_total = 0.0

    for i in range(n):
        wi = w[i]
        if wi <= 0.0:
            continue
        sim_val = sims[i](float(s[i]), float(t[i]))
        # Clip in case a custom similarity leaks outside [0, 1].
        sim_val = max(0.0, min(1.0, sim_val))
        weighted_sum += wi * sim_val
        weight_total += wi

    if weight_total <= 0.0:
        return 0.0

    return weighted_sum / weight_total


def distributional_ratio(
    subject: Sequence[float],
    target_a: Sequence[float],
    target_b: Sequence[float],
    weights: Optional[Sequence[float]] = None,
    similarity: Optional[Iterable[SimilarityFunc]] = None,
    scales: Optional[Sequence[float]] = None,
    eps: float = 1e-12,
) -> float:
    """
    Compute the Distributional Ratio (DR) between two targets A and B:

        DR = WCS(subject, A) / WCS(subject, B)

    Args:
        subject: attribute vector for the subject.
        target_a: first reference profile.
        target_b: second reference profile.
        weights, similarity, scales: passed through to weighted_cohesion_score.
        eps: small value to avoid division by zero.

    Returns:
        Ratio in [0, +inf). Values > 1 indicate closer to A than B.
    """
    wcs_a = weighted_cohesion_score(subject, target_a, weights, similarity, scales)
    wcs_b = weighted_cohesion_score(subject, target_b, weights, similarity, scales)

    if wcs_b <= eps:
        if wcs_a <= eps:
            return 1.0  # both near zero: treat as neutral
        return math.inf

    return wcs_a / wcs_b
