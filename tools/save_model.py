import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .mcp_context import mcp
from tools.load_model import manager

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
    
    This tool exports the currently loaded Honeybee model to an HBJSON file.
    The model can be saved with custom formatting and property filtering options.
    
    Args:
        name: File name for the HBJSON file. If not provided, uses the model's
            display_name or identifier. The .hbjson extension is added automatically.
        folder: Directory path to save the file. If not provided, saves to the
            current working directory.
        indent: Number of spaces for JSON indentation. If not provided, the JSON
            is compact (no indentation). Use for human-readable files.
        included_prop: List of property types to include in the export. If None,
            all properties are included. Options include:
            - "energy": EnergyPlus properties
            - "radiance": Radiance properties
            - "doe2": DOE-2 properties
            Example: ["energy", "radiance"]
        triangulate_sub_faces: If True, triangulate all sub-faces (apertures, doors)
            before export. Useful for compatibility with some simulation engines.
            Default is False.
    
    Returns:
        dict: Dictionary containing:
            - file_path (str): Absolute path to the saved HBJSON file
            - error (str): Error message if save failed (if applicable)
    
    Example:
        save_model()  # Save with default name to current directory
        save_model(name="my_model", folder="/path/to/output")
        save_model(name="energy_model", included_prop=["energy"])
        save_model(name="readable", indent=2)
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