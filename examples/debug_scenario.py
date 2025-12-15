import pandas as pd
import numpy as np
from epydemics import DataContainer

# Replicate the code from scenario_analysis_measles.ipynb
dates = pd.date_range(start="2000-01-01", periods=25, freq="YE")

np.random.seed(42)
I = (np.random.poisson(5, 25) * np.random.choice([0, 1, 10], 25, p=[0.6, 0.3, 0.1])).astype(float)

data = pd.DataFrame({
    "I": I,
    "N": [1000.0] * 25,
    "D": [0.0] * 25
}, index=dates)

print("Data types:")
print(data.dtypes)

print("Creating DataContainer...")
try:
    container = DataContainer(data, mode="incidence")
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")
    import traceback
    traceback.print_exc()
