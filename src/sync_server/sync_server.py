from aiokcp import create_server,KCPStreamTransport
from aiokcp.crypto import get_crypto
from aiokcp.sync import KCPSocket,KCPServer
import msgpack
from typing import Dict,List
from sync_core import SyncCore
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
        self.core_dict: Dict[int,SyncCore] = {}
        for i in range(initial_num_of_rooms):
            self.core_dict[i] = SyncCore(host, port)
            self.sync_core_count += 1

        self.kcp_server: KCPServer = create_server(
            protocol_factory=self.Protocol,
            host = self.host,
            port = self.port,
            kcp_kwargs = kcp_kwargs
            )
        self.user_info: Dict = {}
        
        
    def allocate_user(self, uid: str, ip_address:str, token: str, room_id: int, crypto_key: bytes, crypto_salt: bytes):
        self.user_info[uid] = {
            'token': token,
            'ip_address': ip_address,
            'room_id': room_id,
            'crypto_key': crypto_key,
            'crypto_salt': crypto_salt,
            
            }
        
        

    def get_user_info(self, uid: str):
        return self.user_info.get(uid)

    

    class Protocol(asyncio.Protocol):
        def connection_made(self, transport):
            peername = transport.get_extra_info('peername')
            logger.info('Connection from {}'.format(peername))
            self.transport:KCPStreamTransport = transport

        def data_received(self, data):
            SYNC_SERVER.data_received(self.transport, data)
        

    def data_received(self, transport:KCPStreamTransport, data:bytes):
        try:
            peername = transport.get_extra_info('peername')
            ip_address = peername[0]
            msg = msgpack.unpackb(data)
            uid = msg.get('uid')
            if uid == None or uid not in self.user_info:
                return
            
            if self.user_info[uid]['ip_address'] != ip_address:
                return
            
            proto = msg.get('proto')
            
            if proto == 'authentication':
                self.authentication_handler(msg)
            else:
                logger.warning("unkown proto")          
           
        except Exception as e:
            logger.warning(e)
            return
            
    
    def authentication_handler(self, msg):
        uid = msg.get('uid')
        token = msg.get('token')
        if not uid or not token:
            return
    
        if uid not in self.user_info:
            return
        
        if token != self.user_info[uid].get('token'):
            return
        
        logger.info(f"{msg}")
        
        
    
                
    

    def start(self):
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
    
    

crypto_key = config['SyncServer']['crypto']['key']
crypto_salt = config['SyncServer']['crypto']['salt']
SYNC_SERVER = SyncServer(
    config['Network']['host'], 
    config['Network']['port'],
    config['SyncServer']['initial_num_of_rooms'],
    config['SyncServer']['max_num_of_rooms'],
    )