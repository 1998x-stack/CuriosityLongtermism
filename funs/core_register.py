"""Build the app Registry registering all fun-sim simulations.

Sims are registered lazily (import-on-demand) so each experiment's bare
modules (core/config/models/utils) never collide in one process.
"""
from fun_sim_core.registry import Registry


def _lazy(module: str, obj: str, interactive: bool):
    def factory():
        mod = __import__(module, fromlist=["*"])
        return getattr(mod, obj)()
    return factory


def build_registry() -> Registry:
    reg = Registry()
    # (registry name, subpackage module path, class name, interactive)
    specs = [
        ("date_calc", "funs.sims.date_calc.sim", "DateCalcSim", False),
        ("battery",  "funs.sims.battery.sim", "BatterySim", False),
        ("conway",   "funs.sims.conway_game.sim", "ConwaySim", False),
        ("boids",    "funs.sims.boids_simulation.sim", "BoidsSim", False),
        ("romance",  "funs.sims.romance.sim", "RomanticSim", False),
        ("matchstick", "funs.sims.matchstick_system.sim", "MatchstickSim", False),
        ("tent",     "funs.sims.tent_game.sim", "TentSim", True),
        ("railway",  "funs.sims.railway.sim", "RailwaySim", True),
    ]
    for name, module, cls, interactive in specs:
        reg.register_factory(name, _lazy(module, cls, interactive), interactive=interactive)
    return reg