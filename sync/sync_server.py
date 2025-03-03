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
from queue import Queue
from threading import Thread

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





@singleton
class SyncServer(SyncServerInterface):
    def __init__(self, host: str, port: int, num_of_rooms: int, kcp_kwargs=None):
        self._host = host
        self._port = port
        
        self.transport_dict: Dict[str, KCPStreamTransport] = {}
        self._room_list: List[Room] = []
        self._max_num_of_rooms = num_of_rooms
        self._kcp_kwargs:dict = kcp_kwargs
        self._running:bool = False

        for i in range(num_of_rooms):
            self._room_list.append(Room(i,self))

        

        self._kcp_server: Optional[KCPServer] = None
   
        self.proto_dict:Dict[str, SyncServer.Protocol] = {}
        self.token_dict:Dict[str,str] = {}
        self.crypto_dict:Dict[str,AES_CBC] = {}
        self._thread_pool:ThreadPoolExecutor = ThreadPoolExecutor(max_workers=config["Server"]["num_of_rooms"])

        self._lock = RLock()  # 使用可重入锁
        self._message_queue = Queue()
        self._write_thread = Thread(target=self._process_message_queue, daemon=True)
        
        
        
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
        self._thread_pool.shutdown(wait=True)


    async def initialize_server(self):
        self._kcp_server = await create_server(
            protocol_factory=self.Protocol,
            host=self._host,
            port=self._port,
            kcp_kwargs=self._kcp_kwargs
        )
        self._running = True
        self._write_thread.start()
        async with self._kcp_server:
            await self._kcp_server.serve_forever()
    
        

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
        self._thread_pool.submit(self._room_list[room_id].msg_handle,msg)
        
    def send_msg(self, uid: str, proto: str, data: dict):
        """发送消息的公开接口"""
        try:
            with self._safe_operation("send_msg"):
                msg: bytes = utils.encrypt_msg(uid, self.token_dict[uid], proto, data, time.time(), self.crypto_dict[uid])
            
            # 将消息放入队列
            self._message_queue.put((uid, msg))
        except Exception as e:
            logger.error(f"Error preparing message for {uid}: {e}")
        
    def _process_message_queue(self):
        """处理消息队列的后台线程"""
        while self._running:
            try:
                uid, msg = self._message_queue.get()
                if uid is None:  # 停止信号
                    break
                    
                try:
                    with self._safe_operation("_process_message_queue"):
                        transport = self.transport_dict.get(uid)
                        if transport and transport.is_closing() == False and transport._closed == False: 
                            transport.write(msg)
                        else:
                            # logger.warning(f"No transport found for uid: {uid}")
                            pass
                except Exception as e:
                    logger.warning(f"Error sending message to {uid}: {e}")
                finally:
                    self._message_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing message queue: {e}")

            time.sleep(config['KCP']['update_interval'] / 1000)
    
    async def run(self):
        await self.initialize_server() 


    def shutdown(self):
        """关闭服务器时清理资源"""
        self._running = False
        # 发送停止信号
        self._message_queue.put((None, None))
        # 等待队列处理完成
        if not self._message_queue.empty():
            logger.info("Waiting for message queue to empty...")
            self._message_queue.join()
        # 等待写线程结束
        self._write_thread.join(timeout=5.0)
        if self._write_thread.is_alive():
            logger.warning("Write thread did not terminate properly")

    class Protocol(asyncio.Protocol):
        def __init__(self):
            self.sync_server = sync_server
            self.on_con_lost:asyncio.Future = asyncio.Future()
            self.uid:Optional[str] = None

        def connection_made(self, transport):
            peername = transport.get_extra_info('peername')
            logger.info('Connection from {}'.format(peername))
            self.transport: KCPStreamTransport = transport

        def connection_lost(self, exc):
            logger.info(f'uid: {self.uid} Connection lost')
            self.on_con_lost.set_result(True)
            self.sync_server.transport_dict.pop(self.uid)

        def data_received(self, data:bytes):
            
            msg = utils.decrypt_msg(
                data,
                self.sync_server.token_dict,
                self.sync_server.crypto_dict
            )
            if msg is None:
                return
            self.uid = msg['uid']
            self.sync_server.msg_handle(msg,self.transport)


        
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
    sync_server.allocate_user('lifesize1','114514',0,crypto_key,crypto_salt)
    sync_server.allocate_user('lifesize2','114514',0,crypto_key,crypto_salt)
    asyncio.run(sync_server.run())
    
    

    