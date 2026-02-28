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


def get_map_path(name: str) -> str:
    """Get the file path for memory-mapped file."""
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, MAP_NAME_PREFIX + name + ".mmap")


def read_model_from_mmap(name: str = DEFAULT_NAME):
    """
    Read model dictionary from memory-mapped file.
    
    Returns:
        Tuple of (model_dict or None, message)
    """
    try:
        map_path = get_map_path(name)
        
        if not os.path.exists(map_path):
            return None, "Shared memory '{}' not found. Run Grasshopper Writer first.".format(name)
        
        with open(map_path, 'rb') as f:
            header = f.read(HEADER_SIZE)
            data_size = struct.unpack('<Q', header)[0]
            
            if data_size == 0:
                return None, "No data in shared memory"
            
            json_bytes = f.read(data_size)
            json_data = json_bytes.decode('utf-8')
            model_dict = json.loads(json_data)
            
        return model_dict, "Model read from shared memory '{}'".format(name)
        
    except Exception as e:
        return None, "Error: {}".format(str(e))


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
def load_model_from_shared_memory(name: str = DEFAULT_NAME, cleanup_irrational: bool = False) -> dict:
    """
    Load a Honeybee model from shared memory.
    
    This tool reads a model that was written to shared memory by Grasshopper.
    Use this after the HB_Model_SharedMemory_Writer component in Grasshopper
    has written a model to shared memory.
    
    Args:
        name: Shared memory name (must match the name used in Grasshopper)
        cleanup_irrational: Boolean to clean irrational geometry (Default: False)
    
    Returns:
        Dictionary with model statistics and status
    """
    try:
        model_dict, message = read_model_from_mmap(name)
        
        if model_dict is None:
            return {
                "success": False,
                "error": message,
                "hint": "Make sure the Grasshopper Writer component has written the model first"
            }
        
        manager.load_from_dict(model_dict, cleanup_irrational=cleanup_irrational)
        
        return {
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
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def save_model_to_shared_memory(name: str = DEFAULT_NAME) -> dict:
    """
    Save the current model to shared memory.
    
    This tool writes the current model to shared memory so that
    Grasshopper can read it using the HB_Model_SharedMemory_Reader component.
    
    Args:
        name: Shared memory name (must match the name used in Grasshopper)
    
    Returns:
        Dictionary with status and model statistics
    """
    try:
        if manager.model is None:
            return {
                "success": False,
                "error": "No model loaded. Load a model first."
            }
        
        model_dict = manager.model.to_dict()
        success, message = write_model_to_mmap(model_dict, name)
        
        if success:
            return {
                "success": True,
                "message": message,
                "display_name": manager.model.display_name,
                "rooms_count": len(manager.model.rooms),
                "hint": "Use HB_Model_SharedMemory_Reader in Grasshopper to read this model"
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
    
    Use this to free up shared memory after you're done with model exchange.
    
    Args:
        name: Shared memory name to clear
    
    Returns:
        Dictionary with status
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
    
    Args:
        name: Shared memory name to check
    
    Returns:
        Dictionary with status information
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
            
            return {
                "exists": True,
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
