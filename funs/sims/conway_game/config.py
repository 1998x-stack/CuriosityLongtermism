from pathlib import Path

# 全局配置参数[3,8](@ref)
class Config:
    # 网格参数
    GRID_WIDTH = 80
    GRID_HEIGHT = 40
    CELL_SIZE = 10  # 像素
    
    # 演化参数
    INIT_DENSITY = 0.15    # 随机初始化密度
    TOROIDAL_BOUNDARY = True  # 环形边界
    
    # 可视化参数
    COLOR_ALIVE = 'black'
    COLOR_DEAD = 'white'
    FPS = 10               # 帧率控制
    # 新增统计配置
    STATS_ENABLED = True
    STATS_HISTORY_SIZE = 200  # 保留的历史数据量
    
    # GIF导出配置
    GIF_EXPORT_PATH = Path("exports/animations")
    GIF_FILENAME = "conway_evolution.gif"
    GIF_FPS = 5
    
    # 日志配置
    LOG_PATH = Path("logs/conway.log")