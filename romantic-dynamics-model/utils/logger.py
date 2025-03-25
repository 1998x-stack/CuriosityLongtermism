from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

from loguru import logger
from config.settings import OUTPUT_DIR

# 配置日志系统
logger.add(
    OUTPUT_DIR / "logs" / "runtime_{time}.log",
    rotation="100 MB",
    retention="30 days",
    enqueue=True,
    encoding="utf-8",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

__all__ = ["logger"]