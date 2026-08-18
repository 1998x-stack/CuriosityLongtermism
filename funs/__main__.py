#!/usr/bin/env python3
"""Core-driven CLI: python -m funs list | run <name> --config ..."""
from fun_sim_core.cli import make_parser, run_from_parser
from funs.core_register import build_registry


def main(argv=None) -> int:
    reg = build_registry()
    parser = make_parser("funs", "Curiosity & Long-termism simulation factory")
    args = parser.parse_args(argv)
    return run_from_parser(args, reg)


if __name__ == "__main__":
    raise SystemExit(main())
