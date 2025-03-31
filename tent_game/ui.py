"""
支持动态需求显示的UI系统
"""

import pygame
from config import *
from typing import List, Set
from loguru import logger

class GameVisualizer:
    """动态渲染游戏界面"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("动态帐篷游戏")
        self.font = self._init_font_system()
        self.tree_icon = self._create_tree_icon()
        logger.success("UI系统初始化完成")
    
    def _init_font_system(self) -> pygame.font.Font:
        """初始化字体系统"""
        pygame.font.init()
        return pygame.font.SysFont('Arial', CELL_SIZE//2, bold=True)
    
    def _create_tree_icon(self) -> pygame.Surface:
        """创建树形图标"""
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.polygon(surface, COLOR_PALETTE["tree"], [
            (CELL_SIZE//2, CELL_SIZE//4),
            (CELL_SIZE//4, CELL_SIZE*3//4),
            (CELL_SIZE*3//4, CELL_SIZE*3//4)
        ])
        return surface
    
    def render(self, session) -> None:
        """主渲染入口"""
        self.screen.fill(COLOR_PALETTE["background"])
        self._draw_grid_lines()
        self._draw_trees(session.grid.trees)
        self._draw_tents(session.user_tents)
        self._draw_requirements(session.grid)
        self._draw_error_indicator(session.error_count)
        pygame.display.flip()
    
    def _draw_grid_lines(self) -> None:
        """绘制网格线"""
        for i in range(1, GRID_SIZE):
            thickness = 2 if i % (GRID_SIZE//2) == 0 else 1
            # 垂直方向
            pygame.draw.line(self.screen, COLOR_PALETTE["grid_line"],
                            (i*CELL_SIZE, 0), (i*CELL_SIZE, WINDOW_SIZE), thickness)
            # 水平方向
            pygame.draw.line(self.screen, COLOR_PALETTE["grid_line"],
                            (0, i*CELL_SIZE), (WINDOW_SIZE, i*CELL_SIZE), thickness)
    
    def _draw_trees(self, trees: List[Tuple[int, int]]) -> None:
        """渲染树木"""
        for x, y in trees:
            pos = (y*CELL_SIZE + CELL_SIZE//2, x*CELL_SIZE + CELL_SIZE//2)
            self.screen.blit(self.tree_icon, (pos[0]-CELL_SIZE//2, pos[1]-CELL_SIZE//2))
    
    def _draw_tents(self, tents: Set[Tuple[int, int]]) -> None:
        """渲染用户放置的帐篷"""
        for x, y in tents:
            rect = (
                y*CELL_SIZE + CELL_SIZE//4,
                x*CELL_SIZE + CELL_SIZE//4,
                CELL_SIZE//2,
                CELL_SIZE//2
            )
            color = COLOR_PALETTE["tree"] if (x,y) in tents else COLOR_PALETTE["error"]
            pygame.draw.rect(self.screen, color, rect, 4)
    
    def _draw_requirements(self, grid) -> None:
        """渲染动态行列需求"""
        # 行需求（左侧）
        for row in range(GRID_SIZE):
            text = self.font.render(str(grid.row_requirements[row]), True, COLOR_PALETTE["text"])
            self.screen.blit(text, (5, row*CELL_SIZE + 5))
        
        # 列需求（顶部）
        for col in range(GRID_SIZE):
            text = self.font.render(str(grid.col_requirements[col]), True, COLOR_PALETTE["text"])
            self.screen.blit(text, (col*CELL_SIZE + 5, 5))
    
    def _draw_error_indicator(self, errors: int) -> None:
        """错误指示器动画"""
        if errors > 0:
            radius = int(CELL_SIZE * 0.4 * min(errors/MAX_ERRORS, 1.0))
            pos = (WINDOW_SIZE - CELL_SIZE//2, WINDOW_SIZE - CELL_SIZE//2)
            pygame.draw.circle(self.screen, COLOR_PALETTE["error"], pos, radius, 4)