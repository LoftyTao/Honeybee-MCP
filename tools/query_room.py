import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .mcp_context import mcp
from tools.load_model import manager

@mcp.tool()
def query_rooms(
    room_identifiers: list,
    identifier: bool = False,
    display_name: bool = False,
    faces: bool = False,
    multiplier: bool = False,
    zone: bool = False,
    story: bool = False,
    exclude_floor_area: bool = False,
    indoor_furniture: bool = False,
    indoor_shades: bool = False,
    outdoor_shades: bool = False,
    walls: bool = False,
    floors: bool = False,
    roof_ceilings: bool = False,
    air_boundaries: bool = False,
    sub_faces: bool = False,
    doors: bool = False,
    apertures: bool = False,
    exterior_apertures: bool = False,
    floor_area: bool = False,
    exposed_area: bool = False,
    exterior_wall_area: bool = False,
    exterior_aperture_area: bool = False,
    exterior_wall_aperture_area: bool = False,
    exterior_skylight_aperture_area: bool = False,
    average_floor_height: bool = False,
    return_count: bool = False
) -> dict:
    """
    Query various properties for multiple rooms.
    """
    result = {}

    # Process each room identifier in the list
    for room_identifier in room_identifiers:
        # Search for room in model's rooms collection
        room = None
        for r in manager.model.rooms:
            if r.identifier == room_identifier:
                room = r
                break

        # Handle case where room is not found
        if room is None:
            result[room_identifier] = {"error": f"Room with identifier '{room_identifier}' not found"}
            continue

        # Build result dictionary for this room
        room_result = {}

        # Query identifier if requested
        if identifier:
            room_result["identifier"] = room.identifier

        # Query display name if requested
        if display_name:
            room_result["display_name"] = room.display_name

        # Query faces if requested
        if faces:
            faces_list = room.faces
            if return_count:
                room_result["faces"] = {"count": len(faces_list)}
            else:
                room_result["faces"] = {"identifiers": [face.identifier for face in faces_list]}

        # Query multiplier if requested
        if multiplier:
            room_result["multiplier"] = room.multiplier

        # Query zone if requested
        if zone:
            room_result["zone"] = room.zone

        # Query story if requested
        if story:
            room_result["story"] = room.story

        # Query exclude floor area if requested
        if exclude_floor_area:
            room_result["exclude_floor_area"] = room.exclude_floor_area

        # Query indoor furniture if requested
        if indoor_furniture:
            indoor_furniture_list = room.indoor_furniture
            if return_count:
                room_result["indoor_furniture"] = {"count": len(indoor_furniture_list)}
            else:
                room_result["indoor_furniture"] = {"identifiers": [furniture.identifier for furniture in indoor_furniture_list]}

        # Query indoor shades if requested
        if indoor_shades:
            indoor_shades_list = room.indoor_shades
            if return_count:
                room_result["indoor_shades"] = {"count": len(indoor_shades_list)}
            else:
                room_result["indoor_shades"] = {"identifiers": [shade.identifier for shade in indoor_shades_list]}

        # Query outdoor shades if requested
        if outdoor_shades:
            outdoor_shades_list = room.outdoor_shades
            if return_count:
                room_result["outdoor_shades"] = {"count": len(outdoor_shades_list)}
            else:
                room_result["outdoor_shades"] = {"identifiers": [shade.identifier for shade in outdoor_shades_list]}

        # Query walls if requested
        if walls:
            walls_list = room.walls
            if return_count:
                room_result["walls"] = {"count": len(walls_list)}
            else:
                room_result["walls"] = {"identifiers": [wall.identifier for wall in walls_list]}

        # Query floors if requested
        if floors:
            floors_list = room.floors
            if return_count:
                room_result["floors"] = {"count": len(floors_list)}
            else:
                room_result["floors"] = {"identifiers": [floor.identifier for floor in floors_list]}

        # Query roof ceilings if requested
        if roof_ceilings:
            roof_ceilings_list = room.roof_ceilings
            if return_count:
                room_result["roof_ceilings"] = {"count": len(roof_ceilings_list)}
            else:
                room_result["roof_ceilings"] = {"identifiers": [roof.identifier for roof in roof_ceilings_list]}

        # Query air boundaries if requested
        if air_boundaries:
            air_boundaries_list = room.air_boundaries
            if return_count:
                room_result["air_boundaries"] = {"count": len(air_boundaries_list)}
            else:
                room_result["air_boundaries"] = {"identifiers": [boundary.identifier for boundary in air_boundaries_list]}

        # Query sub-faces if requested
        if sub_faces:
            sub_faces_list = room.sub_faces
            if return_count:
                room_result["sub_faces"] = {"count": len(sub_faces_list)}
            else:
                room_result["sub_faces"] = {"identifiers": [face.identifier for face in sub_faces_list]}

        # Query doors if requested
        if doors:
            doors_list = room.doors
            if return_count:
                room_result["doors"] = {"count": len(doors_list)}
            else:
                room_result["doors"] = {"identifiers": [door.identifier for door in doors_list]}

        # Query apertures if requested
        if apertures:
            apertures_list = room.apertures
            if return_count:
                room_result["apertures"] = {"count": len(apertures_list)}
            else:
                room_result["apertures"] = {"identifiers": [aperture.identifier for aperture in apertures_list]}

        # Query exterior apertures if requested
        if exterior_apertures:
            exterior_apertures_list = room.exterior_apertures
            if return_count:
                room_result["exterior_apertures"] = {"count": len(exterior_apertures_list)}
            else:
                room_result["exterior_apertures"] = {"identifiers": [aperture.identifier for aperture in exterior_apertures_list]}

        # Query floor area if requested
        if floor_area:
            room_result["floor_area"] = room.floor_area

        # Query exposed area if requested
        if exposed_area:
            room_result["exposed_area"] = room.exposed_area

        # Query exterior wall area if requested
        if exterior_wall_area:
            room_result["exterior_wall_area"] = room.exterior_wall_area

        # Query exterior aperture area if requested
        if exterior_aperture_area:
            room_result["exterior_aperture_area"] = room.exterior_aperture_area

        # Query exterior wall aperture area if requested
        if exterior_wall_aperture_area:
            room_result["exterior_wall_aperture_area"] = room.exterior_wall_aperture_area

        # Query skylight aperture area if requested
        if exterior_skylight_aperture_area:
            room_result["exterior_skylight_aperture_area"] = room.exterior_skylight_aperture_area

        # Query average floor height if requested
        if average_floor_height:
            room_result["average_floor_height"] = room.average_floor_height

        # Add room results to main result dictionary
        result[room_identifier] = room_result

    return result
