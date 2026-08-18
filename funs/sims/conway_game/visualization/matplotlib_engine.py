import matplotlib.pyplot as plt
from config import Config
import numpy as np
from visualization.gif_exporter import GIFExporter
from visualization.stats_visualizer import StatsVisualizer
from utils.logger import logger

class VisualizationEngine:
    """基于Matplotlib的可视化引擎[3,5](@ref)"""
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(
            Config.GRID_WIDTH*Config.CELL_SIZE/100,
            Config.GRID_HEIGHT*Config.CELL_SIZE/100
        ))
        self.img = self.ax.imshow(
            np.zeros((Config.GRID_HEIGHT, Config.GRID_WIDTH)), 
            cmap='gray', 
            vmin=0, 
            vmax=1
        )
        plt.axis('off')
        
        self.gif_exporter = GIFExporter(self.fig)
        self.stats_visualizer = StatsVisualizer() if Config.STATS_ENABLED else None
    
    
    def update_frame(self, grid, generation: int):
        """更新动画帧"""
        self.img.set_data(grid.cells)
        self.ax.set_title(f'Generation: {generation}')
        plt.pause(1/Config.FPS)
        # 捕获GIF帧
        self.gif_exporter.capture_frame()
        
        # 更新统计数据
        if self.stats_visualizer:
            current_population = np.sum(grid.cells)
            self.stats_visualizer.update_stats(current_population)
            
        
    def finalize(self):
        """结束可视化"""
        if Config.STATS_ENABLED:
            self.stats_visualizer.show_stats()
            
        gif_path = self.gif_exporter.save_gif()
        logger.info(f"Animation saved to: {gif_path}")
        plt.close('all')