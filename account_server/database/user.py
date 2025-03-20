from sqlalchemy import Sequence, Column, Integer, String, case
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from account_server.database.base import Base
from sqlalchemy.orm import Mapped
import bcrypt

class User(Base):
    __tablename__ = 'user'
    
    id: Mapped[str] = Column(String(36), primary_key=True)
    _password: Mapped[str] = Column('password', String(128))
    _name: Mapped[str] = Column('name', String(50), nullable=False)

    def __init__(self, **kwargs):
        password = kwargs.pop('password', None)
        name = kwargs.pop('name', None)
        super().__init__(**kwargs)
        if password is not None:
            self.password = password
        

    @hybrid_property
    def name(self):
        return self._name or self.id

    @name.setter
    def name(self, value):
        if value is not None:
            self._name = value
        else:
            self._name = id


    @property
    def password(self):
        raise AttributeError("密码不可读")
    
    @password.setter
    def password(self, value):
        if value is None:
            self._password = None
        else:
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(value.encode('utf-8'), salt)
            self._password = hashed.decode('utf-8')

    def verify_password(self, password)->bool:
        if self._password is None or password is None:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self._password.encode('utf-8'))