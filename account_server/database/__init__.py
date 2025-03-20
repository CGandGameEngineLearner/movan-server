import base
import user

__all__ = [
    "user"
]

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session,Session
from account_server.config import config

from account_server.database.base import Base

from contextlib import contextmanager


# 创建引擎
engine = create_engine(
    config['DataBase']['url'],
    echo=False,  # 设置为True可以看到SQL语句
    pool_pre_ping=True,  # 连接池健康检查
    pool_recycle=3600,  # 连接回收时间(秒)
)



Base.metadata.create_all(bind=engine)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# 创建线程安全的会话工厂
db_session = scoped_session(SessionLocal)




@contextmanager
def get_db_context():
    session:Session = db_session()
    try:
        yield session
    finally:
        db_session.remove()


if __name__ == "__main__":
    with get_db_context() as session:
        session.add(user.User(id="test_user4",password="1"))
        session.commit()