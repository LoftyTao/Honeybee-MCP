import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .mcp_context import mcp
from tools.load_model import manager

@mcp.tool()
def remove_room_shades(
    room_identifiers: list,
    indoor_shades: bool = True,
    outdoor_shades: bool = True
) -> dict:
    """
    Remove shades from specified rooms.
    """
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded. Please use load_model to load a model first."
        }

    # Validate that at least one shade type is selected
    if not indoor_shades and not outdoor_shades:
        return {
            "success": False,
            "message": "At least one of indoor_shades or outdoor_shades must be True."
        }

    results = []
    not_found = []

    # Process each room identifier in the list
    for room_id in room_identifiers:
        # Search for room in model's rooms collection
        room = None
        for r in manager.model.rooms:
            if r.identifier == room_id:
                room = r
                break

        # Handle case where room is not found
        if room is None:
            not_found.append(room_id)
            continue

        # Track how many shades were removed
        removed_count = 0

        # Remove indoor shades if requested
        if indoor_shades:
            removed_count += len(room.indoor_shades)
            room.remove_indoor_shades()

        # Remove outdoor shades if requested
        if outdoor_shades:
            removed_count += len(room.outdoor_shades)
            room.remove_outdoor_shades()

        # Build list of shade types removed for messaging
        shade_type = []
        if indoor_shades:
            shade_type.append("indoor")
        if outdoor_shades:
            shade_type.append("outdoor")

        # Add result for this room
        results.append({
            "room_identifier": room_id,
            "removed_count": removed_count,
            "shade_type": "、".join(shade_type)
        })

    return {
        "success": True,
        "message": f"Processed {len(results)} rooms, {len(not_found)} rooms not found.",
        "results": results,
        "not_found": not_found
    }
