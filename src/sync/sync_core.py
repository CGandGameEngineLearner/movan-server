from typing import List

import threading
import time
from config import config
from sync_server import SyncServer


class SyncCore:
    def __init__(self,player_num:int,sync_server:SyncServer):
        self.frames:List = []
        self.running:bool = False
        self.action_buffer:list = []
        self.player_num:int = player_num
        self.mutex = threading.Lock()
        self.frame_count:int = 0
        self.update_interval = config["SyncCore"]["update_interval"]
        self.sync_server = sync_server

    async def run(self):
        self.running = True
        while self.running:
            self.mutex.acquire()

            self.frames.append(self.action_buffer)
            self.action_buffer.clear()
            self.frame_count += 1

            self.mutex.release()
            time.sleep(self.update_interval/1000)
            
            
            
    
    async def stop(self):
        self.running = False
        
    def receive_action(self,opertation):
        self.mutex.acquire()
        self.action_buffer.append(opertation)
        self.mutex.release()

    


    