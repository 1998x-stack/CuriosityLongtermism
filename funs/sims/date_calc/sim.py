"""DateCalculator as a core Simulation (pure logic, no heavy deps)."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date

from fun_sim_core.simulation import Simulation

WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

ZODIAC_RANGES = [
    (1, 20, 2, 18, "水瓶座"), (2, 19, 3, 20, "双鱼座"),
    (3, 21, 4, 19, "白羊座"), (4, 20, 5, 20, "金牛座"),
    (5, 21, 6, 21, "双子座"), (6, 22, 7, 22, "巨蟹座"),
    (7, 23, 8, 22, "狮子座"), (8, 23, 9, 22, "处女座"),
    (9, 23, 10, 23, "天秤座"), (10, 24, 11, 22, "天蝎座"),
    (11, 23, 12, 21, "射手座"), (12, 22, 12, 31, "摩羯座"),
    (1, 1, 1, 19, "摩羯座"),
]


@dataclass
class DateCalcConfig:
    year: int = 2026
    offset_days: int = 100


class DateCalcSim(Simulation):
    name = "date_calc"
    default_config = DateCalcConfig()
    interactive = False

    def configure(self, overrides=None):
        cfg = self.default_config.__dict__.copy()
        cfg.update(overrides or {})
        self.config = DateCalcConfig(**cfg)

    def setup(self):
        self.base = date(self.config.year, 1, 1)

    @staticmethod
    def _zodiac(d):
        for sm, sd, em, ed, sign in ZODIAC_RANGES:
            if (d.month == sm and d.day >= sd) or (d.month == em and d.day <= ed):
                return sign
        return None

    def step(self):
        d = self.base.strftime("%Y-%m-%d")
        self.result = {
            "date": d,
            "weekday": WEEKDAYS[self.base.weekday()],
            "zodiac": self._zodiac(self.base),
        }
        return self.result