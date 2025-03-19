from sqlalchemy import Sequence, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from account_server.entity.base import Base
from sqlalchemy.orm import Mapped
import bcrypt

# 定义模型类
class User(Base):
    __tablename__ = 'user'
    
    id: Mapped[str] = Column(String(36), primary_key=True)
    _password: Mapped[str] = Column(String(128))
    name: Mapped[str] = Column(String(50))

    @hybrid_property
    def password(self):
        """
        密码的 getter 方法 - 不允许直接获取密码哈希
        """
        raise AttributeError("密码不可读")
    
    @password.setter
    def password(self, value):
        if value is None:
            self._password = None
        else:
            # 生成盐并对密码进行哈希
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(value.encode('utf-8'), salt)
            self._password = hashed.decode('utf-8')

    def verify_password(self, password):
        """
        验证密码是否匹配
        """
        if self._password is None or password is None:
            return False
        
        # 检查提供的密码是否与存储的哈希匹配
        return bcrypt.checkpw(password.encode('utf-8'), self._password.encode('utf-8'))
    
    
