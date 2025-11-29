# WCS-DR
Weighted Cohesion Score (WCS) and Dissolution Risk (DR)

This repository contains a minimal implementation of the Weighted Cohesion Score (WCS) and Dissolution Risk (DR) framework described in:

Weighted Cohesion Score v1.4.1 – Steven F. Srebranig
DOI: 10.5281/zenodo.17691769

For each decision option (or future-self branch), three components are scored by the user on a 0-to-1 scale:

F: Fit
P: Phase
D: Dissolution

The Weighted Cohesion Score combines these into a single cohesion value:

D* = 1 − D
WCS = (wF · F + wP · P + wD* · D*) / (wF + wP + wD*)

Dissolution Risk (DR) integrates raw Dissolution and lack of cohesion:

DR = lambda · D + (1 − lambda) · (1 − WCS)

The mixing parameter lambda typically defaults to 0.7 so that raw Dissolution dominates but low cohesion still increases risk.

A high-Dissolution veto may be applied: if D exceeds a threshold such as 0.8, the option is marked as vetoed regardless of DR.

Files included:

wcsdr.py — core implementation:
• wcs(F, P, D, ...)
• dissolution_risk(D, wcs_value, lambda)
• evaluate_option(...) and rank_options(...)

example_wcsdr.py — small demonstration comparing two options, such as “Jog” vs “Rest.”

Reference
This implementation follows the framework defined in:

Weighted Cohesion Score v1.4.1 – Steven F. Srebranig
DOI: 10.5281/zenodo.17691769


License:
MIT License — free for commercial and noncommercial use with attribution.
