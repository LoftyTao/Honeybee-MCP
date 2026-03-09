from ..mcp_context import mcp
from ..state.manager import manager
from ..state.hooks import sync_model_to_shared_memory
from ..sync.service import cleanup_old_cache_files
from .service import (
    clear_versions,
    compare_versions,
    delete_version,
    get_all_model_names,
    get_version_details,
    list_versions,
    load_version,
    redo_last,
    save_version_auto,
    undo_last,
)


@mcp.tool()
def version_control(
    action: str,
    model_name: str = None,
    version_id: str = None,
    version_id_2: str = None,
    description: str = "",
) -> dict:
    action = action.lower().strip()
    if action == "list":
        return _action_list(model_name)
    if action == "save":
        return _action_save(description)
    if action == "load":
        return _action_load(model_name, version_id)
    if action == "undo":
        return _action_undo(model_name)
    if action == "redo":
        return _action_redo(model_name)
    if action == "compare":
        return _action_compare(model_name, version_id, version_id_2)
    if action == "info":
        return _action_info(model_name, version_id)
    if action == "delete":
        return _action_delete(model_name, version_id)
    if action == "clear":
        return _action_clear(model_name)
    if action == "cleanup":
        return cleanup_old_cache_files()
    return {
        "success": False,
        "error": "Unknown action '{}'. Available actions: list, save, load, undo, redo, compare, info, delete, clear, cleanup".format(action),
    }


def _load_versioned_model(result: dict, model_name: str, version_id: str, success_message: str) -> dict:
    shared_source_name = manager.source_name if manager.source == "shared_memory" else None

    if shared_source_name is not None:
        manager.load_from_dict(
            result["model_dict"],
            source="shared_memory",
            source_name=shared_source_name,
        )
        shared_memory_sync = sync_model_to_shared_memory(
            save_version=False,
            description="Synced after version control action",
        )
    else:
        manager.load_from_dict(
            result["model_dict"],
            source="version_control",
            source_name=f"{model_name}_v{version_id}",
        )
        shared_memory_sync = None

    response = {
        "success": True,
        "message": success_message,
        "model_name": model_name,
        "version_id": result["version_id"],
        "timestamp": result["timestamp"],
        "description": result.get("description", ""),
        "rooms_count": len(manager.model.rooms),
    }
    if shared_memory_sync is not None:
        response["shared_memory_sync"] = shared_memory_sync
    return response


def _action_list(model_name: str = None) -> dict:
    if model_name:
        return list_versions(model_name)
    all_models = get_all_model_names()
    if not all_models:
        return {"success": True, "models": [], "total_models": 0, "message": "No models with version history"}
    model_list = []
    for mname in all_models:
        versions_info = list_versions(mname)
        if versions_info.get("success"):
            model_list.append(
                {
                    "model_name": mname,
                    "total_versions": versions_info["total_versions"],
                    "max_versions": versions_info["max_versions"],
                }
            )
    return {"success": True, "models": model_list, "total_models": len(model_list)}


def _action_save(description: str = "") -> dict:
    if manager.model is None:
        return {"success": False, "error": "No model loaded. Load a model first."}
    return save_version_auto(manager.serialized_model_dict(), manager.model.identifier, description)


def _action_load(model_name: str, version_id: str) -> dict:
    if not model_name:
        return {"success": False, "error": "model_name is required for load action"}
    if not version_id:
        return {"success": False, "error": "version_id is required for load action"}
    result = load_version(model_name, version_id)
    if result.get("success"):
        return _load_versioned_model(
            result,
            model_name,
            version_id,
            "Loaded version {} of model '{}'".format(version_id, model_name),
        )
    return result


def _action_undo(model_name: str = None) -> dict:
    if model_name is None:
        if manager.model is None:
            return {"success": False, "error": "No model loaded and no model_name specified."}
        model_name = manager.model.identifier
    result = undo_last(model_name)
    if result.get("success"):
        return _load_versioned_model(
            result,
            model_name,
            result["version_id"],
            "Undo successful. Restored to version {}".format(result["version_id"]),
        )
    return result


def _action_redo(model_name: str = None) -> dict:
    if model_name is None:
        if manager.model is None:
            return {"success": False, "error": "No model loaded and no model_name specified."}
        model_name = manager.model.identifier
    result = redo_last(model_name)
    if result.get("success"):
        return _load_versioned_model(
            result,
            model_name,
            result["version_id"],
            "Redo successful. Restored to version {}".format(result["version_id"]),
        )
    return result


def _action_compare(model_name: str, version_id_1: str, version_id_2: str) -> dict:
    if not model_name:
        return {"success": False, "error": "model_name is required for compare action"}
    if not version_id_1:
        return {"success": False, "error": "version_id is required for compare action"}
    if not version_id_2:
        return {"success": False, "error": "version_id_2 is required for compare action"}
    return compare_versions(model_name, version_id_1, version_id_2)


def _action_info(model_name: str, version_id: str) -> dict:
    if not model_name:
        return {"success": False, "error": "model_name is required for info action"}
    if not version_id:
        return {"success": False, "error": "version_id is required for info action"}
    return get_version_details(model_name, version_id)


def _action_delete(model_name: str, version_id: str) -> dict:
    if not model_name:
        return {"success": False, "error": "model_name is required for delete action"}
    if not version_id:
        return {"success": False, "error": "version_id is required for delete action"}
    return delete_version(model_name, version_id)


def _action_clear(model_name: str = None) -> dict:
    return clear_versions(model_name)
