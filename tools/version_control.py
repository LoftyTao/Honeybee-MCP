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
    
    _version_counter[model_name] += 1
    version_id = str(_version_counter[model_name]).zfill(3)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    version_data = {
        "version_id": version_id,
        "timestamp": timestamp,
        "description": description,
        "model_dict": model_dict,
        "rooms_count": len(model_dict.get("rooms", [])),
        "outdoor_shades_count": len(model_dict.get("outdoor_shades", []))
    }
    
    _version_history[model_name].append(version_data)
    
    return {
        "success": True,
        "version_id": version_id,
        "model_name": model_name,
        "timestamp": timestamp,
        "total_versions": len(_version_history[model_name])
    }


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
            "outdoor_shades_count": v.get("outdoor_shades_count", "N/A")
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
    
    previous_version = versions[-2]
    
    return {
        "success": True,
        "model_dict": previous_version["model_dict"],
        "version_id": previous_version["version_id"],
        "timestamp": previous_version["timestamp"],
        "description": previous_version.get("description", ""),
        "message": "Restored to version {}".format(previous_version["version_id"])
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
    global _version_history, _version_counter
    
    if model_name:
        if model_name in _version_history:
            del _version_history[model_name]
            del _version_counter[model_name]
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
        return {
            "success": True,
            "message": "Cleared all versions for {} models".format(count)
        }
