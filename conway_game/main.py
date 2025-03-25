import argparse
import numpy as np
from core.grid_system import ToroidalGrid
from core.game_rules import conway_rule
from core.pattern_loader import PatternLoader
from visualization.matplotlib_engine import VisualizationEngine
from config import Config

def simulate():
    """主模拟循环[8,10](@ref)"""
    grid = ToroidalGrid()
    
    # 初始化模式
    parser = argparse.ArgumentParser(description='康威生命游戏模拟器')
    parser.add_argument('-p', '--pattern', choices=['random', 'glider'], default='random')
    args = parser.parse_args()
    
    if args.pattern == 'glider':
        PatternLoader.glider(grid, 10, 10)
    else:
        grid.random_init()
    
    visualizer = VisualizationEngine()
    
    try:
        for gen in range(1000):
            new_state = np.zeros_like(grid.cells)
            for y in range(grid.height):
                for x in range(grid.width):
                    neighbors = grid.get_neighbors_count(x, y)
                    new_state[y, x] = conway_rule(grid.cells[y, x], neighbors)
            grid.cells[:, :] = new_state
            visualizer.update_frame(grid, gen)
    except KeyboardInterrupt:
        print("\nSimulation terminated by user")

if __name__ == "__main__":
    simulate()