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
    
    Removes all apertures (windows, skylights) from all faces including room faces and orphaned faces.
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
    
    Removes all doors from all faces including room faces and orphaned faces.
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
def remove_all_shades(shade_mesh_ids: list = None) -> dict:
    """
    Remove shades from the model.
    
    SHADE TYPES:
    - Shade: Attached shading (louvers, overhangs, blinds) on windows/doors/faces
      Subtypes: outdoor_shades, indoor_shades, orphaned_shades
    - ShadeMesh: Independent context geometry (trees, surrounding buildings)
    
    AI BEHAVIOR GUIDE:
    When user says "delete shades" without specifying type:
    1. First query the model to show what shading elements exist
    2. If BOTH Shade and ShadeMesh exist, ASK user which to remove:
       - "Found X attached shades (louvers, overhangs) and Y context meshes (trees, buildings). Remove all, or specific type?"
    3. If only one type exists, proceed to remove that type
    4. Default behavior (no arguments): removes ALL shading elements (both Shade and ShadeMesh)
    
    Args:
        shade_mesh_ids: Optional list of ShadeMesh identifiers to remove ONLY those meshes.
                       If None, removes ALL shading elements (both Shade and ShadeMesh).
    """
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded. Please use load_model to load a model first."
        }
    
    if shade_mesh_ids is None:
        outdoor_count = len(manager.model.outdoor_shades)
        indoor_count = len(manager.model.indoor_shades)
        orphaned_count = len(manager.model.orphaned_shades)
        mesh_count = len(manager.model.shade_meshes)
        total_count = outdoor_count + indoor_count + orphaned_count + mesh_count
        
        manager.model.remove_all_shades()
        manager.model.remove_shade_meshes()
        
        return {
            "success": True,
            "message": "All shading elements have been removed from the model.",
            "removed": {
                "outdoor_shades": outdoor_count,
                "indoor_shades": indoor_count,
                "orphaned_shades": orphaned_count,
                "shade_meshes": mesh_count,
                "total": total_count
            }
        }
    
    current_count = len(manager.model.shade_meshes)
    
    if current_count == 0:
        return {
            "success": True,
            "message": "No shade meshes found in the model.",
            "removed_count": 0,
            "hint": "Use remove_all_shades() without arguments to remove all shading elements."
        }
    
    removed = []
    not_found = []
    
    for mesh_id in shade_mesh_ids:
        mesh = manager.model.shade_meshes_by_identifier.get(mesh_id)
        if mesh:
            removed.append(mesh_id)
        else:
            not_found.append(mesh_id)
    
    if removed:
        manager.model.remove_shade_meshes(removed)
    
    return {
        "success": True,
        "message": "Removed {} shade mesh(es) from the model.".format(len(removed)),
        "removed_count": len(removed),
        "removed_ids": removed,
        "not_found": not_found,
        "remaining_count": len(manager.model.shade_meshes)
    }
