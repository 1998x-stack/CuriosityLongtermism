"""
主程序入口
集成日志系统和游戏循环
"""

import pygame
from loguru import logger
from game_manager import GameSession
from ui import GameVisualizer
from config import *

def configure_logging():
    """配置日志系统"""
    logger.add("game.log", rotation="1 MB", retention="10 days",
              format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
    logger.info("日志系统初始化完成")

def main():
    configure_logging()
    visualizer = GameVisualizer()
    session = GameSession()
    clock = pygame.time.Clock()
    
    running = True
    while running:
        clock.tick(30)
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                grid_coord = (y // CELL_SIZE, x // CELL_SIZE)
                result = session.process_click(grid_coord)
                
                if result == "reset":
                    logger.info("执行游戏重置")
                    session = GameSession()
        
        # 渲染界面
        visualizer.render(session)
    
    pygame.quit()
    logger.info("游戏正常退出")

if __name__ == "__main__":
    main()