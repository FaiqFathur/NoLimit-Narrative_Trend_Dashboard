import time
from functools import wraps
from typing import Callable, Any
import hashlib
import json

# Dictionary untuk menyimpan cache di RAM server
_CACHE_STORE = {}

def in_memory_cache(ttl_seconds: int = 60):
    """
    Decorator untuk meng-cache hasil response API di dalam memory RAM (Dictionary).
    Sangat berguna untuk endpoint agregasi (seperti Dashboard) yang memakan waktu query lama.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Membuat kunci (key) unik berdasarkan argumen yang dikirim
            # Hapus argumen non-hashable (seperti Session database) dari key
            cache_kwargs = {k: v for k, v in kwargs.items() if k not in ["db", "request", "response"]}
            
            # Ubah dictionary argument menjadi string untuk hashing
            # Sort keys agar urutan param tidak mempengaruhi hasil hash
            serialized_kwargs = json.dumps(cache_kwargs, sort_keys=True, default=str)
            
            # Format Key: nama_fungsi:hash_dari_parameter
            key_hash = hashlib.md5(serialized_kwargs.encode()).hexdigest()
            cache_key = f"{func.__name__}:{key_hash}"
            
            now = time.time()
            
            # Cek apakah data ada di cache dan belum expired
            if cache_key in _CACHE_STORE:
                cached_data, timestamp = _CACHE_STORE[cache_key]
                if now - timestamp < ttl_seconds:
                    return cached_data
                else:
                    # Hapus data yang sudah basi
                    del _CACHE_STORE[cache_key]
                    
            # Jika tidak ada di cache (atau sudah expired), eksekusi fungsi asli (query ke DB)
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Simpan hasilnya ke cache
            _CACHE_STORE[cache_key] = (result, now)
            
            return result
        return wrapper
    return decorator

import asyncio # Dibutuhkan untuk nge-cek iscoroutinefunction
