"""
系统日志配置模块
基于loguru的工业级日志配置
"""

from loguru import logger
from pathlib import Path
import sys

def configure_logging(log_dir: Path = Path("logs"), 
                     retention: str = "10 days",
                     rotation: str = "500 MB"):
    """配置日志系统"""
    log_dir.mkdir(exist_ok=True)
    
    logger.remove()  # 移除默认配置
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
        level="INFO"
    )
    logger.add(
        log_dir / "system_{time}.log",
        rotation=rotation,
        retention=retention,
        enqueue=True,
        encoding="utf-8"
    )
    logger.info("Logging system initialized")