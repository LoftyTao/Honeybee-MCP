from .mcp_context import mcp
from .state.manager import manager
from .state.energy_resources import dump_json


def _resolve_output_path(name=None, folder=None):
    import os

    if manager.model is None:
        raise ValueError("No model loaded. Load a model first.")

    target_name = name or manager.model.identifier
    if not target_name.lower().endswith(".hbjson"):
        target_name = target_name + ".hbjson"
    target_folder = folder or os.getcwd()
    os.makedirs(target_folder, exist_ok=True)
    return os.path.join(target_folder, target_name)

@mcp.tool()
def save_model(
    name: str = None,
    folder: str = None,
    indent: int = None,
    included_prop: list = None,
    triangulate_sub_faces: bool = False
) -> dict:
    """
    Save the current model to an HBJSON file.
    
    Exports the currently loaded Honeybee model with optional formatting and property filtering.
    """
    if manager.model is None:
        return {"success": False, "error": "No model loaded. Load a model first."}

    model_dict = manager.serialized_model_dict()
    if included_prop is not None:
        filtered = manager.model.to_dict(
            included_prop=included_prop,
            triangulate_sub_faces=triangulate_sub_faces,
        )
        filtered["properties"]["energy"] = model_dict.get("properties", {}).get("energy", {})
        filtered["properties"]["radiance"] = model_dict.get("properties", {}).get("radiance", {})
        model_dict = filtered

    file_path = _resolve_output_path(name=name, folder=folder)
    dump_json(file_path, model_dict, indent=indent)

    return {"success": True, "file_path": file_path}
