import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .mcp_context import mcp
from tools.load_model import manager


def _get_nested_attr(obj, attr_path):
    """
    Safely retrieves a nested attribute from an object using a dot-separated path.
    Returns None if any part of the chain is missing.
    """
    try:
        attributes = attr_path.split('.')
        current = obj
        for attr in attributes:
            if current is None:
                return None
            if attr == '__class__':
                current = current.__class__
            elif attr == '__name__':
                current = current.__name__
            else:
                current = getattr(current, attr, None)
        return current
    except Exception:
        return None


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
    energy_properties: bool = False,
    radiance_properties: bool = False,
    return_count: bool = False
) -> dict:
    """
    Query various properties for multiple faces including Energy and Radiance attributes.
    
    Retrieves geometric, topological, and simulation properties for the specified faces.
    """
    if not manager.model:
        raise ValueError("Model is not loaded.")

    result = {}

    # Optimize Lookup: Build a map for requested faces to avoid O(N*M) complexity
    # Note: Since faces can be in Rooms or Orphaned, we search both.
    found_faces_map = {}
    
    # 1. Search in Rooms
    for room in manager.model.rooms:
        for face in room.faces:
            if face.identifier in face_identifiers:
                found_faces_map[face.identifier] = face
    
    # 2. Search in Orphaned Faces (only if we haven't found everything)
    if len(found_faces_map) < len(face_identifiers):
        for face in manager.model.orphaned_faces:
            if face.identifier in face_identifiers:
                found_faces_map[face.identifier] = face

    # Process each requested identifier
    for face_identifier in face_identifiers:
        face = found_faces_map.get(face_identifier)

        # Handle case where face is not found
        if face is None:
            result[face_identifier] = {"error": f"Face with identifier '{face_identifier}' not found"}
            continue

        # Build result dictionary for this face
        face_result = {}

        # --- Standard Geometry & Topology Queries ---
        if identifier:
            face_result["identifier"] = face.identifier
        if display_name:
            face_result["display_name"] = face.display_name
        if type:
            face_result["type"] = str(face.type)
        if boundary_condition:
            face_result["boundary_condition"] = str(face.boundary_condition)
        if apertures:
            items = face.apertures
            face_result["apertures"] = {"count": len(items)} if return_count else {"identifiers": [i.identifier for i in items]}
        if doors:
            items = face.doors
            face_result["doors"] = {"count": len(items)} if return_count else {"identifiers": [i.identifier for i in items]}
        if sub_faces:
            items = face.sub_faces
            face_result["sub_faces"] = {"count": len(items)} if return_count else {"identifiers": [i.identifier for i in items]}
        if indoor_shades:
            items = face.indoor_shades
            face_result["indoor_shades"] = {"count": len(items)} if return_count else {"identifiers": [i.identifier for i in items]}
        if outdoor_shades:
            items = face.outdoor_shades
            face_result["outdoor_shades"] = {"count": len(items)} if return_count else {"identifiers": [i.identifier for i in items]}
        if parent:
            face_result["parent"] = str(face.parent) if face.parent else None
        if has_parent:
            face_result["has_parent"] = face.has_parent
        if has_sub_faces:
            face_result["has_sub_faces"] = face.has_sub_faces
        if can_be_ground:
            face_result["can_be_ground"] = face.can_be_ground
        if geometry:
            face_result["geometry"] = str(face.geometry)
        if punched_geometry:
            face_result["punched_geometry"] = str(face.punched_geometry)
        if vertices:
            face_result["vertices"] = [[v.x, v.y, v.z] for v in face.vertices]
        if punched_vertices:
            face_result["punched_vertices"] = [[v.x, v.y, v.z] for v in face.punched_vertices]
        if upper_left_vertices:
            face_result["upper_left_vertices"] = [[v.x, v.y, v.z] for v in face.upper_left_vertices]
        if normal:
            face_result["normal"] = [face.normal.x, face.normal.y, face.normal.z]
        if center:
            face_result["center"] = [face.center.x, face.center.y, face.center.z]
        if area:
            face_result["area"] = face.area
        if perimeter:
            face_result["perimeter"] = face.perimeter
        if min:
            face_result["min"] = [face.min.x, face.min.y, face.min.z]
        if max:
            face_result["max"] = [face.max.x, face.max.y, face.max.z]
        if aperture_area:
            face_result["aperture_area"] = face.aperture_area
        if aperture_ratio:
            face_result["aperture_ratio"] = face.aperture_ratio
        if tilt:
            face_result["tilt"] = face.tilt
        if altitude:
            face_result["altitude"] = face.altitude
        if azimuth:
            face_result["azimuth"] = face.azimuth
        if is_exterior:
            face_result["is_exterior"] = face.is_exterior
        if type_color:
            face_result["type_color"] = face.type_color
        if bc_color:
            face_result["bc_color"] = face.bc_color

        # --- New Energy Properties Query ---
        if energy_properties:
            # Helper to extract material names safely
            layers_obj = _get_nested_attr(face, "properties.energy.construction.layers")
            layer_names = [mat.identifier for mat in layers_obj] if layers_obj else None

            face_result.update({
                "construction": _get_nested_attr(face, "properties.energy.construction.display_name"),
                "materials": layer_names,
                "thickness": _get_nested_attr(face, "properties.energy.construction.thickness"),
                "density": _get_nested_attr(face, "properties.energy.construction.mass_area_density"),
                "heat_capacity": _get_nested_attr(face, "properties.energy.construction.area_heat_capacity"),
                "construction_r_value": _get_nested_attr(face, "properties.energy.construction.r_value"),
                "construction_u_value": _get_nested_attr(face, "properties.energy.construction.u_value"),
                "construction_u_factor": _get_nested_attr(face, "properties.energy.construction.u_factor"),
                "construction_shgc": _get_nested_attr(face, "properties.energy.construction.shgc"),
                "r_factor": _get_nested_attr(face, "properties.energy.r_factor"),
                "u_factor": _get_nested_attr(face, "properties.energy.u_factor"),
                "shgc": _get_nested_attr(face, "properties.energy.shgc"),
                "solar_transmittance": _get_nested_attr(face, "properties.energy.construction.solar_transmittance"),
                "visible_transmittance": _get_nested_attr(face, "properties.energy.construction.visible_transmittance"),
                "solar_reflectance_outside": _get_nested_attr(face, "properties.energy.construction.outside_solar_reflectance"),
                "solar_reflectance_inside": _get_nested_attr(face, "properties.energy.construction.inside_solar_reflectance"),
                "fraction_area_operable": _get_nested_attr(face, "properties.energy.vent_opening.fraction_area_operable"),
                "fraction_height_operable": _get_nested_attr(face, "properties.energy.vent_opening.fraction_height_operable"),
                "discharge_coefficient": _get_nested_attr(face, "properties.energy.vent_opening.discharge_coefficient")
            })

        # --- New Radiance Properties Query ---
        if radiance_properties:
            # Helper to extract state names safely
            states_obj = _get_nested_attr(face, "properties.radiance.states")
            state_names = [st.identifier for st in states_obj] if states_obj else None

            face_result.update({
                "modifier": _get_nested_attr(face, "properties.radiance.modifier.display_name"),
                "average_reflectance": _get_nested_attr(face, "properties.radiance.modifier.average_reflectance"),
                "average_transmittance": _get_nested_attr(face, "properties.radiance.modifier.average_transmittance"),
                "modifier_blk": _get_nested_attr(face, "properties.radiance.modifier_blk.display_name"),
                "is_opaque": _get_nested_attr(face, "properties.radiance.is_opaque"),
                "dynamic_group": _get_nested_attr(face, "properties.radiance.dynamic_group_identifier"),
                "state_count": _get_nested_attr(face, "properties.radiance.state_count"),
                "states": state_names
            })

        result[face_identifier] = face_result

    return result