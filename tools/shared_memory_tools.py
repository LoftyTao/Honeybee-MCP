"""
MCP tools for loading and saving Honeybee models via memory-mapped files.

This enables real-time interaction between Grasshopper and AI IDE.
Compatible with both IronPython (Rhino 7) and Python 3 (Rhino 8).
"""

import sys
import os
import json
import struct
import mmap
import tempfile

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .mcp_context import mcp
from tools.load_model import manager


MAP_NAME_PREFIX = "hb_model_"
HEADER_SIZE = 8
DEFAULT_NAME = "hb_model_shared"
MAX_CACHE_FILES = 5
CACHE_AGE_HOURS = 24


def get_map_path(name: str) -> str:
    """Get the file path for memory-mapped file."""
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, MAP_NAME_PREFIX + name + ".mmap")


def read_model_from_mmap(name: str = DEFAULT_NAME):
    """
    Read model dictionary from memory-mapped file.
    
    Returns:
        Tuple of (model_dict or None, message, signal_type)
        signal_type: "clear", "write", or None
    """
    try:
        map_path = get_map_path(name)
        
        if not os.path.exists(map_path):
            return None, "Shared memory '{}' not found. Run Grasshopper Writer first.".format(name), None
        
        with open(map_path, 'rb') as f:
            header = f.read(HEADER_SIZE)
            data_size = struct.unpack('<Q', header)[0]
            
            if data_size == 0:
                return None, "No data in shared memory", None
            
            json_bytes = f.read(data_size)
            json_data = json_bytes.decode('utf-8')
            model_dict = json.loads(json_data)
            
        if model_dict.get("cleared") == True:
            return None, "Clear signal received from Grasshopper", "clear"
        
        writer_signal = model_dict.pop("_writer_signal", None)
        if writer_signal and writer_signal.get("written") == True:
            return model_dict, "Model read from shared memory '{}' (writer signal)".format(name), "write"
        
        return model_dict, "Model read from shared memory '{}'".format(name), None
        
    except Exception as e:
        return None, "Error: {}".format(str(e)), None


def write_model_to_mmap(model_dict: dict, name: str = DEFAULT_NAME):
    """
    Write model dictionary to memory-mapped file.
    
    Returns:
        Tuple of (success, message)
    """
    try:
        json_data = json.dumps(model_dict, ensure_ascii=False)
        json_bytes = json_data.encode('utf-8')
        data_size = len(json_bytes)
        total_size = HEADER_SIZE + data_size
        
        map_path = get_map_path(name)
        
        with open(map_path, 'wb') as f:
            f.write(b'\x00' * total_size)
        
        with open(map_path, 'r+b') as f:
            mm = mmap.mmap(f.fileno(), total_size)
            
            header = struct.pack('<Q', data_size)
            mm[:HEADER_SIZE] = header
            mm[HEADER_SIZE:total_size] = json_bytes
            
            mm.flush()
            mm.close()
        
        return True, "Model written to shared memory '{}', size: {} bytes".format(name, data_size)
        
    except Exception as e:
        return False, "Error: {}".format(str(e))


def clear_mmap_file(name: str = DEFAULT_NAME) -> bool:
    """
    Delete the memory-mapped file.
    """
    try:
        map_path = get_map_path(name)
        if os.path.exists(map_path):
            os.remove(map_path)
        return True
    except:
        return False


@mcp.tool()
def load_model_from_shared_memory(name: str = None, cleanup_irrational: bool = False) -> dict:
    """
    Load a Honeybee model from shared memory.
    
    Reads a model written by Grasshopper's HB_Model_SharedMemory_Writer component.
    If no name is specified, automatically detects and loads the most recent model.
    """
    from .load_model import _check_grasshopper_models
    
    if name is None:
        gh_models = _check_grasshopper_models()
        if gh_models:
            name = gh_models[0]["name"]
        else:
            name = DEFAULT_NAME
    
    try:
        model_dict, message, signal_type = read_model_from_mmap(name)
        
        if signal_type == "clear":
            manager.model = None
            return {
                "success": True,
                "cleared": True,
                "message": "Model cleared from MCP memory (clear signal from Grasshopper)"
            }
        
        if model_dict is None:
            return {
                "success": False,
                "error": message,
                "hint": "Make sure the Grasshopper Writer component has written the model first"
            }
        
        manager.load_from_dict(model_dict, cleanup_irrational=cleanup_irrational)
        manager.source = "shared_memory"
        manager.source_name = name
        
        from .version_control import save_version_auto
        model_name = manager.model.identifier
        save_version_auto(manager.model.to_dict(), model_name, "Loaded from shared memory")
        
        result = {
            "success": True,
            "message": message,
            "display_name": manager.model.display_name,
            "floor_area": sum(room.floor_area for room in manager.model.rooms),
            "rooms_count": len(manager.model.rooms),
            "outdoor_shades_count": len(manager.model.outdoor_shades),
            "orphaned_faces_count": len(manager.model.orphaned_faces),
            "orphaned_shades_count": len(manager.model.orphaned_shades) + len(manager.model.shade_meshes),
            "orphaned_apertures_count": len(manager.model.orphaned_apertures),
            "orphaned_doors_count": len(manager.model.orphaned_doors)
        }
        
        if signal_type == "write":
            result["writer_signal"] = True
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def save_model_to_shared_memory(name: str = None) -> dict:
    """
    Save the current model to shared memory.
    
    Writes the current model so Grasshopper's HB_Model_SharedMemory_Reader can read it.
    If no name is specified, automatically uses the model's identifier.
    """
    try:
        if manager.model is None:
            return {
                "success": False,
                "error": "No model loaded. Load a model first."
            }
        
        if name is None:
            name = manager.model.identifier
        
        model_dict = manager.model.to_dict()
        
        from .version_control import save_version_auto
        model_name = manager.model.identifier
        save_version_auto(model_dict, model_name, "Saved to shared memory")
        
        success, message = write_model_to_mmap(model_dict, name)
        
        if success:
            return {
                "success": True,
                "message": message,
                "name": name,
                "display_name": manager.model.display_name,
                "rooms_count": len(manager.model.rooms),
                "hint": "Connect 'name' output to HB-MCP Reader's _name input"
            }
        else:
            return {
                "success": False,
                "error": message
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def clear_shared_memory_model(name: str = DEFAULT_NAME) -> dict:
    """
    Clear and remove the shared memory segment.
    
    Deletes the memory-mapped file from the temp directory.
    """
    try:
        success = clear_mmap_file(name)
        return {
            "success": success,
            "message": "Shared memory '{}' cleared".format(name) if success else "Failed to clear shared memory '{}'".format(name)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def check_shared_memory_status(name: str = DEFAULT_NAME) -> dict:
    """
    Check if there is a model in shared memory.
    
    Inspects the shared memory segment and returns information about its contents.
    """
    try:
        map_path = get_map_path(name)
        
        if not os.path.exists(map_path):
            return {
                "exists": False,
                "message": "Shared memory '{}' does not exist".format(name)
            }
        
        with open(map_path, 'rb') as f:
            header = f.read(HEADER_SIZE)
            data_size = struct.unpack('<Q', header)[0]
            
            if data_size == 0:
                return {
                    "exists": False,
                    "message": "No model found in shared memory '{}'".format(name)
                }
            
            json_bytes = f.read(data_size)
            json_data = json_bytes.decode('utf-8')
            model_dict = json.loads(json_data)
            
            if model_dict.get("cleared") == True:
                return {
                    "exists": True,
                    "signal_type": "clear",
                    "model_name": model_dict.get("model_name", "unknown"),
                    "message": "Clear signal from Grasshopper - model should be cleared"
                }
            
            writer_signal = model_dict.get("_writer_signal", {})
            if writer_signal.get("written") == True:
                return {
                    "exists": True,
                    "signal_type": "write",
                    "writer_timestamp": writer_signal.get("timestamp", ""),
                    "size_bytes": data_size,
                    "size_kb": round(data_size / 1024, 2),
                    "name": name,
                    "message": "Model written by Grasshopper (writer signal detected)"
                }
            
            return {
                "exists": True,
                "signal_type": None,
                "size_bytes": data_size,
                "size_kb": round(data_size / 1024, 2),
                "size_mb": round(data_size / (1024 * 1024), 2),
                "name": name,
                "path": map_path
            }
            
    except Exception as e:
        return {
            "exists": False,
            "error": str(e)
        }


@mcp.tool()
def cleanup_shared_memory_cache() -> dict:
    """
    Clean up old shared memory cache files.
    
    Removes old memory-mapped files from the temp directory, keeping only the most recent files.
    """
    return cleanup_old_cache_files()


def cleanup_old_cache_files():
    """
    Clean up old shared memory cache files.
    
    Keeps only the most recent MAX_CACHE_FILES files.
    Removes files older than CACHE_AGE_HOURS.
    """
    import time
    
    temp_dir = tempfile.gettempdir()
    current_time = time.time()
    age_threshold = CACHE_AGE_HOURS * 3600
    
    try:
        files_info = []
        
        for filename in os.listdir(temp_dir):
            if filename.startswith(MAP_NAME_PREFIX) and filename.endswith(".mmap"):
                map_path = os.path.join(temp_dir, filename)
                
                try:
                    file_time = os.path.getmtime(map_path)
                    file_age = current_time - file_time
                    file_size = os.path.getsize(map_path)
                    
                    files_info.append({
                        "name": filename,
                        "path": map_path,
                        "age_hours": file_age / 3600,
                        "size_kb": round(file_size / 1024, 2)
                    })
                except:
                    pass
        
        files_info.sort(key=lambda x: x["age_hours"])
        
        if len(files_info) > MAX_CACHE_FILES:
            files_to_keep = files_info[:MAX_CACHE_FILES]
            files_to_remove = files_info[MAX_CACHE_FILES:]
            
            for file_info in files_to_remove:
                try:
                    os.remove(file_info["path"])
                except:
                    pass
            
            return {
                "success": True,
                "kept_files": len(files_to_keep),
                "removed_files": len(files_to_remove),
                "removed_details": [
                    {
                        "name": f["name"],
                        "age_hours": round(f["age_hours"], 2),
                        "size_kb": f["size_kb"]
                    }
                    for f in files_to_remove
                ]
            }
        
        return {
            "success": True,
            "kept_files": len(files_info),
            "removed_files": 0,
            "message": "Cache cleanup completed"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
