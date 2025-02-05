from aiokcp import create_server,KCPStreamTransport
from aiokcp.crypto import AES_CBC
from aiokcp.sync import KCPSocket,KCPServer
import msgpack
from typing import Dict,List,Any,Optional,Union,Tuple
from room import Room
import asyncio
import toml
import os
import logging

logger = logging.getLogger(__name__)

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建 config.toml 文件的绝对路径
config_path = os.path.join(current_dir, 'config.toml')

# 读取并解析 TOML 文件
config = toml.load(config_path)


class SyncServer:
    def __init__(self, host: str, port: int, initial_num_of_rooms: int, max_num_of_rooms: int,kcp_kwargs = None):
        self.host = host
        self.port = port
        self.sync_core_count: int = 0
        self.transport_dict: Dict[str,KCPSocket] = {}
        self.room_dict: Dict[int,Room] = {}
        self.max_num_of_rooms = max_num_of_rooms
        for i in range(initial_num_of_rooms):
            self.room_dict[i] = Room(host, port)
            self.sync_core_count += 1

        self.kcp_server: KCPServer = create_server(
            protocol_factory=self.Protocol,
            host = self.host,
            port = self.port,
            kcp_kwargs = kcp_kwargs
            )
        self.user_info: Dict = {}
        
        
    def allocate_user(self, uid: str, ip_address:str, token: str, room_id: int, crypto_key: bytes, crypto_salt: bytes):
        crypto: AES_CBC = AES_CBC(crypto_key, crypto_salt)
        self.user_info[uid] = {
            'token': token,
            'room_id': room_id,
            'crypto': crypto,
            }
        
    def remove_user(self,uid):
        pass
        
        

    def get_user_info(self, uid: str):
        return self.user_info.get(uid)

    

    class Protocol(asyncio.Protocol):
        def connection_made(self, transport):
            peername = transport.get_extra_info('peername')
            logger.info('Connection from {}'.format(peername))
            self.transport:KCPStreamTransport = transport

        def data_received(self, data):
            SYNC_SERVER.data_received(self.transport, data)
        

    def data_received(self, transport:KCPStreamTransport, msg:bytes):
        try:
            msg = self.decrypt_msg(msg)
            if msg is None:
                return
               
        except Exception as e:
            logger.warning(e)
            return
    
    def encrypt_msg(self,uid:str, proto:str, data:Any)->bytes:
        data = msgpack.pack(data)
        crypto: AES_CBC = self.user_info["crypto"]
        data = crypto.encrypt(data)
        msg = {"uid":uid, "proto":proto, "data":data}
        msg = msgpack.pack(data)
        return msg
    
    def decrypt_msg(self, msg:bytes)->Optional[dict]:
        try:
            msg = msgpack.unpack(msg)
        except Exception as e:
            logger.warning(e)
            return None

        uid = msg.get('uid')
        
        if uid not in self.user_info:
            return None
        
        proto = msg.get('proto')
        if not isinstance(proto,str):
            return

        data = msg.get('data')
        if not isinstance(data,dict):
            return
        
        crypto: AES_CBC = self.user_info["crypto"]
        
        try:
            data = crypto.decrypt(data)
            data = msgpack.unpack(data)
        except Exception as e:
            logger.warning(e)
            return None
        
        token:str = data['token']
        if token != self.user_info[uid]['token']:
            logger.warning(f"UID为{uid}的客户端发来消息的token错误")
            return None

        return {'uid':uid,'proto':proto,'data':data}

    async def loop(self):
        while True:
            sock, _ = self.kcp_server.handle_request
            msg = sock.recv(1024)
            try: 
                msg = msgpack.unpackb(msg)
                proto = msg.get('proto')
                if proto == 'authentication':
                   self.authentication_handler(msg)
                else:
                    logger.info('Unknown protocol')    
            except Exception as e:
                logger.info(e)

    def start(self):
        asyncio.run(self.loop())
       
    
    


SYNC_SERVER = SyncServer(
    config['Network']['host'], 
    config['Network']['port'],
    config['SyncServer']['initial_num_of_rooms'],
    config['SyncServer']['max_num_of_rooms'],
    )


if __name__ == '__main__':
    SYNC_SERVER.start()