import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import common
from . import user

__all__ = [
    "user"
]

from contextlib import contextmanager
from database.base import get_connection

@contextmanager
def get_db_context():
    """提供一个数据库连接的上下文管理器"""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


if __name__ == "__main__":
    # 测试用例
    test_user = user.User(id="test_user4", password="1")
    test_user.save()