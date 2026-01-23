import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .mcp_context import mcp
from tools.load_model import manager

@mcp.tool()
def save_model(name: str = None, folder: str = None, indent: int = None, included_prop: list = None, triangulate_sub_faces: bool = False) -> dict:
    """
    Save the current model to an HBJSON file.
    """
    # Use the Honeybee model's built-in to_hbjson method to export the model
    file_path = manager.model.to_hbjson(
        name=name,
        folder=folder,
        indent=indent,
        included_prop=included_prop,
        triangulate_sub_faces=triangulate_sub_faces
    )

    return {"file_path": file_path}