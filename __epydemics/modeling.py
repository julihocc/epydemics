import os
import itertools

import numpy as np
import pandas as pd
from collections import OrderedDict

# Import Statsmodels
from statsmodels.tsa.api import VAR

ratios = ["alpha", "beta", "gamma"]
logit_ratios = ["logit_alpha", "logit_beta", "logit_gamma"]


# codes = {
# "A":"Available":, 
# "C": "Confirmed", 
# "S":"Susceptible", 
# "I":"Infectious", 
# "R":"Recovered", 
# "D":"Deceased"
# }


def inverse_logit(x):
    return np.exp(x) / (1 + np.exp(x))


def fit_model(training_data, ic="aic"):
    model = VAR(training_data[logit_ratios])
    model_fitted = model.fit(ic=ic)
    return model_fitted


def forecasting_ratios(
    training_data,
    future,
    model_fitted,
    horizon=0,
    significance_level=0.01,
    lag_order=None,
):
    print("Forecasting ratios")
    if lag_order is None:
        lag_order = model_fitted.k_ar

    forecasting_interval = model_fitted.forecast_interval(
        training_data[logit_ratios].values[-lag_order:],
        horizon,
        alpha=significance_level,
    )

    forecasting = OrderedDict()

    for k, pair in enumerate(zip(ratios, logit_ratios)):
        ratio, lratio = pair
        print(k, ratio, lratio)
        forecasting[lratio] = OrderedDict()
        forecasting[ratio] = OrderedDict()
        forecasting[lratio]["mid"] = pd.Series(
            forecasting_interval[0][:, k], name=f"{lratio}-mid", index=future
        )
        forecasting[ratio]["mid"] = pd.Series(
            inverse_logit(forecasting[lratio]["mid"]), name=f"{ratio}-mid", index=future
        )
        forecasting[lratio]["lower"] = pd.Series(
            forecasting_interval[1][:, k], name=f"{lratio}-lower", index=future
        )
        forecasting[ratio]["lower"] = pd.Series(
            inverse_logit(forecasting[lratio]["lower"]),
            name=f"{ratio}-lower",
            index=future,
        )
        forecasting[lratio]["upper"] = pd.Series(
            forecasting_interval[2][:, k], name=f"{lratio}-upper", index=future
        )
        forecasting[ratio]["upper"] = pd.Series(
            inverse_logit(forecasting[lratio]["upper"]),
            name=f"{ratio}-upper",
            index=future,
        )

    return forecasting


def simulate(training_data, predicted_radii, future):
    ics = training_data[["A", "C", "S", "I", "R", "D"]].iloc[-1:]
    print(ics.index[0])

    simulations = OrderedDict()

    cases = ["mid", "upper", "lower"]

    for triple in itertools.product(cases, cases, cases):
        iteration = ics.copy()
        t0 = ics.index[0]
        alpha = training_data["alpha"][t0]
        beta = training_data["beta"][t0]
        gamma = training_data["gamma"][t0]

        for index, t1 in enumerate(future):
            s = iteration["S"][t0]
            i = iteration["I"][t0]
            a = iteration["A"][t0]
            r = iteration["R"][t0]
            d = iteration["D"][t0]

            S = s - i * alpha * s / a
            I = i + i * alpha * s / a - beta * i - gamma * i
            R = r + beta * i
            D = d + gamma * i
            C = I + R + D
            A = a

            output = [A, C, S, I, R, D]

            iteration.loc[t1] = output

            alpha = predicted_radii["alpha"][triple[0]][t1]
            beta = predicted_radii["beta"][triple[1]][t1]
            gamma = predicted_radii["gamma"][triple[2]][t1]

            t0 = t1

        simulations[tuple(triple)] = iteration

    return simulations


def simulate_R0(fc):
    simulations = OrderedDict()

    cases = ["mid", "upper", "lower"]

    for triple in itertools.product(cases, cases, cases):
        alpha = fc["alpha"][triple[0]]
        beta = fc["beta"][triple[1]]
        gamma = fc["gamma"][triple[2]]
        simulations[triple] = OrderedDict()
        simulations[triple]["R0"] = alpha / (beta + gamma)

    return simulations
