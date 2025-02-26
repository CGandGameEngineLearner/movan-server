from loguru import logger
import sys

def custom_format(record):
    # 获取调用位置的文件名和行号
    frame = sys._getframe(8)  # 可能需要根据实际情况调整帧数
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    
    # 替换时间戳为文件路径和行号
    record["extra"]["filepath"] = f"{filename}, line {lineno}"
    
    return "{extra[filepath]} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}"

# 移除默认的处理器
logger.remove()

# 添加新的处理器，使用自定义格式
logger.add(sys.stderr, format=custom_format)

# 测试
logger.info("Sync server started")