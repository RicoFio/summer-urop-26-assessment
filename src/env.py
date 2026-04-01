from __future__ import annotations
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, model_validator
from enum import Enum


Route = Enum("Route", "r1 r2")
Accident = Enum("Accident", "a n")
Lambda = Enum("Lambda", "L1 L2 L3")


class BaseEnv(BaseModel, ABC):
    # TODO: Fill the missing parameters with correct typing and comments

    @model_validator(mode="after")
    def validate_b_ordering(self):
        if not (self.b_1 < self.b_2):
            raise ValueError("b_1 must be less than b_2")
        return self

    @model_validator(mode="after")
    def validate_alpha_ordering(self):
        if not (self.alpha_1_a > self.alpha_2 > self.alpha_1_n):
            raise ValueError("alpha_1_a > alpha_2 > alpha_1_n must hold")
        return self

    @model_validator(mode="after")
    def validate_total_demand(self):
        if not (self.D > (self.b_2 - self.b_1) / self.alpha_1_n):
            raise ValueError("Total demand D must be positive")
        return self

    def cost_1_a(self, f_1):
        return self.alpha_1_a * f_1 + self.b_1

    def cost_1_n(self, f_1):
        return self.alpha_1_n * f_1 + self.b_1

    def cost_2(self, f_2):
        return self.alpha_2 * f_2 + self.b_2

    @property
    def cost_diff(self):
        raise NotImplementedError("You gotta implement this method in the subclass")

    @property
    def p_top(self):
        return (
            1
            / (self.alpha_1_a - self.alpha_1_n)
            * ((self.cost_diff) / (self.D - self.tau) - self.alpha_2 - self.alpha_1_n)
        )

    def theta(self, state: Accident) -> float:
        if state == Accident.a:
            return self.p
        else:
            return 1 - self.p

    def pi(self, signal: Accident, omega: Accident) -> float:
        if signal == Accident.a:
            return self.theta(omega)
        else:
            return 1 - self.theta(omega)

    def mu(self, omega, signal):
        return self.theta(omega) * self.pi(signal, omega)

    def alpha_1_top(self, beta: float):
        return self.alpha_1_n + beta * (self.alpha_1_a - self.alpha_1_n)

    def big_p(self, signal: Accident):
        return self.theta(Accident.a) * self.pi(signal, Accident.a) + self.theta(
            Accident.n
        ) * self.pi(signal, Accident.n)

    def beta(self, signal: Accident, omega: Accident):
        return self.mu(omega, signal) / (self.big_p(signal))

    def alpha_1_top_beta(self, signal: Accident):
        return self.alpha_1_a * self.beta(
            signal, Accident.a
        ) + self.alpha_1_n * self.beta(signal, Accident.n)

    @property
    def alpha_1_top_theta(self):
        return self.p * self.alpha_1_a + (1 - self.p) * self.alpha_1_n

    @abstractmethod
    def opt_flow_2(self, signal: Accident) -> float:
        raise NotImplementedError("You gotta implement this method in the subclass")

    def opt_flow_1(self, signal: Accident):
        return self.D - self.opt_flow_2(signal)
