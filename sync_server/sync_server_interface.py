from abc import ABC, abstractmethod
from aiokcp import KCPStreamTransport

class SyncServerInterface(ABC):

    @abstractmethod
    def allocate_user(self, uid: str, token: str, room_id: int, crypto_key: bytes, crypto_salt: bytes):
        pass

    @abstractmethod
    def remove_user(self, uid):
        pass

    @abstractmethod
    def msg_handle(self,msg:dict,transport:KCPStreamTransport):
        pass

    @abstractmethod
    def send_msg(self, uid: str, proto: str, data: dict):
        pass

    @abstractmethod
    async def run(self):
        pass