import grpc
import proto
import config
import proto

from loguru import logger

from typing import Dict

SYNC_SERVER_STUBS:Dict[int,proto.server_pb2_grpc.SyncServerStub] = {}

for i,url in enumerate(config['SyncServer']['urls']):
    with grpc.aio.insecure_channel(url) as channel:
        stub = proto.server_pb2_grpc.SyncServerStub(channel)
        SYNC_SERVER_STUBS[i] = stub
        



if __name__ == '__main__':
    crypto_key = b'12345678901234567890123456789012'
    crypto_salt = b'1234567890123456'
    SYNC_SERVER_STUBS[0].allocate_user('lifesize0', '114514', 0, crypto_key, crypto_salt)