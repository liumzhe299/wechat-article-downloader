"""
配置文件
"""
import os

# 默认路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DEFAULT_INPUT_DIR = os.path.join(BASE_DIR, "input")

# 请求配置
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

# 下载配置
DEFAULT_DELAY = 2.0  # 请求间隔(秒)
BATCH_SIZE = 5       # 每批数量，每此休息
BATCH_REST = (5, 8)  # 批间休息时间范围
REQUEST_TIMEOUT = 30  # 请求超时

# 输出格式
SUPPORTED_FORMATS = ['text', 'markdown', 'html']
DEFAULT_FORMAT = 'html'

# 文件命名
MAX_FILENAME_LENGTH = 80