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
        self.token_dict[uid] = token
        crypto: AES_CBC = AES_CBC(crypto_key, crypto_salt)
        self.crypto_dict[uid] = crypto
        user_info_manager.set_user_info(uid,{"room_id":room_id})


    def remove_user(self, uid):
        pass

    
    

   


    def msg_received(self,msg:dict,transport:KCPStreamTransport):

        uid = msg['uid']
        
        self.transport_dict[uid] = transport
        
        proto = msg['extra_data']['proto']

        if proto == 'join_room':
            self._join_room(msg)
        elif proto == 'action':
            self._action(msg)

    def send_msg(self, uid: str, proto: str, data: dict):
        msg: bytes = utils.encrypt_msg(uid, proto, self.token_dict[uid], data, time.time(), self.crypto_dict[uid])
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
                self.sync_server.msg_received(msg,self.transport)
            except Exception as e:
                logger.warning(e)
                return

    def _action(self,msg:dict):
        uid = msg['uid']
        room_id:int = user_info_manager.get_user_info(uid)['room_id']
        self.room_list[room_id].receive_action(msg)

    def _join_room(self,msg:dict):
        logger.info(f"UID为\"{msg['uid']}\"的客户端发送了个加入请求")
        
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
    
    

    