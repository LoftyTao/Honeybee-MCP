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
    
    This tool retrieves information about the currently loaded Honeybee model.
    You can query for object identifiers, counts, and geometric properties.
    Multiple properties can be queried in a single call.
    
    Args:
        identifier: Return the model identifier string.
        display_name: Return the model display name.
        rooms: Return room identifiers or count.
        faces: Return face identifiers or count.
        apertures: Return aperture identifiers or count.
        doors: Return door identifiers or count.
        shades: Return all shade identifiers or count.
        shade_meshes: Return shade mesh identifiers or count.
        indoor_shades: Return indoor shade identifiers or count.
        outdoor_shades: Return outdoor shade identifiers or count.
        orphaned_faces: Return orphaned face identifiers or count.
        orphaned_shades: Return orphaned shade identifiers or count.
        orphaned_apertures: Return orphaned aperture identifiers or count.
        orphaned_doors: Return orphaned door identifiers or count.
        stories: Return the list of story names.
        volume: Return the total model volume in m³.
        floor_area: Return the total floor area in m².
        exposed_area: Return the total exposed area in m².
        exterior_wall_area: Return the exterior wall area in m².
        exterior_roof_area: Return the exterior roof area in m².
        exterior_aperture_area: Return the total exterior aperture area in m².
        exterior_wall_aperture_area: Return the exterior wall aperture area in m².
        exterior_skylight_aperture_area: Return the exterior skylight aperture area in m².
        return_count: If True, return counts instead of identifier lists for objects.
            (Default: False)
    
    Returns:
        dict: Dictionary containing requested properties. Each property is only
            included if its corresponding flag is True. Object queries return
            either {"identifiers": [...]} or {"count": N} based on return_count.
    
    Example:
        query_model(identifier=True, display_name=True, rooms=True)
        query_model(floor_area=True, volume=True)
        query_model(rooms=True, return_count=True)  # Returns count only
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
