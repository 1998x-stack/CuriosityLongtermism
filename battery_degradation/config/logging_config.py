from loguru import logger
import sys

def configure_logger():
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{module}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/degradation.log",
        rotation="10 MB",
        retention="30 days",
        encoding="utf-8"
    )