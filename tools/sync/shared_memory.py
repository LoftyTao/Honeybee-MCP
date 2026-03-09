import json
import struct
from multiprocessing import shared_memory
from typing import Optional, Tuple


SHM_NAME_PREFIX = "hb_model_"
SHM_DEFAULT_NAME = "hb_model_shared"
HEADER_SIZE = 8
MAX_MODEL_SIZE = 100 * 1024 * 1024


class SharedMemoryManager:
    """Shared memory manager for Honeybee model data exchange."""

    def __init__(self, name: str = SHM_DEFAULT_NAME):
        self.name = name
        self._shm: Optional[shared_memory.SharedMemory] = None
        self._is_creator = False

    def _get_shm_name(self) -> str:
        return f"{SHM_NAME_PREFIX}{self.name}" if not self.name.startswith(SHM_NAME_PREFIX) else self.name

    def write_model(self, model_dict: dict, create: bool = True) -> bool:
        try:
            json_bytes = json.dumps(model_dict, ensure_ascii=False).encode("utf-8")
            data_size = len(json_bytes)
            if data_size > MAX_MODEL_SIZE:
                raise ValueError(f"Model data too large: {data_size} bytes (max: {MAX_MODEL_SIZE})")
            total_size = HEADER_SIZE + data_size
            shm_name = self._get_shm_name()

            if self._shm is not None:
                self.close()

            if create:
                try:
                    self._shm = shared_memory.SharedMemory(name=shm_name, create=True, size=total_size)
                    self._is_creator = True
                except FileExistsError:
                    self._shm = shared_memory.SharedMemory(name=shm_name)
                    self._is_creator = False
                    if self._shm.size < total_size:
                        self.close()
                        raise ValueError(f"Existing shared memory too small: {self._shm.size} < {total_size}")
            else:
                self._shm = shared_memory.SharedMemory(name=shm_name)
                self._is_creator = False

            self._shm.buf[:HEADER_SIZE] = struct.pack("<Q", data_size)
            self._shm.buf[HEADER_SIZE:total_size] = json_bytes
            return True
        except Exception as e:
            print(f"Error writing to shared memory: {e}")
            return False

    def read_model(self) -> Optional[dict]:
        try:
            shm_name = self._get_shm_name()
            if self._shm is None:
                self._shm = shared_memory.SharedMemory(name=shm_name)
                self._is_creator = False
            header = bytes(self._shm.buf[:HEADER_SIZE])
            data_size = struct.unpack("<Q", header)[0]
            if data_size == 0 or data_size > MAX_MODEL_SIZE:
                return None
            json_bytes = bytes(self._shm.buf[HEADER_SIZE:HEADER_SIZE + data_size])
            return json.loads(json_bytes.decode("utf-8"))
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error reading from shared memory: {e}")
            return None

    def get_model_size(self) -> Optional[int]:
        try:
            shm_name = self._get_shm_name()
            if self._shm is None:
                self._shm = shared_memory.SharedMemory(name=shm_name)
                self._is_creator = False
            header = bytes(self._shm.buf[:HEADER_SIZE])
            return struct.unpack("<Q", header)[0]
        except Exception:
            return None

    def clear(self):
        if self._shm is not None:
            self._shm.buf[:HEADER_SIZE] = struct.pack("<Q", 0)

    def close(self):
        if self._shm is not None:
            self._shm.close()
            if self._is_creator:
                try:
                    self._shm.unlink()
                except FileNotFoundError:
                    pass
            self._shm = None
            self._is_creator = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


def write_model_to_shared_memory(model_dict: dict, name: str = SHM_DEFAULT_NAME) -> Tuple[bool, str]:
    with SharedMemoryManager(name) as shm:
        success = shm.write_model(model_dict)
        if success:
            size = shm.get_model_size()
            return True, f"Model written to shared memory '{name}', size: {size} bytes"
        return False, "Failed to write model to shared memory"


def read_model_from_shared_memory(name: str = SHM_DEFAULT_NAME) -> Tuple[Optional[dict], str]:
    with SharedMemoryManager(name) as shm:
        model_dict = shm.read_model()
        if model_dict is not None:
            return model_dict, f"Model read from shared memory '{name}'"
        return None, f"No model found in shared memory '{name}'"


def clear_shared_memory(name: str = SHM_DEFAULT_NAME) -> bool:
    try:
        shm = shared_memory.SharedMemory(
            name=f"{SHM_NAME_PREFIX}{name}" if not name.startswith(SHM_NAME_PREFIX) else name
        )
        shm.close()
        shm.unlink()
        return True
    except FileNotFoundError:
        return True
    except Exception:
        return False
