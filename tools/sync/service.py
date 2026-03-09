import json
import mmap
import os
import struct
import tempfile


MAP_NAME_PREFIX = "hb_model_"
HEADER_SIZE = 8
DEFAULT_NAME = "hb_model_shared"
MAX_CACHE_FILES = 5
CACHE_AGE_HOURS = 24


def _extract_model_identity(model_dict: dict, fallback_name: str):
    identifier = model_dict.get("identifier") or fallback_name
    display_name = model_dict.get("display_name") or identifier
    return identifier, display_name


def get_map_path(name: str) -> str:
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, MAP_NAME_PREFIX + name + ".mmap")


def read_model_from_mmap(name: str = DEFAULT_NAME):
    try:
        map_path = get_map_path(name)
        if not os.path.exists(map_path):
            return None, "Shared memory '{}' not found. Run Grasshopper Writer first.".format(name), None

        with open(map_path, "rb") as f:
            header = f.read(HEADER_SIZE)
            data_size = struct.unpack("<Q", header)[0]
            if data_size == 0:
                return None, "No data in shared memory", None
            json_bytes = f.read(data_size)
            model_dict = json.loads(json_bytes.decode("utf-8"))

        if model_dict.get("cleared") is True:
            return None, "Clear signal received from Grasshopper", "clear"

        writer_signal = model_dict.pop("_writer_signal", None)
        if writer_signal and writer_signal.get("written") is True:
            return model_dict, "Model read from shared memory '{}' (writer signal)".format(name), "write"

        return model_dict, "Model read from shared memory '{}'".format(name), None
    except Exception as e:
        return None, "Error: {}".format(str(e)), None


def write_model_to_mmap(model_dict: dict, name: str = DEFAULT_NAME):
    try:
        json_bytes = json.dumps(model_dict, ensure_ascii=False).encode("utf-8")
        data_size = len(json_bytes)
        total_size = HEADER_SIZE + data_size
        map_path = get_map_path(name)

        with open(map_path, "wb") as f:
            f.write(b"\x00" * total_size)

        with open(map_path, "r+b") as f:
            mm = mmap.mmap(f.fileno(), total_size)
            mm[:HEADER_SIZE] = struct.pack("<Q", data_size)
            mm[HEADER_SIZE:total_size] = json_bytes
            mm.flush()
            mm.close()

        return True, "Model written to shared memory '{}', size: {} bytes".format(name, data_size)
    except Exception as e:
        return False, "Error: {}".format(str(e))


def clear_mmap_file(name: str = DEFAULT_NAME) -> bool:
    try:
        map_path = get_map_path(name)
        if os.path.exists(map_path):
            os.remove(map_path)
        return True
    except Exception:
        return False


def check_grasshopper_models():
    found_models = []
    temp_dir = tempfile.gettempdir()
    try:
        for filename in os.listdir(temp_dir):
            if filename.startswith(MAP_NAME_PREFIX) and filename.endswith(".mmap"):
                name = filename[len(MAP_NAME_PREFIX):-5]
                map_path = os.path.join(temp_dir, filename)
                try:
                    last_write_time = os.path.getmtime(map_path)
                    with open(map_path, "rb") as f:
                        header = f.read(HEADER_SIZE)
                        data_size = struct.unpack("<Q", header)[0]
                        if data_size <= 0:
                            continue
                        model_dict = json.loads(f.read(data_size).decode("utf-8"))
                        if model_dict.get("cleared"):
                            continue
                        identifier, display_name = _extract_model_identity(model_dict, name)
                        found_models.append(
                            {
                                "name": name,
                                "shared_name": name,
                                "identifier": identifier,
                                "display_name": display_name,
                                "rooms_count": len(model_dict.get("rooms", [])),
                                "last_write_time": last_write_time,
                                "size_kb": round(data_size / 1024, 1),
                            }
                        )
                except Exception:
                    pass
    except Exception:
        pass

    found_models.sort(key=lambda m: m["last_write_time"], reverse=True)
    return found_models


def cleanup_old_cache_files():
    import time

    temp_dir = tempfile.gettempdir()
    current_time = time.time()
    age_threshold = CACHE_AGE_HOURS * 3600
    files_info = []

    try:
        for filename in os.listdir(temp_dir):
            if filename.startswith(MAP_NAME_PREFIX) and filename.endswith(".mmap"):
                map_path = os.path.join(temp_dir, filename)
                try:
                    file_time = os.path.getmtime(map_path)
                    file_age = current_time - file_time
                    if file_age > age_threshold:
                        os.remove(map_path)
                        continue
                    files_info.append(
                        {
                            "name": filename,
                            "path": map_path,
                            "age_hours": file_age / 3600,
                            "size_kb": round(os.path.getsize(map_path) / 1024, 2),
                        }
                    )
                except Exception:
                    pass

        files_info.sort(key=lambda x: x["age_hours"])
        files_to_remove = files_info[MAX_CACHE_FILES:]
        for file_info in files_to_remove:
            try:
                os.remove(file_info["path"])
            except Exception:
                pass

        return {
            "success": True,
            "kept_files": min(len(files_info), MAX_CACHE_FILES),
            "removed_files": len(files_to_remove),
            "removed_details": [
                {
                    "name": f["name"],
                    "age_hours": round(f["age_hours"], 2),
                    "size_kb": f["size_kb"],
                }
                for f in files_to_remove
            ],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
