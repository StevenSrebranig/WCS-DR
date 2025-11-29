"""
example_wcsdr.py

Example from the Weighted Cohesion Score framework:
Compare two options (e.g., "Jog" vs "Rest") using WCS and Dissolution Risk.
"""

from wcsdr import evaluate_option, rank_options


def main():
    # Example scores (0–1). These can be adjusted to match your paper’s table.
    # Jog option
    jog = evaluate_option(
        name="Jog",
        F=0.7,    # Fit
        P=0.4,    # Phase
        D=0.65,   # Dissolution
        wF=1.0,
        wP=1.0,
        wD_star=1.0,
        lambda_=0.7,
        veto_threshold=0.8,
    )

    # Rest option
    rest = evaluate_option(
        name="Rest",
        F=0.55,
        P=0.8,
        D=0.2,
        wF=1.0,
        wP=1.0,
        wD_star=1.0,
        lambda_=0.7,
        veto_threshold=0.8,
    )

    options = [jog, rest]
    ranked = rank_options(options)

    for opt in ranked:
        status = "VETOED" if opt.vetoed else "OK"
        print(
            f"{opt.name}: F={opt.F:.2f}, P={opt.P:.2f}, D={opt.D:.2f}, "
            f"WCS={opt.wcs:.3f}, DR={opt.dr:.3f}, {status}"
        )

    best = ranked[0]
    print(f"\nBest non-vetoed option (lowest DR): {best.name}")


if __name__ == "__main__":
    main()
