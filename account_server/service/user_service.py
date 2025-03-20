from account_server import proto
from account_server.repository import user_repository

def account_register(request:proto.common_pb2.AccountRegisterRequest):
    return user_repository.create_user(request)



def account_login(request:proto.common_pb2.AccountLoginRequest):
    return user_repository.login_user(request)