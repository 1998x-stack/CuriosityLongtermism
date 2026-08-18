"""
游戏状态管理模块
支持动态行列需求
"""

from typing import Set, Tuple
from config import *
from grid_manager import DynamicGridGenerator
from loguru import logger

class GameSession:
    """管理游戏会话状态"""
    
    def __init__(self):
        self.grid = DynamicGridGenerator()
        self.user_tents: Set[Tuple[int, int]] = set()
        self.error_count = 0
        
    def process_click(self, coord: Tuple[int, int]) -> str:
        """处理点击事件返回状态码"""
        if not self._is_valid_coord(coord):
            logger.warning(f"无效坐标: {coord}")
            return "invalid"
            
        if coord in self.user_tents:
            self.user_tents.remove(coord)
            logger.info(f"移除帐篷: {coord}")
            return "removed"
            
        validation_result = self._validate_tent_position(coord)
        if validation_result == "valid":
            self.user_tents.add(coord)
            logger.info(f"放置帐篷: {coord}")
            if self.check_victory():
                return "victory"
            return "placed"
        else:
            self.error_count += 1
            logger.warning(f"错误放置: {coord} | 错误类型: {validation_result}")
            if self.error_count >= MAX_ERRORS:
                logger.critical("错误次数超限，重置游戏")
                return "reset"
            return "error"
    
    def _is_valid_coord(self, coord: Tuple[int, int]) -> bool:
        """坐标边界检查"""
        return all(0 <= c < GRID_SIZE for c in coord)
    
    def _validate_tent_position(self, coord: Tuple[int, int]) -> str:
        """多条件验证返回错误类型"""
        if coord in self.grid.trees:
            return "tree_collision"
        if not self.grid._has_adjacent_tree(coord):
            return "no_adjacent_tree"
        if any(abs(coord[0]-x) <=1 and abs(coord[1]-y) <=1 for (x,y) in self.user_tents):
            return "tent_adjacent"
        if coord not in self.grid.tents:
            return "wrong_position"
        return "valid"
    
    def check_victory(self) -> bool:
        """精确胜利条件检查"""
        return self.user_tents == self.grid.tents
    
    def reset(self) -> None:
        """重置游戏状态"""
        self.__init__()
        logger.info("游戏已重置")