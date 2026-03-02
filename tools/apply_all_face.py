import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .mcp_context import mcp
from tools.load_model import manager, auto_save_to_shared_memory

# --- Core Dependencies ---
from honeybee.boundarycondition import Outdoors
from honeybee.facetype import Wall
from honeybee.model import Model
from honeybee.room import Room
from honeybee.face import Face
from honeybee.aperture import Aperture
from honeybee.door import Door
from honeybee.shade import Shade
from honeybee.orientation import angles_from_num_orient, face_orient_index

# --- Library Dependencies ---
try:
    from honeybee_energy.lib.constructions import opaque_construction_by_identifier, \
        window_construction_by_identifier, shade_construction_by_identifier
except ImportError:
    pass

try:
    from honeybee_radiance.lib.modifiers import modifier_by_identifier
except ImportError:
    pass


# ==============================================================================
# 1. SHARED HELPER FUNCTIONS 
# ==============================================================================

def _is_exterior_wall(face):
    """Check if a Face is an exterior Wall (for filtering Room children)."""
    return isinstance(face.boundary_condition, Outdoors) and isinstance(face.type, Wall)


def _get_model_objects(identifier_list, obj_type_class):
    """
    Retrieves objects by ID from the global model. 
    Searches both Room children and Orphaned objects.
    """
    if not identifier_list: return []
    if not manager.model: raise ValueError("Model is not loaded.")
    
    found_objs = []
    ids_set = set(identifier_list)
    
    # Search Hierarchy
    for room in manager.model.rooms:
        if obj_type_class == Room:
            if room.identifier in ids_set: found_objs.append(room)
            continue
            
        # If looking for geometry, search inside rooms
        for face in room.faces:
            if obj_type_class == Face and face.identifier in ids_set:
                found_objs.append(face)
            
            if obj_type_class in [Aperture, Door, Shade]:
                if obj_type_class == Aperture:
                    for ap in face.apertures:
                        if ap.identifier in ids_set: found_objs.append(ap)
                elif obj_type_class == Door:
                    for dr in face.doors:
                        if dr.identifier in ids_set: found_objs.append(dr)
                
                # Shades are everywhere
                if obj_type_class == Shade:
                    for shd in face.shades:
                        if shd.identifier in ids_set: found_objs.append(shd)
                    for ap in face.apertures:
                        for shd in ap.shades:
                            if shd.identifier in ids_set: found_objs.append(shd)
                    for dr in face.doors:
                        for shd in dr.shades:
                            if shd.identifier in ids_set: found_objs.append(shd)
        
        if obj_type_class == Shade:
            for shd in room.shades:
                if shd.identifier in ids_set: found_objs.append(shd)

    # Search Orphaned
    if obj_type_class == Face:
        for face in manager.model.orphaned_faces:
            if face.identifier in ids_set: found_objs.append(face)
    elif obj_type_class == Shade:
        for shd in manager.model.orphaned_shades:
            if shd.identifier in ids_set: found_objs.append(shd)
    
    return found_objs


def _apply_properties_by_orientation(targets, constructions, modifiers, prop_check_func, get_children_func):
    """
    Core engine: Applies attributes to targets/children based on Single vs Orientation logic.
    """
    updated = 0
    
    def _set_props(obj, c, m):
        did_set = False
        if c and hasattr(obj.properties.energy, 'construction'):
            obj.properties.energy.construction = c
            did_set = True
        if m and hasattr(obj.properties.radiance, 'modifier'):
            obj.properties.radiance.modifier = m
            did_set = True
        return 1 if did_set else 0

    # CASE A: Single Assignment (1 material -> All)
    if (constructions and len(constructions) == 1) or (modifiers and len(modifiers) == 1):
        c_single = constructions[0] if constructions else None
        m_single = modifiers[0] if modifiers else None
        
        for obj in targets:
            if prop_check_func(obj):
                updated += _set_props(obj, c_single, m_single)
            
            for child in get_children_func(obj):
                updated += _set_props(child, c_single, m_single)

    # CASE B: Orientation Assignment (>1 material -> N/E/S/W)
    else:
        count = max(len(constructions) if constructions else 0, len(modifiers) if modifiers else 0)
        angles = angles_from_num_orient(count)
        
        for obj in targets:
            # Main Object Orientation (Direct assignment)
            if prop_check_func(obj):
                orient_i = face_orient_index(obj, angles)
                if orient_i is not None:
                    c = constructions[orient_i] if constructions else None
                    m = modifiers[orient_i] if modifiers else None
                    updated += _set_props(obj, c, m)

            # Children Orientation (Iterate children and check THEIR orientation)
            for child in get_children_func(obj):
                orient_i = face_orient_index(child, angles)
                if orient_i is not None:
                    c = constructions[orient_i] if constructions else None
                    m = modifiers[orient_i] if modifiers else None
                    updated += _set_props(child, c, m)
    
    return updated


# ==============================================================================
# TOOL 1: OPAQUE ATTRIBUTES (Wall/Floor/Roof/Door)
# ==============================================================================
@mcp.tool()
def apply_opaque_attributes(
    construction_identifiers: list = None,
    modifier_identifiers: list = None,
    face_identifiers: list = None,
    door_identifiers: list = None,
    room_identifiers: list = None
) -> dict:
    """
    Apply Opaque Constructions (Energy) or Modifiers (Radiance).
    
    Applies opaque constructions and/or modifiers to faces, doors, or exterior walls. Supports orientation-based assignment.
    """
    if not manager.model: raise ValueError("Model is not loaded.")
    
    # Load Library Objects
    constrs = [opaque_construction_by_identifier(cid) for cid in construction_identifiers] if construction_identifiers else []
    mods = [modifier_by_identifier(mid) for mid in modifier_identifiers] if modifier_identifiers else []

    if not constrs and not mods:
        return {"status": "skipped", "message": "No constructions or modifiers provided."}

    # Resolve Targets
    t_faces = _get_model_objects(face_identifiers, Face)
    t_doors = _get_model_objects(door_identifiers, Door)
    t_rooms = _get_model_objects(room_identifiers, Room)
    
    # Default to all rooms if nothing selected
    if not any([face_identifiers, door_identifiers, room_identifiers]):
        t_rooms = list(manager.model.rooms)

    all_targets = t_faces + t_doors + t_rooms

    def _can_have_props(obj):
        return isinstance(obj, (Face, Door))

    def _get_children(obj):
        # Rooms -> Exterior Walls only
        if isinstance(obj, Room):
            return [f for f in obj.faces if _is_exterior_wall(f)]
        return []

    updated = _apply_properties_by_orientation(all_targets, constrs, mods, _can_have_props, _get_children)
    result = {"status": "success", "updated_count": updated}
    
    auto_save_result = auto_save_to_shared_memory()
    if auto_save_result:
        result["auto_save"] = auto_save_result
    
    return result


# ==============================================================================
# TOOL 2: WINDOW ATTRIBUTES (Aperture/GlassDoor)
# ==============================================================================
@mcp.tool()
def apply_window_attributes(
    construction_identifiers: list = None,
    modifier_identifiers: list = None,
    aperture_identifiers: list = None,
    door_identifiers: list = None,
    face_identifiers: list = None,
    room_identifiers: list = None
) -> dict:
    """
    Apply Window Constructions (Energy) or Modifiers (Radiance).
    
    Applies window constructions and/or modifiers to apertures, glass doors, or child apertures. Supports orientation-based assignment.
    """
    if not manager.model: raise ValueError("Model is not loaded.")

    constrs = [window_construction_by_identifier(cid) for cid in construction_identifiers] if construction_identifiers else []
    mods = [modifier_by_identifier(mid) for mid in modifier_identifiers] if modifier_identifiers else []

    if not constrs and not mods:
        return {"status": "skipped", "message": "No constructions or modifiers provided."}

    t_aps = _get_model_objects(aperture_identifiers, Aperture)
    t_drs = _get_model_objects(door_identifiers, Door)
    t_faces = _get_model_objects(face_identifiers, Face)
    t_rooms = _get_model_objects(room_identifiers, Room)
    
    if not any([aperture_identifiers, door_identifiers, face_identifiers, room_identifiers]):
        t_rooms = list(manager.model.rooms)

    all_targets = t_aps + t_drs + t_faces + t_rooms

    def _can_have_props(obj):
        return isinstance(obj, (Aperture, Door))

    def _get_children(obj):
        if isinstance(obj, Face):
            return list(obj.apertures)
        elif isinstance(obj, Room):
            # Rooms -> Exterior Wall -> Apertures
            aps = []
            for f in obj.faces:
                if _is_exterior_wall(f):
                    aps.extend(list(f.apertures))
            return aps
        return []

    updated = _apply_properties_by_orientation(all_targets, constrs, mods, _can_have_props, _get_children)
    result = {"status": "success", "updated_count": updated}
    
    auto_save_result = auto_save_to_shared_memory()
    if auto_save_result:
        result["auto_save"] = auto_save_result
    
    return result


# ==============================================================================
# TOOL 3: SHADE ATTRIBUTES (Shade)
# ==============================================================================
@mcp.tool()
def apply_shade_attributes(
    construction_identifiers: list = None,
    modifier_identifiers: list = None,
    shade_identifiers: list = None,
    aperture_identifiers: list = None,
    door_identifiers: list = None,
    face_identifiers: list = None,
    room_identifiers: list = None
) -> dict:
    """
    Apply Shade Constructions (Energy) or Modifiers (Radiance).
    
    Applies shade constructions and/or modifiers to shading elements. Supports orientation-based assignment.
    """
    if not manager.model: raise ValueError("Model is not loaded.")

    constrs = [shade_construction_by_identifier(cid) for cid in construction_identifiers] if construction_identifiers else []
    mods = [modifier_by_identifier(mid) for mid in modifier_identifiers] if modifier_identifiers else []

    if not constrs and not mods:
        return {"status": "skipped", "message": "No constructions or modifiers provided."}

    t_shds = _get_model_objects(shade_identifiers, Shade)
    t_aps = _get_model_objects(aperture_identifiers, Aperture)
    t_drs = _get_model_objects(door_identifiers, Door)
    t_faces = _get_model_objects(face_identifiers, Face)
    t_rooms = _get_model_objects(room_identifiers, Room)

    if not any([shade_identifiers, aperture_identifiers, door_identifiers, face_identifiers, room_identifiers]):
        t_rooms = list(manager.model.rooms)
        t_shds.extend(manager.model.orphaned_shades)

    all_targets = t_shds + t_aps + t_drs + t_faces + t_rooms

    def _can_have_props(obj):
        return isinstance(obj, Shade)

    def _get_children(obj):
        # Recursively gather all attached shades
        shades = []
        if hasattr(obj, 'shades'):
            shades.extend(list(obj.shades))
        
        if isinstance(obj, Face):
            for ap in obj.apertures: shades.extend(list(ap.shades))
            for dr in obj.doors: shades.extend(list(dr.shades))
            
        elif isinstance(obj, Room):
            for f in obj.faces:
                shades.extend(list(f.shades))
                for ap in f.apertures: shades.extend(list(ap.shades))
                for dr in f.doors: shades.extend(list(dr.shades))
        return shades

    updated = _apply_properties_by_orientation(all_targets, constrs, mods, _can_have_props, _get_children)
    result = {"status": "success", "updated_count": updated}
    
    auto_save_result = auto_save_to_shared_memory()
    if auto_save_result:
        result["auto_save"] = auto_save_result
    
    return result