"""
工业级群体智能模拟系统
基于Boids算法实现高可靠、可扩展的群体行为模拟
"""

from typing import Tuple
import numpy as np
import logging
from pathlib import Path
from dataclasses import dataclass

# 类型别名定义
Vector2D = Tuple[float, float]
PositionArray = np.ndarray  # 形状: (N,2)
VelocityArray = np.ndarray  # 形状: (N,2)

@dataclass
class BoidsConfig:
    """Boids算法参数配置类"""
    num_boids: int = 100        # 粒子数量
    screen_size: float = 20.0   # 模拟区域尺寸
    max_speed: float = 2.0      # 最大速度限制
    separation_dist: float = 1.5  # 分离作用阈值
    alignment_factor: float = 0.1  # 对齐因子
    cohesion_factor: float = 0.01  # 聚合因子
    separation_factor: float = 0.05  # 分离因子
    dt: float = 0.1             # 时间步长

class BoidsSystem:
    """工业级群体行为模拟引擎"""
    
    def __init__(self, config: BoidsConfig):
        """
        初始化粒子系统
        Args:
            config: 系统配置参数
        """
        self.cfg = config
        self._init_particles()
        self.logger = self._configure_logger()
        
    def _init_particles(self) -> None:
        """初始化粒子状态"""
        # 使用Halton序列实现确定性初始化[2](@ref)
        n = self.cfg.num_boids
        self.positions = self._halton_sequence(n) * self.cfg.screen_size
        self.velocities = np.random.normal(0, 0.1, (n, 2))
        
    def _halton_sequence(self, n: int) -> np.ndarray:
        """生成低差异序列确保均匀分布"""
        def _halton(index: int, base: int):
            result = 0.0
            f = 1.0
            i = index
            while i > 0:
                f /= base
                result += f * (i % base)
                i = i // base
            return result
            
        return np.array([(_halton(i,2), _halton(i,3)) for i in range(1, n+1)])
    
    def _configure_logger(self) -> logging.Logger:
        """配置工业级日志系统"""
        logger = logging.getLogger('BoidsSystem')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(Path('logs') / 'simulation.log')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        return logger
    
    def _apply_periodic_boundary(self) -> None:
        """应用周期性边界条件[6,7](@ref)"""
        self.positions %= self.cfg.screen_size
        
    def _calculate_separation(self) -> np.ndarray:
        """
        计算分离作用力（修复广播错误）
        Returns:
            separation_forces: 分离力向量 (N,2)
        """
        # 计算粒子间相对位置差
        delta_pos = self.positions[:, np.newaxis] - self.positions  # 形状: (N,N,2)
        distances = np.linalg.norm(delta_pos, axis=2)  # 形状: (N,N)
        
        # 构建分离作用掩码（排除自身）
        mask = (distances < self.cfg.separation_dist) & ~np.eye(self.cfg.num_boids, dtype=bool)
        
        # 计算有效邻居数量（避免除零）
        neighbor_counts = np.maximum(mask.sum(axis=1), 1)
        
        # 加权平均分离向量
        separation_vectors = (delta_pos * mask[:, :, np.newaxis]).sum(axis=1)
        return separation_vectors / neighbor_counts[:, np.newaxis] * self.cfg.separation_factor
    
    def _calculate_alignment(self) -> np.ndarray:
        """计算对齐作用力"""
        avg_velocity = np.mean(self.velocities, axis=0)
        return (avg_velocity - self.velocities) * self.cfg.alignment_factor
    
    def _calculate_cohesion(self) -> np.ndarray:
        """计算聚合作用力"""
        center = np.mean(self.positions, axis=0)
        return (center - self.positions) * self.cfg.cohesion_factor
    
    def update(self) -> None:
        """执行系统状态更新"""
        try:
            # 计算各类作用力
            sep_force = self._calculate_separation()
            ali_force = self._calculate_alignment()
            coh_force = self._calculate_cohesion()
            
            # 综合作用力更新速度
            self.velocities += (sep_force + ali_force + coh_force) * self.cfg.dt
            
            # 应用速度限制
            speed = np.linalg.norm(self.velocities, axis=1)
            overspeed = speed > self.cfg.max_speed
            self.velocities[overspeed] = (self.velocities[overspeed].T / speed[overspeed]).T * self.cfg.max_speed
            
            # 更新位置并处理边界
            self.positions += self.velocities * self.cfg.dt
            self._apply_periodic_boundary()
            
            # 记录关键指标
            self.logger.info(f"Average velocity: {np.mean(self.velocities):.2f}")
            
        except Exception as e:
            self.logger.error(f"Update failed: {str(e)}")
            raise RuntimeError("System update error") from e

# 验证代码正确性
if __name__ == "__main__":
    # 初始化配置
    config = BoidsConfig(
        num_boids=100,
        screen_size=20.0,
        max_speed=2.0,
        separation_dist=1.5
    )
    
    # 创建系统实例
    system = BoidsSystem(config)
    
    # 执行验证步骤
    for _ in range(10):
        system.update()
        assert np.all(system.positions >= 0), "边界条件失效"
        assert np.all(system.positions <= config.screen_size), "边界条件失效"
        print(f"系统状态验证通过 - 位置范围: {system.positions.min():.2f} ~ {system.positions.max():.2f}")