from pydantic import model_validator

from env import Accident, Lambda


# TODO: Figure out what's wrong here
class OptimalInformationDesignEnv:
    
    @model_validator(mode="after")
    def validate_tau(self):
        ub = self.D - (self.cost_diff) / (self.alpha_1_a + self.alpha_2)
        lb = self.D - (self.cost_diff) / (self.alpha_1_n + self.alpha_2)
        if not (self.alpha_1_a > self.alpha_2 > self.alpha_1_n):
            raise ValueError("alpha_1_a > alpha_2 > alpha_1_n must hold")
        if not (lb < self.tau < ub):
            raise ValueError("tau must be within the valid range")
        return self

    @property
    def pop_lambda_top(self):
        return (
            1
            - (self.cost_diff) / ((self.alpha_1_a + self.alpha_2) * self.D)
            - self.tau / self.D
        )

    @property
    def pop_lambda_bottom(self):
        return (
            (self.D - self.tau) * (self.alpha_1_top_theta + self.alpha_2)
            - self.cost_diff
        ) / (self.D * self.p * (self.alpha_1_a + self.alpha_2))

    @property
    def p_top(self):
        return (
            1
            / (self.alpha_1_a - self.alpha_1_n)
            * ((self.cost_diff) / (self.D - self.tau) - self.alpha_2 - self.alpha_1_n)
        )

    @property
    def regime(self) -> Lambda:
        if 0 <= self.pop_lambda < self.pop_lambda_bottom:
            return Lambda.L1
        elif self.pop_lambda_bottom <= self.pop_lambda < self.pop_lambda_top:
            return Lambda.L2
        elif self.pop_lambda_top <= self.pop_lambda <= 1:
            return Lambda.L3
        else:
            raise ValueError("Invalid population parameter lambda")

    def pi_star(self, signal: Accident, omega: Accident) -> float:
        if self.regime == Lambda.L1:
            if signal == Accident.a and omega == Accident.a:
                return 1
            elif signal == Accident.n and omega == Accident.n:
                return 1
            else:
                return 0
        elif self.regime == Lambda.L2:
            if signal == Accident.a and omega == Accident.a:
                return (
                    (self.D - self.tau) * (self.alpha_1_top_theta + self.alpha_2)
                    - self.cost_diff
                ) / (
                    self.pop_lambda * self.D * self.p * (self.alpha_1_a + self.alpha_2)
                )
            elif signal == Accident.n and omega == Accident.n:
                return 1
            elif signal == Accident.a and omega == Accident.n:
                return 0
            elif signal == Accident.n and omega == Accident.a:
                return 1 - self.pi_star(Accident.a, Accident.a)
        elif self.regime == Lambda.L3:
            if signal == Accident.a and omega == Accident.a:
                return (
                    (self.D - self.tau) * (self.alpha_1_top_theta + self.alpha_2)
                    - self.cost_diff
                ) / (
                    (
                        (self.D - self.tau) * (self.alpha_1_a + self.alpha_2)
                        - self.cost_diff
                    )
                    * self.p
                )
            elif signal == Accident.n and omega == Accident.n:
                return 1
            elif signal == Accident.a and omega == Accident.n:
                return 0
            elif signal == Accident.n and omega == Accident.a:
                return 1 - self.pi_star(Accident.a, Accident.a)

        raise ValueError(
            f"Invalid signal/omega combination: signal={signal}, omega={omega}"
        )

    @property
    def cost_1_star(self):
        cost = 0
        for signal in Accident:
            p_signal = self.theta(Accident.a) * self.pi_star(
                signal, Accident.a
            ) + self.theta(Accident.n) * self.pi_star(signal, Accident.n)
            f_1 = self.opt_flow_1(signal)
            f_2 = self.opt_flow_2(signal)
            route_1 = (
                self.theta(Accident.a)
                * self.pi_star(signal, Accident.a)
                * self.cost_1_a(f_1)
                + self.theta(Accident.n)
                * self.pi_star(signal, Accident.n)
                * self.cost_1_n(f_1)
            ) / p_signal
            route_2 = self.cost_2(f_2)
            cost += p_signal * min(route_1, route_2)
        return cost

    @property
    def cost_2_star(self):
        route_1 = 0
        route_2 = 0
        for signal in Accident:
            p_signal = self.theta(Accident.a) * self.pi_star(
                signal, Accident.a
            ) + self.theta(Accident.n) * self.pi_star(signal, Accident.n)
            f_1 = self.opt_flow_1(signal)
            f_2 = self.opt_flow_2(signal)
            route_1 += (
                self.theta(Accident.a)
                * self.pi_star(signal, Accident.a)
                * self.cost_1_a(f_1)
            )
            route_1 += (
                self.theta(Accident.n)
                * self.pi_star(signal, Accident.n)
                * self.cost_1_n(f_1)
            )
            route_2 += p_signal * self.cost_2(f_2)
        return min(route_1, route_2)

    @property
    def avg_traffic_spillover_l_pi_star(self):
        if self.regime == Lambda.L1:
            return (
                self.D
                - self.tau
                - (
                    self.cost_diff
                    + self.pop_lambda
                    * self.D
                    * self.p
                    * (1 - self.p)
                    * (self.alpha_1_a - self.alpha_1_n)
                )
                / (self.alpha_1_top_theta + self.alpha_2)
            )
        elif self.regime == Lambda.L2 or self.regime == Lambda.L3:
            return (
                (self.D - self.tau) * (self.alpha_1_top_theta + self.alpha_2)
                - self.cost_diff
            ) / (self.alpha_1_a + self.alpha_2)

    @property
    def avg_traffic_spillover_zero_info(self):
        return max(
            self.D
            - self.tau
            - self.cost_diff / (self.alpha_1_top_theta + self.alpha_2),
            0,
        )

    @property
    def avg_traffic_spillover_complete_info(self):
        f_2_n = self.D - (
            self.cost_diff
            + self.pop_lambda * self.D * self.p * (self.alpha_1_a + self.alpha_2)
        ) / (self.alpha_1_top_theta + self.alpha_2)
        f_2_a = f_2_n + self.pop_lambda * self.D
        return self.p * max(f_2_a - self.tau, 0) + (1 - self.p) * max(
            f_2_n - self.tau, 0
        )

    @property
    def avg_cost_c_star(self):
        return (
            self.pop_lambda * self.cost_1_star
            + (1 - self.pop_lambda) * self.cost_2_star
        )

    @property
    def avg_cost_zero_info(self):
        f_2 = self.D - self.cost_diff / (self.alpha_1_top_theta + self.alpha_2)
        f_1 = self.D - f_2
        route_1 = self.alpha_1_top_theta * f_1 + self.b_1
        route_2 = self.cost_2(f_2)
        return min(route_1, route_2)

    @property
    def avg_cost_complete_info(self):
        g_complete_info = self.cost_diff / (
            (self.alpha_1_n + self.alpha_2) * self.D
        ) - self.cost_diff / ((self.alpha_1_a + self.alpha_2) * self.D)
        if self.pop_lambda <= g_complete_info:
            f_2_n = self.D - (
                self.cost_diff
                + self.pop_lambda * self.D * self.p * (self.alpha_1_a + self.alpha_2)
            ) / (self.alpha_1_top_theta + self.alpha_2)
            f_2_a = f_2_n + self.pop_lambda * self.D
        else:
            f_2_n = self.D - self.cost_diff / (self.alpha_1_n + self.alpha_2)
            f_2_a = self.D - self.cost_diff / (self.alpha_1_a + self.alpha_2)
        f_1_n = self.D - f_2_n
        f_1_a = self.D - f_2_a
        cost_1 = (1 - self.p) * min(
            self.cost_1_n(f_1_n), self.cost_2(f_2_n)
        ) + self.p * min(self.cost_1_a(f_1_a), self.cost_2(f_2_a))
        route_1 = (1 - self.p) * self.cost_1_n(f_1_n) + self.p * self.cost_1_a(f_1_a)
        route_2 = (1 - self.p) * self.cost_2(f_2_n) + self.p * self.cost_2(f_2_a)
        cost_2 = min(route_1, route_2)
        return self.pop_lambda * cost_1 + (1 - self.pop_lambda) * cost_2

    def opt_flow_2(self, signal: Accident) -> float:
        if self.regime == Lambda.L1:
            if signal == Accident.a:
                return self.opt_flow_2(Accident.n) + self.pop_lambda * self.D
            else:
                return self.D - (
                    self.cost_diff
                    + self.pop_lambda
                    * self.D
                    * self.p
                    * (self.alpha_1_a + self.alpha_2)
                ) / (self.alpha_1_top_theta + self.alpha_2)
        elif self.regime == Lambda.L2:
            if signal == Accident.a:
                return self.tau + self.pop_lambda * self.D
            else:
                return self.tau
        elif self.regime == Lambda.L3:
            if signal == Accident.a:
                return self.D - (self.cost_diff) / (self.alpha_1_a + self.alpha_2)
            else:
                return self.tau
        else:
            raise ValueError("Invalid regime")

    def avg_traffic_spillover(self):
        return self.avg_traffic_spillover_l_pi_star
