import matplotlib.pyplot as plt


# Improved version of view_ratios
def view_ratios(ratios, forecasting, testing_data):
    future = testing_data.index
    for ratio in ratios:
        print(len(future), len(forecasting[ratio]["mid"]))

        # Adding legends and labels
        plt.plot(testing_data[ratio], label="Actual Data")
        plt.plot(
            future, forecasting[ratio]["mid"], linestyle="--", label="Forecast Mid"
        )
        plt.plot(
            future, forecasting[ratio]["lower"], linestyle="--", label="Forecast Lower"
        )
        plt.plot(
            future, forecasting[ratio]["upper"], linestyle="--", label="Forecast Upper"
        )

        plt.xlabel("Time")
        plt.ylabel("Value")
        plt.title(f"Ratio: {ratio}")
        plt.xticks(rotation=45)
        plt.grid()
        plt.legend()
        plt.show()


# Improved version of view_data
def view_data(data, layout=(4, -1), figsize=(30, 20)):
    axes = data.plot(subplots=True, layout=layout, figsize=figsize)
    for ax in axes.flatten():
        ax.set_xlabel("Time")
        ax.set_ylabel("Value")
        ax.legend()
    plt.show()


# Improved version of view_simulation_r0
def view_simulation_r0(simulations):
    for key, simula in simulations.items():
        label = "Simulation: " + str(key) if key == ("mid", "mid", "mid") else None
        plt.plot(
            simula.index,
            simula.values,
            linestyle="--" if key == ("mid", "mid", "mid") else ":",
            alpha=0.5,
            label=label,
        )

        # Adding legends and labels
        plt.xlabel("Time")
        plt.ylabel("R0 Value")
        plt.title("R0 Value Over Time")
        plt.xticks(rotation=25)
        plt.grid()
        plt.legend()
    plt.show()


# Improved version of view_simulation
def view_simulation(
    simulations, category, testing_data, logaritmic_scale=False, debug=False
):
    function_for_plot = plt.semilogy if logaritmic_scale else plt.plot
    simulations["actual"] = testing_data
    for key, simula in simulations.items():
        if debug:
            print(key)
        if key == "actual":
            label = "Actual Data"
            linestyle = "-."
            alpha = 1
            color = "red"
        elif key == ("mid", "mid", "mid"):
            label = "Simulation: Mid"
            linestyle = "--"
            alpha = 0.5
            color = "blue"
        else:
            label = None
            linestyle = ":"
            alpha = 0.25
            color = "gray"
        function_for_plot(
            simula.index,
            simula[category],
            label=label,
            linestyle=linestyle,
            alpha=alpha,
            color=color,
        )

        # Adding legends and labels
        plt.xlabel("Time")
        plt.ylabel(f"{category}")
        plt.title(f"{category} Over Time")
        plt.xticks(rotation=25)
        plt.grid()
        plt.legend()
    plt.show()
