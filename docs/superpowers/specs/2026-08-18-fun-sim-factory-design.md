# fun-sim Factory Refactor — Design Spec

**Date:** 2026-08-18
**Status:** Approved (brainstorming complete)
**Scope owners:** `fun-sim/` category — `lifeproj`, `CuriosityLongtermism`, and new `fun-sim-core`

---

## 1. Goal

Systematically reorganize the two `fun-sim` repos into a professional, **factory-mode**
architecture consistent with the rest of the workspace (`mlfactory`, `recsys_factory`,
`alpha101_factory`, etc.): a shared core library + thin app layers, with pluggable
simulation modules, YAML-config-driven, one unified CLI, and uniform logging/IO/docs.

## 2. Repository Architecture (approved plan)

Flat trio of sibling git repos in `fun-sim/`:

```
fun-sim/
├─ fun-sim-core/          # NEW standalone pip-installable package (new git repo)
├─ lifeproj/              # refactor → consumes fun-sim-core
└─ CuriosityLongtermism/  # refactor → consumes fun-sim-core
```

- `fun-sim-core` has **no experiment logic** — it is the shared library only.
- Each app repo **depends on** `fun-sim-core` (path/dev install `pip install -e ../fun-sim-core`)
  and self-registers its own simulations programmatically at import.
- **No cross-repo plugin auto-discovery** (Q6-B): each app owns its own `Registry` and
  registers explicitly.

## 3. `fun-sim-core` API (approved plan — Section B)

Python 3.10+, `pyproject.toml`, package name `fun_sim_core`.

### 3.1 `Simulation` (abstract base class)
The one standardized lifecycle every experiment implements:

```python
class Simulation(ABC):
    name: str                       # registry key, e.g. "boids"
    default_config: Config          # typed defaults
    interactive: bool = False       # True if GUI/notebook (see §6)

    @abstractmethod
    def configure(self, overrides: dict | None = None) -> None: ...
    @abstractmethod
    def setup(self) -> None: ...            # prepare state, RNG seed, allocations
    @abstractmethod
    def step(self, *args) -> object: ...    # advance one step
    def run(self, steps): ...               # default loop over step()
    def visualize(self) -> None: ...        # optional, default no-op
    def export(self, out_dir: Path) -> Path | None: ...  # optional
```

- **Stateful**: setup() initializes owned state; step() mutates it (matches existing sims:
  boids, conway, matchstick, romance, tent).
- `visualize`/`export` optional — sims without them (e.g. date_calc) omit them.

### 3.2 `Registry` (factory)
- `@registry.register("name")` decorator; `registry.create(name)`; `registry.list()`.
- Name normalization to lowercase/slug; unknown name -> `RegistryError` listing available names.
- `interactive` surfaced by `list()` for annotation and CLI/smoke handling.

### 3.3 `ConfigLoader`
- `load_yaml(path) -> dict`; `as_dataclass(yaml, Dataclass) -> typed config`.
- Validation: required keys, type coercion, clear errors; unknown keys warned.

### 3.4 `setup_logger(name, log_dir, level="DEBUG")`
- Standard loguru setup: console + rotating file (`rotation="1MB"`, `retention="7 days"`),
  consistent format. Replaces per-experiment hand-rolled loguru boilerplate.

### 3.5 `io` / `viz` helpers
- `OutputManager(out_dir)` — run-dir + timestamps, cleaned output folders.
- `save_array(img, path)`, `save_video(frames, path, fps)` (numpy + imageio),
  generic `plot_series(...)` (matplotlib, optional dep).
- Reused by both `lifeproj` (GIF/MP4) and `conway`/`boids`.

### 3.6 `base_cli`
- `make_parser(prog, description, registry)` — standardized
  `run <name> --config <yaml> --out <dir> [--steps N] [--seed S]` plus `list`.
- App CLI wrappers decorate/override per need.

## 4. `lifeproj` refactor (approved plan — Section C)

Keep all existing Life functionality (engines, RLE, YAML patterns, GIF/MP4 export);
**rebuild on core**, replacing its hand-rolled factory/logging/viz.

| Current `lifex/…` | Refactored |
|---|---|
| `factory.py` (own engine registry) | core `Registry`; Life-specific engine fallback becomes a local `engine_builder` |
| `cli.py` + argparse | `base_cli` + `run life --engine … --rule …` |
| own logging/io | core `setup_logger`, `io`, `OutputManager` |
| `lifex` package | kept as the Life domain lib (engines/rules/patterns/RLE/YAML) |
| (new) | `life_sim.py` registers `LifeSim(Simulation)` wrapping `lifex` — config: pattern, rule, engine, steps, export GIF/MP4 |

- Add dependency `pip install -e ../fun-sim-core`.
- Expose **one primary sim** = `life` (sparse/hashlife selectable; keep hashlife→sparse fallback).
- Remove `lifex/factory.py`, replace by core registry + local `engine_builder`.
- Preserve RLE/YAML patterns, `example.sh`. Rewrite README with core integration + standard CLI.
- **No engine/pattern logic rewrite** (out of scope; they work).

## 5. `CuriosityLongtermism` refactor (approved plan — Section D)

### New package layout
```
CuriosityLongtermism/
├─ funs/                      # app package (replaces loose dirs)
│  ├─ core_register.py        # own Registry; registers all sims
│  ├─ sims/
│  │  ├─ boids.py  conway.py  matchstick.py  romance.py  tent.py
│  │  ├─ battery.py  date_calc.py  railway.py
│  ├─ references/
│  │  ├─ data/                # 全国火车站点.xlsx, 省.zip, 市.zip, 火车站点/
│  │  └─ 好奇心和长期主义/     # notes, verbatim
│  └─ viz.py, io.py           # thin glue over core (if needed)
├─ configs/                    # one YAML per sim
├─ pyproject.toml             # depends on fun-sim-core
├─ tests/
└─ README.md
```

### Per-experiment mapping
| Old | New | Notes |
|---|---|---|
| boids_simulation | sims/boids.py | core Simulation + ConfigLoader; drop own loguru |
| conway_game | sims/conway.py | core; reuse core viz/io |
| matchstick_system | sims/matchstick.py | core; keep existing tests/ |
| romantic-dynamics-model | sims/romance.py | core; output via OutputManager; keep `.md` |
| tent_game (pygame) | sims/tent.py | **interactive** (see §6); pygame kept as visualize |
| battery_degradation | sims/battery.py | wrap existing models/degradation_mech.py into a Simulation (batch run + plot) |
| date_calculate | sims/date_calc.py | stateless calc, no viz/export |
| railway_network_analysis | sims/railway.py | notebook port to module; data under references/data; **interactive** |
| 好奇心和长期主义 | references/好奇心和长期主义/ | notes verbatim |

Conventions: each sim = `Simulation` subclass + `{name}.yaml` + optional viz/export,
registered in `core_register.py`; one CLI; unified logging/IO; no auto-discovery.

## 6. `interactive` tag (approved plan — Q7/B)

`railway` and `tent` marked `interactive=True` on `Simulation`:
- `registry.list()` annotates them.
- Smoke tests skip their headless batch path (only setup/import tested).
- CLI `run` prints "this is interactive (GUI/notebook)".

Still registered and importable; simply not forced into headless batch tests.

## 7. Testing strategy

- **fun-sim-core**: unit tests — `Registry` (register/create/list/unknown), `ConfigLoader`
  (validation/coercion/errors), `io` output-manager, `setup_logger`.
- **lifeproj**: registry + a few engine/step smoke tests; RLE/YAML round-trip.
- **CuriosityLongtermism**: registry + one smoke test per sim (construct + a few steps /
  batched run); interactive sims tested for setup/import only.

## 8. Documentation plan

- New `README.md` per repo (professional, aligned with workspace style).
- `fun-sim-core`: API doc (Simulation/Registry/Config/CLI) + quickstart.
- Each app README: install, quickstart CLI, sim list table (with interactive annotation).
- Keep existing experiment `.md` notes; link canonical module paths.

## 9. Migration / build steps

1. Scaffold `fun-sim-core` repo + package, implement core modules, its tests, README.
2. Refactor `lifeproj` onto core; update pyproject/dep; docs.
3. Refactor `CuriosityLongtermism` onto core; port railway notebook; move data/notes; docs; tests.
4. Wire dependencies (`pip install -e ../fun-sim-core`), run tests, smoke-run each sim via CLI.
5. Commit each repo; (push per prior workflow, with care on the two previously-flaky repos).

## 10. Out of scope / non-goals
- No plugin auto-discovery across repos (Q6-B).
- No porting of the `好奇心和长期主义/` notes folder; kept verbatim under `references/`.
- No engine rewrites in `lifeproj`.
- `tent_game`/`railway` are not forced headless (they're interactive).