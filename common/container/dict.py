import threading
from collections import UserDict
from typing import Any, Optional, Iterator, Dict,  AsyncGenerator
import asyncio

class ThreadSafeDict(UserDict):
    """
    线程安全字典，完整实现标准字典接口
    保持与dict完全一致的方法签名
    """
    def __init__(self, *args, **kwargs):
        self._lock = threading.RLock()
        super().__init__(*args, **kwargs)

    def __setitem__(self, key: Any, value: Any) -> None:
        with self._lock:
            super().__setitem__(key, value)

    def __getitem__(self, key: Any) -> Any:
        with self._lock:
            return super().__getitem__(key)

    def __delitem__(self, key: Any) -> None:
        with self._lock:
            super().__delitem__(key)

    def __contains__(self, key: Any) -> bool:
        with self._lock:
            return super().__contains__(key)

    def __len__(self) -> int:
        with self._lock:
            return super().__len__()

    def __iter__(self) -> Iterator:
        with self._lock:
            return iter(self.data.copy())

    def __repr__(self) -> str:
        with self._lock:
            return f"ThreadSafeDict({self.data})"

    def get(self, key: Any, default: Optional[Any] = None) -> Any:
        with self._lock:
            return super().get(key, default)

    def pop(self, key: Any, default: Optional[Any] = None) -> Any:
        with self._lock:
            return self.data.pop(key, default)

    def popitem(self) -> tuple:
        with self._lock:
            return self.data.popitem()

    def setdefault(self, key: Any, default: Optional[Any] = None) -> Any:
        with self._lock:
            return self.data.setdefault(key, default)

    def update(self, other=(), /, **kwargs) -> None:
        with self._lock:
            self.data.update(other, **kwargs)

    def clear(self) -> None:
        with self._lock:
            self.data.clear()

    def keys(self):
        with self._lock:
            return list(self.data.keys())

    def values(self):
        with self._lock:
            return list(self.data.values())

    def items(self):
        with self._lock:
            return list(self.data.items())

    def copy(self) -> 'ThreadSafeDict':
        with self._lock:
            return ThreadSafeDict(self.data.copy())

    @classmethod
    def fromkeys(cls, iterable, value=None) -> 'ThreadSafeDict':
        return cls(dict.fromkeys(iterable, value))
    







class AsyncSafeDict:
    """
    协程安全字典，优化异步编程场景
    使用asyncio同步原语实现原子操作
    """
    def __init__(self, initial_data: Optional[Dict] = None):
        self._data = initial_data.copy() if initial_data else {}
        self._lock = asyncio.Lock()
        self._version = 0  # 用于检测并发修改

    async def get(self, key: Any, default: Optional[Any] = None) -> Any:
        async with self._lock:
            return self._data.get(key, default)

    async def set(self, key: Any, value: Any) -> None:
        async with self._lock:
            self._data[key] = value
            self._version += 1

    async def delete(self, key: Any) -> bool:
        async with self._lock:
            if key in self._data:
                del self._data[key]
                self._version += 1
                return True
            return False

    async def contains(self, key: Any) -> bool:
        async with self._lock:
            return key in self._data

    async def keys(self) -> list:
        async with self._lock:
            return list(self._data.keys())

    async def values(self) -> list:
        async with self._lock:
            return list(self._data.values())

    async def items(self) -> list:
        async with self._lock:
            return list(self._data.items())

    async def update(self, new_items: Dict) -> None:
        async with self._lock:
            self._data.update(new_items)
            self._version += 1

    def snapshot(self) -> Dict:
        """获取非安全状态的快速只读视图"""
        return self._data.copy()

    async def watch_changes(self) -> AsyncGenerator[Dict, None]:
        """
        变更监听通道
        使用示例：
        async for versioned_data in dict.watch_changes():
            handle_update(versioned_data)
        """
        last_version = self._version
        while True:
            async with self._lock:
                if self._version != last_version:
                    yield self._data.copy()
                    last_version = self._version
            await asyncio.sleep(0.01)  # 防止busy loop

    async def transaction(self, operations: callable) -> Any:
        """
        原子事务执行上下文
        使用示例：
        result = await dict.transaction(lambda d: d.update({'x':1}))
        """
        async with self._lock:
            return operations(self._data.copy())