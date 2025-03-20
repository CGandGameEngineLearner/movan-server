from account_server import proto
from account_server import database

def create_user(user:proto.common_pb2.AccountRegisterRequest)->bool:
    with database.get_db_context() as session:
        # 先检查用户是否已存在
        existing_user = session.query(database.user.User).filter(
            database.user.User.id == user.account
        ).first()
        
        if existing_user:
            # 用户已存在
            return False
        
        user_model = database.user.User()
        user_model.id = user.account
        user_model.name = user.name
        user_model.password = user.password
        session.add(user_model)
        session.commit()
    return True

def login_user(user:proto.common_pb2.AccountLoginRequest)->bool:
    with database.get_db_context() as session:
        # 先检查用户是否已存在
        existing_user = session.query(database.user.User).filter(
            database.user.User.id == user.account
        )

        if existing_user is None:
            # 用户不存在
            return False
        
        user_model = existing_user.first()
        if user_model.verify_password(user.password):
            return True
        return False
