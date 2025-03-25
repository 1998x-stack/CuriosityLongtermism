from pathlib import Path
# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.integrate import solve_ivp
from config.settings import IMAGES_DIR
from utils.logger import logger

class DynamicsVisualizer:
    """专业级可视化引擎"""
    
    def __init__(self):
        self._init_style()
        
    def _init_style(self):
        """初始化绘图风格"""
        sns.set_palette("husl")
        plt.rcParams['font.sans-serif'] = [
            'Heiti TC',        # 苹果华文黑体（简体中文）
            'Lantinghei SC',   # 苹果兰亭黑
            'STHeiti',         # 华文黑体
            'PingFang SC',     # 苹方（推荐）
            'Arial Unicode MS' # 备选方案
        ]
        plt.rcParams['axes.unicode_minus'] = False
        logger.debug("可视化引擎初始化完成")

    def plot_time_series(self, solution: solve_ivp, params_pair: tuple, 
                        filename: str) -> None:
        """生成时间序列图并保存"""
        try:
            fig = plt.figure(figsize=(12, 6))
            t = np.linspace(*solution.t[[0, -1]], 300)
            y = solution.sol(t)
            
            plt.plot(t, y[0], label=f'R(t) - {params_pair[0].type.value}')
            plt.plot(t, y[1], label=f'J(t) - {params_pair[1].type.value}')
            
            plt.xlabel("时间 (年)")
            plt.ylabel("情感强度")
            plt.title(f"情感演化：{params_pair[0].type.value} vs {params_pair[1].type.value}")
            plt.legend()
            
            save_path = IMAGES_DIR / filename
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            logger.info(f"已保存图像到: {save_path}")
            
        except Exception as e:
            logger.error(f"绘图失败: {str(e)}")
            raise