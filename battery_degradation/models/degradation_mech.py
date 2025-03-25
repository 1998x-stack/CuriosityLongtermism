import numpy as np
from scipy.integrate import solve_ivp
from loguru import logger

class ElectrochemicalDegradation:
    def __init__(self, T=298, SOC=0.5):
        self.k_SEI = 1e-10 * np.exp(-5000/(8.314*T))  # SEI生长速率常数[6](@ref)
        self.k_ox = 2e-12 * (SOC**0.5)                # 电解液氧化速率[6](@ref)
        self.alpha_LAM = 0.001                         # 活性物质损失系数[6](@ref)
        
    def _reaction_rates(self, t, y):
        """ 微分方程定义：y = [Q_loss_SEI, Q_loss_ox, LAM] """
        dQ_SEI = self.k_SEI * np.sqrt(t)               # SEI平方根时间依赖[6](@ref)
        dQ_ox = self.k_ox * y[2]                       # 氧化与活性物质相关
        dLAM = self.alpha_LAM * (y[0]+y[1])            # 耦合衰减机制
        return [dQ_SEI, dQ_ox, dLAM]
    
    def predict(self, cycles):
        """ 求解微分方程组 """
        sol = solve_ivp(self._reaction_rates, [0, cycles], [0,0,0], 
                       method='BDF', max_step=10)
        logger.info(f"Solved degradation ODE for {cycles} cycles")
        total_loss = sum(sol.y[:,-1])                  # 总容量损失
        return 1 - total_loss                          # 剩余容量比例