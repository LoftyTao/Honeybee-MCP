from ..mcp_context import mcp
from ..state.manager import manager
from ..state.summary import summarize_model
from ..versioning.service import save_version_auto
from .service import (
    DEFAULT_NAME,
    _extract_model_identity,
    check_grasshopper_models,
    cleanup_old_cache_files,
    clear_mmap_file,
    get_map_path,
    read_model_from_mmap,
    write_model_to_mmap,
)


@mcp.tool()
def load_model_from_shared_memory(name: str = None, cleanup_irrational: bool = False) -> dict:
    if name is None:
        gh_models = check_grasshopper_models()
        name = gh_models[0]["name"] if gh_models else DEFAULT_NAME

    try:
        model_dict, message, signal_type = read_model_from_mmap(name)
        if signal_type == "clear":
            manager.clear()
            return {
                "success": True,
                "cleared": True,
                "message": "Model cleared from MCP memory (clear signal from Grasshopper)",
            }
        if model_dict is None:
            return {
                "success": False,
                "error": message,
                "hint": "Make sure the Grasshopper Writer component has written the model first",
            }
        manager.load_from_dict(
            model_dict,
            cleanup_irrational=cleanup_irrational,
            source="shared_memory",
            source_name=name,
        )
        save_version_auto(manager.serialized_model_dict(), manager.model.identifier, "Loaded from shared memory")
        identifier, display_name = _extract_model_identity(model_dict, name)
        result = {"success": True, "message": message}
        result.update(summarize_model(manager.model))
        result["shared_name"] = name
        result["identifier"] = identifier
        result["display_name"] = display_name
        if signal_type == "write":
            result["writer_signal"] = True
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def save_model_to_shared_memory(name: str = None) -> dict:
    try:
        if manager.model is None:
            return {"success": False, "error": "No model loaded. Load a model first."}
        if name is None:
            name = manager.model.identifier
        model_dict = manager.serialized_model_dict()
        save_version_auto(model_dict, manager.model.identifier, "Saved to shared memory")
        success, message = write_model_to_mmap(model_dict, name)
        if success:
            return {
                "success": True,
                "message": message,
                "name": name,
                "shared_name": name,
                "identifier": manager.model.identifier,
                "display_name": manager.model.display_name,
                "rooms_count": len(manager.model.rooms),
                "hint": "Connect 'name' output to HB-MCP Reader's _name input",
            }
        return {"success": False, "error": message}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def clear_shared_memory_model(name: str = DEFAULT_NAME) -> dict:
    try:
        success = clear_mmap_file(name)
        return {
            "success": success,
            "message": "Shared memory '{}' cleared".format(name) if success else "Failed to clear shared memory '{}'".format(name),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def check_shared_memory_status(name: str = DEFAULT_NAME) -> dict:
    try:
        map_path = get_map_path(name)
        import os
        import json
        import struct

        if not os.path.exists(map_path):
            return {"exists": False, "message": "Shared memory '{}' does not exist".format(name)}
        with open(map_path, "rb") as f:
            header = f.read(8)
            data_size = struct.unpack("<Q", header)[0]
            if data_size == 0:
                return {"exists": False, "message": "No model found in shared memory '{}'".format(name)}
            model_dict = json.loads(f.read(data_size).decode("utf-8"))
            identifier, display_name = _extract_model_identity(model_dict, name)
            if model_dict.get("cleared") is True:
                return {
                    "exists": True,
                    "signal_type": "clear",
                    "model_name": model_dict.get("model_name", identifier),
                    "message": "Clear signal from Grasshopper - model should be cleared",
                }
            writer_signal = model_dict.get("_writer_signal", {})
            if writer_signal.get("written") is True:
                return {
                    "exists": True,
                    "signal_type": "write",
                    "identifier": identifier,
                    "display_name": display_name,
                    "writer_timestamp": writer_signal.get("timestamp", ""),
                    "size_bytes": data_size,
                    "size_kb": round(data_size / 1024, 2),
                    "name": name,
                    "message": "Model written by Grasshopper (writer signal detected)",
                }
            return {
                "exists": True,
                "signal_type": None,
                "identifier": identifier,
                "display_name": display_name,
                "size_bytes": data_size,
                "size_kb": round(data_size / 1024, 2),
                "size_mb": round(data_size / (1024 * 1024), 2),
                "name": name,
                "path": map_path,
            }
    except Exception as e:
        return {"exists": False, "error": str(e)}


@mcp.tool()
def cleanup_shared_memory_cache() -> dict:
    return cleanup_old_cache_files()
