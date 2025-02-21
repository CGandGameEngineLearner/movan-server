from typing import Dict, List, Any, Optional, Union, Tuple
from aiokcp.crypto import AES_CBC
import msgpack
from loguru import logger

def encrypt_msg(uid: str, token:str,proto: str, data: Any, timestamp: float,crypto:AES_CBC) -> bytes:
    # 加密数据
    data_bytes = msgpack.packb(data)
    encrypted_data = crypto.encrypt(data_bytes)
    
    # 加密额外数据
    extra_data = {"proto": proto, "timestamp": timestamp, "token": token}
    extra_data_bytes = msgpack.packb(extra_data)
    encrypted_extra_data = crypto.encrypt(extra_data_bytes)
    
    # 打包消息
    msg = {"uid": uid, "data": encrypted_data, "extra_data": encrypted_extra_data}
    return msgpack.packb(msg)

def decrypt_msg(data: bytes, token_dict:Dict[str,str], crypto_dict:Dict[str,AES_CBC]) -> Optional[dict]:
    try:
        msg = msgpack.unpackb(data)
    except Exception as e:
        logger.warning(f"Failed to unpack message: {e}")
        return None

    uid = msg.get('uid')
    if uid == None:
        logger.warning(f"Message no uid")
        return None
    
    crypto: AES_CBC= crypto_dict[uid]

    try:
        # 解密数据
        encrypted_data = msg.get('data')
        if not isinstance(encrypted_data, bytes):
            logger.warning(f"Invalid data format for UID: {uid}")
            return None
        decrypted_data = crypto.decrypt(encrypted_data)
        data = msgpack.unpackb(decrypted_data)

        # 解密额外数据
        encrypted_extra_data = msg.get('extra_data')
        if not isinstance(encrypted_extra_data, bytes):
            logger.warning(f"Invalid extra_data format for UID: {uid}")
            return None
        decrypted_extra_data = crypto.decrypt(encrypted_extra_data)
        extra_data = msgpack.unpackb(decrypted_extra_data)

        # 验证额外数据
        proto = extra_data.get('proto')
        if not isinstance(proto, str):
            logger.warning(f"Invalid proto format for UID: {uid}")
            return None
        
        msg_token = extra_data.get('token')
        if msg_token != token_dict[uid]:
            logger.warning(f"Invalid token for UID: {uid}")
            return None
        
        timestamp = extra_data.get('timestamp')
        if not isinstance(timestamp, float):
            logger.warning(f"Invalid timestamp format for UID: {uid}")
            return None

        return {"uid": uid, "data": data, "extra_data": extra_data}
    except Exception as e:
        logger.warning(f"Error decrypting message: {e}")
        return None
    

if __name__ == '__main__':
    crypto_key = b'12345678901234567890123456789012'
    crypto_salt = b'1234567890123456'
    crypto: AES_CBC = AES_CBC(crypto_key, crypto_salt)
    crypto_dict = {'1234567890':crypto}
    token_dict = {'1234567890':'token'}
    import time
    start = time.time()
    origin_msg = encrypt_msg("1234567890", "token", "proto", {"data": "hello"}, 1693548000.00, crypto)

    print(decrypt_msg(origin_msg,token_dict,crypto_dict))
    print(time.time()-start)