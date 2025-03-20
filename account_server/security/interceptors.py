import grpc
from grpc_interceptor import ServerInterceptor
import jwt
from typing import Callable, Any
from account_server.config import config

JWT_SECRET = config["Security"]["jwt_secret"]


EXCLUDED_METHODS = config["Security"]["excluded_methods"]

class AuthInterceptor(ServerInterceptor):
    def intercept(
        self,
        method: Callable,
        request: Any,
        context: grpc.ServicerContext,
        method_name: str
    ) -> Any:
        """拦截每个gRPC请求并验证JWT令牌"""
        # 跳过登录等不需要认证的方法
        if method_name in EXCLUDED_METHODS:
            return method(request, context)

        # 从元数据中获取令牌
        metadata = dict(context.invocation_metadata())
        auth_header = metadata.get("authorization", "")
        
        if not auth_header.startswith("Bearer "):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "缺少有效的认证令牌")
        
        token = auth_header[7:]  # 移除 "Bearer " 前缀
        
        try:
            # 验证JWT令牌
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            
            # 将解码后的用户信息添加到上下文，方便后续处理
            context.user_id = payload.get("user_id")
            
            # 调用原始方法
            return method(request, context)
        except jwt.PyJWTError as e:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, f"无效的认证令牌: {str(e)}")

