import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .mcp_context import mcp
from tools.load_model import manager


@mcp.tool()
def query_apertures(
    aperture_identifiers: list,
    identifier: bool = False,
    display_name: bool = False,
    boundary_condition: bool = False,
    is_operable: bool = False,
    is_exterior: bool = False,
    has_parent: bool = False,
    parent: bool = False,
    top_level_parent: bool = False,
    geometry: bool = False,
    vertices: bool = False,
    upper_left_vertices: bool = False,
    normal: bool = False,
    center: bool = False,
    area: bool = False,
    perimeter: bool = False,
    min: bool = False,
    max: bool = False,
    tilt: bool = False,
    altitude: bool = False,
    azimuth: bool = False,
    indoor_shades: bool = False,
    outdoor_shades: bool = False,
    type_color: bool = False,
    bc_color: bool = False,
    triangulated_mesh3d: bool = False,
    return_count: bool = False
) -> dict:
    """
    Query various properties for multiple apertures.
    
    This tool retrieves geometric, topological, and physical properties for
    the specified apertures (windows, skylights). Multiple properties can be
    queried in a single call.
    
    Args:
        aperture_identifiers: List of aperture identifiers to query.
        identifier: Return the aperture identifier string.
        display_name: Return the aperture display name.
        boundary_condition: Return the boundary condition (Outdoors, Surface).
        is_operable: Return True if aperture can be opened for natural ventilation.
        is_exterior: Return True if aperture is on an exterior face.
        has_parent: Return True if aperture has a parent face.
        parent: Return the parent face identifier.
        top_level_parent: Return the top-level parent (room) identifier.
        geometry: Return the aperture geometry string representation.
        vertices: Return list of vertex coordinates [[x,y,z], ...].
        upper_left_vertices: Return vertices starting from upper-left corner.
        normal: Return the normal vector [x, y, z].
        center: Return the center point [x, y, z].
        area: Return the aperture area in m².
        perimeter: Return the aperture perimeter in m.
        min: Return the minimum bounding box coordinates [x, y, z].
        max: Return the maximum bounding box coordinates [x, y, z].
        tilt: Return the tilt angle in degrees (0=up, 180=down).
        altitude: Return the altitude angle in degrees.
        azimuth: Return the azimuth angle in degrees (0=North, 90=East).
        indoor_shades: Return indoor shade identifiers or count.
        outdoor_shades: Return outdoor shade identifiers or count.
        type_color: Return the color associated with aperture type.
        bc_color: Return the color associated with boundary condition.
        triangulated_mesh3d: Return a triangulated mesh representation.
        return_count: If True, return counts instead of identifier lists for shades.
            Default is False.
    
    Returns:
        dict: Dictionary mapping aperture identifiers to their queried properties.
            Each aperture entry contains only the requested properties.
    
    Example:
        query_apertures(["Window_1"], area=True, normal=True)
        query_apertures(["Window_1", "Window_2"], is_operable=True)
        query_apertures(["Skylight_1"], outdoor_shades=True, return_count=True)
    """
    result = {}

    # Process each aperture identifier in the list
    for aperture_identifier in aperture_identifiers:
        aperture = None

        # Search for aperture in rooms first
        for room in manager.model.rooms:
            for face in room.faces:
                for a in face.apertures:
                    if a.identifier == aperture_identifier:
                        aperture = a
                        break
                if aperture is not None:
                    break
            if aperture is not None:
                break

        # If not found in rooms, search orphaned apertures
        if aperture is None:
            for a in manager.model.orphaned_apertures:
                if a.identifier == aperture_identifier:
                    aperture = a
                    break

        # Handle case where aperture is not found
        if aperture is None:
            result[aperture_identifier] = {"error": f"Aperture with identifier '{aperture_identifier}' not found"}
            continue

        # Build result dictionary for this aperture
        aperture_result = {}

        # Query identifier if requested
        if identifier:
            aperture_result["identifier"] = aperture.identifier

        # Query display name if requested
        if display_name:
            aperture_result["display_name"] = aperture.display_name

        # Query boundary condition if requested
        if boundary_condition:
            aperture_result["boundary_condition"] = str(aperture.boundary_condition)

        # Query is_operable if requested
        if is_operable:
            aperture_result["is_operable"] = aperture.is_operable

        # Query indoor shades if requested
        if indoor_shades:
            indoor_shades_list = aperture.indoor_shades
            if return_count:
                aperture_result["indoor_shades"] = {"count": len(indoor_shades_list)}
            else:
                aperture_result["indoor_shades"] = {"identifiers": [shade.identifier for shade in indoor_shades_list]}

        # Query outdoor shades if requested
        if outdoor_shades:
            outdoor_shades_list = aperture.outdoor_shades
            if return_count:
                aperture_result["outdoor_shades"] = {"count": len(outdoor_shades_list)}
            else:
                aperture_result["outdoor_shades"] = {"identifiers": [shade.identifier for shade in outdoor_shades_list]}

        # Query parent if requested
        if parent:
            aperture_result["parent"] = str(aperture.parent) if aperture.parent else None

        # Query top-level parent if requested
        if top_level_parent:
            aperture_result["top_level_parent"] = str(aperture.top_level_parent) if aperture.top_level_parent else None

        # Query has_parent if requested
        if has_parent:
            aperture_result["has_parent"] = aperture.has_parent

        # Query geometry if requested
        if geometry:
            aperture_result["geometry"] = str(aperture.geometry)

        # Query vertices if requested
        if vertices:
            aperture_result["vertices"] = [[v.x, v.y, v.z] for v in aperture.vertices]

        # Query upper left vertices if requested
        if upper_left_vertices:
            aperture_result["upper_left_vertices"] = [[v.x, v.y, v.z] for v in aperture.upper_left_vertices]

        # Query triangulated mesh if requested
        if triangulated_mesh3d:
            aperture_result["triangulated_mesh3d"] = str(aperture.triangulated_mesh3d)

        # Query normal vector if requested
        if normal:
            aperture_result["normal"] = [aperture.normal.x, aperture.normal.y, aperture.normal.z]

        # Query center point if requested
        if center:
            aperture_result["center"] = [aperture.center.x, aperture.center.y, aperture.center.z]

        # Query area if requested
        if area:
            aperture_result["area"] = aperture.area

        # Query perimeter if requested
        if perimeter:
            aperture_result["perimeter"] = aperture.perimeter

        # Query minimum coordinates if requested
        if min:
            aperture_result["min"] = [aperture.min.x, aperture.min.y, aperture.min.z]

        # Query maximum coordinates if requested
        if max:
            aperture_result["max"] = [aperture.max.x, aperture.max.y, aperture.max.z]

        # Query tilt angle if requested
        if tilt:
            aperture_result["tilt"] = aperture.tilt

        # Query altitude angle if requested
        if altitude:
            aperture_result["altitude"] = aperture.altitude

        # Query azimuth angle if requested
        if azimuth:
            aperture_result["azimuth"] = aperture.azimuth

        # Query is_exterior if requested
        if is_exterior:
            aperture_result["is_exterior"] = aperture.is_exterior

        # Query type color if requested
        if type_color:
            aperture_result["type_color"] = aperture.type_color

        # Query boundary condition color if requested
        if bc_color:
            aperture_result["bc_color"] = aperture.bc_color

        # Add aperture results to main result dictionary
        result[aperture_identifier] = aperture_result

    return result
