"""
火柴数字系统核心数据模型
包含所有数据类定义和类型别名
"""

from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass(frozen=True)
class DigitTransformation:
    """数字转换规则数据类"""
    add: Tuple[str, ...]
    remove: Tuple[str, ...]
    move: Tuple[str, ...]

TransformationRules = Dict[str, DigitTransformation]
MutationMap = Dict[str, int]