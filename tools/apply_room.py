import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .mcp_context import mcp
from tools.load_model import manager

# Import library functions
from honeybee_energy.lib.constructionsets import construction_set_by_identifier
from honeybee_radiance.lib.modifiersets import modifier_set_by_identifier
from honeybee_energy.lib.programtypes import program_type_by_identifier, \
    building_program_type_by_identifier


@mcp.tool()
def apply_room_attributes(
    construction_set_identifier: str = None,
    modifier_set_identifier: str = None,
    program_type_identifier: str = None,
    is_conditioned: bool = None,
    reset_loads: bool = False,
    room_identifiers: list = None
) -> dict:
    """
    Apply Construction Set, Modifier Set, Program Type, or conditioning status to specific rooms.
    
    This tool applies energy and radiance properties to rooms. You can apply one or
    multiple attributes in a single call. Use search_properties to find available
    construction sets, modifier sets, and program types.
    
    Args:
        construction_set_identifier: Name of the Construction Set to apply.
            Construction sets define wall, floor, roof, and window constructions.
            Use search_properties with category="ConstructionSet" to find options.
        modifier_set_identifier: Name of the Modifier Set to apply for Radiance.
            Modifier sets define material properties for daylight simulation.
            Use search_properties with category="ModifierSet" to find options.
        program_type_identifier: Name of the Program Type to apply.
            Program types define loads, schedules, and setpoints for the space.
            Use search_properties with category="ProgramType" to find options.
        is_conditioned: Control HVAC conditioning status:
            - True: Add default Ideal Air system to unconditioned rooms
            - False: Remove HVAC system (make room unconditioned)
            - None: Do not change conditioning status
        reset_loads: If True and program_type_identifier is set, reset all room
            loads (people, lighting, equipment, etc.) to match the program type.
            If False, existing overridden loads are preserved. Default is False.
        room_identifiers: List of room IDs to apply changes to. If None or empty,
            applies to all rooms in the model.
    
    Returns:
        dict: Dictionary containing:
            - status (str): "success" or "skipped"
            - updated_room_count (int): Number of rooms modified
            - conditioning_changes (int): Number of rooms with HVAC changes
            - applied_attributes (dict): Attributes that were applied
            - warnings (list): Any warnings about overridden loads
            - target_scope (str): "specific_rooms" or "all_rooms"
    
    Example:
        apply_room_attributes(program_type_identifier="Office_Open")
        apply_room_attributes(construction_set_identifier="Default", room_identifiers=["Room_1"])
        apply_room_attributes(is_conditioned=True, reset_loads=True)
    """
    if not manager.model:
        raise ValueError("Model is not loaded.")

    # Check if any action is requested
    if all(v is None for v in [construction_set_identifier, modifier_set_identifier, 
                               program_type_identifier, is_conditioned]):
        return {
            "status": "skipped",
            "message": "No attributes provided to apply."
        }

    # --- 1. Pre-fetch and Validate Library Objects ---
    con_set = None
    mod_set = None
    prog_type = None

    # Resolve Construction Set
    if construction_set_identifier:
        con_set = construction_set_by_identifier(construction_set_identifier)
        if not con_set:
            raise ValueError(f"Construction Set '{construction_set_identifier}' not found.")

    # Resolve Modifier Set
    if modifier_set_identifier:
        mod_set = modifier_set_by_identifier(modifier_set_identifier)
        if not mod_set:
            raise ValueError(f"Modifier Set '{modifier_set_identifier}' not found.")

    # Resolve Program Type
    if program_type_identifier:
        try:
            prog_type = building_program_type_by_identifier(program_type_identifier)
        except ValueError:
            try:
                prog_type = program_type_by_identifier(program_type_identifier)
            except ValueError:
                raise ValueError(f"Program Type '{program_type_identifier}' not found.")

    # --- 2. Determine Target Scope ---
    target_rooms = []
    if room_identifiers:
        room_map = {r.identifier: r for r in manager.model.rooms}
        for r_id in room_identifiers:
            if r_id in room_map:
                target_rooms.append(room_map[r_id])
    else:
        target_rooms = list(manager.model.rooms)

    # --- 3. Apply Attributes Loop ---
    warnings = []
    updated_conditioned_status = 0
    
    for room in target_rooms:
        # --- A. Apply Conditioning Status (First Priority) ---
        if is_conditioned is not None:
            if is_conditioned:
                # Turn ON conditioning
                # Only add default ideal air if it's not already conditioned
                # This prevents overwriting an existing VAV/DOAS system if the user just wanted to ensure it's ON
                if not room.properties.energy.is_conditioned:
                    room.properties.energy.add_default_ideal_air()
                    updated_conditioned_status += 1
            else:
                # Turn OFF conditioning
                # Setting hvac to None removes the system completely
                if room.properties.energy.is_conditioned:
                    room.properties.energy.hvac = None
                    updated_conditioned_status += 1

        # --- B. Apply Construction Set ---
        if con_set:
            room.properties.energy.construction_set = con_set
        
        # --- C. Apply Modifier Set ---
        if mod_set:
            room.properties.radiance.modifier_set = mod_set

        # --- D. Apply Program Type ---
        if prog_type:
            room.properties.energy.program_type = prog_type
            
            if reset_loads:
                room.properties.energy.reset_loads_to_program()
            elif room.properties.energy.has_overridden_loads:
                msg = (f"Room '{room.display_name}' has overridden loads. "
                       "Set reset_loads=True to force update.")
                warnings.append(msg)

    # --- 4. Construct Return Object ---
    return {
        "status": "success",
        "updated_room_count": len(target_rooms),
        "conditioning_changes": updated_conditioned_status if is_conditioned is not None else 0,
        "applied_attributes": {
            "is_conditioned": is_conditioned,
            "construction_set": con_set.identifier if con_set else None,
            "modifier_set": mod_set.identifier if mod_set else None,
            "program_type": prog_type.identifier if prog_type else None
        },
        "warnings": warnings if warnings else None,
        "target_scope": "specific_rooms" if room_identifiers else "all_rooms"
    }