import logging
import sys
from pathlib import Path

# 创建 logs 目录
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 配置日志格式
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

# 创建 logger
logger = logging.getLogger("chatbot")
logger.setLevel(logging.INFO)

# 控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format, date_format))

# 文件处理器
file_handler = logging.FileHandler(log_dir / "chatbot.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(log_format, date_format))

# 错误日志文件处理器
error_handler = logging.FileHandler(log_dir / "error.log", encoding="utf-8")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(log_format, date_format))

# 添加处理器
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(error_handler)
