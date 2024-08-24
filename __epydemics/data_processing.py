import os

import numpy as np
import pandas as pd

dirname = os.path.dirname(os.path.abspath(__file__))


def filter_for_logit(data):
    condition = (
        (data["alpha"] > 0)
        & (data["beta"] > 0)
        & (data["gamma"] > 0)
        & (data["alpha"] < 1)
        & (data["beta"] < 1)
        & (data["gamma"] < 1)
    )
    return data[condition]


def logit(x):
    return np.log(x / (1 - x))


# def logit_transformation(data):
#     data = data.assign(logit_alpha=logit(data['alpha']))
#     data = data.assign(logit_beta=logit(data['beta']))
#     data = data.assign(logit_gamma=logit(data['gamma']))
#     return data


def logit_transformation(data):
    data.loc[:, "logit_alpha"] = logit(data["alpha"])
    data.loc[:, "logit_beta"] = logit(data["beta"])
    data.loc[:, "logit_gamma"] = logit(data["gamma"])
    return data


def process_data(
    country, total_population=None, window=None, local_file=None, since = None, until=None
):
    if local_file is not None:
        try:
            path = os.path.join(dirname, local_file)
            world_data = pd.read_csv(path)
        except FileNotFoundError:
            raise FileNotFoundError("File not found")
    else:
        try:
            world_data = pd.read_csv(
                "https://covid.ourworldindata.org/data/owid-covid-data.csv"
            )
        except:
            raise ConnectionError("Connection error")

    data = world_data[world_data["location"] == country]

    data.loc[:, "date"] = pd.to_datetime(data["date"]).values.astype("datetime64[D]")

    data = data.set_index("date")

    if since is not None:
        try:
            data = data.loc[since:]
        except KeyError:
            raise KeyError("Date not found")

    if until is not None:
        try:
            data = data.loc[:until]
        except KeyError:
            raise KeyError("Date not found")

    data = data[["total_cases", "total_deaths"]]
    data = data.dropna(how="all")
    data = data.fillna(0)

    first_confirmed = data.index[data["total_cases"] > 0][0]

    print(first_confirmed)

    data = data.loc[first_confirmed:]

    if total_population is None:
        data["N"] = data.loc[first_confirmed].sum(axis=0)
    else:
        data["N"] = total_population
    data.columns = ["C", "D", "N"]

    if window is not None:
        data = data.rolling(window).mean()[window:]

    data = data.assign(R=data["C"].shift(14).fillna(0) - data["D"])
    data = data.assign(I=data["C"] - data["R"] - data["D"])
    data = data.assign(S=data["N"] - data["C"])
    data = data.assign(A=data["S"] + data["I"])
    data = data[["A", "C", "S", "I", "R", "D"]]
    data = data.assign(dC=-data["C"].diff(periods=-1))
    data = data.assign(dA=-data["A"].diff(periods=-1))
    data = data.assign(dS=-data["S"].diff(periods=-1))
    data = data.assign(dI=-data["R"].diff(periods=-1))
    data = data.assign(dR=-data["R"].diff(periods=-1))
    data = data.assign(dD=-data["D"].diff(periods=-1))
    data = data.assign(alpha=(data.A * data.dC) / (data.I * data.S))
    data = data.assign(beta=data.dR / data.I)
    data = data.assign(gamma=data.dD / data.I)
    data = data.assign(R0=data["alpha"] / (data["beta"] + data["gamma"]))

    data = filter_for_logit(data)
    data = logit_transformation(data)

    return data
