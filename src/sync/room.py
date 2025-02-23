from sync_core import SyncCore
from typing import Dict

class Room:
    def __init__(self,room_id:int,sync_server):
        self.room_id:int = room_id
        self.sync_server = sync_server
        self.sync_core:SyncCore = SyncCore(sync_server)
        self.user_set: set = set()    

        
    
    def receive_action(self,msg:dict):
        self.sync_core.receive_action(msg)

    def join_room(self,uid:int,user_info:dict):
        self.user_set.add(uid)
        self.sync_core.add_user(uid)

    def leave_room(self,uid):
        self.sync_core.user_set.pop(uid)
        self.user_set.pop(uid)

    async def run(self,):
        self.sync_core.run()

    def stop(self):
        self.sync_core.stop()

    
    