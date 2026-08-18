"""Matchstick transformation system as a core Simulation (headless data step)."""
from __future__ import annotations
import json
import os
import sys
from dataclasses import dataclass
from typing import Optional

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from fun_sim_core.simulation import Simulation  # noqa: E402

_RULES = os.path.join(HERE, "config", "transformation_rules.json")


@dataclass
class MatchstickConfig:
    rules_file: str = _RULES


class MatchstickSim(Simulation):
    name = "matchstick"
    default_config = MatchstickConfig()
    interactive = False

    def configure(self, overrides=None):
        cfg = self.default_config.__dict__.copy()
        cfg.update(overrides or {})
        self.config = MatchstickConfig(**cfg)

    def setup(self):
        with open(self.config.rules_file, "r", encoding="utf-8") as f:
            self.rules = json.load(f)

    def step(self):
        self.result = {"transformations": len(self.rules or {})}
        return self.result