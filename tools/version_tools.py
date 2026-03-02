"""
MCP Tools for Model Version Control

Unified version control tool with multiple actions.
"""

from .mcp_context import mcp
from .version_control import (
    save_version_auto,
    list_versions,
    load_version,
    undo_last,
    get_latest_version,
    clear_versions,
    get_all_model_names,
    redo_last,
    compare_versions,
    get_version_details,
    delete_version
)
from .shared_memory_tools import cleanup_old_cache_files
from .load_model import manager


@mcp.tool()
def version_control(
    action: str,
    model_name: str = None,
    version_id: str = None,
    version_id_2: str = None,
    description: str = ""
) -> dict:
    """
    Unified version control tool for managing model version history.
    
    Actions:
    - "list": List all versions for a model (model_name optional)
    - "save": Save current model as a version snapshot
    - "load": Load a specific version (requires model_name, version_id)
    - "undo": Undo to previous version
    - "redo": Redo last undone change
    - "compare": Compare two versions (requires model_name, version_id, version_id_2)
    - "info": Get detailed info about a version (requires model_name, version_id)
    - "delete": Delete a specific version (requires model_name, version_id)
    - "clear": Clear version history (model_name optional, clears all if not specified)
    - "cleanup": Clean up old shared memory cache files
    
    Args:
        action: The action to perform (list, save, load, undo, redo, compare, info, delete, clear, cleanup)
        model_name: Name of the model (required for load, compare, info, delete)
        version_id: Version number (required for load, compare, info, delete)
        version_id_2: Second version number (required for compare)
        description: Description for save action
    
    Returns:
        dict: Result of the action
    """
    action = action.lower().strip()
    
    if action == "list":
        return _action_list(model_name)
    elif action == "save":
        return _action_save(description)
    elif action == "load":
        return _action_load(model_name, version_id)
    elif action == "undo":
        return _action_undo(model_name)
    elif action == "redo":
        return _action_redo(model_name)
    elif action == "compare":
        return _action_compare(model_name, version_id, version_id_2)
    elif action == "info":
        return _action_info(model_name, version_id)
    elif action == "delete":
        return _action_delete(model_name, version_id)
    elif action == "clear":
        return _action_clear(model_name)
    elif action == "cleanup":
        return cleanup_old_cache_files()
    else:
        return {
            "success": False,
            "error": "Unknown action '{}'. Available actions: list, save, load, undo, redo, compare, info, delete, clear, cleanup".format(action)
        }


def _action_list(model_name: str = None) -> dict:
    """List versions for a model or all models."""
    if model_name:
        return list_versions(model_name)
    else:
        all_models = get_all_model_names()
        if not all_models:
            return {
                "success": True,
                "models": [],
                "total_models": 0,
                "message": "No models with version history"
            }
        
        model_list = []
        for mname in all_models:
            versions_info = list_versions(mname)
            if versions_info.get("success"):
                model_list.append({
                    "model_name": mname,
                    "total_versions": versions_info["total_versions"],
                    "max_versions": versions_info["max_versions"]
                })
        
        return {
            "success": True,
            "models": model_list,
            "total_models": len(model_list)
        }


def _action_save(description: str = "") -> dict:
    """Save current model as a version."""
    if manager.model is None:
        return {
            "success": False,
            "error": "No model loaded. Load a model first."
        }
    
    model_name = manager.model.identifier
    model_dict = manager.model.to_dict()
    
    return save_version_auto(model_dict, model_name, description)


def _action_load(model_name: str, version_id: str) -> dict:
    """Load a specific version."""
    if not model_name:
        return {
            "success": False,
            "error": "model_name is required for load action"
        }
    if not version_id:
        return {
            "success": False,
            "error": "version_id is required for load action"
        }
    
    result = load_version(model_name, version_id)
    
    if result.get("success"):
        manager.load_from_dict(result["model_dict"])
        manager.source = "version_control"
        manager.source_name = "{}_v{}".format(model_name, version_id)
        
        return {
            "success": True,
            "message": "Loaded version {} of model '{}'".format(version_id, model_name),
            "model_name": model_name,
            "version_id": result["version_id"],
            "timestamp": result["timestamp"],
            "description": result.get("description", ""),
            "rooms_count": len(manager.model.rooms),
            "hint": "Model loaded from version control. Use save_model_to_shared_memory() to sync with Grasshopper."
        }
    
    return result


def _action_undo(model_name: str = None) -> dict:
    """Undo to previous version."""
    if model_name is None:
        if manager.model is None:
            return {
                "success": False,
                "error": "No model loaded and no model_name specified."
            }
        model_name = manager.model.identifier
    
    result = undo_last(model_name)
    
    if result.get("success"):
        manager.load_from_dict(result["model_dict"])
        manager.source = "version_control"
        manager.source_name = "{}_v{}".format(model_name, result["version_id"])
        
        return {
            "success": True,
            "message": "Undo successful. Restored to version {}".format(result["version_id"]),
            "model_name": model_name,
            "version_id": result["version_id"],
            "timestamp": result["timestamp"],
            "rooms_count": len(manager.model.rooms)
        }
    
    return result


def _action_redo(model_name: str = None) -> dict:
    """Redo last undone change."""
    if model_name is None:
        if manager.model is None:
            return {
                "success": False,
                "error": "No model loaded and no model_name specified."
            }
        model_name = manager.model.identifier
    
    result = redo_last(model_name)
    
    if result.get("success"):
        manager.load_from_dict(result["model_dict"])
        manager.source = "version_control"
        manager.source_name = "{}_v{}".format(model_name, result["version_id"])
        
        return {
            "success": True,
            "message": "Redo successful. Restored to version {}".format(result["version_id"]),
            "model_name": model_name,
            "version_id": result["version_id"],
            "timestamp": result["timestamp"],
            "rooms_count": len(manager.model.rooms)
        }
    
    return result


def _action_compare(model_name: str, version_id_1: str, version_id_2: str) -> dict:
    """Compare two versions."""
    if not model_name:
        return {
            "success": False,
            "error": "model_name is required for compare action"
        }
    if not version_id_1:
        return {
            "success": False,
            "error": "version_id is required for compare action"
        }
    if not version_id_2:
        return {
            "success": False,
            "error": "version_id_2 is required for compare action"
        }
    
    return compare_versions(model_name, version_id_1, version_id_2)


def _action_info(model_name: str, version_id: str) -> dict:
    """Get detailed info about a version."""
    if not model_name:
        return {
            "success": False,
            "error": "model_name is required for info action"
        }
    if not version_id:
        return {
            "success": False,
            "error": "version_id is required for info action"
        }
    
    return get_version_details(model_name, version_id)


def _action_delete(model_name: str, version_id: str) -> dict:
    """Delete a specific version."""
    if not model_name:
        return {
            "success": False,
            "error": "model_name is required for delete action"
        }
    if not version_id:
        return {
            "success": False,
            "error": "version_id is required for delete action"
        }
    
    return delete_version(model_name, version_id)


def _action_clear(model_name: str = None) -> dict:
    """Clear version history."""
    return clear_versions(model_name)
