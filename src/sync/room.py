from sync_core import SyncCore
from sync_server import SyncServer
class Room:
    def __init__(self,room_id:int,sync_server:SyncServer):
        self.room_id:int = room_id
        self.sync_server:SyncServer = sync_server
        self.sync_core:SyncCore = SyncCore(sync_server)
        
    
    def receive_action(self,msg:dict):
        self.sync_core.receive_action(msg)

    def run(self,user_dict:dict):
        pass

        
    
    