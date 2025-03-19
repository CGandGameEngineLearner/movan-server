import base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from account_server.config import config

from account_server.entity.base import Base

from contextlib import contextmanager


# 创建引擎
engine = create_engine(
    config['DataBase']['url'],
    echo=False,  # 设置为True可以看到SQL语句
    pool_pre_ping=True,  # 连接池健康检查
    pool_recycle=3600,  # 连接回收时间(秒)
)

# 导入所有的实体
import user

Base.metadata.create_all(bind=engine)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# 创建线程安全的会话工厂
db_session = scoped_session(SessionLocal)



def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    db = get_db().__next__()
    try:
        yield db
    finally:
        db.close()