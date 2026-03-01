import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .mcp_context import mcp
from tools.load_model import manager

@mcp.tool()
def remove_all_apertures() -> dict:
    """
    Remove all apertures from the model.
    
    This tool removes all apertures (windows, skylights) from all faces
    in the model, including both room faces and orphaned faces. This is
    useful for creating a model without any glazing for analysis purposes.
    
    Returns:
        dict: Dictionary containing:
            - success (bool): Whether the operation was successful
            - message (str): Status message
            - error (str): Error message if operation failed
    
    Example:
        remove_all_apertures()
    """
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded. Please use load_model to load a model first."
        }

    manager.model.remove_all_apertures()

    return {
        "success": True,
        "message": "All apertures (Aperture) have been removed from the model."
    }

@mcp.tool()
def remove_all_doors() -> dict:
    """
    Remove all doors from the model.
    
    This tool removes all doors from all faces in the model, including
    both room faces and orphaned faces. Both glass and opaque doors are removed.
    
    Returns:
        dict: Dictionary containing:
            - success (bool): Whether the operation was successful
            - message (str): Status message
            - error (str): Error message if operation failed
    
    Example:
        remove_all_doors()
    """
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded. Please use load_model to load a model first."
        }

    manager.model.remove_all_doors()

    return {
        "success": True,
        "message": "All doors (Door) have been removed from the model."
    }


@mcp.tool()
def remove_all_shades() -> dict:
    """
    Remove all shades from the model.
    
    This tool removes all shading elements from the model, including:
    - Outdoor shades (overhangs, fins, louvers)
    - Indoor shades (blinds, curtains)
    - Orphaned shades
    - Shade meshes
    
    Returns:
        dict: Dictionary containing:
            - success (bool): Whether the operation was successful
            - message (str): Status message
            - error (str): Error message if operation failed
    
    Example:
        remove_all_shades()
    """
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded. Please use load_model to load a model first."
        }

    manager.model.remove_all_shades()

    return {
        "success": True,
        "message": "All shades (Shade) have been removed from the model."
    }