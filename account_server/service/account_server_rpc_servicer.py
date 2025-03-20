from account_server import proto

import user_service

class AccountServerRpcServicer(proto.client_pb2_grpc.AccountServerServicer):

    async def account_register(
            self, 
            request:proto.common_pb2.AccountRegisterRequest, 
            context
        ):
        try:
            if not user_service.account_register(request):
                return proto.common_pb2.BoolResponse(success=True,error_message="")
            return proto.common_pb2.BoolResponse(success=False,error_message="此账号已被注册")
        except Exception as e:
            return proto.common_pb2.BoolResponse(success=False,error_message=str(e))
        
    
    async def account_login(
            self,
            request:proto.common_pb2.AccountLoginRequest,
            context
    ):
        try:
            if not user_service.account_login(request):
                return proto.common_pb2.BoolResponse(success=True,error_message="")
            return proto.common_pb2.BoolResponse(success=False,error_message="账号或密码错误")
        except Exception as e:
            return proto.common_pb2.BoolResponse(success=False,error_message=str(e))
