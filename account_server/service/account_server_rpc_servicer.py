from account_server import proto


class AccountServerRpcServicer(proto.client_pb2_grpc.AccountServerServicer):

    async def account_register(
            self, 
            request:proto.common_pb2.AccountRegisterRequest, 
            context
        ):
        pass