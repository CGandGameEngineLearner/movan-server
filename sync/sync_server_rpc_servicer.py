
import proto
from sync_server_interface import SyncServerInterface
from logger import logger

class SyncServerRpcServicer():
    def __init__(self,sync_server:SyncServerInterface):
        self.sync_server = sync_server
        
    
    async def allocate_user(self, request:proto.server_pb2.AllocateUserRequest, context):
        try:
            uid = request.uid
            token = request.token
            room_id = request.room_id
            crypto_key = request.crypto_key
            crypto_salt = request.crypto_salt
            await self.sync_server.allocate_user(
                            uid=uid,
                            token=token,
                            room_id=room_id,
                            crypto_key=crypto_key,
                            crypto_salt=crypto_salt
                        )
            return proto.common_pb2.BoolResponse(success=True,error_message="")
        except Exception as e:
            logger.warning(str(e))
            return proto.common_pb2.BoolResponse(success=False,error_message=str(e))
        

    async def remove_user(self, request:proto.server_pb2.RemoveUserRequest, context):
        try:
            uid = request.uid
            await self.sync_server.remove_user(uid)
            return proto.common_pb2.BoolResponse(success=True,error_message="")
        
        except Exception as e:
            return proto.common_pb2.BoolResponse(success=False,error_message=str(e))



