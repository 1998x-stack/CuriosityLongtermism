"""
文件操作工具模块
包含报告生成和文件输出功能
"""

from pathlib import Path
from typing import Dict
from loguru import logger

class ReportGenerator:
    """工业级报告生成系统"""
    
    @staticmethod
    def save_markdown(report: Dict, output_path: Path) -> None:
        """生成Markdown格式分析报告"""
        try:
            content = ReportGenerator._build_markdown_content(report)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with output_path.open('w', encoding='utf-8') as f:
                f.write(content)
            
            logger.success(f"Report saved to {output_path}")
        except (IOError, PermissionError) as e:
            logger.error(f"Failed to save report: {str(e)}")
            raise

    @staticmethod
    def _build_markdown_content(report: Dict) -> str:
        """构建Markdown内容"""
        md = [
            "# 火柴算式校正分析报告\n",
            "| 错误算式 | 原始正确式 | 校正方案 | 所需火柴数 |",
            "|---------|-----------|---------|-----------|"
        ]
        
        for broken, data in report.items():
            for corr, cost in data['corrections']:
                md.append(f"| `{broken}` | `{data['original']}` | `{corr}` | {cost} |")
        
        return "\n".join(md)