import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .mcp_context import mcp
from tools.load_model import manager


@mcp.tool()
def query_model(
    identifier: bool = False,
    display_name: bool = False,
    rooms: bool = False,
    faces: bool = False,
    apertures: bool = False,
    doors: bool = False,
    shades: bool = False,
    shade_meshes: bool = False,
    indoor_shades: bool = False,
    outdoor_shades: bool = False,
    orphaned_faces: bool = False,
    orphaned_shades: bool = False,
    orphaned_apertures: bool = False,
    orphaned_doors: bool = False,
    stories: bool = False,
    volume: bool = False,
    floor_area: bool = False,
    exposed_area: bool = False,
    exterior_wall_area: bool = False,
    exterior_roof_area: bool = False,
    exterior_aperture_area: bool = False,
    exterior_wall_aperture_area: bool = False,
    exterior_skylight_aperture_area: bool = False,
    return_count: bool = False
) -> dict:
    """
    Query various properties and objects from the loaded model.
    """
    result = {}

    # Query model identifier if requested
    if identifier:
        result["identifier"] = manager.model.identifier

    # Query display name if requested
    if display_name:
        result["display_name"] = manager.model.display_name

    # Query rooms if requested
    if rooms:
        rooms_list = manager.model.rooms
        if return_count:
            result["rooms"] = {"count": len(rooms_list)}
        else:
            result["rooms"] = {"identifiers": [room.identifier for room in rooms_list]}

    # Query faces if requested
    if faces:
        faces_list = manager.model.faces
        if return_count:
            result["faces"] = {"count": len(faces_list)}
        else:
            result["faces"] = {"identifiers": [face.identifier for face in faces_list]}

    # Query apertures if requested
    if apertures:
        apertures_list = manager.model.apertures
        if return_count:
            result["apertures"] = {"count": len(apertures_list)}
        else:
            result["apertures"] = {"identifiers": [aperture.identifier for aperture in apertures_list]}

    # Query doors if requested
    if doors:
        doors_list = manager.model.doors
        if return_count:
            result["doors"] = {"count": len(doors_list)}
        else:
            result["doors"] = {"identifiers": [door.identifier for door in doors_list]}

    # Query shades if requested
    if shades:
        shades_list = manager.model.shades
        if return_count:
            result["shades"] = {"count": len(shades_list)}
        else:
            result["shades"] = {"identifiers": [shade.identifier for shade in shades_list]}

    # Query shade meshes if requested
    if shade_meshes:
        shade_meshes_list = manager.model.shade_meshes
        if return_count:
            result["shade_meshes"] = {"count": len(shade_meshes_list)}
        else:
            result["shade_meshes"] = {"identifiers": [shade.identifier for shade in shade_meshes_list]}

    # Query indoor shades if requested
    if indoor_shades:
        indoor_shades_list = manager.model.indoor_shades
        if return_count:
            result["indoor_shades"] = {"count": len(indoor_shades_list)}
        else:
            result["indoor_shades"] = {"identifiers": [shade.identifier for shade in indoor_shades_list]}

    # Query outdoor shades if requested
    if outdoor_shades:
        outdoor_shades_list = manager.model.outdoor_shades
        if return_count:
            result["outdoor_shades"] = {"count": len(outdoor_shades_list)}
        else:
            result["outdoor_shades"] = {"identifiers": [shade.identifier for shade in outdoor_shades_list]}

    # Query orphaned faces if requested
    if orphaned_faces:
        orphaned_faces_list = manager.model.orphaned_faces
        if return_count:
            result["orphaned_faces"] = {"count": len(orphaned_faces_list)}
        else:
            result["orphaned_faces"] = {"identifiers": [face.identifier for face in orphaned_faces_list]}

    # Query orphaned shades if requested
    if orphaned_shades:
        orphaned_shades_list = manager.model.orphaned_shades
        if return_count:
            result["orphaned_shades"] = {"count": len(orphaned_shades_list)}
        else:
            result["orphaned_shades"] = {"identifiers": [shade.identifier for shade in orphaned_shades_list]}

    # Query orphaned apertures if requested
    if orphaned_apertures:
        orphaned_apertures_list = manager.model.orphaned_apertures
        if return_count:
            result["orphaned_apertures"] = {"count": len(orphaned_apertures_list)}
        else:
            result["orphaned_apertures"] = {"identifiers": [aperture.identifier for aperture in orphaned_apertures_list]}

    # Query orphaned doors if requested
    if orphaned_doors:
        orphaned_doors_list = manager.model.orphaned_doors
        if return_count:
            result["orphaned_doors"] = {"count": len(orphaned_doors_list)}
        else:
            result["orphaned_doors"] = {"identifiers": [door.identifier for door in orphaned_doors_list]}

    # Query stories if requested
    if stories:
        result["stories"] = manager.model.stories

    # Query volume if requested
    if volume:
        result["volume"] = manager.model.volume

    # Query floor area if requested
    if floor_area:
        result["floor_area"] = manager.model.floor_area

    # Query exposed area if requested
    if exposed_area:
        result["exposed_area"] = manager.model.exposed_area

    # Query exterior wall area if requested
    if exterior_wall_area:
        result["exterior_wall_area"] = manager.model.exterior_wall_area

    # Query exterior roof area if requested
    if exterior_roof_area:
        result["exterior_roof_area"] = manager.model.exterior_roof_area

    # Query exterior aperture area if requested
    if exterior_aperture_area:
        result["exterior_aperture_area"] = manager.model.exterior_aperture_area

    # Query exterior wall aperture area if requested
    if exterior_wall_aperture_area:
        result["exterior_wall_aperture_area"] = manager.model.exterior_wall_aperture_area

    # Query skylight aperture area if requested
    if exterior_skylight_aperture_area:
        result["exterior_skylight_aperture_area"] = manager.model.exterior_skylight_aperture_area

    return result
