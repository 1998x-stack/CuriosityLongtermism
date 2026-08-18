import sys
from loguru import logger
from config import Config

def configure_logger():
    """配置日志系统"""
    Config.LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        Config.LOG_PATH,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>"
    )