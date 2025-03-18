import grpc

import proto.server_pb2
import proto.common_pb2
import proto.server_pb2_grpc
from sync_server_interface import SyncServerInterface

class SyncServerRpcServicer(proto.server_pb2_grpc.SyncServerServicer):
    def __init__(self,sync_server:SyncServerInterface):
        self.sync_server = sync_server
        
    
    async def allocate_user(self, request:proto.server_pb2.AllocateUserRequest, context):
        try:
            uid = request.uid
            token = request.token
            room_id = request.room_id
            crypto_key = request.crypto_key
            crypto_salt = request.crypto_salt
            self.sync_server.allocate_user(uid,token,room_id,crypto_key,crypto_salt)
            return proto.common_pb2.BoolResponse(True,"")
        except Exception as e:
            return proto.common_pb2.BoolResponse(False,str(e))
        

    async def remove_user(self, request:proto.server_pb2.RemoveUserRequest, context):
        try:
            uid = request.uid
            self.sync_server.remove_user(uid)
            return proto.common_pb2.BoolResponse(True,"")
        
        except Exception as e:
            return proto.common_pb2.BoolResponse(False,str(e))



