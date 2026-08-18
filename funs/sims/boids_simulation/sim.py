"""Boids flocking as a core Simulation (headless system stepping)."""
from __future__ import annotations
import os
import sys
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from fun_sim_core.simulation import Simulation  # noqa: E402


@dataclass
class BoidsConfig:
    num_boids: int = 100
    steps_per_step: int = 1


class BoidsSim(Simulation):
    name = "boids"
    default_config = BoidsConfig()
    interactive = False

    def configure(self, overrides=None):
        cfg = self.default_config.__dict__.copy()
        cfg.update(overrides or {})
        self.config = BoidsConfig(**cfg)

    def setup(self):
        import os
        os.makedirs("logs", exist_ok=True)  # boids writes a relative logs/simulation.log
        import config as bconf
        from boids import BoidsSystem

        b_conf = bconf.BoidsConfig(num_boids=self.config.num_boids)
        self.system = BoidsSystem(b_conf)

    def step(self):
        for _ in range(self.config.steps_per_step):
            self.system.update()
        self.result = {"num_boids": self.config.num_boids}
        return self.result