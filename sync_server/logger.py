from config import config
import logging
import logging.handlers  # 显式导入 logging.handlers
import os
import sys  # 需要导入 sys 模块，因为后面用到了 sys.stdout

# 创建 logger
logger = logging.getLogger("sync_server")

# 清除现有的处理器
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# 设置日志级别
level = getattr(logging, config['Log']['level'], logging.INFO)
logger.setLevel(level)

# 创建日志格式化器
formatter = logging.Formatter('%(asctime)s | %(levelname)8s | %(filename)s:%(lineno)d - %(message)s')

# 创建日志文件目录（如果不存在）
log_path = config['Log']['sink']
log_dir = os.path.dirname(log_path)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置文件处理器
if config['Log'].get('rotation'):
    # 使用 RotatingFileHandler 实现日志轮转
    rotation = config['Log']['rotation']
    if isinstance(rotation, str) and "MB" in rotation:
        max_bytes = int(rotation.split()[0]) * 1024 * 1024
    elif isinstance(rotation, str) and "GB" in rotation:
        max_bytes = int(rotation.split()[0]) * 1024 * 1024 * 1024
    else:
        max_bytes = 10 * 1024 * 1024  # 默认10MB
    
    # 确定要保留的备份数量
    backup_count = 10  # 默认值
    if config['Log'].get('retention') and isinstance(config['Log']['retention'], str):
        if "days" in config['Log']['retention']:
            try:
                backup_count = int(config['Log']['retention'].split()[0])
            except (ValueError, IndexError):
                pass
    
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
else:
    # 使用基本的 FileHandler
    file_handler = logging.FileHandler(log_path, encoding='utf-8')

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 可选：添加控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


if __name__ == "__main__":
    # setup_logger 函数未定义，将此块改为直接使用上面配置的 logger
    logger.info("日志系统已初始化完成")
    logger.error("这是一条错误日志")