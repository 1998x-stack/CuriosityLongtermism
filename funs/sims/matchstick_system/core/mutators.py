"""
算式变异生成引擎
包含等式变异逻辑和成本计算
"""

from typing import Set
from loguru import logger
from pathlib import Path
from .models import DigitTransformation, TransformationRules, MutationMap
from .database import MatchstickDatabase

class EquationMutator:
    """算式变异引擎（支持多步变异）"""
    
    def __init__(self):
        self._operator_map = {'+': '-', '-': '+'}
        self._operator_cost = 1
        self._rules = MatchstickDatabase.get_rules()
        logger.info("Mutator initialized with latest rules")

    def _generate_digit_variants(self, digit: str) -> Set[str]:
        """生成单数字所有可能变异"""
        if digit not in self._rules:
            logger.warning(f"Invalid digit {digit} in mutation")
            return set()
        
        variants = set()
        rule = self._rules[digit]
        variants.update(rule.add)
        variants.update(rule.remove)
        variants.update(rule.move)
        return variants - {digit}

    def mutate_equation(self, equation: str) -> MutationMap:
        """生成所有单步变异可能性"""
        from urllib.parse import unquote  # 用于URL编码处理
        
        mutations = {}
        try:
            left, right = equation.split('=')
            left = unquote(left)  # 处理可能的URL编码字符
        except ValueError:
            logger.error(f"Invalid equation format: {equation}")
            return mutations

        # 变异左侧表达式
        for i, char in enumerate(left):
            if char.isdigit():
                self._mutate_digit(left, i, right, mutations)
            elif char in self._operator_map:
                self._mutate_operator(left, i, right, mutations)

        # 变异右侧结果
        for i, char in enumerate(right):
            if char.isdigit():
                self._mutate_right_digit(left, right, i, mutations)

        # 变异等号
        self._mutate_equals(equation, mutations)
        
        logger.debug(f"Generated {len(mutations)} mutations for {equation}")
        return mutations

    def _mutate_digit(self, left: str, index: int, right: str, mutations: MutationMap) -> None:
        """处理数字变异逻辑"""
        char = left[index]
        for variant in self._generate_digit_variants(char):
            new_left = left[:index] + variant + left[index+1:]
            mutations[f"{new_left}={right}"] = 1

    def _mutate_operator(self, left: str, index: int, right: str, mutations: MutationMap) -> None:
        """处理操作符变异逻辑"""
        new_op = self._operator_map[left[index]]
        new_left = left[:index] + new_op + left[index+1:]
        mutations[f"{new_left}={right}"] = self._operator_cost

    def _mutate_right_digit(self, left: str, right: str, index: int, mutations: MutationMap) -> None:
        """处理右侧数字变异"""
        char = right[index]
        for variant in self._generate_digit_variants(char):
            new_right = right[:index] + variant + right[index+1:]
            mutations[f"{left}={new_right}"] = 1

    def _mutate_equals(self, equation: str, mutations: MutationMap) -> None:
        """处理等号变异"""
        if '=' in equation:
            eq_pos = equation.index('=')
            for new_symbol in ('-', '+'):
                mutated = equation[:eq_pos] + new_symbol + equation[eq_pos+1:]
                mutations[mutated] = self._operator_cost