from .mcp_context import mcp
from tools.load_model import manager
from honeybee.shade import Shade


@mcp.tool()
def query_shades(
    shade_identifiers: list,
    identifier: bool = False,
    display_name: bool = False,
    is_detached: bool = False,
    is_indoor: bool = False,
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
    type_color: bool = False,
    bc_color: bool = False,
    return_count: bool = False
) -> dict:
    """
    Query various properties for multiple shades.
    
    Retrieves geometric, topological, and physical properties for the specified shading elements (overhangs, louvers, blinds).
    """
    result = {}

    # Process each shade identifier in the list
    for shade_identifier in shade_identifiers:
        shade = None

        # Search for shade in rooms first (check indoor and outdoor shades at room level)
        for room in manager.model.rooms:
            for s in room.indoor_shades:
                if s.identifier == shade_identifier:
                    shade = s
                    break
            if shade is not None:
                break
            for s in room.outdoor_shades:
                if s.identifier == shade_identifier:
                    shade = s
                    break
            if shade is not None:
                break

            # Search in face-level shades
            for face in room.faces:
                for s in face.indoor_shades:
                    if s.identifier == shade_identifier:
                        shade = s
                        break
                if shade is not None:
                    break
                for s in face.outdoor_shades:
                    if s.identifier == shade_identifier:
                        shade = s
                        break
                if shade is not None:
                    break

                # Search in aperture-level shades
                for a in face.apertures:
                    for s in a.indoor_shades:
                        if s.identifier == shade_identifier:
                            shade = s
                            break
                    if shade is not None:
                        break
                    for s in a.outdoor_shades:
                        if s.identifier == shade_identifier:
                            shade = s
                            break
                    if shade is not None:
                        break

                # Search in door-level shades
                for d in face.doors:
                    for s in d.indoor_shades:
                        if s.identifier == shade_identifier:
                            shade = s
                            break
                    if shade is not None:
                        break
                    for s in d.outdoor_shades:
                        if s.identifier == shade_identifier:
                            shade = s
                            break
                    if shade is not None:
                        break

            if shade is not None:
                break

        # If not found in rooms, search orphaned shades
        if shade is None:
            for s in manager.model.orphaned_shades:
                if s.identifier == shade_identifier:
                    shade = s
                    break

        # Handle case where shade is not found
        if shade is None:
            result[shade_identifier] = {"error": f"Shade with identifier '{shade_identifier}' not found"}
            continue

        # Build result dictionary for this shade
        shade_result = {}

        # Query identifier if requested
        if identifier:
            shade_result["identifier"] = shade.identifier

        # Query display name if requested
        if display_name:
            shade_result["display_name"] = shade.display_name

        # Query is_detached if requested
        if is_detached:
            shade_result["is_detached"] = shade.is_detached

        # Query parent if requested
        if parent:
            shade_result["parent"] = str(shade.parent) if shade.parent else None

        # Query top-level parent if requested
        if top_level_parent:
            shade_result["top_level_parent"] = str(shade.top_level_parent) if shade.top_level_parent else None

        # Query has_parent if requested
        if has_parent:
            shade_result["has_parent"] = shade.has_parent

        # Query is_indoor if requested
        if is_indoor:
            shade_result["is_indoor"] = shade.is_indoor

        # Query geometry if requested
        if geometry:
            shade_result["geometry"] = str(shade.geometry)

        # Query vertices if requested
        if vertices:
            shade_result["vertices"] = [[v.x, v.y, v.z] for v in shade.vertices]

        # Query upper left vertices if requested
        if upper_left_vertices:
            shade_result["upper_left_vertices"] = [[v.x, v.y, v.z] for v in shade.upper_left_vertices]

        # Query normal vector if requested
        if normal:
            shade_result["normal"] = [shade.normal.x, shade.normal.y, shade.normal.z]

        # Query center point if requested
        if center:
            shade_result["center"] = [shade.center.x, shade.center.y, shade.center.z]

        # Query area if requested
        if area:
            shade_result["area"] = shade.area

        # Query perimeter if requested
        if perimeter:
            shade_result["perimeter"] = shade.perimeter

        # Query minimum coordinates if requested
        if min:
            shade_result["min"] = [shade.min.x, shade.min.y, shade.min.z]

        # Query maximum coordinates if requested
        if max:
            shade_result["max"] = [shade.max.x, shade.max.y, shade.max.z]

        # Query tilt angle if requested
        if tilt:
            shade_result["tilt"] = shade.tilt

        # Query altitude angle if requested
        if altitude:
            shade_result["altitude"] = shade.altitude

        # Query azimuth angle if requested
        if azimuth:
            shade_result["azimuth"] = shade.azimuth

        # Query type color if requested
        if type_color:
            shade_result["type_color"] = shade.type_color

        # Query boundary condition color if requested
        if bc_color:
            shade_result["bc_color"] = shade.bc_color

        # Add shade results to main result dictionary
        result[shade_identifier] = shade_result

    return result
