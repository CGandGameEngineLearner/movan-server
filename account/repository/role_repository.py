from ..database.role import Role
from typing import Optional, List

def create_role(role_id: str, uid: str) -> bool:
    # 检查角色是否已存在
    existing_role = Role.find_by_id(role_id)
    if existing_role is not None:
        # 角色已存在
        return False

    # 创建新角色
    role_model = Role(
        id=role_id,
        uid=uid
    )
    return role_model.save()

def get_role(role_id: str) -> Role:
    # 根据ID查找角色
    return Role.find_by_id(role_id)

def get_roles_by_uid(uid: str) -> List["Role"]:
    # 根据uid查找所有角色
    return Role.find_by_uid(uid)