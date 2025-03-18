import asyncio
import grpc
import proto


class account_server:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

        