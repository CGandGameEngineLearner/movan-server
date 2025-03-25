import sqlite3
import os

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'movan.db')

# 创建表的SQL语句
CREATE_USER_TABLE = '''
CREATE TABLE IF NOT EXISTS user (
    id TEXT PRIMARY KEY,
    password TEXT,
    name TEXT
)
'''

def get_connection():
    """获取SQLite数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 让查询结果支持通过列名访问
    return conn

def init_db():
    """初始化数据库表"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(CREATE_USER_TABLE)
    conn.commit()
    conn.close()

# 初始化数据库
init_db()

