"""Romantic dynamics model as a core Simulation (couple ODE integration)."""
from __future__ import annotations
import os
import sys
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from fun_sim_core.simulation import Simulation  # noqa: E402
import numpy as np  # noqa: E402


@dataclass
class RomanticConfig:
    t_end: float = 5.0
    y0: tuple = (0.5, 0.5)  # type: ignore


class RomanticSim(Simulation):
    name = "romance"
    default_config = RomanticConfig()
    interactive = False

    def configure(self, overrides=None):
        cfg = self.default_config.__dict__.copy()
        cfg.update(overrides or {})
        self.config = RomanticConfig(**cfg)

    def setup(self):
        from core.models import (PersonalityParams, RomanticType, RomanticDynamics)

        pair = (
            PersonalityParams(a=0.5, b=0.7, type=RomanticType.EAGER_BEAVER),
            PersonalityParams(a=0.7, b=0.5, type=RomanticType.CAUTIOUS_LOVER),
        )
        y0 = np.array(self.config.y0, dtype=float)
        self.system = RomanticDynamics(pair, t_span=(0, self.config.t_end), y0=y0)

    def step(self):
        self.system.solve_ode()
        self.result = {"t_end": self.config.t_end}
        return self.result