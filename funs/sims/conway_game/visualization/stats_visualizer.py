import matplotlib.pyplot as plt
from collections import deque
from config import Config

class StatsVisualizer:
    def __init__(self):
        self.stats_history = {
            'population': deque(maxlen=Config.STATS_HISTORY_SIZE),
            'change_rate': deque(maxlen=Config.STATS_HISTORY_SIZE)
        }
        
    def update_stats(self, current_population: int):
        """更新统计数据"""
        if len(self.stats_history['population']) > 0:
            prev = self.stats_history['population'][-1]
            change_rate = (current_population - prev) / (prev + 1e-6)  # 防止除零
            self.stats_history['change_rate'].append(change_rate)
            
        self.stats_history['population'].append(current_population)
    
    def show_stats(self):
        """显示统计图表"""
        fig, axs = plt.subplots(2, 1, figsize=(10, 6))
        
        # 人口数量图表
        axs[0].plot(self.stats_history['population'], 'b-')
        axs[0].set_title('Cell Population Over Time')
        axs[0].set_ylabel('Living Cells')
        
        # 变化率图表
        axs[1].plot(self.stats_history['change_rate'], 'r--')
        axs[1].set_title('Population Change Rate')
        axs[1].set_ylabel('Rate')
        axs[1].set_xlabel('Generation')
        
        plt.tight_layout()
        plt.show()