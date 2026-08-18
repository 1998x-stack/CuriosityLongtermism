"""Conway's Game of Life as a core Simulation (headless grid stepping)."""
from __future__ import annotations
import os
import sys
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
from fun_sim_core.simulation import Simulation  # noqa: E402


@dataclass
class ConwayConfig:
    width: int = 80
    height: int = 40
    pattern: str = "glider"  # random | glider
    generations_per_step: int = 5


class ConwaySim(Simulation):
    name = "conway"
    default_config = ConwayConfig()
    interactive = False

    def configure(self, overrides=None):
        cfg = self.default_config.__dict__.copy()
        cfg.update(overrides or {})
        self.config = ConwayConfig(**cfg)

    def setup(self):
        from core.grid_system import ToroidalGrid
        from core.pattern_loader import PatternLoader
        from core.game_rules import conway_rule

        self._conway_rule = conway_rule
        self.grid = ToroidalGrid()
        self.grid.cells = np.zeros((self.config.height, self.config.width), dtype=np.uint8)
        self.grid.width = self.config.width
        self.grid.height = self.config.height
        if self.config.pattern == "glider":
            PatternLoader.glider(self.grid, 10, 10)
        else:
            self.grid.random_init()

    def step(self):
        rule = self._conway_rule
        for _ in range(self.config.generations_per_step):
            new_state = np.zeros_like(self.grid.cells)
            for y in range(self.grid.height):
                for x in range(self.grid.width):
                    neighbors = self.grid.get_neighbors_count(x, y)
                    new_state[y, x] = rule(self.grid.cells[y, x], neighbors)
            self.grid.cells[:, :] = new_state
        self.result = {"alive": int((self.grid.cells > 0).sum())}
        return self.result