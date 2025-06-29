from sync_core import SyncCore
from typing import Dict
from concurrent.futures import ThreadPoolExecutor
from config import CONFIG
from logger import logger
import time
class Room:

    thread_pool:ThreadPoolExecutor = ThreadPoolExecutor(max_workers=CONFIG["Server"]["num_of_rooms"])
    def __init__(self,room_id:int,sync_server):
        self.room_id:int = room_id
        self.sync_server = sync_server
        self.sync_core:SyncCore = SyncCore(sync_server)
        self.user_set: set = set()
        self.prepare_user_set:set = set()
        self.running = False
        self.last_request_time_dict:Dict[str:float] = {}
    
    
    def _sync_action_handle(self,msg:dict):
        logger.debug(f"receive sync action msg:\n{msg}")
        self.sync_core.receive_action_msg(msg)

    def _enter_room_msg_handle(self,msg:dict):
        uid:str = msg.get('uid')
        self.user_set.add(uid)
        self.sync_core.add_user(uid)
        logger.info(f"{uid} enter room")

    def _leave_room_msg_handle(self,msg:dict):
        uid:str = msg.get('uid')
        self.leave_room(uid)

    def _prepare_handle(self,msg:dict):
        uid:str = msg.get('uid')
        self.prepare_user_set.add(uid)
        logger.info(f"{uid} prepare")

        # 如果所有人都准备好了 就开始
        if self.running == False and len(self.user_set) == len(self.prepare_user_set):
            logger.info("第{self.room_id}号房间开始运行")
            self.run()

    def leave_room(self,uid:str):
        if uid in self.user_set:
            self.user_set.remove(uid)
        if uid in self.sync_core.user_set:
            self.sync_core.user_set.remove(uid)
        if uid in self.prepare_user_set:
            self.prepare_user_set.remove(uid)
        
        if len(self.user_set) == 0:
            self.stop()

    def _sync_request_reload_frames_handle(self,msg:dict):
        try:
            start_frame = msg['data']["start_frame"]
            uid = msg['uid']
        except Exception as e:
            logger.warning(e)

        logger.info(f"{uid} request reload frames")

        if uid in self.last_request_time_dict and time.time() - self.last_request_time_dict[uid] < 1:
            return
        self.last_request_time_dict[uid] = time.time()
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
        elif proto == 'sync_action':
            self._sync_action_handle(msg)
        elif proto == 'sync_request_reload_frames':
            self._sync_request_reload_frames_handle(msg)
        else:
            return