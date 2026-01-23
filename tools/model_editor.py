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
    """
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded. Please use load_model to load a model first."
        }

    # Remove all apertures from the model
    manager.model.remove_all_apertures()

    return {
        "success": True,
        "message": "All apertures (Aperture) have been removed from the model."
    }

@mcp.tool()
def remove_all_doors() -> dict:
    """
    Remove all doors from the model.
    """
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded. Please use load_model to load a model first."
        }

    # Remove all doors from the model
    manager.model.remove_all_doors()

    return {
        "success": True,
        "message": "All doors (Door) have been removed from the model."
    }


@mcp.tool()
def remove_all_shades() -> dict:
    """
    Remove all shades from the model.
    """
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded. Please use load_model to load a model first."
        }

    # Remove all shades from the model
    manager.model.remove_all_shades()

    return {
        "success": True,
        "message": "All shades (Shade) have been removed from the model."
    }