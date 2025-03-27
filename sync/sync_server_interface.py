from abc import ABC, abstractmethod
import asyncio

class SyncServerInterface(ABC):

    @abstractmethod
    async def allocate_user(self, uid: str, token: str, room_id: int, crypto_key: str, crypto_salt: str):
        pass

    @abstractmethod
    async def remove_user(self, uid):
        pass

    @abstractmethod
    def msg_handle(self,msg:dict,transport:asyncio.Transport):
        pass

    @abstractmethod
    def send_msg(self, uid: str, proto: str, data: dict):
        pass

    @abstractmethod
    async def run(self):
        pass