"""
系统主入口模块
包含命令行接口和主流程控制
"""

from pathlib import Path
from typing import Dict, List
from loguru import logger
from core.database import MatchstickDatabase
from core.mutators import EquationMutator
from core.validators import EquationValidator
from utils.logger import configure_logging
from utils.file_handler import ReportGenerator

class MatchstickSystem:
    """火柴系统主控制器"""
    
    def __init__(self):
        configure_logging()
        self.validator = EquationValidator()
        self.mutator = EquationMutator()
        logger.info("System initialized")

    def analyze_equations(self, output_dir: Path = Path("reports")) -> Dict:
        """执行完整分析流程"""
        report = {}
        equations = self._generate_valid_equations()
        
        for eq in equations:
            self._process_equation(eq, report)
        
        ReportGenerator.save_markdown(report, output_dir / "analysis.md")
        return report

    def _generate_valid_equations(self) -> List[str]:
        """生成合法两位数算式"""
        valid = []
        for a in range(10, 100):
            for b in range(10, 100):
                if a // 10 == 0 or b // 10 == 0:
                    continue
                
                if a + b < 100:
                    valid.append(f"{a}+{b}={a+b}")
                if a > b:
                    valid.append(f"{a}-{b}={a-b}")
        return valid

    def _process_equation(self, eq: str, report: Dict) -> None:
        """处理单个算式"""
        mutations = self.mutator.mutate_equation(eq)
        for broken in mutations:
            if self.validator._safe_eval(broken) is False:
                corrections = self.validator.find_corrections(broken)
                if corrections:
                    report[broken] = {
                        'original': eq,
                        'corrections': corrections
                    }

if __name__ == "__main__":
    system = MatchstickSystem()
    
    # 导出转换规则
    rules_path = Path("config/transformation_rules.json")
    MatchstickDatabase.export_rules(rules_path)
    
    # 执行分析
    report = system.analyze_equations()
    
    # 示例验证
    sample = "13+42=55"
    logger.info(f"Sample analysis for {sample}:")
    print(system.validator.find_corrections(sample))