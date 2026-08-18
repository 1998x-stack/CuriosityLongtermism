from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
# print(BASE_DIR)
# 输出目录配置
OUTPUT_DIR = BASE_DIR / "output"
IMAGES_DIR = OUTPUT_DIR / "images"

# 创建必要目录
(OUTPUT_DIR / "logs").mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)