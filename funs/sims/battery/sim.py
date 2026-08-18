"""Battery degradation as a Simulation wrapping the electrochemical ODE model."""
from __future__ import annotations
import os
import sys
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from fun_sim_core.simulation import Simulation  # noqa: E402


@dataclass
class BatteryConfig:
    cycles: int = 1000
    T: float = 298.0
    SOC: float = 0.5


class BatterySim(Simulation):
    name = "battery"
    default_config = BatteryConfig()
    interactive = False

    def configure(self, overrides=None):
        cfg = self.default_config.__dict__.copy()
        cfg.update(overrides or {})
        self.config = BatteryConfig(**cfg)

    def setup(self):
        from models.degradation_mech import ElectrochemicalDegradation
        self.model = ElectrochemicalDegradation(T=self.config.T, SOC=self.config.SOC)

    def step(self):
        cap = self.model.predict(self.config.cycles)
        self.result = {"cycles": self.config.cycles, "capacity_remaining": float(cap)}
        return self.result