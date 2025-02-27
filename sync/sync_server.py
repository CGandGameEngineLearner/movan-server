from aiokcp import create_server,create_connection, KCPStreamTransport
from aiokcp.crypto import AES_CBC
from aiokcp.sync import KCPServer
from typing import Dict, List, Any, Optional, Union, Tuple
from room import Room
import asyncio

from loguru import logger
import utils
import time
from sync_server_interface import SyncServerInterface
from base.singleton import singleton
from config import config

from user_info_manager import user_info_manager

from concurrent.futures import ThreadPoolExecutor
from threading import RLock
from contextlib import contextmanager

logger.add(
    sink=config['Log']['sink'],
    rotation=config['Log']['rotation'],
    retention=config['Log']['retention'],
    compression=config['Log']['compression'],
    enqueue=config['Log']['enqueue'],
    backtrace=config['Log']['backtrace'],
    diagnose=config['Log']['diagnose'],
    level=config['Log']['level'],
)

1



@singleton
class SyncServer(SyncServerInterface):
    def __init__(self, host: str, port: int, num_of_rooms: int, kcp_kwargs=None):
        self.host = host
        self.port = port
        
        self.transport_dict: Dict[str, KCPStreamTransport] = {}
        self.room_list: List[Room] = []
        self.max_num_of_rooms = num_of_rooms
        self.kcp_kwargs:dict = kcp_kwargs

        for i in range(num_of_rooms):
            self.room_list.append(Room(i,self))

        

        self.kcp_server: Optional[KCPServer] = None
   
        self.proto_dict:Dict[str, SyncServer.Protocol] = {}
        self.token_dict:Dict[str,str] = {}
        self.crypto_dict:Dict[str,AES_CBC] = {}
        self.thread_pool:ThreadPoolExecutor = ThreadPoolExecutor(max_workers=config["Server"]["num_of_rooms"])

        self._lock = RLock()  # 使用可重入锁
        
    @contextmanager
    def _safe_operation(self, operation: str):
        """
        安全操作的上下文管理器
        用于确保所有操作都是线程安全的，并提供适当的错误处理
        """
        try:
            self._lock.acquire()
            yield
        except Exception as e:
            logger.error(f"Error during {operation}: {e}")
            raise
        finally:
            self._lock.release()

    def __del__(self):
        self.thread_pool.shutdown(wait=True)


    async def initialize_server(self):
        self.kcp_server = await create_server(
            protocol_factory=self.Protocol,
            host=self.host,
            port=self.port,
            kcp_kwargs=self.kcp_kwargs
        )
        async with self.kcp_server:
            await self.kcp_server.serve_forever()
    
        

    def allocate_user(self, uid: str, token: str, room_id: int, crypto_key: bytes, crypto_salt: bytes):
        with self._safe_operation("allocate_user"):
            self.token_dict[uid] = token
            crypto: AES_CBC = AES_CBC(crypto_key, crypto_salt)
            self.crypto_dict[uid] = crypto
        user_info_manager.set_user_info(uid,{"room_id":room_id})


    def remove_user(self, uid):
        with self._safe_operation("remove_user"):
            user_info_manager.remove_user_info(uid)
            self.transport_dict.pop(uid, None)
            self.token_dict.pop(uid, None)
            self.crypto_dict.pop(uid, None)
        user_info_manager.remove_user_info(uid)
    
    


        
        
        
            

    def msg_handle(self, msg:dict,transport:KCPStreamTransport):
        logger.info(msg)
        uid = msg['uid']

        with self._safe_operation("update transport"):
            self.transport_dict[uid] = transport

        uid = msg['uid']
        room_id:int = user_info_manager.get_user_info(uid)['room_id']
        self.thread_pool.submit(self.room_list[room_id].msg_handle,msg)
        

    def send_msg(self, uid: str, proto: str, data: dict):
        with self._safe_operation("send_msg"):
            msg: bytes = utils.encrypt_msg(uid,self.token_dict[uid], proto, data, time.time(), self.crypto_dict[uid])
            self.transport_dict[uid].write(msg)
    
        
    
    async def run(self):
        await self.initialize_server() 


    class Protocol(asyncio.Protocol):
        def __init__(self):
            self.sync_server = sync_server
            

        def connection_made(self, transport):
            peername = transport.get_extra_info('peername')
            logger.info('Connection from {}'.format(peername))
            self.transport: KCPStreamTransport = transport

        def data_received(self, data:bytes):
            try:
                msg = utils.decrypt_msg(
                    data,
                    self.sync_server.token_dict,
                    self.sync_server.crypto_dict
                )
                if msg is None:
                    return
                self.sync_server.msg_handle(msg,self.transport)
            except Exception as e:
                logger.warning(e)
                return
    
    


        
kcp_kwargs = {
    'no_delay'              : config['KCP']['no_delay'],
    'update_interval'       : config['KCP']['update_interval'],
    'resend_count'          : config['KCP']['resend_count'],
    'no_congestion_control' : config['KCP']['no_congestion_control']
}

sync_server = SyncServer(
    config['Network']['host'],
    config['Network']['port'],
    config['Server']['num_of_rooms'],
    kcp_kwargs
)

if __name__ == '__main__':
    logger.info("Sync server started")
    crypto_key = b'12345678901234567890123456789012'
    crypto_salt = b'1234567890123456'
    sync_server.allocate_user('lifesize','114514',0,crypto_key,crypto_salt)
    asyncio.run(sync_server.run())
    
    

    