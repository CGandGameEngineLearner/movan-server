"""
Protocol Buffers 生成的模块

包含服务定义和消息类型
"""

# 在外部引用时，为了避免 common_pb2 等文件不在 Python 路径中
# 这里我们可以提前在包内导入它们
import os
import sys

# 添加当前目录到 Python 路径，以便导入 common_pb2 等文件
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导出所有 protobuf 生成的模块
# 不使用相对导入，因为这些模块已经被传统的 protoc 生成
import client_pb2
import client_pb2_grpc
import common_pb2
import common_pb2_grpc
import server_pb2
import server_pb2_grpc

# 为了允许 from proto import xxx 这样的导入
__all__ = [
    'client_pb2', 'client_pb2_grpc',
    'common_pb2', 'common_pb2_grpc',
    'server_pb2', 'server_pb2_grpc'
]