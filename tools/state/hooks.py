from .manager import manager


def ensure_model_loaded():
    if manager.model is None:
        raise ValueError("No model loaded. Please use load_model to load a model first.")


def sync_model_to_shared_memory(save_version: bool = True, description: str = "Auto-saved after edit"):
    """Sync the current model back to shared memory when the active source is shared memory."""
    if manager.model is None or manager.source != "shared_memory" or manager.source_name is None:
        return None

    from ..sync.service import write_model_to_mmap
    from ..versioning.service import save_version_auto

    model_dict = manager.serialized_model_dict()
    model_name = manager.model.identifier
    if save_version:
        save_version_auto(model_dict, model_name, description)
    success, message = write_model_to_mmap(model_dict, manager.source_name)
    if success:
        return {
            "auto_saved": True,
            "message": message,
            "source_name": manager.source_name,
            "saved_version": save_version,
        }
    return {
        "auto_saved": False,
        "error": message,
        "saved_version": save_version,
    }


def auto_save_to_shared_memory():
    """Auto-save edits when the model source is shared memory."""
    return sync_model_to_shared_memory(save_version=True, description="Auto-saved after edit")


def post_edit_pipeline(result: dict) -> dict:
    """Attach cross-cutting edit side effects to a tool result."""
    auto_save_result = auto_save_to_shared_memory()
    if auto_save_result:
        result["auto_save"] = auto_save_result
    return result
