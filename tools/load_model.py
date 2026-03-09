from .mcp_context import mcp
from .state.hooks import auto_save_to_shared_memory
from .state.manager import manager
from .state.summary import summarize_model
from .sync.service import check_grasshopper_models as _check_grasshopper_models
from .sync.service import cleanup_old_cache_files
from .versioning.service import save_version_auto


@mcp.tool()
def load_model(hb_file: str = None, cleanup_irrational: bool = False) -> dict:
    """
    Load a Honeybee model from HBJSON/HBpkl file or Grasshopper shared memory.
    
    Automatically detects and loads models from Grasshopper shared memory with priority.
    Falls back to file loading if no Grasshopper model is found.
    """
    cleanup_result = cleanup_old_cache_files()
    
    gh_models = _check_grasshopper_models()
    
    if hb_file == "latest" and gh_models:
        from .sync.bus import load_model_from_shared_memory
        
        latest_model = max(gh_models, key=lambda m: m["last_write_time"])
        result = load_model_from_shared_memory(latest_model["name"], cleanup_irrational)
        
        if result.get("success"):
            result["source"] = "grasshopper"
            result["available_grasshopper_models"] = gh_models
            if cleanup_result.get("success"):
                result["cache_cleanup"] = cleanup_result
            return result
    
    if hb_file is None and gh_models:
        from .sync.bus import load_model_from_shared_memory
        
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
    save_version_auto(manager.serialized_model_dict(), manager.model.identifier, "Loaded from file")
    result = {"success": True, "source": "file"}
    result.update(summarize_model(manager.model))
    return result


@mcp.tool()
def load_model_from_dict(data: dict, cleanup_irrational: bool = False) -> dict:
    """
    Load a Honeybee model from a dictionary representation.
    
    Useful for loading models from version control, API responses, or manual construction.
    """
    try:
        manager.load_from_dict(data, cleanup_irrational=cleanup_irrational)
        save_version_auto(manager.serialized_model_dict(), manager.model.identifier, "Loaded from dict")
        result = {"success": True}
        result.update(summarize_model(manager.model))
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
