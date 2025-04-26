
from ..repository import user_repository

def account_sign_up(uid:str,password:str):
    return user_repository.create_user(uid,password)



def account_login(uid:str,password:str):
    return user_repository.login_user(uid,password)