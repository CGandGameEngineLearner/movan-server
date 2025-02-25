from sync_core import SyncCore
from typing import Dict
from concurrent.futures import ThreadPoolExecutor
import config
class Room:

    thread_pool:ThreadPoolExecutor = ThreadPoolExecutor(max_workers=config["Server"]["num_of_rooms"])
    def __init__(self,room_id:int,sync_server):
        self.room_id:int = room_id
        self.sync_server = sync_server
        self.sync_core:SyncCore = SyncCore(sync_server)
        self.user_set: set = set()

    def msg_receive(self,msg:dict):
        pass    
    
    def receive_action(self,msg:dict):
        self.sync_core.receive_action(msg)

    def join_room(self,uid:int,user_info:dict):
        self.user_set.add(uid)
        self.sync_core.add_user(uid)

    def leave_room(self,uid):
        self.sync_core.user_set.pop(uid)
        self.user_set.pop(uid)

    def run(self):
        self.thread_pool.submit(self.sync_core.run())

    def stop(self):
        self.sync_core.stop()

    
    