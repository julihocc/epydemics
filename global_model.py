import pandas as pd
import matplotlib.pyplot as plt
from epydemics import Model, process_data_from_owid


data_frame = process_data_from_owid("./owid-covid-data.csv")
print(data_frame.info())
print(data_frame.index[0])
print(data_frame.index[-1])
