from typing import Optional, List
from base import get_connection

class Role:
    def __init__(self, id: Optional[str] = None, uid: Optional[str] = None):
        self.id = id
        self.uid = uid

    @staticmethod
    def find_by_id(role_id: str) -> Optional["Role"]:
        """根据ID查找角色"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, uid FROM role WHERE id = ?", (role_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        role = Role()
        role.id = row['id']
        role.uid = row['uid']
        return role

    @staticmethod
    def find_by_uid(uid: str) -> List["Role"]:
        """根据UID查找所有角色"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, uid FROM role WHERE uid = ?", (uid,))
        rows = cursor.fetchall()
        conn.close()
        
        roles: List[Role] = []
        for row in rows:
            role = Role()
            role.id = row['id']
            role.uid = row['uid']
            roles.append(role)
        return roles

    def save(self) -> bool:
        """保存或更新角色信息"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # 检查角色是否已存在
        cursor.execute("SELECT id FROM role WHERE id = ?", (self.id,))
        exists = cursor.fetchone()
        
        if exists:
            # 更新现有角色
            cursor.execute(
                "UPDATE role SET uid = ? WHERE id = ?",
                (self.uid, self.id)
            )
        else:
            # 插入新角色
            cursor.execute(
                "INSERT INTO role (id, uid) VALUES (?, ?)",
                (self.id, self.uid)
            )
        
        conn.commit()
        conn.close()
        return True