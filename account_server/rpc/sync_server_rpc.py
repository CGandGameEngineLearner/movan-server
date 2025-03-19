import grpc
from account_server.config import config
from account_server import proto
from loguru import logger

from typing import Dict

SYNC_SERVER_STUBS:Dict[int,proto.server_pb2_grpc.SyncServerStub] = {}

for i,url in enumerate(config['SyncServer']['urls']):
    channel = grpc.insecure_channel(url)
    stub = proto.server_pb2_grpc.SyncServerStub(channel)
    SYNC_SERVER_STUBS[i] = stub
        



if __name__ == '__main__':
    crypto_key = b'12345678901234567890123456789012'
    crypto_salt = b'1234567890123456'
    request = proto.server_pb2.AllocateUserRequest(
        uid='lifesize0',
        token ='114514',
        room_id = 0,
        crypto_key=crypto_key,
        crypto_salt=crypto_salt
    )
    import time
    time.sleep(10)
    respond = SYNC_SERVER_STUBS[0].allocate_user(request)
    print(respond)