# CuriosityLongtermism

工厂模式（factory-mode）整合的「好奇心 × 长远主义」仿真合集，构建于 `fun-sim-core` 之上。
每个实验是一个可插拔的 `Simulation`，通过统一的 `Registry`、YAML 配置、日志与 CLI 驱动。

## 架构

```
CuriosityLongtermism/
├─ funs/
│  ├─ core_register.py     # 构建本应用的 Registry（懒加载注册）
│  ├─ __main__.py          # python -m funs list|run <name> --config ...
│  ├─ sims/                # 每个实验的 Simulation 包装（各含 sim.py）
│  │   ├─ date_calc/  battery/  conway_game/  boids_simulation/
│  │   ├─ romance/    matchstick_system/  tent_game/  railway/
│  └─ references/
│     ├─ data/             # 铁路数据（xlsx / zip / shapefile）
│     └─ 好奇心和长期主义/   # 笔记（原样保留）
├─ configs/                # 每个 sim 的 YAML 配置
├─ tests/
└─ pyproject.toml          # 依赖 fun-sim-core
```

## 已注册仿真

| name | 交互 | 说明 |
|------|------|------|
| boids | – | 群集行为（Boids）系统 |
| conway | – | 康威生命游戏 |
| matchstick | – | 火柴匹配系统 |
| romance | – | 浪漫动力学 ODE 模型 |
| battery | – | 电池退化电化学 ODE |
| date_calc | – | 日期/星座/工作日计算 |
| tent | ✅ 交互 | pygame 帐篷游戏（GUI） |
| railway | ✅ 交互 | 铁路网络分析（notebook/数据探索） |

## 安装

```bash
/opt/homebrew/bin/python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ../fun-sim-core
pip install -e .
pip install pytest numpy scipy PyYAML loguru imageio matplotlib
```

## 使用

```bash
python -m funs list                                   # 列出，含 [interactive] 标注
python -m funs run date_calc --config configs/date_calc.yaml --steps 1
python -m funs run battery  --config configs/battery.yaml
```

## 测试

```bash
./.venv/bin/python -m pytest tests/ -q
```

## License

MIT
