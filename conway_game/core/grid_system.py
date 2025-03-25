import numpy as np
from config import Config

class ToroidalGrid:
    """实现环形边界的网格系统[2,8](@ref)"""
    def __init__(self):
        self.width = Config.GRID_WIDTH
        self.height = Config.GRID_HEIGHT
        self.cells = np.zeros((self.height, self.width), dtype=np.uint8)
    
    def get_neighbors_count(self, x: int, y: int) -> int:
        """计算8邻域存活细胞数（支持环形边界）[8](@ref)"""
        y_indices = [(y-1) % self.height, y, (y+1) % self.height]
        x_indices = [(x-1) % self.width, x, (x+1) % self.width]
        neighbors = self.cells[np.ix_(y_indices, x_indices)]
        return np.sum(neighbors) - self.cells[y, x]
    
    def random_init(self):
        """随机初始化网格[3,9](@ref)"""
        self.cells = np.random.choice(
            [0, 1], 
            size=(self.height, self.width),
            p=[1-Config.INIT_DENSITY, Config.INIT_DENSITY]
        )