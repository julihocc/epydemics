from epydemics import process_data_from_owid, DataContainer, Model
import pandas as pd
import numpy as np

print("Loading data...")
# Load global COVID-19 data
raw_data = process_data_from_owid(iso_code="OWID_WRL")
container = DataContainer(raw_data, window=7)

train_start = "2020-03-01"
train_stop = "2020-12-31"

print(f"Creating Model (VAR, max_lag=1)...")
model_var = Model(
    container,
    start=train_start,
    stop=train_stop,
    forecaster="var"
)

model_var.create_model()
try:
    model_var.fit_model(max_lag=1, ic="aic")
    print("VAR model fitted successfully!")
except Exception as e:
    print(f"VAR fit failed: {e}")

# Prophet
try:
    import prophet
    print("Testing Prophet...")
    model_prophet = Model(
        container,
        start=train_start,
        stop=train_stop,
        forecaster="prophet",
        # NO seasonality args here, as per fix
    )
    model_prophet.create_model()
    model_prophet.fit_model()
    print("Prophet fitted successfully!")
except ImportError:
    print("Prophet not installed.")
except Exception as e:
    print(f"Prophet failed: {e}")
