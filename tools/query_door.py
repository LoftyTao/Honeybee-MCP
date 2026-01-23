import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .mcp_context import mcp
from tools.load_model import manager


@mcp.tool()
def query_doors(
    door_identifiers: list,
    identifier: bool = False,
    display_name: bool = False,
    boundary_condition: bool = False,
    is_glass: bool = False,
    indoor_shades: bool = False,
    outdoor_shades: bool = False,
    parent: bool = False,
    top_level_parent: bool = False,
    has_parent: bool = False,
    geometry: bool = False,
    vertices: bool = False,
    upper_left_vertices: bool = False,
    triangulated_mesh3d: bool = False,
    normal: bool = False,
    center: bool = False,
    area: bool = False,
    perimeter: bool = False,
    min: bool = False,
    max: bool = False,
    tilt: bool = False,
    altitude: bool = False,
    azimuth: bool = False,
    is_exterior: bool = False,
    type_color: bool = False,
    bc_color: bool = False,
    return_count: bool = False
) -> dict:
    """
    Query various properties for multiple doors.
    """
    result = {}

    # Process each door identifier in the list
    for door_identifier in door_identifiers:
        door = None

        # Search for door in rooms first
        for room in manager.model.rooms:
            for face in room.faces:
                for d in face.doors:
                    if d.identifier == door_identifier:
                        door = d
                        break
                if door is not None:
                    break
            if door is not None:
                break

        # If not found in rooms, search orphaned doors
        if door is None:
            for d in manager.model.orphaned_doors:
                if d.identifier == door_identifier:
                    door = d
                    break

        # Handle case where door is not found
        if door is None:
            result[door_identifier] = {"error": f"Door with identifier '{door_identifier}' not found"}
            continue

        # Build result dictionary for this door
        door_result = {}

        # Query identifier if requested
        if identifier:
            door_result["identifier"] = door.identifier

        # Query display name if requested
        if display_name:
            door_result["display_name"] = door.display_name

        # Query boundary condition if requested
        if boundary_condition:
            door_result["boundary_condition"] = str(door.boundary_condition)

        # Query is_glass if requested
        if is_glass:
            door_result["is_glass"] = door.is_glass

        # Query indoor shades if requested
        if indoor_shades:
            indoor_shades_list = door.indoor_shades
            if return_count:
                door_result["indoor_shades"] = {"count": len(indoor_shades_list)}
            else:
                door_result["indoor_shades"] = {"identifiers": [shade.identifier for shade in indoor_shades_list]}

        # Query outdoor shades if requested
        if outdoor_shades:
            outdoor_shades_list = door.outdoor_shades
            if return_count:
                door_result["outdoor_shades"] = {"count": len(outdoor_shades_list)}
            else:
                door_result["outdoor_shades"] = {"identifiers": [shade.identifier for shade in outdoor_shades_list]}

        # Query parent if requested
        if parent:
            door_result["parent"] = str(door.parent) if door.parent else None

        # Query top-level parent if requested
        if top_level_parent:
            door_result["top_level_parent"] = str(door.top_level_parent) if door.top_level_parent else None

        # Query has_parent if requested
        if has_parent:
            door_result["has_parent"] = door.has_parent

        # Query geometry if requested
        if geometry:
            door_result["geometry"] = str(door.geometry)

        # Query vertices if requested
        if vertices:
            door_result["vertices"] = [[v.x, v.y, v.z] for v in door.vertices]

        # Query upper left vertices if requested
        if upper_left_vertices:
            door_result["upper_left_vertices"] = [[v.x, v.y, v.z] for v in door.upper_left_vertices]

        # Query triangulated mesh if requested
        if triangulated_mesh3d:
            door_result["triangulated_mesh3d"] = str(door.triangulated_mesh3d)

        # Query normal vector if requested
        if normal:
            door_result["normal"] = [door.normal.x, door.normal.y, door.normal.z]

        # Query center point if requested
        if center:
            door_result["center"] = [door.center.x, door.center.y, door.center.z]

        # Query area if requested
        if area:
            door_result["area"] = door.area

        # Query perimeter if requested
        if perimeter:
            door_result["perimeter"] = door.perimeter

        # Query minimum coordinates if requested
        if min:
            door_result["min"] = [door.min.x, door.min.y, door.min.z]

        # Query maximum coordinates if requested
        if max:
            door_result["max"] = [door.max.x, door.max.y, door.max.z]

        # Query tilt angle if requested
        if tilt:
            door_result["tilt"] = door.tilt

        # Query altitude angle if requested
        if altitude:
            door_result["altitude"] = door.altitude

        # Query azimuth angle if requested
        if azimuth:
            door_result["azimuth"] = door.azimuth

        # Query is_exterior if requested
        if is_exterior:
            door_result["is_exterior"] = door.is_exterior

        # Query type color if requested
        if type_color:
            door_result["type_color"] = door.type_color

        # Query boundary condition color if requested
        if bc_color:
            door_result["bc_color"] = door.bc_color

        # Add door results to main result dictionary
        result[door_identifier] = door_result

    return result
