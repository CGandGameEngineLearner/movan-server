import proto
from repository import user_repository

def account_register(request:proto.common_pb2.AccountRegisterRequest):
    return user_repository.create_user(request)



def account_login(request:proto.common_pb2.AccountLoginRequest):
    return user_repository.login_user(request)