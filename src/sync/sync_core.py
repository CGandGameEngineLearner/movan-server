from typing import List

import threading
import time
from config import config
from sync_server import SyncServer


class SyncCore:
    def __init__(self, sync_server:SyncServer):
        self.frames:List = []
        self.running:bool = False
        self.action_buffer:List[dict] = []
        self.user_dict:dict = []
        self.mutex = threading.Lock()
        self.frame_count:int = 0
        self.update_interval = config["SyncCore"]["update_interval"]
        self.sync_server = sync_server

    async def run(self):
        self.running = True
        while self.running:
            self.mutex.acquire()

            self.action_buffer.sort(key=lambda x:x['extra_data']['timestamp'])
            self.broadcast_actions(self.action_buffer)
            self.frames.append(self.action_buffer)
            self.action_buffer.clear()
            self.frame_count += 1

            self.mutex.release()
            time.sleep(self.update_interval/1000)
            
            
            
    
    def stop(self):
        self.running = False
        
    def receive_action(self,opertation):
        self.mutex.acquire()
        self.action_buffer.append(opertation)
        self.mutex.release()

    def broadcast_actions(self,actions:list):
        for uid in self.user_dict:
            self.sync_server.send_msg(uid,'sync_actions',actions)

    


    