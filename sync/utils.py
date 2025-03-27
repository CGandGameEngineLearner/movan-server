from typing import Dict, List, Any, Optional, Union, Tuple
import json
import struct


from logger import logger

from proto.encrypted_message_pb2 import EncryptedMessage, ExtraData, DecryptedMessage
from google.protobuf.json_format import MessageToDict




class Crypto:
    """简单异或加密类，替代 AES_CBC"""
    def __init__(self, key: Union[bytes,str],salt: Union[bytes,str]):
        if isinstance(key,str):
            key = key.encode('utf-8')
        if isinstance(salt,str):
            salt = salt.encode('utf-8')
        self.key = key
        self.salt = salt
    
    def encrypt(self, data: bytes) -> bytes:
        """使用异或加密数据"""
        return self._xor_process(data)
    
    
    def decrypt(self, data: bytes) -> bytes:
        """使用异或解密数据 (对称操作)"""
        return self._xor_process(data)
    
    def _xor_process(self, data: bytes) -> bytes:
        """执行异或操作，将数据与密钥按字节异或"""
        key_len = len(self.key)
        salt_len = len(self.salt)
        return bytes([data[i] ^ self.salt[i % salt_len] ^ self.key[i % key_len] for i in range(len(data))])


def _serialize_data(data: Any) -> bytes:
    """
    将任意Python数据序列化为字节串
    
    Args:
        data: 任意Python数据对象
        
    Returns:
        bytes: 序列化后的数据
    """
    if hasattr(data, 'SerializeToString'):
        # 如果是Protocol Buffer消息
        return data.SerializeToString()
    elif isinstance(data, (str, int, float, bool, bytes, list, dict)):
        # 基本类型和复合类型使用json序列化
        return json.dumps(data).encode('utf-8')
    else:
        # 其他类型强制转换为字符串后序列化
        return json.dumps(str(data)).encode('utf-8')


def _deserialize_data(data_bytes: bytes) -> Any:
    """
    将字节串反序列化为Python数据
    
    Args:
        data_bytes: 序列化后的数据
        
    Returns:
        Any: 反序列化后的Python对象
    """
    try:
        return json.loads(data_bytes.decode('utf-8'))
    except Exception as e:
        logger.warning(f"Failed to deserialize data: {e}")
        return data_bytes  # 返回原始字节串


def encrypt_msg(uid: str, token: str, proto: str, data: Dict, timestamp: float, crypto: Crypto) -> bytes:
    """
    使用Protocol Buffers加密消息
    
    Args:
        uid: 用户ID
        token: 用户令牌
        proto: 协议名称
        data: 需要加密的数据 (可以是任意Python对象)
        timestamp: 时间戳
        crypto: 加密器实例
        
    Returns:
        bytes: 加密并序列化后的消息字节
    """
    # 序列化数据
    data_bytes = _serialize_data(data)
    
    # 加密数据
    encrypted_data = crypto.encrypt(data_bytes)
    
    # 创建并填充额外数据
    extra_data = ExtraData()
    extra_data.proto = proto
    extra_data.timestamp = timestamp
    extra_data.token = token
    
    # 序列化并加密额外数据
    extra_data_bytes = extra_data.SerializeToString()
    encrypted_extra_data = crypto.encrypt(extra_data_bytes)
    
    # 创建并填充加密消息
    msg = EncryptedMessage()
    msg.uid = uid
    msg.encrypted_data = encrypted_data
    msg.encrypted_extra_data = encrypted_extra_data
    
    # 序列化最终消息
    return msg.SerializeToString()


def decrypt_msg(data: bytes, token_dict: Dict[str, str], crypto_dict: Dict[str, Crypto]) -> Optional[dict]:
    """
    解密并解析Protocol Buffers消息
    
    Args:
        data: 加密的消息字节
        token_dict: 用户ID到令牌的映射
        crypto_dict: 用户ID到加密器的映射
        
    Returns:
        dict: 解密后的消息，格式为 {"uid": str, "data": Any, "extra_data": dict}
              失败时返回 None
    """
    try:
        # 解析加密消息
        encrypted_msg = EncryptedMessage()
        encrypted_msg.ParseFromString(data)
        
        # 检查UID
        uid = encrypted_msg.uid
        if not uid:
            logger.warning("Message has no uid")
            return None
        
        # 检查加密器是否存在
        if uid not in crypto_dict:
            logger.warning(f"No crypto found for uid: {uid}")
            return None
        
        crypto = crypto_dict[uid]
        
        try:
            # 解密数据
            encrypted_data = encrypted_msg.encrypted_data
            decrypted_data_bytes = crypto.decrypt(encrypted_data)
            
            # 尝试反序列化数据
            data_content = _deserialize_data(decrypted_data_bytes)
            
            # 解密额外数据
            encrypted_extra_data = encrypted_msg.encrypted_extra_data
            decrypted_extra_bytes = crypto.decrypt(encrypted_extra_data)
            
            # 解析额外数据
            extra_data = ExtraData()
            extra_data.ParseFromString(decrypted_extra_bytes)
            
            # 验证token
            if extra_data.token != token_dict.get(uid, ''):
                logger.warning(f"Invalid token for UID: {uid}")
                return None
            
            # 转换extra_data为字典，并移除token
            extra_data_dict = MessageToDict(extra_data)
            if "token" in extra_data_dict:
                extra_data_dict.pop("token")
            
            return {
                "uid": uid, 
                "data": data_content, 
                "extra_data": extra_data
            }
        except Exception as e:
            logger.error(f"Error decrypting message: {e}")
            return None
    except Exception as e:
        logger.error(f"Error parsing encrypted message: {e}")
        return None


if __name__ == '__main__':
    # 测试
    crypto_key = b'12345678901234567890123456789012'
    crypto_salt = b'12345678901234567890123456789012'
    crypto = Crypto(crypto_key,crypto_salt)
    crypto_dict = {'1234567890': crypto}
    token_dict = {'1234567890': 'token'}
    
    import time
    start = time.time()
    
    test_data = {"data": "hello", "nested": {"value": 123}}
    origin_msg = encrypt_msg("1234567890", "token", "proto", test_data, 1693548000.00, crypto)
    result = decrypt_msg(origin_msg, token_dict, crypto_dict)
    
    print("Result:", result)
    print("Time elapsed:", time.time()-start)