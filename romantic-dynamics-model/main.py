

from typing import List
from utils.logger import logger
from core.models import RomanticType, PersonalityParams, RomanticDynamics
from core.visualization import DynamicsVisualizer

def generate_all_combinations() -> List[tuple]:
    """生成所有参数组合"""
    params_config = {
        RomanticType.EAGER_BEAVER: PersonalityParams(0.5, 0.3, RomanticType.EAGER_BEAVER),
        RomanticType.NARCISSISTIC_FOOL: PersonalityParams(0.3, -0.5, RomanticType.NARCISSISTIC_FOOL),
        RomanticType.CAUTIOUS_LOVER: PersonalityParams(-0.7, 0.1, RomanticType.CAUTIOUS_LOVER),
        RomanticType.HERMIT: PersonalityParams(-0.1, -0.7, RomanticType.HERMIT)
    }
    return [ (params_config[t1], params_config[t2]) 
            for t1 in RomanticType for t2 in RomanticType ]

def main_analysis():
    """主业务流程"""
    logger.info("启动主分析流程")
    visualizer = DynamicsVisualizer()
    
    for idx, combo in enumerate(generate_all_combinations()):
        system = RomanticDynamics(combo)
        system.solve_ode()
        stability = system.stability_analysis()
        logger.info(f"参数组合 {idx + 1}: {combo[0].type.value} vs {combo[1].type.value} 的稳定性分析结果: {stability}")
        visualizer.plot_time_series(
            system._solution, combo, 
            f"dynamics_{idx}.png"
        )
    
    logger.success("分析流程完成")

if __name__ == "__main__":
    try:
        main_analysis()
    except Exception as e:
        logger.critical(f"程序崩溃: {str(e)}")
        raise