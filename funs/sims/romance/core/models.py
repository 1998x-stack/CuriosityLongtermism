from pathlib import Path
# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

from dataclasses import dataclass
from enum import Enum
import numpy as np
from scipy.integrate import solve_ivp
from typing import Tuple, Dict
from utils.logger import logger

class RomanticType(Enum):
    """浪漫人格类型枚举"""
    EAGER_BEAVER = "热切的海狸"
    NARCISSISTIC_FOOL = "自恋的傻瓜"
    CAUTIOUS_LOVER = "谨慎的爱人"
    HERMIT = "隐士"

@dataclass(frozen=True)
class PersonalityParams:
    """人格参数不可变数据结构"""
    a: float  # 自我反馈系数
    b: float  # 互动反馈系数
    type: RomanticType

class RomanticDynamics:
    """情感动力学系统核心类"""
    
    def __init__(self, 
                 params_pair: Tuple[PersonalityParams, PersonalityParams],
                 t_span: Tuple[float, float] = (0, 5),
                 y0: np.ndarray = np.array([0.5, 0.5])) -> None:
        self.params_pair = params_pair
        self.t_span = t_span
        self.y0 = y0
        self._solution = None
        logger.info(f"初始化系统: {params_pair[0].type.value} vs {params_pair[1].type.value}")

    def _derivative(self, t: float, y: np.ndarray) -> np.ndarray:
        """定义常微分方程系统"""
        r_params, j_params = self.params_pair
        dR = r_params.a * y[0] + r_params.b * y[1]
        dJ = j_params.b * y[0] + j_params.a * y[1]
        return np.array([dR, dJ])
    
    def solve_ode(self) -> None:
        """求解微分方程"""
        try:
            self._solution = solve_ivp(
                fun=self._derivative,
                t_span=self.t_span,
                y0=self.y0,
                method='RK45',
                dense_output=True
            )
            logger.success("微分方程求解成功")
        except Exception as e:
            logger.error(f"求解失败: {str(e)}")
            raise

    def stability_analysis(self) -> Dict:
        """
        计算系统稳定性指标
        Returns:
            包含特征值、稳定性和平衡点类型的字典
        """
        # 构建雅可比矩阵
        r, j = self.params_pair
        jacobian = np.array([[r.a, r.b], 
                            [j.b, j.a]])
        eigenvalues = np.linalg.eigvals(jacobian)
        
        # 判断稳定性
        stable = all(e.real < 0 for e in eigenvalues)
        oscillation = any(e.imag != 0 for e in eigenvalues)
        
        return {
            "eigenvalues": eigenvalues,
            "is_stable": stable,
            "has_oscillation": oscillation,
            "equilibrium_type": self._classify_equilibrium(eigenvalues)
        }
        
    def _classify_equilibrium(self, eigenvalues: np.ndarray) -> str:
        """根据特征值分类平衡点类型"""
        reals = [e.real for e in eigenvalues]
        imags = [e.imag for e in eigenvalues]
        
        if all(r < 0 for r in reals):
            return "稳定吸引焦点" if any(i != 0 for i in imags) else "稳定结点"
        elif all(r > 0 for r in reals):
            return "不稳定排斥焦点" if any(i != 0 for i in imags) else "不稳定结点"
        else:
            return "鞍点"