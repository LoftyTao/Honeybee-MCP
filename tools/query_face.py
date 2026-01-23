import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .mcp_context import mcp
from tools.load_model import manager


@mcp.tool()
def query_faces(
    face_identifiers: list,
    identifier: bool = False,
    display_name: bool = False,
    type: bool = False,
    boundary_condition: bool = False,
    apertures: bool = False,
    doors: bool = False,
    sub_faces: bool = False,
    indoor_shades: bool = False,
    outdoor_shades: bool = False,
    parent: bool = False,
    has_parent: bool = False,
    has_sub_faces: bool = False,
    can_be_ground: bool = False,
    geometry: bool = False,
    punched_geometry: bool = False,
    vertices: bool = False,
    punched_vertices: bool = False,
    upper_left_vertices: bool = False,
    normal: bool = False,
    center: bool = False,
    area: bool = False,
    perimeter: bool = False,
    min: bool = False,
    max: bool = False,
    aperture_area: bool = False,
    aperture_ratio: bool = False,
    tilt: bool = False,
    altitude: bool = False,
    azimuth: bool = False,
    is_exterior: bool = False,
    type_color: bool = False,
    bc_color: bool = False,
    return_count: bool = False
) -> dict:
    """
    Query various properties for multiple faces.
    """
    result = {}

    # Process each face identifier in the list
    for face_identifier in face_identifiers:
        face = None

        # Search for face in rooms first
        for room in manager.model.rooms:
            for f in room.faces:
                if f.identifier == face_identifier:
                    face = f
                    break
            if face is not None:
                break

        # If not found in rooms, search orphaned faces
        if face is None:
            for f in manager.model.orphaned_faces:
                if f.identifier == face_identifier:
                    face = f
                    break

        # Handle case where face is not found
        if face is None:
            result[face_identifier] = {"error": f"Face with identifier '{face_identifier}' not found"}
            continue

        # Build result dictionary for this face
        face_result = {}

        # Query identifier if requested
        if identifier:
            face_result["identifier"] = face.identifier

        # Query display name if requested
        if display_name:
            face_result["display_name"] = face.display_name

        # Query type if requested
        if type:
            face_result["type"] = str(face.type)

        # Query boundary condition if requested
        if boundary_condition:
            face_result["boundary_condition"] = str(face.boundary_condition)

        # Query apertures if requested
        if apertures:
            apertures_list = face.apertures
            if return_count:
                face_result["apertures"] = {"count": len(apertures_list)}
            else:
                face_result["apertures"] = {"identifiers": [aperture.identifier for aperture in apertures_list]}

        # Query doors if requested
        if doors:
            doors_list = face.doors
            if return_count:
                face_result["doors"] = {"count": len(doors_list)}
            else:
                face_result["doors"] = {"identifiers": [door.identifier for door in doors_list]}

        # Query sub-faces if requested
        if sub_faces:
            sub_faces_list = face.sub_faces
            if return_count:
                face_result["sub_faces"] = {"count": len(sub_faces_list)}
            else:
                face_result["sub_faces"] = {"identifiers": [sub_face.identifier for sub_face in sub_faces_list]}

        # Query indoor shades if requested
        if indoor_shades:
            indoor_shades_list = face.indoor_shades
            if return_count:
                face_result["indoor_shades"] = {"count": len(indoor_shades_list)}
            else:
                face_result["indoor_shades"] = {"identifiers": [shade.identifier for shade in indoor_shades_list]}

        # Query outdoor shades if requested
        if outdoor_shades:
            outdoor_shades_list = face.outdoor_shades
            if return_count:
                face_result["outdoor_shades"] = {"count": len(outdoor_shades_list)}
            else:
                face_result["outdoor_shades"] = {"identifiers": [shade.identifier for shade in outdoor_shades_list]}

        # Query parent if requested
        if parent:
            face_result["parent"] = str(face.parent) if face.parent else None

        # Query has_parent if requested
        if has_parent:
            face_result["has_parent"] = face.has_parent

        # Query has_sub_faces if requested
        if has_sub_faces:
            face_result["has_sub_faces"] = face.has_sub_faces

        # Query can_be_ground if requested
        if can_be_ground:
            face_result["can_be_ground"] = face.can_be_ground

        # Query geometry if requested
        if geometry:
            face_result["geometry"] = str(face.geometry)

        # Query punched geometry if requested
        if punched_geometry:
            face_result["punched_geometry"] = str(face.punched_geometry)

        # Query vertices if requested
        if vertices:
            face_result["vertices"] = [[v.x, v.y, v.z] for v in face.vertices]

        # Query punched vertices if requested
        if punched_vertices:
            face_result["punched_vertices"] = [[v.x, v.y, v.z] for v in face.punched_vertices]

        # Query upper left vertices if requested
        if upper_left_vertices:
            face_result["upper_left_vertices"] = [[v.x, v.y, v.z] for v in face.upper_left_vertices]

        # Query normal vector if requested
        if normal:
            face_result["normal"] = [face.normal.x, face.normal.y, face.normal.z]

        # Query center point if requested
        if center:
            face_result["center"] = [face.center.x, face.center.y, face.center.z]

        # Query area if requested
        if area:
            face_result["area"] = face.area

        # Query perimeter if requested
        if perimeter:
            face_result["perimeter"] = face.perimeter

        # Query minimum coordinates if requested
        if min:
            face_result["min"] = [face.min.x, face.min.y, face.min.z]

        # Query maximum coordinates if requested
        if max:
            face_result["max"] = [face.max.x, face.max.y, face.max.z]

        # Query aperture area if requested
        if aperture_area:
            face_result["aperture_area"] = face.aperture_area

        # Query aperture ratio if requested
        if aperture_ratio:
            face_result["aperture_ratio"] = face.aperture_ratio

        # Query tilt angle if requested
        if tilt:
            face_result["tilt"] = face.tilt

        # Query altitude angle if requested
        if altitude:
            face_result["altitude"] = face.altitude

        # Query azimuth angle if requested
        if azimuth:
            face_result["azimuth"] = face.azimuth

        # Query is_exterior if requested
        if is_exterior:
            face_result["is_exterior"] = face.is_exterior

        # Query type color if requested
        if type_color:
            face_result["type_color"] = face.type_color

        # Query boundary condition color if requested
        if bc_color:
            face_result["bc_color"] = face.bc_color

        # Add face results to main result dictionary
        result[face_identifier] = face_result

    return result
