

from database.user import User

def create_user(uid:str,password:str)->bool:
    # 检查用户是否已存在
    existing_user = User.find_by_id(uid)
    
    if existing_user is not None:
        # 用户已存在
        return False
    
    # 创建新用户
    user_model = User(
        id=uid, 
        password=password
    )
    return user_model.save()

def login_user(uid:str,password:str)->bool:
    # 查找用户
    existing_user = User.find_by_id(uid)
    
    if existing_user is None:
        # 用户不存在
        return False
    
    # 验证密码
    return existing_user.verify_password(password)
