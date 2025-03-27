"""
组件单元测试模块
包含核心组件的基础测试
"""

import pytest
from pathlib import Path
from core.database import MatchstickDatabase
from core.validators import EquationValidator

@pytest.fixture
def validator():
    return EquationValidator()

def test_rule_loading():
    rules = MatchstickDatabase.get_rules()
    assert '8' in rules
    assert len(rules['0'].move) == 2

def test_basic_correction(validator):
    result = validator.find_corrections("1+3=5")
    assert any("1+5=6" in str(c) for c in result)

def test_invalid_equation(validator):
    assert not validator.find_corrections("invalid_equation")

def test_report_generation(tmp_path):
    from utils.file_handler import ReportGenerator
    test_report = {"7+7=7": {'original': '7-7=0', 'corrections': [("7-7=0", 1)]}}
    ReportGenerator.save_markdown(test_report, tmp_path / "test.md")
    assert (tmp_path / "test.md").exists()