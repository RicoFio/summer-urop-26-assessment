from src.env import Accident, BaseEnv


class BayesianWardropEnv(BaseEnv):
    @property
    def g_pi(self):
        return (self.cost_diff) / (
            (self.alpha_1_top_beta(Accident.n) + self.alpha_2) * self.D
        ) - (self.cost_diff) / (
            (self.alpha_1_top_beta(Accident.a) + self.alpha_2) * self.D
        )

    def opt_flow_2(self, signal: Accident) -> float:
        if self.g_pi >= self.pop_lambda:
            f_2_star_n = self.D - (
                self.cost_diff
                + self.pop_lambda
                * self.D
                * self.theta(Accident.a)
                * (self.alpha_1_top_beta(Accident.a) + self.alpha_2)
            ) / (self.alpha_1_top_theta + self.alpha_2)
            if signal == Accident.n:
                return f_2_star_n
            else:
                return f_2_star_n + self.pop_lambda * self.D
        else:
            if signal == Accident.n:
                return self.D - (self.cost_diff) / (
                    self.alpha_1_top_beta(Accident.n) + self.alpha_2
                )
            else:
                return self.D - (self.cost_diff) / (
                    self.alpha_1_top_beta(Accident.a) + self.alpha_2
                )
