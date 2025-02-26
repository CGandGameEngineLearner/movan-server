from sync_core import SyncCore
from typing import Dict
from concurrent.futures import ThreadPoolExecutor
from config import config
from loguru import logger

class Room:

    thread_pool:ThreadPoolExecutor = ThreadPoolExecutor(max_workers=config["Server"]["num_of_rooms"])
    def __init__(self,room_id:int,sync_server):
        self.room_id:int = room_id
        self.sync_server = sync_server
        self.sync_core:SyncCore = SyncCore(sync_server)
        self.user_set: set = set()
        self.prepare_user_set:set = set()

    
    
    def receive_action(self,msg:dict):
        self.sync_core.receive_action(msg)

    def _enter_room_msg_handle(self,msg:dict):
        uid:str = msg.get('uid')
        self.user_set.add(uid)
        self.sync_core.add_user(uid)
        logger.info(f"{uid} enter room")

    def _leave_room_msg_handle(self,msg:dict):
        uid:str = msg.get('uid')
        self.sync_core.user_set.pop(uid)
        self.user_set.pop(uid)

    def _prepare_handle(self,msg:dict):
        uid:str = msg.get('uid')
        self.user_set.add(uid)

        # 如果所有人都准备好了 就开始
        if len(self.user_set) == len(self.prepare_user_set):
            self.run()

    def run(self):
        self.thread_pool.submit(self.sync_core.run())

    def stop(self):
        self.sync_core.stop()


    def room_msg_handle(self,msg:dict):
        try:
            proto:str = msg['data']['proto']
        except Exception as e:
            logger.error(e)
            return
        
        if proto == "enter_room":
            self._enter_room_msg_handle(msg)
        elif proto == "leave_room":
            self._leave_room_msg_handle(msg)
        elif proto == "prepare":
            self._prepare_handle(msg)
        else:
            return