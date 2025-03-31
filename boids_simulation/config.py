from pathlib import Path
from loguru import logger
from dataclasses import dataclass

# 路径配置
BASE_DIR = Path(__file__).parent
FIGURES_DIR = BASE_DIR / "figures"
LOGS_DIR = BASE_DIR / "logs"

# 初始化目录
(FIGURES_DIR).mkdir(exist_ok=True)
(LOGS_DIR).mkdir(exist_ok=True)

# 配置loguru
logger.add(
    LOGS_DIR / "simulation.log",
    rotation="1 MB",  # 日志文件超过1MB后轮转[6,7](@ref)
    retention="7 days",  # 保留最近7天的日志[6](@ref)
    level="DEBUG",  # 记录DEBUG及以上级别日志[2,5](@ref)
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"  # 自定义格式[7](@ref)
)

# Boids参数
BOIDS_CONFIG = {
    "num_boids": 50,
    "max_speed": 1.0,
    "screen_size": 10.0,
    "separation_distance": 1.5
}


@dataclass
class BoidsConfig:
    """Boids算法参数配置类"""
    num_boids: int = 100        # 粒子数量
    screen_size: float = 20.0   # 模拟区域尺寸
    max_speed: float = 2.0      # 最大速度限制
    separation_dist: float = 1.5  # 分离作用阈值
    alignment_factor: float = 0.1  # 对齐因子
    cohesion_factor: float = 0.01  # 聚合因子
    separation_factor: float = 0.05  # 分离因子
    dt: float = 0.1             # 时间步长