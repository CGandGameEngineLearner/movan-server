
from account.rpc.rpc_server import ACCOUNT_RPC_SERVER


from account.config import CONFIG


from account.service import user_service
from account.database.role import Role

@ACCOUNT_RPC_SERVER.method
async def account_sign_up(
    uid: str,
    password: str,
) -> bool:
    return user_service.account_sign_up(uid, password)

@ACCOUNT_RPC_SERVER.method
async def account_login(
    uid: str,
    password: str,
) -> bool:
    return user_service.account_login(uid, password)

@ACCOUNT_RPC_SERVER.method
async def create_role(
    role_id: str,
    uid: str,
) -> bool:
    # 创建新角色
    existing_roles = Role.find_by_uid(uid)
    if any(role.id == role_id for role in existing_roles):
        return False
    role = Role(id=role_id, uid=uid)
    return role.save()

@ACCOUNT_RPC_SERVER.method
async def get_role(
    role_id: str,
) -> dict:
    # 获取单个角色信息
    role = Role.find_by_id(role_id)
    if not role:
        return {}
    return {"id": role.id, "uid": role.uid}

@ACCOUNT_RPC_SERVER.method
async def get_roles_by_uid(
    uid: str,
) -> list:
    # 获取指定uid的所有角色
    roles = Role.find_by_uid(uid)
    return [{"id": role.id, "uid": role.uid} for role in roles]
 
