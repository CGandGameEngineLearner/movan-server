from base.singleton import singleton
from typing import Dict

@singleton
class UserInfoManager:
    def __init__(self):
        self._user_info_dict:Dict[str:Dict] = {}

    def set_user_info(self,uid:str,info:dict):
        self._user_info_dict[uid] = info

    def get_user_info(self,uid:str): 
        return self._user_info_dict[uid]

    def remove_user_info(self,uid:str):
        self._user_info_dict.pop(uid)

    


user_info_manager = UserInfoManager()
        
