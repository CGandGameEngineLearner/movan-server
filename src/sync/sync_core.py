from typing import List, Dict

import threading
import time
from config import config
from sync_server_interface import SyncServerInterface
import asyncio


class SyncCore:
    def __init__(self, sync_server: SyncServerInterface):
        self.frames: List = []
        self.running: bool = False
        self.action_buffer: List[dict] = []
        self.user_set: set = set()
        self.mutex = threading.Lock()
        self.frame_count: int = 0
        self.update_interval = config["SyncCore"]["update_interval"]
        self.sync_server: SyncServerInterface = sync_server

    def run(self):
        self.running = True
        while self.running:
            self.mutex.acquire()

            self.action_buffer.sort(key=lambda x: x["extra_data"]["timestamp"])
            self.broadcast_actions(self.frame_count, self.action_buffer)
            self.frames.append(self.action_buffer)
            self.action_buffer.clear()
            self.frame_count += 1

            self.mutex.release()
            time.sleep(self.update_interval / 1000)

    def stop(self):
        self.running = False

    def receive_action(self, opertation):
        self.mutex.acquire()
        self.action_buffer.append(opertation)
        self.mutex.release()

    def broadcast_actions(self, frame_count: int, actions: List[dict]):
        for uid in self.user_set:
            data: dict = {"frame_cout": frame_count, "actions": actions}
            self.sync_server.send_msg(uid, "sync_actions", data)

    def reload_actions(self,uid:int, start_frame:int):
        data = []
        for i in range(start_frame,len(self.frames)):
            data.append({"frame_cout": i, "actions": self.frames[i]})

        self.sync_server.send_msg(uid,"reload_actions",)


    def add_user(self, uid: str):
        self.user_set.add(uid)
