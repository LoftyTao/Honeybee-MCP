"""
Honeybee Model Version Management Tools

Automatic version control - tracks model changes automatically.
Maximum 10 versions are kept in memory.
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, List
from collections import deque

MAX_VERSIONS = 10

_version_history: Dict[str, deque] = {}
_version_counter: Dict[str, int] = {}
_redo_stack: Dict[str, List] = {}


def get_all_model_names() -> List[str]:
    """Get all model names with versions."""
    return list(_version_history.keys())


def save_version_auto(model_dict: dict, model_name: str, description: str = "") -> dict:
    """
    Automatically save a version when model is updated.
    
    Args:
        model_dict: Model dictionary to save.
        model_name: Name of the model.
        description: Optional description of the change.
    
    Returns:
        Dictionary with version info.
    """
    if model_name not in _version_history:
        _version_history[model_name] = deque(maxlen=MAX_VERSIONS)
        _version_counter[model_name] = 0
        _redo_stack[model_name] = []
    
    _version_counter[model_name] += 1
    version_id = str(_version_counter[model_name]).zfill(3)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    version_data = {
        "version_id": version_id,
        "timestamp": timestamp,
        "description": description,
        "model_dict": model_dict,
        "rooms_count": len(model_dict.get("rooms", [])),
        "outdoor_shades_count": len(model_dict.get("outdoor_shades", [])),
        "apertures_count": _count_apertures(model_dict),
        "doors_count": _count_doors(model_dict),
        "shade_meshes_count": len(model_dict.get("shade_meshes", []))
    }
    
    _version_history[model_name].append(version_data)
    _redo_stack[model_name] = []
    
    return {
        "success": True,
        "version_id": version_id,
        "model_name": model_name,
        "timestamp": timestamp,
        "total_versions": len(_version_history[model_name])
    }


def _count_apertures(model_dict: dict) -> int:
    """Count total apertures in model."""
    count = len(model_dict.get("orphaned_apertures", []))
    for room in model_dict.get("rooms", []):
        for face in room.get("faces", []):
            count += len(face.get("apertures", []))
    return count


def _count_doors(model_dict: dict) -> int:
    """Count total doors in model."""
    count = len(model_dict.get("orphaned_doors", []))
    for room in model_dict.get("rooms", []):
        for face in room.get("faces", []):
            count += len(face.get("doors", []))
    return count


def list_versions(model_name: str) -> dict:
    """
    List all saved versions for a model.
    
    Args:
        model_name: Name of the model.
    
    Returns:
        Dictionary with version history.
    """
    if model_name not in _version_history:
        return {
            "success": False,
            "error": "No versions found for model '{}'".format(model_name)
        }
    
    versions = list(_version_history[model_name])
    version_list = []
    
    for v in reversed(versions):
        version_list.append({
            "version": v["version_id"],
            "timestamp": v["timestamp"],
            "description": v.get("description", ""),
            "rooms_count": v.get("rooms_count", "N/A"),
            "outdoor_shades_count": v.get("outdoor_shades_count", "N/A"),
            "apertures_count": v.get("apertures_count", "N/A"),
            "doors_count": v.get("doors_count", "N/A")
        })
    
    return {
        "success": True,
        "model_name": model_name,
        "versions": version_list,
        "total_versions": len(version_list),
        "max_versions": MAX_VERSIONS
    }


def load_version(model_name: str, version_id: str) -> dict:
    """
    Load a specific version of a model.
    
    Args:
        model_name: Name of the model.
        version_id: Version number to load (e.g., "001", "002").
    
    Returns:
        Dictionary with model dictionary and info.
    """
    if model_name not in _version_history:
        return {
            "success": False,
            "error": "No versions found for model '{}'".format(model_name)
        }
    
    version_id = version_id.zfill(3)
    
    for v in _version_history[model_name]:
        if v["version_id"] == version_id:
            return {
                "success": True,
                "model_dict": v["model_dict"],
                "version_id": version_id,
                "timestamp": v["timestamp"],
                "description": v.get("description", "")
            }
    
    available = [v["version_id"] for v in _version_history[model_name]]
    return {
        "success": False,
        "error": "Version {} not found".format(version_id),
        "available_versions": available
    }


def undo_last(model_name: str) -> dict:
    """
    Undo to the previous version (second to last).
    
    Args:
        model_name: Name of the model.
    
    Returns:
        Dictionary with model dictionary and info.
    """
    if model_name not in _version_history:
        return {
            "success": False,
            "error": "No versions found for model '{}'".format(model_name)
        }
    
    versions = list(_version_history[model_name])
    
    if len(versions) < 2:
        return {
            "success": False,
            "error": "Only one version exists, cannot undo",
            "current_version": versions[-1]["version_id"] if versions else None
        }
    
    current_version = versions[-1]
    previous_version = versions[-2]
    
    if model_name not in _redo_stack:
        _redo_stack[model_name] = []
    _redo_stack[model_name].append(current_version["version_id"])
    
    return {
        "success": True,
        "model_dict": previous_version["model_dict"],
        "version_id": previous_version["version_id"],
        "timestamp": previous_version["timestamp"],
        "description": previous_version.get("description", ""),
        "message": "Restored to version {}".format(previous_version["version_id"])
    }


def redo_last(model_name: str) -> dict:
    """
    Redo the last undone change.
    
    Args:
        model_name: Name of the model.
    
    Returns:
        Dictionary with model dictionary and info.
    """
    if model_name not in _redo_stack or not _redo_stack[model_name]:
        return {
            "success": False,
            "error": "No redo available. Nothing has been undone."
        }
    
    version_id = _redo_stack[model_name].pop()
    
    for v in _version_history[model_name]:
        if v["version_id"] == version_id:
            return {
                "success": True,
                "model_dict": v["model_dict"],
                "version_id": v["version_id"],
                "timestamp": v["timestamp"],
                "description": v.get("description", ""),
                "message": "Redo to version {}".format(version_id)
            }
    
    return {
        "success": False,
        "error": "Version {} not found in history".format(version_id)
    }


def compare_versions(model_name: str, version_id_1: str, version_id_2: str) -> dict:
    """
    Compare two versions of a model.
    
    Args:
        model_name: Name of the model.
        version_id_1: First version to compare.
        version_id_2: Second version to compare.
    
    Returns:
        Dictionary with comparison results.
    """
    if model_name not in _version_history:
        return {
            "success": False,
            "error": "No versions found for model '{}'".format(model_name)
        }
    
    v1 = None
    v2 = None
    
    version_id_1 = version_id_1.zfill(3)
    version_id_2 = version_id_2.zfill(3)
    
    for v in _version_history[model_name]:
        if v["version_id"] == version_id_1:
            v1 = v
        if v["version_id"] == version_id_2:
            v2 = v
    
    if v1 is None:
        return {
            "success": False,
            "error": "Version {} not found".format(version_id_1)
        }
    
    if v2 is None:
        return {
            "success": False,
            "error": "Version {} not found".format(version_id_2)
        }
    
    def get_counts(v):
        model_dict = v.get("model_dict", {})
        return {
            "rooms": v.get("rooms_count", 0),
            "outdoor_shades": v.get("outdoor_shades_count", 0),
            "apertures": v.get("apertures_count", 0),
            "doors": v.get("doors_count", 0),
            "shade_meshes": v.get("shade_meshes_count", 0)
        }
    
    counts1 = get_counts(v1)
    counts2 = get_counts(v2)
    
    differences = {}
    for key in counts1:
        diff = counts2[key] - counts1[key]
        if diff != 0:
            differences[key] = {
                "version_1": counts1[key],
                "version_2": counts2[key],
                "change": diff,
                "direction": "increased" if diff > 0 else "decreased"
            }
    
    return {
        "success": True,
        "model_name": model_name,
        "version_1": {
            "version_id": version_id_1,
            "timestamp": v1["timestamp"],
            "description": v1.get("description", ""),
            "counts": counts1
        },
        "version_2": {
            "version_id": version_id_2,
            "timestamp": v2["timestamp"],
            "description": v2.get("description", ""),
            "counts": counts2
        },
        "differences": differences,
        "has_changes": len(differences) > 0
    }


def get_version_details(model_name: str, version_id: str) -> dict:
    """
    Get detailed information about a specific version.
    
    Args:
        model_name: Name of the model.
        version_id: Version number to get info for.
    
    Returns:
        Dictionary with detailed version information.
    """
    if model_name not in _version_history:
        return {
            "success": False,
            "error": "No versions found for model '{}'".format(model_name)
        }
    
    version_id = version_id.zfill(3)
    
    for v in _version_history[model_name]:
        if v["version_id"] == version_id:
            model_dict = v.get("model_dict", {})
            
            room_identifiers = [r.get("identifier", "unknown") for r in model_dict.get("rooms", [])]
            
            return {
                "success": True,
                "model_name": model_name,
                "version_id": version_id,
                "timestamp": v["timestamp"],
                "description": v.get("description", ""),
                "display_name": model_dict.get("display_name", ""),
                "identifier": model_dict.get("identifier", ""),
                "counts": {
                    "rooms": v.get("rooms_count", 0),
                    "outdoor_shades": v.get("outdoor_shades_count", 0),
                    "apertures": v.get("apertures_count", 0),
                    "doors": v.get("doors_count", 0),
                    "shade_meshes": v.get("shade_meshes_count", 0),
                    "orphaned_faces": len(model_dict.get("orphaned_faces", [])),
                    "orphaned_shades": len(model_dict.get("orphaned_shades", [])),
                    "orphaned_apertures": len(model_dict.get("orphaned_apertures", [])),
                    "orphaned_doors": len(model_dict.get("orphaned_doors", []))
                },
                "room_identifiers": room_identifiers
            }
    
    available = [v["version_id"] for v in _version_history[model_name]]
    return {
        "success": False,
        "error": "Version {} not found".format(version_id),
        "available_versions": available
    }


def delete_version(model_name: str, version_id: str) -> dict:
    """
    Delete a specific version from history.
    
    Args:
        model_name: Name of the model.
        version_id: Version number to delete.
    
    Returns:
        Dictionary with deletion result.
    """
    if model_name not in _version_history:
        return {
            "success": False,
            "error": "No versions found for model '{}'".format(model_name)
        }
    
    version_id = version_id.zfill(3)
    
    for i, v in enumerate(_version_history[model_name]):
        if v["version_id"] == version_id:
            del _version_history[model_name][i]
            return {
                "success": True,
                "message": "Version {} deleted from model '{}'".format(version_id, model_name),
                "model_name": model_name,
                "deleted_version": version_id,
                "remaining_versions": len(_version_history[model_name])
            }
    
    available = [v["version_id"] for v in _version_history[model_name]]
    return {
        "success": False,
        "error": "Version {} not found".format(version_id),
        "available_versions": available
    }


def get_latest_version(model_name: str) -> dict:
    """
    Get the latest version of a model.
    
    Args:
        model_name: Name of the model.
    
    Returns:
        Dictionary with model dictionary and info.
    """
    if model_name not in _version_history or not _version_history[model_name]:
        return {
            "success": False,
            "error": "No versions found for model '{}'".format(model_name)
        }
    
    latest = _version_history[model_name][-1]
    
    return {
        "success": True,
        "model_dict": latest["model_dict"],
        "version_id": latest["version_id"],
        "timestamp": latest["timestamp"]
    }


def clear_versions(model_name: str = None) -> dict:
    """
    Clear version history for a model or all models.
    
    Args:
        model_name: Name of the model (clears all if not specified).
    
    Returns:
        Dictionary with status.
    """
    global _version_history, _version_counter, _redo_stack
    
    if model_name:
        if model_name in _version_history:
            del _version_history[model_name]
            del _version_counter[model_name]
            if model_name in _redo_stack:
                del _redo_stack[model_name]
            return {
                "success": True,
                "message": "Cleared all versions for model '{}'".format(model_name)
            }
        return {
            "success": False,
            "error": "Model '{}' not found".format(model_name)
        }
    else:
        count = len(_version_history)
        _version_history = {}
        _version_counter = {}
        _redo_stack = {}
        return {
            "success": True,
            "message": "Cleared all versions for {} models".format(count)
        }
