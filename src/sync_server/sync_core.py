from aiokcp import create_server
from aiokcp.sync import KCPSocket

import msgpack
from typing import Dict,List
class SyncCore:
    def __init__(self, ):
        pass

    def start(self, authentication_information: List[str]):
        self.authentication_information = authentication_information
        
    async def handle_connection(self):
        while True:
            sock, _ = self.kcp_server.accept()
            self.sockets.append(sock)
            msg = sock.recv(1024)

        

        


    def start(self, authentication_information: List[str]):
        self.authentication_information = authentication_information

