import numpy as np
from typing import Tuple

class PatternGenerator:
    """所有经典细胞模式的生成器"""
    
    @staticmethod
    def block(grid, x_offset: int = 0, y_offset: int = 0):
        """2x2方块"""
        pattern = np.array([
            [1, 1],
            [1, 1]
        ])
        PatternGenerator._apply_pattern(grid, pattern, x_offset, y_offset)
    
    @staticmethod
    def glider(grid, x_offset: int = 0, y_offset: int = 0):
        """滑翔机（最小移动结构）"""
        pattern = np.array([
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ])
        PatternGenerator._apply_pattern(grid, pattern, x_offset, y_offset)
    
    @staticmethod
    def pulsar(grid, x_offset: int = 0, y_offset: int = 0):
        """脉冲星振荡器（周期3）"""
        pattern = np.zeros((13, 13))
        # 中心十字
        pattern[2:11:4, 4:9] = 1
        pattern[4:9, 2:11:4] = 1
        # 外围结构
        pattern[[0,5,7,12], 2:11:2] = 1
        pattern[2:11:2, [0,5,7,12]] = 1
        PatternGenerator._apply_pattern(grid, pattern, x_offset, y_offset)
    
    @staticmethod
    def gosper_glider_gun(grid, x_offset: int = 0, y_offset: int = 0):
        """高斯帕滑翔机枪"""
        pattern = np.zeros((36, 9))
        # 左量子结构
        pattern[24:27, 0:4] = [[0,1,0,0], [0,0,1,0], [1,1,1,0]]
        # 右量子结构 
        pattern[14:17, 0:4] = [[1,1,0,0], [1,0,0,1], [0,0,1,0]]
        # 中央振荡器
        pattern[12:15, 4:7] = [[0,1,0], [0,0,1], [1,1,1]]
        PatternGenerator._apply_pattern(grid, pattern, x_offset, y_offset)
    
    @staticmethod
    def _apply_pattern(grid, pattern: np.ndarray, x_offset: int, y_offset: int):
        """将模式应用到网格（自动处理环形边界）"""
        h, w = pattern.shape
        for dy in range(h):
            for dx in range(w):
                if pattern[dy, dx]:
                    y = (y_offset + dy) % grid.height
                    x = (x_offset + dx) % grid.width
                    grid.cells[y, x] = 1