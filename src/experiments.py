import numpy as np
from matplotlib import pyplot as plt

from env import Accident
from optimal_information_design_env import OptimalInformationDesignEnv


if __name__ == "__main__":
    
    env = OptimalInformationDesignEnv(
        # TODO: fill in the parameters here
    )

    # Verify pop_lambda_top and pop_lambda_bottom calculations
    print(f"pop_lambda_top: {env.pop_lambda_top}")
    print(f"pop_lambda_bottom: {env.pop_lambda_bottom}")

    # Recreate the plots from the paper
    pop_lambda = np.linspace(0, 1, 100)
    envs = [
        OptimalInformationDesignEnv(
            # TODO: fill in the parameters here
        )
        for pl in pop_lambda
    ]

    fig, axs = plt.subplots(2, 2, figsize=(10, 10))

    # Accident information revelation probabilities
    axs[0, 0].plot(
        pop_lambda,
        [e.pi_star(Accident.a, Accident.a) for e in envs],
        linewidth=3,
        label="$\\pi^*(\\boldsymbol{a},\\boldsymbol{a})$",
        color="blue",
    )
    axs[0, 0].set_ylabel(
        "Accident information, $\\pi^*(\\boldsymbol{a}|\\boldsymbol{a})$"
    )
    axs[0, 0].set_ylim(0, 1.01)

    # Equilibrium population costs
    axs[0, 1].plot(
        pop_lambda,
        [e.cost_1_star for e in envs],
        linewidth=3,
        color="blue",
        label="$C^{1*}$",
    )
    axs[0, 1].plot(
        pop_lambda,
        [e.cost_2_star for e in envs],
        linewidth=3,
        color="red",
        label="$C^{2*}$",
    )
    axs[0, 1].set_ylabel("Equilibrium population cost, $C^{1*} and C^{2*}$")
    axs[0, 1].set_ylim(23, 26.5)

    # Average traffic spillover
    axs[1, 0].plot(
        pop_lambda,
        [e.avg_traffic_spillover_l_pi_star for e in envs],
        linewidth=3,
        color="black",
        label="$L(\\pi^*)$",
    )
    axs[1, 0].plot(
        pop_lambda,
        [e.avg_traffic_spillover_zero_info for e in envs],
        linewidth=2,
        color="red",
        label="Zero Info.",
    )
    axs[1, 0].plot(
        pop_lambda,
        [e.avg_traffic_spillover_complete_info for e in envs],
        linewidth=2,
        color="green",
        label="Complete Info.",
    )
    axs[1, 0].set_ylabel("Average traffic spillover, $L(\\pi^*)$")
    axs[1, 0].set_ylim(0, 2)

    # Equilibrium average cost
    axs[1, 1].plot(
        pop_lambda,
        [e.avg_cost_c_star for e in envs],
        linewidth=3,
        color="blue",
        label="$C^*$",
    )
    axs[1, 1].plot(
        pop_lambda,
        [e.avg_cost_complete_info for e in envs],
        linewidth=3,
        linestyle="--",
        color="green",
        label="Complete Info.",
    )
    axs[1, 1].plot(
        pop_lambda,
        [e.avg_cost_zero_info for e in envs],
        linewidth=3,
        linestyle="--",
        color="red",
        label="Zero Info.",
    )
    axs[1, 1].set_ylabel("Equilibrium average cost, $C^*$")
    axs[1, 1].set_ylim(25.2, 26.2)

    for ax in axs.flatten():
        ax.set_xlabel("Fraction of population 1, λ")
        ax.set_xlim(0, 1)
        ax.vlines(env.pop_lambda_bottom, 0, 50, color="gray", linestyle="--", alpha=0.5)
        ax.vlines(env.pop_lambda_top, 0, 50, color="gray", linestyle="--", alpha=0.5)
        ax.legend()
    
    # TODO Food for thought:
    # - How do the plots change as we vary the probability of an accident?
    # - What can we say about the optimal information design problem in the different regimes?
    # - And what are the implications of the three information designs that we have analyzed here?

    plt.show()
