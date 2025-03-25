import hashlib
import uuid
from base import get_connection

class User:
    def __init__(self, id=None, password=None, name=None):
        self.id = id
        self._password = None
        self._name = name
        
        if password is not None:
            self.password = password

    @property
    def name(self):
        return self._name or self.id

    @name.setter
    def name(self, value):
        if value is not None:
            self._name = value
        else:
            self._name = self.id

    @property
    def password(self):
        raise AttributeError("密码不可读")
    
    @password.setter
    def password(self, value):
        if value is None:
            self._password = None
        else:
            # 使用SHA-256替代bcrypt
            salt = uuid.uuid4().hex
            hashed = hashlib.sha256((value + salt).encode('utf-8')).hexdigest()
            self._password = f"{salt}${hashed}"

    def verify_password(self, password)->bool:
        if self._password is None or password is None:
            return False
        
        salt, hashed = self._password.split('$', 1)
        password_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        return password_hash == hashed

    @staticmethod
    def find_by_id(user_id):
        """根据ID查找用户"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password, name FROM user WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        user = User()
        user.id = row['id']
        user._password = row['password']
        user._name = row['name']
        return user

    def save(self)->bool:
        """保存或更新用户信息"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # 检查用户是否已存在
        cursor.execute("SELECT id FROM user WHERE id = ?", (self.id,))
        exists = cursor.fetchone()
        
        if exists:
            # 更新现有用户
            cursor.execute(
                "UPDATE user SET password = ?, name = ? WHERE id = ?",
                (self._password, self._name, self.id)
            )
        else:
            # 插入新用户
            cursor.execute(
                "INSERT INTO user (id, password, name) VALUES (?, ?, ?)",
                (self.id, self._password, self._name)
            )
        
        conn.commit()
        conn.close()
        return True
    

if __name__ == "__main__":
    user = User(id="lifesize", password="123456")
    print(user.save())