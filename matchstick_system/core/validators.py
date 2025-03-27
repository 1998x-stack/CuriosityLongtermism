"""
算式验证与校正系统
包含等式验证和校正建议生成
"""

import re
from typing import List, Tuple, Optional
from loguru import logger
from .mutators import EquationMutator
from .models import MutationMap

def safe_calculate(expression: str) -> Optional[int]:
    """安全计算简单数学表达式（仅支持加减）"""
    if not re.match(r'^\d+([+-]\d+)*$', expression):
        return None
    
    try:
        # 提取所有带符号的数字项
        parts = re.findall(r'([+-]?\d+)', expression)
        # 处理首项可能没有符号的情况
        if not parts[0].startswith(('+', '-')):
            parts[0] = '+' + parts[0]
        
        total = 0
        for part in parts:
            total += int(part)
        return total
    except (ValueError, IndexError):
        return None
    
class EquationValidator:
    """工业级算式验证器"""
    
    def __init__(self):
        self.mutator = EquationMutator()
        logger.info("Validator initialized with mutator")

    def _safe_eval(self, equation: str) -> Optional[bool]:
        """安全验证算式正确性"""
        try:
            left, right = equation.split('=')
            left_val = safe_calculate(left)
            right_val = safe_calculate(right)
            
            if left_val is None or right_val is None:
                return None
                
            return left_val == right_val
        except ValueError:
            return None

    def find_corrections(self, broken_eq: str) -> List[Tuple[str, int]]:
        """生成校正建议（按移动次数排序）"""
        if not self._validate_input(broken_eq):
            return []

        mutations = self.mutator.mutate_equation(broken_eq)
        valid = [(m, cost) for m, cost in mutations.items() 
                if self._safe_eval(m) is True]
        
        logger.info(f"Found {len(valid)} corrections for {broken_eq}")
        return sorted(valid, key=lambda x: x[1])

    def _validate_input(self, equation: str) -> bool:
        """验证输入格式有效性"""
        if not isinstance(equation, str) or '=' not in equation:
            logger.error(f"Invalid input format: {equation}")
            return False
        return True