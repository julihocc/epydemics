"""
Core constants for the epydemics library.
"""

RATIOS = ["alpha", "beta", "gamma", "delta"]
LOGIT_RATIOS = ["logit_alpha", "logit_beta", "logit_gamma", "logit_delta"]
FORECASTING_LEVELS = ["lower", "point", "upper"]
COMPARTMENTS = ["A", "C", "S", "I", "R", "D", "V"]
COMPARTMENT_LABELS = {
    "A": "Active",
    "C": "Confirmed",
    "S": "Susceptible",
    "I": "Infected",
    "R": "Recovered",
    "D": "Deaths",
    "V": "Vaccinated",
}
CENTRAL_TENDENCY_METHODS = ["mean", "median", "gmean", "hmean"]
METHOD_NAMES = {
    "mean": "Mean",
    "median": "Median",
    "gmean": "Geometric Mean",
    "hmean": "Harmonic Mean",
}
METHOD_COLORS = {
    "mean": "blue",
    "median": "orange",
    "gmean": "green",
    "hmean": "purple",
}
