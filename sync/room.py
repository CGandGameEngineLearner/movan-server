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
        self.running = False
    
    
    def _action_handle(self,msg:dict):
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
        self.prepare_user_set.add(uid)

        # 如果所有人都准备好了 就开始
        if self.running == False and len(self.user_set) == len(self.prepare_user_set):
            logger.info("第{self.room_id}号房间开始运行")
            self.run()

    def _sync_request_reload_frames_handle(self,msg:dict):
        try:
            start_frame = msg['data']["start_frame"]
            uid = msg['uid']
        except Exception as e:
            logger.warning(e)
        self.sync_core.reload_frames(uid,start_frame)

    def run(self):
        self.running = True
        self.thread_pool.submit(self.sync_core.run())

    def stop(self):
        self.sync_core.stop()


    def msg_handle(self,msg:dict):
        try:
            proto:str = msg['extra_data']['proto']
        except Exception as e:
            logger.error(e)
            return
        
        if proto == "room_enter":
            self._enter_room_msg_handle(msg)
        elif proto == "room_leave":
            self._leave_room_msg_handle(msg)
        elif proto == "room_prepare":
            self._prepare_handle(msg)
        elif proto == 'sync_actions':
            self._action_handle(msg)
        elif proto == 'sync_request_reload_frames':
            self._sync_request_reload_frames_handle(msg)
        else:
            return