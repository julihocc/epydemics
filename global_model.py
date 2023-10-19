import pandas as pd
import matplotlib.pyplot as plt
from epydemics import  process_data_from_owid, DataContainer, Model

global_dataframe = process_data_from_owid("owid-covid-data.csv")

global_data_container = DataContainer(
    global_dataframe
)

print(f"Global data container has {global_data_container.data.shape[0]} rows and {global_data_container.data.shape[1]} columns.")
print(f"Global data container has {global_data_container.data.isna().sum().sum()} missing values.")

global_data_container.data[["C", "D", "N"]].plot(
    subplots=True
)
plt.show()

global_data_container.data[["A", "S", "I", "R"]].plot(
    subplots=True
)
plt.show()

global_model = Model(
    global_data_container,
    start="2020-03-01",
    stop="2020-12-31",
)

print(global_model.forecasting_interval)

global_model.create_logit_ratios_model()
global_model.fit_logit_ratios_model()
global_model.forecast_logit_ratios(steps=30)

global_model.run_simulations()

global_model.generate_result()

global_testing_data = global_data_container.data.loc[global_model.forecasting_interval]

for compartment in ["C", "D", "I"]:
    global_model.visualize_results(
        compartment,
        global_testing_data,
        log_response=True)

evaluation = global_model.evaluate_forecast(global_testing_data, save_evaluation=True, filename="global_evaluation.csv")
print(evaluation)






