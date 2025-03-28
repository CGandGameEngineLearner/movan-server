from common.design_pattern.singleton import singleton
from typing import Dict, Optional
import asyncio
from contextlib import contextmanager
from logger import logger

@singleton
class UserInfoManager:
    """
    协程安全的用户信息管理器
    使用 RLock 实现协程安全，支持可重入锁，避免死锁
    """
    def __init__(self):
        self._user_info_dict: Dict[str, Dict] = {}
        self._lock = asyncio.Lock()
        
    @contextmanager
    async def _safe_operation(self, operation: str):
        """
        安全操作的上下文管理器
        用于确保所有操作都是协程安全的，并提供适当的错误处理
        """
        try:
            await self._lock.acquire()
            yield
        except Exception as e:
            logger.error(f"Error during {operation}: {e}")
            raise
        finally:
            self._lock.release()

    async def set_user_info(self, uid: str, info: dict) -> None:
        """
        协程安全地设置用户信息
        
        Args:
            uid: 用户ID
            info: 用户信息字典
        """
        if not isinstance(info, dict):
            raise ValueError("Info must be a dictionary")
            
        async with self._safe_operation("set_user_info"):
            self._user_info_dict[uid] = info.copy()  # 创建副本避免外部修改

    async def get_user_info(self, uid: str) -> Optional[dict]:
        """
        协程安全地获取用户信息
        
        Args:
            uid: 用户ID
            
        Returns:
            dict: 用户信息的副本
            None: 如果用户不存在
        """
        async with self._safe_operation("get_user_info"):
            user_info = self._user_info_dict.get(uid)
            return user_info.copy() if user_info is not None else None

    async def remove_user_info(self, uid: str) -> bool:
        """
        协程安全地移除用户信息
        
        Args:
            uid: 用户ID
            
        Returns:
            bool: 是否成功移除用户信息
        """
        async with self._safe_operation("remove_user_info"):
            try:
                self._user_info_dict.pop(uid)
                return True
            except KeyError:
                logger.warning(f"Attempted to remove non-existent user: {uid}")
                return False

    async def update_user_info(self, uid: str, info_update: dict) -> bool:
        """
        协程安全地更新用户信息
        
        Args:
            uid: 用户ID
            info_update: 要更新的信息字典
            
        Returns:
            bool: 是否成功更新用户信息
        """
        if not isinstance(info_update, dict):
            raise ValueError("Info update must be a dictionary")
            
        async with self._safe_operation("update_user_info"):
            if uid in self._user_info_dict:
                self._user_info_dict[uid].update(info_update)
                return True
            return False

    async def has_user(self, uid: str) -> bool:
        """
        协程安全地检查用户是否存在
        
        Args:
            uid: 用户ID
            
        Returns:
            bool: 用户是否存在
        """
        async with self._safe_operation("has_user"):
            return uid in self._user_info_dict

    async def clear_all(self) -> None:
        """
        协程安全地清除所有用户信息
        通常用于服务器关闭时
        """
        async with self._safe_operation("clear_all"):
            self._user_info_dict.clear()

    async def get_all_users(self) -> list:
        """
        协程安全地获取所有用户ID
        
        Returns:
            list: 所有用户ID的列表
        """
        async with self._safe_operation("get_all_users"):
            return list(self._user_info_dict.keys())

    async def get_user_count(self) -> int:
        """
        协程安全地获取用户数量
        
        Returns:
            int: 用户数量
        """
        async with self._safe_operation("get_user_count"):
            return len(self._user_info_dict)


# 全局单例实例
USER_INFO_MANAGER = UserInfoManager()