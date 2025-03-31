"""
游戏全局配置模块
Updated: 移除固定行列需求，改为动态生成
"""

from typing import Tuple, List

# 类型别名
Coordinate = Tuple[int, int]
GridMatrix = List[List[int]]

# 游戏常量
GRID_SIZE = 5
TREE_COUNT = 7
MAX_ERRORS = 3

# 颜色配置
COLOR_PALETTE = {
    "background": (255, 204, 153),
    "grid_line": (128, 128, 128),
    "tree": (34, 139, 34),
    "text": (0, 0, 255),
    "error": (255, 0, 0)
}

# 界面尺寸
WINDOW_SIZE = 600
CELL_SIZE = WINDOW_SIZE // GRID_SIZE