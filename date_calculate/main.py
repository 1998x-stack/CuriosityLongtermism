"""
日期计算工具库

包含公历/农历转换、星座计算、节假日处理等核心功能，适用于金融、物流、人力资源等领域的日期计算需求。

Author: AI助手
Created: 2023-10-10
Last Modified: 2023-10-12
"""

from __future__ import annotations
import numpy as np
from datetime import datetime, date, timedelta
from typing import Tuple, List, Optional, Dict
from zhdate import ZhDate  # 需要安装：pip install zhdate
from suntime import Sun  # 需要安装：pip install suntime

class DateCalculator:
    """核心日期计算工具类"""
    
    # 星座区间配置表（月份，起始日，终止日）
    ZODIAC_RANGES = [
        (1, 20, 2, 18, '水瓶座'),
        (2, 19, 3, 20, '双鱼座'),
        (3, 21, 4, 19, '白羊座'),
        (4, 20, 5, 20, '金牛座'),
        (5, 21, 6, 21, '双子座'),
        (6, 22, 7, 22, '巨蟹座'),
        (7, 23, 8, 22, '狮子座'),
        (8, 23, 9, 22, '处女座'),
        (9, 23, 10, 23, '天秤座'),
        (10, 24, 11, 22, '天蝎座'),
        (11, 23, 12, 21, '射手座'),
        (12, 22, 12, 31, '摩羯座'),
        (1, 1, 1, 19, '摩羯座')
    ]

    def __init__(self, timezone: str = 'Asia/Shanghai'):
        """
        初始化日期计算器
        
        Args:
            timezone: 时区设置，默认中国时区
        """
        self.timezone = timezone

    def calculate_offset_date(self, base_date: date, offset_days: int) -> date:
        """
        计算日期偏移
        
        Args:
            base_date: 基准日期
            offset_days: 偏移天数（正数为未来，负数为过去）
            
        Returns:
            计算后的新日期
        """
        return base_date + timedelta(days=offset_days)

    def get_weekday_cn(self, target_date: date) -> str:
        """
        获取中文星期名称
        
        Args:
            target_date: 目标日期
            
        Returns:
            中文星期名称，如"星期一"
        """
        weekdays = ["星期一", "星期二", "星期三", 
                  "星期四", "星期五", "星期六", "星期日"]
        return weekdays[target_date.weekday()]

    def get_zodiac_sign(self, target_date: date) -> Optional[str]:
        """
        计算星座
        
        Args:
            target_date: 目标日期
            
        Returns:
            星座名称或None（输入无效时）
        """
        month = target_date.month
        day = target_date.day
        
        for start_month, start_day, end_month, end_day, sign in self.ZODIAC_RANGES:
            if (month == start_month and day >= start_day) or \
               (month == end_month and day <= end_day):
                return sign
        return None

class WorkdayCalculator(DateCalculator):
    """工作日计算工具类"""
    
    def __init__(self, holidays: List[date], timezone: str = 'Asia/Shanghai'):
        """
        初始化工作日计算器
        
        Args:
            holidays: 节假日列表
            timezone: 时区设置
        """
        super().__init__(timezone)
        self.holidays = holidays
        
    def calculate_workdays(self, start_date: date, end_date: date) -> int:
        """
        计算两个日期之间的工作日数（包含开始日期，不包含结束日期）
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            有效工作日数量
        """
        # 转换为numpy日期类型
        np_start = np.datetime64(start_date)
        np_end = np.datetime64(end_date)
        
        # 计算自然工作日（排除周末）
        workdays = np.busday_count(np_start, np_end)
        
        # 排除节假日
        holiday_dates = [np.datetime64(d) for d in self.holidays]
        overlap_days = np.isin(
            np.arange(np_start, np_end, dtype='datetime64[D]'),
            holiday_dates
        ).sum()
        
        return max(workdays - overlap_days, 0)

class LunarDateConverter:
    """农历公历转换工具类"""
    
    def solar_to_lunar(self, solar_date: date) -> ZhDate:
        """
        公历转农历
        
        Args:
            solar_date: 公历日期
            
        Returns:
            ZhDate对象
        """
        return ZhDate.from_solar(
            solar_date.year, 
            solar_date.month, 
            solar_date.day
        )
    
    def lunar_to_solar(self, lunar_date: ZhDate) -> date:
        """
        农历转公历
        
        Args:
            lunar_date: 农历日期对象
            
        Returns:
            公历日期
        """
        return lunar_date.to_datetime().date()

class SpecialDateFinder:
    """特殊日期查找工具类"""
    
    @staticmethod
    def find_friday_13(start_year: int, end_year: int) -> List[date]:
        """
        查找范围内的星期五13号
        
        Args:
            start_year: 起始年份
            end_year: 结束年份
            
        Returns:
            符合条件的日期列表
        """
        results = []
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                try:
                    d = date(year, month, 13)
                    if d.weekday() == 4:  # 星期五
                        results.append(d)
                except ValueError:
                    continue
        return results
    
    @classmethod
    def calculate_easter(cls, year: int) -> date:
        """
        计算复活节日期（西方算法）
        
        Args:
            year: 目标年份
            
        Returns:
            复活节日期
        """
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19*a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2*e + 2*i - h - k) % 7
        m = (a + 11*h + 22*l) // 451
        month = (h + l - 7*m + 114) // 31
        day = (h + l - 7*m + 114) % 31 + 1
        return date(year, month, day)

# 示例使用 #################################################################

if __name__ == "__main__":
    # 初始化工具实例
    dc = DateCalculator()
    wc = WorkdayCalculator(holidays=[
        date(2024,1,1), 
        date(2024,2,10)
    ])
    lc = LunarDateConverter()
    
    # 测试用例
    test_date = date(2024, 10, 1)
    
    print("=== 基础功能测试 ===")
    print(f"日期计算: {dc.calculate_offset_date(test_date, 100)}")
    print(f"星期计算: {dc.get_weekday_cn(test_date)}")
    print(f"星座判断: {dc.get_zodiac_sign(test_date)}")
    
    print("\n=== 工作日计算 ===")
    print(f"有效工作日: {wc.calculate_workdays(date(2024,1,1), date(2024,1,31))}")
    
    print("\n=== 农历转换 ===")
    lunar_date = lc.solar_to_lunar(date(2024,2,10))
    print(f"公历转农历: {lunar_date}")
    print(f"农历转公历: {lc.lunar_to_solar(lunar_date)}")
    
    print("\n=== 特殊日期查找 ===")
    print(f"星期五13号: {SpecialDateFinder.find_friday_13(2023, 2025)}")
    print(f"复活节日期: {SpecialDateFinder.calculate_easter(2024)}")