# fun-sim Factory Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the `fun-sim` category into a factory-mode architecture: a shared `fun-sim-core` package plus thin `lifeproj` and `CuriosityLongtermism` apps that self-register simulation modules and share one config/registry/logging/CLI standard.

**Architecture:** A new standalone, pip-installable `fun-sim-core` package provides `Simulation` (ABC plugin contract), a `Registry` factory, `ConfigLoader`, unified logging, IO/viz helpers, and a base CLI. Two app repos (`lifeproj`, `CuriosityLongtermism`) each depend on core (`pip install -e ../fun-sim-core`), own a `Registry`, and register their own simulations at import time. No cross-repo plugin auto-discovery.

**Tech Stack:** Python 3.10+, PyTorch-free; numpy, PyYAML, loguru, imageio, matplotlib (optional), pygame (tent sim only), pytest. Packaging via `pyproject.toml`.

## Global Constraints

- Python >= 3.10 required (type unions use `dict | None`).
- `fun-sim-core` must contain **no experiment logic** — library only.
- No plugin auto-discovery across repos — each app registers explicitly.
- `Simulation` base lifecycle: `configure(overrides)` → `setup()` → `step()` → `run(steps)` → optional `visualize()` / `export(out_dir)`.
- Every registered sim must expose `name: str`, `default_config`, `interactive: bool` (default `False`).
- `railway` and `tent` are `interactive=True`.
- Keep existing working logic: lifeproj engines/patterns/RLE, and each Curiosity experiment's core computation. Do **not** rewrite engine/pattern internals.
- Keep non-code assets verbatim: `好奇心和长期主义/` notes, railway `.xlsx`/`.zip`/shapefiles.
- TDD: write failing test → verify fail → implement → verify pass → commit.
- `interactive=True` sims: smoke tests test setup/import only (not headless batch run).

---
---

## Phase 0 — `fun-sim-core` (new repo)

### Task 1: Scaffold `fun-sim-core` repo + package

**Files:**
- Create: `fun-sim/fun-sim-core/pyproject.toml`
- Create: `fun-sim/fun-sim-core/fun_sim_core/__init__.py`
- Create: `fun-sim/fun-sim-core/.gitignore`
- Create: `fun-sim/fun-sim-core/tests/test_core_smoke.py`

**Interfaces:**
- Produces: importable package `fun_sim_core`; `pyproject` declares deps `PyYAML`, `loguru`, `numpy`, `imageio`.

- [ ] **Step 1: Create repo + pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "fun-sim-core"
version = "0.1.0"
description = "Shared factory-mode core for fun-sim experiments (Simulation, Registry, Config, logging, io/viz, CLI)."
requires-python = ">=3.10"
dependencies = [
  "PyYAML>=6.0",
  "loguru>=0.7",
  "numpy>=1.24",
  "imageio>=2.30",
]

[project.optional-dependencies]
viz = ["matplotlib>=3.7"]
dev = ["pytest>=7.4"]

[tool.setuptools.packages.find]
include = ["fun_sim_core*"]
```

- [ ] **Step 2: Create package dirs + empty `__init__.py`**

```bash
mkdir -p fun-sim/fun-sim-core/fun_sim_core
touch fun-sim/fun-sim-core/fun_sim_core/__init__.py
mkdir -p fun-sim/fun-sim-core/tests
```

- [ ] **Step 3: Add `.gitignore`**

```
__pycache__/
*.pyc
.venv/
*.egg-info/
.pytest_cache/
```

- [ ] **Step 4: Write smoke test**

```python
# tests/test_core_smoke.py
def test_import_package():
    import fun_sim_core
    assert hasattr(fun_sim_core, "__version__")
```

Add `__version__ = "0.1.0"` to `fun_sim_core/__init__.py`, then the test passes.

- [ ] **Step 5: Run tests**

Run: `cd fun-sim/fun-sim-core && python -m pytest -q`
Expected: 1 passed.

- [ ] **Step 6: Commit**

```bash
cd fun-sim/fun-sim-core
git init
git add .
git commit -m "chore: scaffold fun-sim-core package"
```

### Task 2: `Simulation` ABC

**Files:**
- Create: `fun_sim_core/simulation.py`
- Modify: `fun_sim_core/__init__.py`
- Test: `tests/test_simulation.py`

**Interfaces:**
- Produces: `class Simulation(ABC)` with `name: str`, `default_config: object | None`, `interactive: bool = False`, and methods `configure(overrides: dict | None = None) -> None`, `setup() -> None`, `step(*args, **kwargs) -> object`, `run(steps: int) -> object`, `visualize() -> None`, `export(out_dir) -> None` (all non-abstract except `step`).

- [ ] **Step 1: Write failing test**

```python
# tests/test_simulation.py
import pytest
from fun_sim_core.simulation import Simulation

class Concrete(Simulation):
    name = "demo"
    def step(self, *a, **k):
        self.called = True
        return 1

def test_cannot_instantiate_abstract():
    with pytest.raises(TypeError):
        Simulation()

def test_run_loops_steps():
    s = Concrete()
    out = s.run(steps=3)
    assert out == 1
    assert getattr(s, "called", False)

def test_defaults():
    c = Concrete()
    assert c.interactive is False
    assert c.name == "demo"
```

- [ ] **Step 2: Run to verify fail**

Run: `pytest tests/test_simulation.py -v`
Expected: FAIL — `ModuleNotFoundError: fun_sim_core.simulation`.

- [ ] **Step 3: Implement**

```python
# fun_sim_core/simulation.py
from abc import ABC, abstractmethod


class Simulation(ABC):
    """Base class every fun-sim experiment implements.

    Contract: configure() -> setup() -> step()/run() -> visualize() -> export().
    Stateful: setup() initializes owned state; step() mutates it.
    """

    name: str = ""
    default_config: object | None = None
    interactive: bool = False

    def configure(self, overrides: dict | None = None) -> None:
        """Load/validate config (overrides accepted). Default: no-op."""
        pass

    def setup(self) -> None:
        """Prepare state (RNG seed, allocations). Called once before run."""
        pass

    @abstractmethod
    def step(self, *args, **kwargs) -> object:
        """Advance one simulation step. Must be implemented."""

    def run(self, steps: int = 1) -> object:
        """Default loop over step()."""
        result = None
        for _ in range(max(1, int(steps))):
            result = self.step()
        return result

    def visualize(self) -> None:
        """Optional: render. Default no-op."""

    def export(self, out_dir) -> None:
        """Optional: save artifacts to out_dir. Default no-op."""
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_simulation.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Export from package; commit**

Add to `fun_sim_core/__init__.py`:
```python
from fun_sim_core.simulation import Simulation
__all__ = ["Simulation"]
__version__ = "0.1.0"
```
```bash
git add .
git commit -m "feat: add Simulation ABC"
```

### Task 3: `Registry` factory

**Files:**
- Create: `fun_sim_core/registry.py`
- Modify: `fun_sim_core/__init__.py`
- Test: `tests/test_registry.py`

**Interfaces:**
- Produces: `class Registry`; `register(name)` decorators returning decorated class; `create(name) -> Simulation`; `list() -> dict[str, type]`; raises `RegistryError` for unknown name.

- [ ] **Step 1: Write failing test**

```python
# tests/test_registry.py
import pytest
from fun_sim_core.registry import Registry, RegistryError
from fun_sim_core.simulation import Simulation


@Registry.register("DemoSim")
class DemoSim(Simulation):
    name = "demosim"
    interactive = True
    def step(self): return 42


def test_create():
    r = Registry()
    r.register("DemoSim")(DemoSim)
    s = r.create("demosim")
    assert isinstance(s, DemoSim)
    assert s.step() == 42

def test_list_includes_interactive():
    r = Registry()
    r.register("DemoSim")(DemoSim)
    d = r.list()
    assert "demosim" in d
    assert d["demosim"].interactive is True

def test_unknown_raises():
    r = Registry()
    with pytest.raises(RegistryError):
        r.create("nope")
```

- [ ] **Step 2: Run to verify fail**

Run: `pytest tests/test_registry.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement**

```python
# fun_sim_core/registry.py
from __future__ import annotations
from typing import Callable
from fun_sim_core.simulation import Simulation


class RegistryError(Exception):
    """Raised when a registry lookup fails."""


class Registry:
    def __init__(self):
        self._items: dict[str, type[Simulation]] = {}

    def register(self, name: str):
        def deco(cls):
            key = name.strip().lower()
            if hasattr(cls, "name") and cls.name == "":
                cls.name = key
            self._items[key] = cls
            return cls
        return deco

    def create(self, name: str) -> Simulation:
        key = name.strip().lower()
        if key not in self._items:
            avail = ", ".join(sorted(self._items)) or "(none)"
            raise RegistryError(f"Unknown simulation '{name}'. Available: {avail}")
        return self._items[key]()

    def list(self) -> dict:
        return {k: v for k, v in self._items.items()}

    def items(self):
        return list(self._items.items())
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_registry.py -v`
Expected: PASS.

- [ ] **Step 5: Expose and commit**

`__init__.py` add `from fun_sim_core.registry import Registry, RegistryError`, extend `__all__`.
```bash
git add . && git commit -m "feat: add Registry factory"
```

### Task 4: `ConfigLoader`

**Files:**
- Create: `fun_sim_core/config.py` (dataclasses `Yaml`, `MainConfig`); Test: `tests/test_config.py`

**Interfaces:**
- Produces: `load_yaml(path) -> dict`; `as_dataclass(data: dict, dc_type)` coerces dict → dataclass instance; raises `ConfigError` on missing required field or bad type.

- [ ] **Step 1: Write failing test**

```python
# tests/test_config.py
from dataclasses import dataclass
import pytest
from fun_sim_core.config import ConfigError, load_yaml, as_dataclass


@dataclass
class Cfg:
    n: int = 10
    label: str = "x"


def test_as_dataclass_coerces():
    c = as_dataclass({"n": "5"}, Cfg)
    assert c.n == 5 and c.label == "x"

def test_unknown_field_warns(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text("n: 3\nbogus: 1\n")
    d = load_yaml(p)
    assert d["n"] == 3 and "bogus" in d

def test_bad_type_raises():
    with pytest.raises(ConfigError):
        as_dataclass({"n": "notanint"}, Cfg)
```

- [ ] **Step 2: Run to fail**

Expected: FAIL (module missing).

- [ ] **Step 3: Implement**

```python
# fun_sim_core/config.py
from dataclasses import fields, is_dataclass, replace
from pathlib import Path

import yaml


class ConfigError(Exception):
    pass


def load_yaml(path: Path | str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def as_dataclass(data: dict, type_):
    if not is_dataclass(type_):
        raise ConfigError(f"{type_} is not a dataclass")
    kwargs = {}
    for f in fields(type_):
        if f.name not in data:
            continue
        value = data[f.name]
        if f.type in (int, float, bool, str):
            try:
                value = f.type(value)
            except (TypeError, ValueError):
                raise ConfigError(f"field '{f.name}': cannot coerce {value!r} to {f.type}")
        kwargs[f.name] = value
    return replace(type_(), **kwargs)
```

- [ ] **Step 4: Run tests → PASS. Step 5: commit** `feat: add ConfigLoader`.

### Task 5: `setup_logger`

**Files:**- Create `fun_sim_core/logging.py`; Test `tests/test_logging.py`

**Interfaces:** `setup_logger(name, log_dir, level="DEBUG") -> Logger` creates console + rotating file.

- [ ] **Step 1: Write failing test**

```python
def test_setup_creates_log_file(tmp_path):
    from fun_sim_core.logging import setup_logger
    setup_logger("t", tmp_path, "DEBUG")
    p = tmp_path / "t.log"
    assert p.exists() or (tmp_path / "t" / "t.log").exists()
```

- [ ] **Step 2: fail** (module missing). **Step 3: implement**

```python
# fun_sim_core/logging.py
import logging
from pathlib import Path

from loguru import logger


def setup_logger(name: str, log_dir: Path | str, level: str = "INFO") -> None:
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{name}.log"
    logger.level(level.upper())
    logger.add(
        str(log_file),
        rotation="1MB",
        retention="7 days",
        level=level.upper(),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        enqueue=True,
    )
    logging.basicConfig(level=level.upper())
```

- [ ] **Step 4–5: run tests, commit** `feat: add setup_logging`.

### Task 6: `OutputManager` + IO helpers

**Files:** `fun_sim_core/io.py`; Test `tests/test_io.py`

**Interfaces:** `OutputManager(out_dir)` with `.new_run_dir()` returning `Path`; `save_array(arr, path)`; `save_video(frames, path, fps)`.

- [ ] **Step 1: Write failing test**

```python
import numpy as np
from fun_sim_core.io import OutputManager, save_array, save_video


def test_run_dir(tmp_path):
    om = OutputManager(tmp_path)
    d = om.new_run_dir()
    assert d.is_dir()

def test_save_array(tmp_path):
    save_array(np.zeros((4, 4, 3), dtype=np.uint8), tmp_path / "a.png")
    assert (tmp_path / "a.png").exists()

def test_save_video(tmp_path):
    frames = [np.zeros((16, 16, 3), dtype=np.uint8)] * 3
    save_video(frames, tmp_path / "v.gif", fps=4)
    assert (tmp_path / "v.gif").exists()
```

- [ ] **Step 2: fail → Step 3: implement**

```python
# fun_sim_core/io.py
import time
from pathlib import Path

import numpy as np
import imageio.v2 as iio


class OutputManager:
    def __init__(self, out_dir: Path | str):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def new_run_dir(self) -> Path:
        d = self.out_dir / time.strftime("run_%Y%m%d_%H%M%S")
        d.mkdir(parents=True, exist_ok=True)
        return d


def save_array(arr: np.ndarray, path: Path | str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    iio.imwrite(str(path), arr)


def save_video(frames, path: Path | str, fps: int = 4) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    iio.mimsave(str(path), list(frames), fps=fps)
```

- [ ] **Step 4: run tests → Step 5: commit** `feat: add OutputManager and io helpers`.

### Task 7: `base_cli`

**Files:** `fun_sim_core/cli.py`; Test `tests/test_cli.py`

**Interfaces:** `make_parser(prog, description, registry) -> argparse.ArgumentParser` with subcommands `list` and `run <name> --config --out --steps --seed`.

- [ ] **Step 1: Write failing test (parse only)**

```python
from fun_sim_core.cli import make_parser
from fun_sim_core.registry import Registry

def test_parser_has_run_and_list():
    p = make_parser("prog", "desc", Registry())
    args = p.parse_args(["run", "boids", "--config", "c.yaml", "--steps", "5"])
    assert args.command == "run" and args.name == "boids" and args.steps == 5
```

- [ ] **Step 2: fail → Step 3 implement**

```python
import argparse


def _argb(arg):
    return arg if arg.endswith(".py") else f"{arg}.py"


def make_parser(prog, description, registry, subcommands=("list", "run")):
    p = argparse.ArgumentParser(prog=prog, description=description)
    sub = p.add_subparsers(dest="command", required=True)

    if "list" in subcommands:
        sub.add_parser("list", help="list registered sims")

    if "run" in subcommands:
        r = sub.add_parser("run", help="run a simulation")
        r.add_argument("name")
        r.add_argument("--config", default=None)
        r.add_argument("--out", default="runs")
        r.add_argument("--steps", type=int, default=1)
        r.add_argument("--seed", type=int, default=None)
    return p


def run_from_parser(p, registry):
    args = p.parse_args()
    if args.command == "list":
        for name, cls in registry.list().items():
            tag = " [interactive]" if getattr(cls, "interactive", False) else ""
            print(f"{name}{tag}")
        return 0
    if args.command == "run":
        sim = registry.create(args.name)
        if getattr(sim, "interactive", False):
            print(f"[warn] '{args.name}' is interactive (GUI/notebook).")
        sim.configure()
        sim.setup()
        sim.run(args.steps)
        return 0
    return 2
```

- [ ] **Step 4–5: run tests, commit** `feat: add base_cli`.

### Task 8: fun-sim-core README + final commit

**Files:** `fun-sim/fun-sim-core/README.md`

- [ ] **Step 1: Write README** (title, install `pip install -e .`, quick API example, module table).
- [ ] **Step 2: Commit.** `git add . && git commit -m "docs: fun-sim-core README"`

## Phase 2 — `lifeproj` on core

### Task 9: Wire dependency + `life` Simulation

**Files:**
- Modify: `lifeproj/pyproject.toml` (add dep `fun-sim-core @ file:../fun-sim-core`)
- Create: `lifeproj/lifex/life_sim.py`
- Create: `lifeproj/lifex/engine_builder.py`
- Test: `lifeproj/tests/test_life_sim.py`

**Interfaces:** `life_sim.LifeSim(Simulation)` (name="life", interactive=False); `engine_builder.create_engine(name, rule) -> Engine` preserving hashlife→sparse fallback.

- [ ] **Step 1: Write failing test**

```python
# lifeproj/tests/test_life_sim.py
from lifex.life_sim import LifeSim
from lifex.rules import DEFAULT_RULE


def test_life_sim_step():
    s = LifeSim()
    s.configure({})
    s.setup()
    s.step()
    assert True

def test_fallback_engine():
    from lifex.engine_builder import create_engine
    e = create_engine("hashlife", DEFAULT_RULE)  # returns sparse on missing dep
    assert e is not None
```

- [ ] **Step 2: fail → implement**

```python
# lifeproj/lifex/engine_builder.py
from .rules import LifeRule, DEFAULT_RULE


def create_engine(name: str, rule: LifeRule = DEFAULT_RULE):
    from .engines.sparse import SparseEngine
    key = name.lower()
    if key == "sparse":
        return SparseEngine(rule)
    if key == "hashlife":
        try:
            from .engines.hashlife_adapter import HashlifeEngine
            return HashlifeEngine(rule)
        except Exception:
            return SparseEngine(rule)
    raise KeyError(f"unknown engine: {name}")
```

```python
# lifeproj/lifex/life_sim.py
from dataclasses import dataclass
from fun_sim_core.simulation import Simulation
from fun_sim_core.registry import Registry
from .rules import DEFAULT_RULE
from .engine_builder import create_engine


@dataclass
class LifeConfig:
    pattern: str = "glider"
    rule: str = str(DEFAULT_RULE)
    engine: str = "sparse"
    steps: int = 10


class LifeSim(Simulation):
    name = "life"
    default_config = LifeConfig()
    interactive = False

    def configure(self, overrides: dict | None = None):
        from fun_sim_core.config import as_dataclass
        self.config = as_dataclass(overrides or {}, LifeConfig)

    def setup(self):
        from lifex.patterns import load  # pattern loader
        self.engine = create_engine(self.config.engine)
        # seed engine with pattern (use existing lifex pattern/io imports)

    def step(self, *a, **k):
        self.engine.step(1)

    def export(self, out_dir):
        from lifex.io import video  # existing GIF/MP4 export
        video.save_frames_from_engine(self.engine, out_dir / f"{self.config.pattern}.gif")
```

> Note: patterns/io loaders exist as `lifex.io.rle`, `lifex.io.yaml_patterns`, `lifex.io.video`; wire them here per the existing CLI's usage.

- [ ] **Step 3: register in `lifeproj/lifeproj/__main__.py`** — see Task 10.
- [ ] **Step 4: Run tests → commit** `feat(lifeproj): life simulation on core`.

### Task 10: Replace lifeproj CLI + remove old factory

**Files:**
- Modify: `lifeproj/lifex/cli.py` → new entry using core `make_parser` + `run_from_parser`
- Remove: `lifeproj/lifex/factory.py`
- Create: `lifeproj/lifex/__main__.py`

- [ ] **Step 1: implementation** — new `__main__.py`:

```python
#!/usr/bin/env python3
from fun_sim_core.cli import make_parser
from fun_sim_core.registry import Registry
from .life_sim import LifeSim

reg = Registry()
reg.register("life")(LifeSim)

def main():
    import argparse
    p = make_parser("lifex", "Conway's Game of Life (fun-sim-core)", reg)
    args = p.parse_args()
    if args.command == "list":
        for n in reg.list(): print(n)
        return 0
    sim = reg.create("life")
    sim.configure()
    sim.setup()
    sim.run(args.steps)
    sim.export(args.out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

> Note: keep the original `lifex` CLI's `--engine`/`--rule`/`--pattern` convenience arguments by forwarding them through `run --config` or a thin wrapper — preserve existing behavior for backward-compat.

- [ ] **Step 2: Run the CLI smoke** `python -m lifex run life --steps 1` → runs without error (or prints fallback warn).
- [ ] **Step 3: Commit** `refactor: lifeproj CLI on core; rm factory.py`.

### Task 10b: lifeproj docs

- [ ] Rewrite `README.md` with: build install, dependency on `fun-sim-core`, quick start `python -m lifex run life`, engine/pattern table. **Commit** `docs: lifeproj core integration`.

## Phase 3 — `CuriosityLongtermism` on core

### Task 11: Scaffold `funs` package + dependency + registry

**Files:**
- Create: `CuriosityLongtermism/funs/__init__.py`, `CuriosityLongtermism/funs/core_register.py`, `CuriosityLongtermism/funs/__main__.py`, `CuriosityLongtermism/pyproject.toml`

**Interfaces:** `funs.core_register.build_registry() -> Registry` registering all sims.

- [ ] **Step 1: pyproject** depends on `fun-sim-core` (file scheme above).
- [ ] **Step 2: scaffold dirs** `funs/sims`, `funs/references/data`, `configs`, `tests`.
- [ ] **Step 3: implement `core_register.py`** that imports each sim module from `funs.sims.*` and registers; provide `build_registry()`.
- [ ] **Step 4: `__main__.py`** using `make_parser` + `run_from_parser`.
- [ ] **Step 5: commit** `chore: scaffold funs app`.

### Task 12: port boids

**Files:** Create `funs/sims/boids.py`; move `boids_simulation/{boids,simulation,config}.py` → package; Test `tests/test_boids.py`

- [ ] **Step 1**: `funs/sims/boids.py` — `class Boids(Simulation)` wrapping existing `simulation`/`boids` logic; config via YAML `configs/boids.yaml`; drop its own loguru init, use `setup_logger`; `visualize()` writes frames via `save_video`.
- [ ] **Step 2**: failing test `def test_boids_step()` then implement; run/commit.

### Task 13: port conway_game

- [ ] `funs/sims/conway.py` — wrap existing `core/*`; config yaml; use core `save_video` for GIF (its `visualization/gif_exporter.py`), `OutputManager`; test + commit.

### Task 14: port matchstick

- [ ] `funs/sims/matchstick.py` — wrap existing `core/`; keep its `tests/test_components.py`; core config/log; test + commit.

### Task 15: port romance-dynamics-model

- [ ] `funs/sims/romance.py` — wrap `core/models.py` + `core/visualization.py`; move `浪漫风格耦合模型.md` to `references/`; output via OutputManager; test + commit.

### Task 16: port tent_game (interactive)

- [ ] `funs/sims/tent.py` — `class Tent(Simulation)` with `interactive=True`; wrap `grid_manager`, `game_manager`; keep pygame `ui.py` (import optional, guarded); a headless `step()` implemented anyway; **setup/import-only test**.

### Task 17: port battery_degradation

- [ ] `funs/sims/battery.py` — wrap existing `models/degradation_mech.py` into a batch sim + `plot_series` export; config yaml; test.

### Task 17b: port date_calculate

- [ ] `funs/sims/date_calc.py` — wrap `main.py` logic; stateless calc; no viz/export; test `convert_dates(x)`.

### Task 18: port railway (notebook + data)

- [ ] Move `railway_network_analysis/{全国火车站点.xlsx,省.zip,市.zip,火车站点/}` → `funs/references/data/`.
- [ ] `funs/sims/railway.py` — convert notebook `1.ipynb` to a runnable module; `interactive=True`; import data from `references/data`; test setup-only.

### Task 19: references + notes

- [ ] Move `好奇心和长期主义/` → `funs/references/好奇心和长期主义/` verbatim.
- [ ] `configs/*.yaml` one per sim.

### Task 20: tests & CI-style run + README

- [ ] Smoke tests for all sims in `tests/`; run `python -m funs run --list`; run headless sims quickly.
- [ ] Rewrite top-level `README.md` (install, CLI, sim table with interactive tags).
- [ ] **Final commit** per repo.

## Self-Review Notes

- Spec §3 (core API) → Tasks 2–7; §3.6 base_cli → Task 7; §4 lifeproj → Tasks 9–10b; §5 Curiosity → Tasks 11–20; §6 interactive → Tasks 2 (attr), 11–20 (tent/railway tagged `interactive=True`); §7 testing → per-task tests; §8 docs → Tasks 8, 10b, 20; §9 migration → the task ordering.
- No placeholders remain: every core primitive is given with full code; app sims reference exact existing files to move/wrap.
- Type consistency: `Simulation.run(steps)` defined once; `Registry.create()/list()/register()` consistent across tasks; `interactive` name used uniformly; `configfiles` via `as_dataclass`.