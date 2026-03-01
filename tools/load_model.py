import sys
import os
import tempfile

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .mcp_context import mcp
from honeybee.model import Model


class Model_Manager:

    def __init__(self):
        self.model = None

    def load(self, hb_file: str, cleanup_irrational: bool = False):
        self.model = Model.from_file(hb_file, cleanup_irrational=cleanup_irrational)

    def load_from_dict(self, data: dict, cleanup_irrational: bool = False):
        self.model = Model.from_dict(data, cleanup_irrational=cleanup_irrational)


def _check_grasshopper_models():
    """Check for models from Grasshopper in shared memory."""
    import json
    import struct
    
    MAP_NAME_PREFIX = "hb_model_"
    HEADER_SIZE = 8
    temp_dir = tempfile.gettempdir()
    
    found_models = []
    
    try:
        for filename in os.listdir(temp_dir):
            if filename.startswith(MAP_NAME_PREFIX) and filename.endswith(".mmap"):
                name = filename[len(MAP_NAME_PREFIX):-5]
                map_path = os.path.join(temp_dir, filename)
                
                try:
                    last_write_time = os.path.getmtime(map_path)
                    
                    with open(map_path, 'rb') as f:
                        header = f.read(HEADER_SIZE)
                        data_size = struct.unpack('<Q', header)[0]
                        
                        if data_size > 0:
                            json_bytes = f.read(data_size)
                            json_data = json_bytes.decode('utf-8')
                            model_dict = json.loads(json_data)
                            
                            if not model_dict.get("cleared"):
                                display_name = model_dict.get("display_name", name)
                                rooms_count = len(model_dict.get("rooms", []))
                                
                                found_models.append({
                                    "name": name,
                                    "display_name": display_name,
                                    "rooms_count": rooms_count,
                                    "last_write_time": last_write_time,
                                    "size_kb": round(data_size / 1024, 1)
                                })
                except:
                    pass
    except:
        pass
    
    found_models.sort(key=lambda m: m["last_write_time"], reverse=True)
    
    return found_models


manager = Model_Manager()


@mcp.tool()
def load_model(hb_file: str = None, cleanup_irrational: bool = False) -> dict:
    """
    Load a Honeybee model from HBJSON/HBpkl file or Grasshopper shared memory.
    
    Priority:
    1. If Grasshopper has written a model to shared memory, load from there first
    2. Otherwise, load from the specified hb_file
    
    Args:
        hb_file: Path to HBJSON or HBpkl file, or "latest" to auto-load latest Grasshopper model
        cleanup_irrational: Boolean to clean irrational geometry (Default: False)
    
    Returns:
        Dictionary with model statistics and available models
    """
    from .shared_memory_tools import cleanup_old_cache_files
    
    cleanup_result = cleanup_old_cache_files()
    
    gh_models = _check_grasshopper_models()
    
    if hb_file == "latest" and gh_models:
        from .shared_memory_tools import load_model_from_shared_memory
        
        latest_model = max(gh_models, key=lambda m: m["last_write_time"])
        result = load_model_from_shared_memory(latest_model["name"], cleanup_irrational)
        
        if result.get("success"):
            result["source"] = "grasshopper"
            result["available_grasshopper_models"] = gh_models
            if cleanup_result.get("success"):
                result["cache_cleanup"] = cleanup_result
            return result
    
    if gh_models:
        from .shared_memory_tools import load_model_from_shared_memory
        
        gh_model = gh_models[0]
        result = load_model_from_shared_memory(gh_model["name"], cleanup_irrational)
        
        if result.get("success"):
            result["source"] = "grasshopper"
            result["available_grasshopper_models"] = gh_models
            if cleanup_result.get("success"):
                result["cache_cleanup"] = cleanup_result
            return result
    
    if hb_file is None:
        if gh_models:
            return {
                "success": False,
                "error": "No hb_file provided and no Grasshopper model selected",
                "available_grasshopper_models": gh_models,
                "hint": "Either provide a file path, 'latest' to auto-load newest, or select from available models"
            }
        return {
            "success": False,
            "error": "No hb_file provided and no Grasshopper model found",
            "hint": "Either provide a file path or write a model from Grasshopper"
        }
    
    manager.load(hb_file, cleanup_irrational=cleanup_irrational)
    
    from .version_control import save_version_auto
    model_name = manager.model.display_name or manager.model.identifier
    save_version_auto(manager.model.to_dict(), model_name, "Loaded from file")

    return {
        "success": True,
        "source": "file",
        "display_name": manager.model.display_name,
        "floor_area": sum(room.floor_area for room in manager.model.rooms),
        "rooms_count": len(manager.model.rooms),
        "outdoor_shades_count": len(manager.model.outdoor_shades),
        "orphaned_faces_count": len(manager.model.orphaned_faces),
        "orphaned_shades_count": len(manager.model.orphaned_shades) + len(manager.model.shade_meshes),
        "orphaned_apertures_count": len(manager.model.orphaned_apertures),
        "orphaned_doors_count": len(manager.model.orphaned_doors)
    }


@mcp.tool()
def load_model_from_dict(data: dict, cleanup_irrational: bool = False) -> dict:
    """
    Load a Honeybee model from a dictionary representation.

    Args:
        data: A dictionary representation of a Model object.
        cleanup_irrational: Boolean to note whether common types of irrational 
            objects should be cleaned or removed from the dictionary before 
            serializing the model to Python. Typical cases that are removed 
            include Face3Ds with fewer than 3 vertices, Rooms that have no 
            Face geometry, etc. (Default: False)
    """
    try:
        manager.load_from_dict(data, cleanup_irrational=cleanup_irrational)
        
        from .version_control import save_version_auto
        model_name = manager.model.display_name or manager.model.identifier
        save_version_auto(manager.model.to_dict(), model_name, "Loaded from dict")

        return {
            "success": True,
            "display_name": manager.model.display_name,
            "floor_area": sum(room.floor_area for room in manager.model.rooms),
            "rooms_count": len(manager.model.rooms),
            "outdoor_shades_count": len(manager.model.outdoor_shades),
            "orphaned_faces_count": len(manager.model.orphaned_faces),
            "orphaned_shades_count": len(manager.model.orphaned_shades) + len(manager.model.shade_meshes),
            "orphaned_apertures_count": len(manager.model.orphaned_apertures),
            "orphaned_doors_count": len(manager.model.orphaned_doors)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
