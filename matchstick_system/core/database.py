"""
火柴数字规则数据库
包含数字转换规则和验证逻辑
"""

import json
from pathlib import Path
from loguru import logger
from .models import DigitTransformation, TransformationRules

class MatchstickDatabase:
    """火柴数字规则库（工业级安全设计）"""
    
    _TRANSFORMATIONS: TransformationRules = {
        '0': DigitTransformation(add=('8',), remove=(), move=('6', '9')),
        '1': DigitTransformation(add=('7',), remove=(), move=()),
        '2': DigitTransformation(add=(), remove=(), move=('3',)),
        '3': DigitTransformation(add=('9',), remove=(), move=('2', '5')),
        '4': DigitTransformation(add=(), remove=(), move=()),
        '5': DigitTransformation(add=('6', '9'), remove=(), move=('3',)),
        '6': DigitTransformation(add=('8',), remove=('5',), move=('0', '9')),
        '7': DigitTransformation(add=(), remove=('1',), move=()),
        '8': DigitTransformation(add=(), remove=('0', '6', '9'), move=()),
        '9': DigitTransformation(add=('8',), remove=('3', '5'), move=('0', '6'))
    }

    @classmethod
    def get_rules(cls) -> TransformationRules:
        """获取转换规则"""
        logger.debug("Loading transformation rules from in-memory database")
        return cls._TRANSFORMATIONS

    @classmethod
    def export_rules(cls, output_path: Path) -> None:
        """导出规则到JSON文件"""
        try:
            json_data = {
                d: {'add': t.add, 'remove': t.remove, 'move': t.move}
                for d, t in cls._TRANSFORMATIONS.items()
            }
            with output_path.open('w') as f:
                json.dump(json_data, f, indent=2)
            logger.info(f"Rules exported to {output_path}")
        except (IOError, PermissionError) as e:
            logger.error(f"Rule export failed: {str(e)}")
            raise