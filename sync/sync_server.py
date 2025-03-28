import asyncio
from asyncio import Transport
from utils import Crypto

from typing import Dict, List, Any, Optional, Union, Tuple
from room import Room
import asyncio

from common.movan_rpc.server import RPCServer

from rpc.rpc_server import SYNC_RPC_SERVER

import utils
import time
from sync_server_interface import SyncServerInterface
from common.design_pattern.singleton import singleton
from config import CONFIG

from user_info_manager import user_info_manager

from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
import asyncio.queues


import proto

from logger import logger


@singleton
class SyncServer(SyncServerInterface):
    def __init__(self, host: str, port: int, num_of_rooms: int, kcp_kwargs=None):
        self._host = host
        self._port = port
        
        self.transport_dict: Dict[str, Transport] = {}
        self._room_list: List[Room] = []
        self._max_num_of_rooms = num_of_rooms
        self._kcp_kwargs: dict = kcp_kwargs
        self._running: bool = False

        for i in range(num_of_rooms):
            self._room_list.append(Room(i, self))

        self._server: Optional[asyncio.Server] = None
        self.proto_dict: Dict[str, SyncServer.Protocol] = {}
        self.token_dict: Dict[str, str] = {}
        self.crypto_dict: Dict[str, Crypto] = {}
        self._thread_pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=CONFIG["Server"]["num_of_rooms"])

        self._lock = asyncio.Lock()  # 使用异步锁
        self._message_queue = asyncio.Queue()  # 使用异步队列
        self._last_message_time_dict: Dict[str, float] = dict()
        self._process_message_task = None  # 消息处理任务
        self._process_rpc_task = None  # RPC 服务任务
        self._temp_queue = []  # 用于存储非协程上下文中的消息
        
        
    @asynccontextmanager
    async def _safe_operation(self, operation: str):
        """异步安全操作的上下文管理器"""
        try:
            await self._lock.acquire()
            yield
        except Exception as e:
            logger.error(f"Error during {operation}: {e}")
            raise
        finally:
            self._lock.release()

    def __del__(self):
        self.shutdown()

    async def start(self):
        loop = asyncio.get_running_loop()

        self._server = await loop.create_server(
            lambda: self.Protocol(self),
            host=self._host,
            port=self._port,
        )
        self._running = True
        self._process_message_task = asyncio.create_task(self._process_message_queue())
        self._process_rpc_task = asyncio.create_task(self._process_rpc_server())
        async with self._server:
            await self._server.serve_forever()

    async def _process_rpc_server(self):
        await SYNC_RPC_SERVER.start()


    @SYNC_RPC_SERVER.method
    async def allocate_user(self, uid: str, token: str, room_id: int, crypto_key: str, crypto_salt: str):
        logger.info(f"{uid}")
        async with self._safe_operation("allocate_user"):
            self.token_dict[uid] = token
            crypto: Crypto = Crypto(crypto_key, crypto_salt)
            self.crypto_dict[uid] = crypto
        user_info_manager.set_user_info(uid, {"room_id": room_id})

    @SYNC_RPC_SERVER.method
    async def remove_user(self, uid):
        self._cleanup_user(uid)
        async with self._safe_operation("remove_user"):
            user_info_manager.remove_user_info(uid)
            if uid in self.transport_dict:
                self.transport_dict.pop(uid, None)

            if uid in self.token_dict:
                self.token_dict.pop(uid, None)
            
            if uid in self.crypto_dict:
                self.crypto_dict.pop(uid, None)
        user_info_manager.remove_user_info(uid)

    async def msg_handle(self, msg: dict, transport: Transport):
        # logger.debug(msg)
        uid = msg['uid']
        async with self._safe_operation("update transport"):
            self.transport_dict[uid] = transport
            self._last_message_time_dict[uid] = time.time()

        room_id: int = user_info_manager.get_user_info(uid)['room_id']
        # 使用线程池处理房间消息
        await asyncio.get_event_loop().run_in_executor(
            self._thread_pool, 
            self._room_list[room_id].msg_handle, 
            msg
        )

    def send_msg(self, uid: str, proto: str, data: dict):
        """发送消息的公开接口"""
        try:
            msg: bytes = utils.encrypt_msg(
                uid, self.token_dict[uid], proto, data, 
                time.time(), self.crypto_dict[uid]
            )
            
            # 检查是否在事件循环中
            try:
                loop = asyncio.get_running_loop()
                # 如果在事件循环中，使用异步方式
                loop.create_task(self._message_queue.put((uid, msg)))
            except RuntimeError:
                # 如果不在事件循环中，使用同步方式
                if not hasattr(self, '_temp_queue'):
                    self._temp_queue = []
                self._temp_queue.append((uid, msg))
                
        except Exception as e:
            logger.error(f"Error preparing message for {uid}: {e}")

    async def _process_message_queue(self):
        """异步处理消息队列"""
        while self._running:
            try:
                # 处理临时队列中的消息
                if hasattr(self, '_temp_queue') and self._temp_queue:
                    for uid, msg in self._temp_queue:
                        await self._message_queue.put((uid, msg))
                    self._temp_queue.clear()

                try:
                    # 使用 wait_for 添加超时
                    uid, msg = await asyncio.wait_for(
                        self._message_queue.get(),
                        timeout=CONFIG['KCP']['update_interval'] / 1000
                    )
                except asyncio.TimeoutError:
                    await self._check_connections()
                    continue

                if uid is None:  # 停止信号
                    continue

                await self._send_message(uid, msg)
                await self._check_connections()

            except Exception as e:
                logger.error(f"Error in message queue processor: {e}")
                await asyncio.sleep(0.1)

    async def _send_message(self, uid: str, msg: bytes):
        """异步处理单个消息的发送"""
        success:bool = False
        async with self._safe_operation("send_message"):
            transport = self.transport_dict.get(uid)
            
            if transport and not transport.is_closing():
                try:
                    transport.write(msg)
                    success = True
                except Exception as e:
                    logger.warning(f"Error sending message to {uid}: {e}")
        if not success:
            await self._cleanup_user(uid)

    async def _check_connections(self):
        """异步检查连接状态"""
        async with self._safe_operation("check_connections"):
            current_time = time.time()
            timeout_uids = []
            
            for uid, timestamp in list(self._last_message_time_dict.items()):
                if current_time - timestamp > CONFIG['Server']['timeout']:
                    timeout_uids.append(uid)
                    
        for uid in timeout_uids:
            logger.info(f"Connection timeout for uid: {uid}")
            await self._cleanup_user(uid)

    async def _cleanup_user(self, uid: str):
        """异步清理用户资源"""
        async with self._safe_operation("cleanup_user"):
            if uid in self.transport_dict:
                self.transport_dict.pop(uid, None)
            if uid in self._last_message_time_dict:
                self._last_message_time_dict.pop(uid, None)
        room_id: int = user_info_manager.get_user_info(uid)['room_id']
        if room_id is not None:
            self._room_list[room_id].leave_room(uid)
        logger.info(f"Cleaned up resources for {uid}")

    def run(self):
        asyncio.run(self.start())

    async def shutdown(self):
        """异步关闭服务器"""
        self._running = False
        self._thread_pool.shutdown(wait=True)
        if self._process_message_task:
            await self._message_queue.put((None, None))
            await self._process_message_task
        await self._server.close()
        await SYNC_RPC_SERVER.shutdown()

    class Protocol(asyncio.Protocol):
        def __init__(self):
            self.sync_server = SYNC_SERVER
            self.on_con_lost: asyncio.Future = asyncio.Future()
            self.uid: Optional[str] = None

        def connection_made(self, transport):
            peername = transport.get_extra_info('peername')
            logger.info(f'Connection from {peername}')
            self.transport: Transport = transport

        def connection_lost(self, exc):
            logger.info(f'uid: {self.uid} Connection lost')
            self.on_con_lost.set_result(True)
            if self.uid:
                asyncio.create_task(self.sync_server._cleanup_user(self.uid))

        def data_received(self, data: bytes):
            msg = utils.decrypt_msg(
                data,
                self.sync_server.token_dict,
                self.sync_server.crypto_dict
            )
            if msg is None:
                return
            self.uid = msg['uid']
            asyncio.create_task(self.sync_server.msg_handle(msg, self.transport))

kcp_kwargs = {
    'no_delay': CONFIG['KCP']['no_delay'],
    'update_interval': CONFIG['KCP']['update_interval'],
    'resend_count': CONFIG['KCP']['resend_count'],
    'no_congestion_control': CONFIG['KCP']['no_congestion_control']
}

SYNC_SERVER = SyncServer(
    CONFIG['Network']['sync_host'],
    CONFIG['Network']['sync_port'],
    CONFIG['Server']['num_of_rooms'],
    kcp_kwargs
)

if __name__ == '__main__':
    logger.info("Sync server started")
    crypto_key = b'12345678901234567890123456789012'
    crypto_salt = b'1234567890123456'

    async def test():
        await SYNC_SERVER.allocate_user('lifesize', '114514', 0, crypto_key, crypto_salt)
        await SYNC_SERVER.allocate_user('lifesize', '114514', 0, crypto_key, crypto_salt)
        await SYNC_SERVER.allocate_user('lifesize', '114514', 0, crypto_key, crypto_salt)
        await SYNC_SERVER.allocate_user('lifesize', '114514', 0, crypto_key, crypto_salt)
        await SYNC_SERVER.start()
    asyncio.run(test())