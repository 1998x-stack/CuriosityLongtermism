"""Railway network analysis as an interactive Simulation (notebook-ported)."""
from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

from fun_sim_core.simulation import Simulation

REFS_DATA = Path(__file__).resolve().parents[2] / "references" / "data"


@dataclass
class RailwayConfig:
    data_dir: str = str(REFS_DATA)


class RailwaySim(Simulation):
    name = "railway"
    default_config = RailwayConfig()
    interactive = True

    def configure(self, overrides=None):
        cfg = self.default_config.__dict__.copy()
        cfg.update(overrides or {})
        self.config = RailwayConfig(**cfg)

    def setup(self):
        # Data-heavy exploratory sim — verify data present; analysis lives in the
        # supplied data xlsx/shapefiles and the ported notebook.
        data_dir = Path(self.config.data_dir)
        if not data_dir.exists():
            raise FileNotFoundError(f"railway data dir missing: {data_dir}")
        self.result = {"data_files": sorted(p.name for p in data_dir.iterdir())}
        return self.result

    def step(self):
        raise NotImplementedError("railway is interactive (notebook/exploratory).")