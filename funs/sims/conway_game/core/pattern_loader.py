import numpy as np

class PatternLoader:
    """预设图案加载器[3,9](@ref)"""
    @staticmethod
    def glider(grid, x_offset=0, y_offset=0):
        """滑翔机图案[6,9](@ref)"""
        pattern = np.array([
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ], dtype=np.uint8)
        grid.cells[y_offset:y_offset+3, x_offset:x_offset+3] = pattern
    
    @staticmethod  
    def blinker(grid, x_offset=10, y_offset=10):
        """信号灯振荡器[1](@ref)"""
        grid.cells[y_offset, x_offset:x_offset+3] = 1