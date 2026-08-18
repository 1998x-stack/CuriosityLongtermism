"""Tent game as an interactive Simulation (pygame GUI)."""
from __future__ import annotations
import os
import sys
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from fun_sim_core.simulation import Simulation  # noqa: E402


@dataclass
class TentConfig:
    grid_rows: int = 6
    grid_cols: int = 6


class TentSim(Simulation):
    name = "tent"
    default_config = TentConfig()
    interactive = True

    def configure(self, overrides=None):
        cfg = self.default_config.__dict__.copy()
        cfg.update(overrides or {})
        self.config = TentConfig(**cfg)

    def setup(self):
        # interactive pygame GUI — verify the preserved package is present without
        # importing (avoids requiring pygame at import/registration time).
        if not os.path.isfile(os.path.join(HERE, "main.py")):
            raise FileNotFoundError("tent game package files missing")
        self.result = {"interactive": True}
        return self.result

    def step(self):
        raise NotImplementedError("tent is interactive (pygame GUI); use `visualize`/launch.")

    def visualize(self):
        from main import main as tent_main  # the preserved pygame entrypoint
        tent_main()