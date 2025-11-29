"""
Weighted Cohesion Score (WCS) and Dissolution Risk (DR)

Minimal implementation matching:
"Weighted Cohesion Score v1.4.1" – Steven F. Srebranig (2025)

Concept
-------

For each decision option (or future-self branch), the user scores:

    F  = Fit       (0.0 to 1.0)
    P  = Phase     (0.0 to 1.0)
    D  = Dissolution (0.0 to 1.0)

WCS combines these into a single cohesion score:

    D* = 1 - D     (anti-dissolution: higher is better)
    WCS = (wF * F + wP * P + wD_star * D*) / (wF + wP + wD_star)

Dissolution Risk (DR) then integrates raw D and WCS:

    DR = lambda_ * D + (1 - lambda_) * (1 - WCS)

By default, lambda_ ~ 0.7: raw dissolution dominates, but low WCS also
raises risk. A high-Dissolution veto can be applied if D exceeds some
threshold (e.g., 0.8), marking an option as unacceptable regardless of DR.
"""

from dataclasses import dataclass
from typing import List, Optional


def wcs(
    F: float,
    P: float,
    D: float,
    wF: float = 1.0,
    wP: float = 1.0,
    wD_star: float = 1.0,
) -> float:
    """
    Compute the Weighted Cohesion Score for a single option.

    Args:
        F: Fit score in [0, 1].
        P: Phase score in [0, 1].
        D: Dissolution score in [0, 1].
        wF: weight for Fit.
        wP: weight for Phase.
        wD_star: weight for D* = 1 - D.

    Returns:
        WCS in [0, 1]. Returns 0.0 if all weights are zero.
    """
    # Clamp inputs defensively.
    F = max(0.0, min(1.0, F))
    P = max(0.0, min(1.0, P))
    D = max(0.0, min(1.0, D))

    D_star = 1.0 - D

    numerator = wF * F + wP * P + wD_star * D_star
    denom = wF + wP + wD_star

    if denom <= 0.0:
        return 0.0

    return numerator / denom


def dissolution_risk(
    D: float,
    wcs_value: float,
    lambda_: float = 0.7,
) -> float:
    """
    Compute Dissolution Risk (DR) for an option.

    DR integrates raw Dissolution (D) with the lack of cohesion (1 - WCS):

        DR = lambda_ * D + (1 - lambda_) * (1 - WCS)

    Args:
        D: Dissolution score in [0, 1].
        wcs_value: WCS in [0, 1].
        lambda_: mixing parameter in [0, 1]. Default 0.7.

    Returns:
        Dissolution Risk in [0, 1].
    """
    D = max(0.0, min(1.0, D))
    wcs_value = max(0.0, min(1.0, wcs_value))
    lambda_ = max(0.0, min(1.0, lambda_))

    return lambda_ * D + (1.0 - lambda_) * (1.0 - wcs_value)


@dataclass
class OptionResult:
    name: str
    F: float
    P: float
    D: float
    wcs: float
    dr: float
    vetoed: bool


def evaluate_option(
    name: str,
    F: float,
    P: float,
    D: float,
    wF: float = 1.0,
    wP: float = 1.0,
    wD_star: float = 1.0,
    lambda_: float = 0.7,
    veto_threshold: float = 0.8,
) -> OptionResult:
    """
    Convenience function to compute WCS, DR, and high-Dissolution veto
    for a single option.

    Args:
        name: label for the option (e.g., "Jog", "Rest").
        F, P, D: scores in [0, 1].
        wF, wP, wD_star: weights for WCS.
        lambda_: mixing parameter for DR.
        veto_threshold: if D > veto_threshold, mark the option as vetoed.

    Returns:
        OptionResult with WCS, DR, and veto flag.
    """
    w = wcs(F, P, D, wF=wF, wP=wP, wD_star=wD_star)
    dr = dissolution_risk(D, wcs_value=w, lambda_=lambda_)
    vetoed = D > veto_threshold

    return OptionResult(
        name=name,
        F=F,
        P=P,
        D=D,
        wcs=w,
        dr=dr,
        vetoed=vetoed,
    )


def rank_options(
    options: List[OptionResult],
) -> List[OptionResult]:
    """
    Sort options by Dissolution Risk (ascending). Vetoed options are placed last.

    Args:
        options: list of evaluated options.

    Returns:
        New list sorted so that:
            - non-vetoed options with lowest DR come first,
            - vetoed options come last, sorted by DR.
    """
    def sort_key(opt: OptionResult):
        return (opt.vetoed, opt.dr)

    return sorted(options, key=sort_key)
