import proto
import database
from database.user import User

def create_user(user:proto.common_pb2.AccountRegisterRequest)->bool:
    # 检查用户是否已存在
    existing_user = User.find_by_id(user.account)
    
    if existing_user is not None:
        # 用户已存在
        return False
    
    # 创建新用户
    user_model = User(
        id=user.account, 
        password=user.password
    )
    return user_model.save()

def login_user(user:proto.common_pb2.AccountLoginRequest)->bool:
    # 查找用户
    existing_user = User.find_by_id(user.account)
    
    if existing_user is None:
        # 用户不存在
        return False
    
    # 验证密码
    return existing_user.verify_password(user.password)
