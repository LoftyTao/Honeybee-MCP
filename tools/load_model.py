import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .mcp_context import mcp
from honeybee.model import Model


class Model_Manager:

    def __init__(self):
        self.model = None

    def load(self, hb_file: str, cleanup_irrational: bool = False):
        self.model = Model.from_file(hb_file, cleanup_irrational=cleanup_irrational)

    def load_from_dict(self, data: dict, cleanup_irrational: bool = False):
        self.model = Model.from_dict(data, cleanup_irrational=cleanup_irrational)

manager = Model_Manager()


@mcp.tool()
def load_model(hb_file: str, cleanup_irrational: bool = False) -> dict:
    """
    Load a Honeybee model from HBJSON or HBpkl file.
    """
    manager.load(hb_file, cleanup_irrational=cleanup_irrational)

    # Calculate and return basic model statistics
    return {
        "display_name": manager.model.display_name,
        "floor_area": sum(room.floor_area for room in manager.model.rooms),
        "rooms_count": len(manager.model.rooms),
        "outdoor_shades_count": len(manager.model.outdoor_shades),
        "orphaned_faces_count": len(manager.model.orphaned_faces),
        "orphaned_shades_count": len(manager.model.orphaned_shades) + len(manager.model.shade_meshes),
        "orphaned_apertures_count": len(manager.model.orphaned_apertures),
        "orphaned_doors_count": len(manager.model.orphaned_doors)
    }


@mcp.tool()
def load_model_from_dict(data: dict, cleanup_irrational: bool = False) -> dict:
    """
    Load a Honeybee model from a dictionary representation.

    Args:
        data: A dictionary representation of a Model object.
        cleanup_irrational: Boolean to note whether common types of irrational 
            objects should be cleaned or removed from the dictionary before 
            serializing the model to Python. Typical cases that are removed 
            include Face3Ds with fewer than 3 vertices, Rooms that have no 
            Face geometry, etc. (Default: False)
    """
    try:
        manager.load_from_dict(data, cleanup_irrational=cleanup_irrational)

        return {
            "success": True,
            "display_name": manager.model.display_name,
            "floor_area": sum(room.floor_area for room in manager.model.rooms),
            "rooms_count": len(manager.model.rooms),
            "outdoor_shades_count": len(manager.model.outdoor_shades),
            "orphaned_faces_count": len(manager.model.orphaned_faces),
            "orphaned_shades_count": len(manager.model.orphaned_shades) + len(manager.model.shade_meshes),
            "orphaned_apertures_count": len(manager.model.orphaned_apertures),
            "orphaned_doors_count": len(manager.model.orphaned_doors)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
