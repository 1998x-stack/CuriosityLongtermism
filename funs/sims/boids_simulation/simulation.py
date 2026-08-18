"""
工业级群体行为模拟可视化模块
集成高性能渲染、状态监控和异常处理机制
"""

from typing import Any
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pathlib import Path
from loguru import logger
import numpy as np

# 类型注解
from config import BoidsConfig, FIGURES_DIR, LOGS_DIR
from boids import BoidsSystem

class BoidsVisualizer:
    """群体行为可视化引擎"""
    
    def __init__(self, config: BoidsConfig):
        """
        初始化可视化系统
        Args:
            config: 群体行为配置参数
        """
        self.cfg = config
        self.system = BoidsSystem(config)
        self._init_visualization()
        self._frame_counter = 0
        logger.info("可视化系统初始化完成")

    def _init_visualization(self) -> None:
        """配置Matplotlib渲染参数"""
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(
            figsize=(10, 10),
            dpi=120,
            facecolor='#1a1a1a'
        )
        self._setup_axes()
        self.scatter = self.ax.scatter(
            [], [],
            s=35,
            alpha=0.7,
            edgecolor='w',
            linewidth=0.3,
            cmap='viridis'
        )

    def _setup_axes(self) -> None:
        """配置坐标轴显示参数"""
        self.ax.set_xlim(0, self.cfg.screen_size)
        self.ax.set_ylim(0, self.cfg.screen_size)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_title("工业级群体行为模拟", fontsize=14, color='white')

    def _save_simulation_frame(self) -> None:
        """
        使用Pathlib保存当前帧图像
        工业级错误处理机制
        """
        try:
            fig_path = FIGURES_DIR / f"sim_frame_{self._frame_counter:06d}.png"
            self.fig.savefig(
                fig_path,
                dpi=150,
                bbox_inches='tight',
                facecolor=self.fig.get_facecolor()
            )
            logger.debug(f"帧数据已保存至 {fig_path}")
        except PermissionError as e:
            logger.critical(f"文件权限异常: {str(e)}")
            raise RuntimeError("文件保存失败") from e
        except Exception as e:
            logger.error(f"未知保存错误: {str(e)}")
            raise

    def _update_animation(self, frame: int) -> Any:
        """
        动画帧更新回调函数
        Args:
            frame: 当前帧序号
        Returns:
            更新后的散点图对象
        """
        try:
            self.system.update()
            self.scatter.set_offsets(self.system.positions)
            
            # 动态颜色映射反映速度变化
            speeds = np.linalg.norm(self.system.velocities, axis=1)
            self.scatter.set_array(speeds)
            
            # 每10帧保存一次状态
            if self._frame_counter % 10 == 0:
                self._save_simulation_frame()
                
            self._frame_counter += 1
            return self.scatter,
            
        except RuntimeError as e:
            logger.error(f"动画更新失败: {str(e)}")
            self._emergency_shutdown()
            raise

    def _emergency_shutdown(self) -> None:
        """紧急关闭程序时的资源回收"""
        plt.close('all')
        logger.warning("已执行紧急关闭程序")

    def run_simulation(self, duration: float = 60.0) -> None:
        """
        启动主模拟循环
        Args:
            duration: 模拟时长（秒）
        """
        try:
            logger.info("启动主模拟循环")
            interval = int(self.cfg.dt * 1000)
            total_frames = int(duration / self.cfg.dt)
            
            anim = FuncAnimation(
                self.fig,
                self._update_animation,
                frames=total_frames,
                interval=interval,
                blit=True,
                repeat=False
            )
            
            plt.show()
            
        except KeyboardInterrupt:
            logger.warning("用户中断模拟过程")
        except Exception as e:
            logger.critical(f"致命错误: {str(e)}")
            raise
        finally:
            logger.success("模拟过程正常终止")

if __name__ == "__main__":
    # 初始化工业级配置
    industrial_config = BoidsConfig(
        num_boids=500,
        screen_size=40.0,
        max_speed=3.0,
        separation_dist=2.0,
        alignment_factor=0.08,
        cohesion_factor=0.015,
        dt=0.08
    )
    
    # 创建并运行可视化系统
    visualizer = BoidsVisualizer(industrial_config)
    visualizer.run_simulation(duration=120.0)