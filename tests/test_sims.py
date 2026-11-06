import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

HEADLESS = ["date_calc", "battery", "conway", "boids", "romance", "matchstick"]
INTERACTIVE = ["tent", "railway"]


def _run(name):
    code = (
        "from funs.core_register import build_registry\n"
        f"r = build_registry()\n"
        f"s = r.create('{name}'); s.configure({{}}); s.setup()\n"
        f"print('OK', s.step())\n"
    )
    p = subprocess.run([PY, "-c", code], cwd=ROOT, capture_output=True, text=True)
    return p



def test_subprocess_uses_current_interpreter(monkeypatch):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="OK", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = _run("date_calc")
    assert result.returncode == 0
    assert len(calls) == 1
    command, kwargs = calls[0]
    assert command[0] == sys.executable
    assert command[1] == "-c"
    assert kwargs["cwd"] == ROOT
    assert kwargs["capture_output"] is True


def test_all_headless_step():
    for name in HEADLESS:
        p = _run(name)
        assert p.returncode == 0, f"{name} failed:\n{p.stderr[-1500:]}"
        assert "OK" in p.stdout


def test_interactive_listed_but_not_headless():
    for name in INTERACTIVE:
        # Interactive simulations should only be checked for setup, never stepped.
        code = (
            "from funs.core_register import build_registry\n"
            f"r = build_registry()\n"
            f"s = r.create('{name}'); s.configure({{}})\n"
            f"print('setup', s.setup())\n"
        )
        p = subprocess.run([PY, "-c", code], cwd=ROOT, capture_output=True, text=True)
        assert p.returncode == 0, f"{name} setup failed:\n{p.stderr[-1200:]}"


def test_registry_lists_all_and_interactive_tags():
    from funs.core_register import build_registry
    r = build_registry()
    for n in HEADLESS:
        assert n in r.names() and r.is_interactive(n) is False
    for n in INTERACTIVE:
        assert n in r.names() and r.is_interactive(n) is True
