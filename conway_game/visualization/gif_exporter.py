from config import Config
from PIL import Image
import numpy as np

class GIFExporter:
    def __init__(self, fig):
        self.fig = fig
        self.frames = []
        self.dpi = fig.get_dpi()
        self.width, self.height = map(int, fig.get_size_inches() * self.dpi)
        
    def capture_frame(self):
        """捕获当前帧"""
        # 使用renderer捕获RGBA缓冲区
        canvas = self.fig.canvas
        canvas.draw()
        rgba = np.asarray(canvas.buffer_rgba())
        
        # 将RGBA转换为RGB
        rgb = np.delete(rgba, 3, axis=2)
        self.frames.append(Image.fromarray(rgb))
    
    def save_gif(self):
        """保存为GIF"""
        
        Config.GIF_EXPORT_PATH.mkdir(parents=True, exist_ok=True)
        output_path = Config.GIF_EXPORT_PATH / Config.GIF_FILENAME
        
        # 分帧保存以降低内存消耗
        if self.frames:
            self.frames[0].save(
                output_path,
                save_all=True,
                append_images=self.frames[1:],
                optimize=True,
                duration=1000//Config.GIF_FPS,
                loop=0,
                disposal=2  # 清理前一帧
            )
        return output_path