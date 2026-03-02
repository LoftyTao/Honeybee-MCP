import sys
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .mcp_context import mcp
from tools.load_model import manager, auto_save_to_shared_memory

from honeybee.typing import clean_and_id_ep_string
from honeybee.altnumber import autosize, no_limit
from honeybee_energy.lib.schedules import schedule_by_identifier

# Import HVAC Classes
from honeybee_energy.hvac.idealair import IdealAirSystem
from honeybee_energy.hvac.allair import EQUIPMENT_TYPES_DICT as AA_TYPES
from honeybee_energy.hvac.doas import EQUIPMENT_TYPES_DICT as DOAS_TYPES
from honeybee_energy.hvac.heatcool import EQUIPMENT_TYPES_DICT as HC_TYPES
from honeybee_energy.shw import SHWSystem


def _load_registry():
    """Loads the external JSON configuration for HVAC types and vintages."""
    json_path = os.path.join(current_dir, 'hvac_config.json')
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"HVAC configuration file not found at: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load registry once at module level
REGISTRY = _load_registry()
VINTAGE_MAPPING = REGISTRY.get('vintages', {})
HVAC_MAPPINGS = REGISTRY.get('mappings', {})

# Valid Radiant Types
VALID_RADIANT_TYPES = [
    "Floor", "Ceiling", "FloorWithCarpet", "CeilingMetalPanel", "FloorWithHardwood"
]


def _parse_alt_number(value):
    if value is None: return None
    str_val = str(value).lower().strip()
    if str_val == 'autosize': return autosize
    elif str_val == 'nolimit': return no_limit
    try: return float(value)
    except ValueError:
        raise ValueError(f"Invalid limit: '{value}'. Expected number, 'Autosize', or 'NoLimit'.")

def _parse_shw_condition(value, room_map):
    if value is None: return 22.0
    try: return float(value)
    except (ValueError, TypeError): pass
    str_val = str(value)
    return str_val if str_val in room_map else str_val

def _get_target_rooms(room_identifiers):
    if not manager.model: raise ValueError("Model is not loaded.")
    if room_identifiers:
        room_map = {r.identifier: r for r in manager.model.rooms}
        return [room_map[rid] for rid in room_identifiers if rid in room_map]
    return list(manager.model.rooms)

def _get_hvac_class_and_key(category, system_type):
    if category not in HVAC_MAPPINGS:
        raise ValueError(f"Unknown category '{category}'")
    
    mapping = HVAC_MAPPINGS[category]
    sys_key = mapping.get(system_type, system_type)
    
    if category == "SHW":
        if sys_key not in mapping.values() and sys_key not in mapping:
             raise ValueError(f"SHW Type '{system_type}' not found in library.")
        return SHWSystem, sys_key

    type_dict = None
    if category == "AllAir": type_dict = AA_TYPES
    elif category == "DOAS": type_dict = DOAS_TYPES
    elif category == "HeatCool": type_dict = HC_TYPES
    
    if sys_key not in type_dict:
        raise ValueError(f"System Type '{system_type}' not found in {category} library.")
        
    return type_dict[sys_key], sys_key


@mcp.tool()
def apply_hvac(
    system_category: str = "Ideal", 
    system_type: str = None,
    vintage: str = "ASHRAE_2019",
    name: str = None,
    room_identifiers: list = None,
    list_options: bool = False,
    economizer_type: str = None,
    sensible_heat_recovery: float = None,
    latent_heat_recovery: float = None,
    demand_controlled_ventilation: bool = False,
    heating_air_temperature: float = None,
    cooling_air_temperature: float = None,
    heating_limit: str = None,
    cooling_limit: str = None,
    heating_availability_schedule: str = None,
    cooling_availability_schedule: str = None,
    doas_availability_schedule: str = None,
    shw_efficiency: float = None,
    shw_ambient_condition: str = None,
    shw_loss_coefficient: float = None,
    radiant_type: str = None,
    radiant_switch_over_time: float = None
) -> dict:
    """
    Unified tool to apply ANY HVAC system (Ideal, AllAir, DOAS, HeatCool, SHW) to rooms.
    
    Supports Ideal Air, All-Air (VAV, PVAV), DOAS, Radiant systems, and Service Hot Water.
    """
    
    valid_cats = ["AllAir", "DOAS", "HeatCool", "SHW"]

    if list_options:
        if system_category == "Ideal":
            return {"status": "info", "message": "Ideal Air System does not have subtypes."}
        
        if system_category not in valid_cats:
            return {"status": "error", "message": f"Invalid category. Choose from: {valid_cats}"}
            
        cat_mapping = HVAC_MAPPINGS.get(system_category, {})
        vintages = sorted(list(set(VINTAGE_MAPPING.keys()) - {None, "null"}))
        
        return {
            "status": "info", 
            "category": system_category,
            "available_types": list(cat_mapping.keys()),
            "available_vintages": vintages,
            "available_radiant_types": VALID_RADIANT_TYPES
        }

    if not manager.model: raise ValueError("Model is not loaded.")
    
    target_rooms = _get_target_rooms(room_identifiers)
    
    selected_vintage = VINTAGE_MAPPING.get(vintage, vintage)
    if selected_vintage == "null": selected_vintage = "ASHRAE_2019"
    
    heat_sch = schedule_by_identifier(heating_availability_schedule) if heating_availability_schedule else None
    cool_sch = schedule_by_identifier(cooling_availability_schedule) if cooling_availability_schedule else None
    doas_sch = schedule_by_identifier(doas_availability_schedule) if doas_availability_schedule else None

    # Validate Radiant Type
    if radiant_type and radiant_type not in VALID_RADIANT_TYPES:
        raise ValueError(f"Invalid radiant_type '{radiant_type}'. Options: {VALID_RADIANT_TYPES}")

    updated_count = 0
    warnings = []
    vent_schedules = set()
    no_setpoint_rooms = []
    final_hvac_name = ""
    final_sys_key = "IdealAirSystem"

    # --- BRANCH A: IDEAL AIR ---
    if system_category.lower() == "ideal":
        for room in target_rooms:
            if not room.properties.energy.is_conditioned: continue
            
            if not isinstance(room.properties.energy.hvac, IdealAirSystem):
                room.properties.energy.add_default_ideal_air()
            
            hvac_obj = room.properties.energy.hvac.duplicate()
            
            if economizer_type: hvac_obj.economizer_type = economizer_type
            if sensible_heat_recovery is not None: hvac_obj.sensible_heat_recovery = sensible_heat_recovery
            if latent_heat_recovery is not None: hvac_obj.latent_heat_recovery = latent_heat_recovery
            if demand_controlled_ventilation is not None: hvac_obj.demand_controlled_ventilation = demand_controlled_ventilation
            if heating_air_temperature: hvac_obj.heating_air_temperature = heating_air_temperature
            if cooling_air_temperature: hvac_obj.cooling_air_temperature = cooling_air_temperature
            if heating_limit: hvac_obj.heating_limit = _parse_alt_number(heating_limit)
            if cooling_limit: hvac_obj.cooling_limit = _parse_alt_number(cooling_limit)
            if heat_sch: hvac_obj.heating_availability = heat_sch
            if cool_sch: hvac_obj.cooling_availability = cool_sch
            if name: hvac_obj.display_name = name

            room.properties.energy.hvac = hvac_obj
            updated_count += 1
        
        final_hvac_name = "Custom Ideal Air"

    # --- BRANCH B: SHW SYSTEMS ---
    elif system_category == "SHW":
        if not system_type: raise ValueError(f"system_type is required for {system_category}")
        _, final_sys_key = _get_hvac_class_and_key("SHW", system_type)
        sys_id_base = name if name else f"SHW_{final_sys_key}"
        sys_id = clean_and_id_ep_string(sys_id_base)
        
        room_map_full = {r.identifier: r for r in manager.model.rooms}
        cond = _parse_shw_condition(shw_ambient_condition, room_map_full)
        loss_coeff = shw_loss_coefficient if shw_loss_coefficient is not None else 6.0
        
        shw_obj = SHWSystem(
            identifier=sys_id, 
            equipment_type=final_sys_key, 
            heater_efficiency=shw_efficiency, 
            ambient_condition=cond, 
            ambient_loss_coefficient=loss_coeff
        )
        if name: shw_obj.display_name = name
        final_hvac_name = shw_obj.display_name

        skipped_no_load = 0
        for room in target_rooms:
            if room.properties.energy.service_hot_water is not None:
                room.properties.energy.shw = shw_obj
                updated_count += 1
            else:
                skipped_no_load += 1
        
        if skipped_no_load > 0:
            warnings.append(f"{skipped_no_load} rooms skipped (no SHW load).")

    # --- BRANCH C: TEMPLATE HVAC (AllAir, DOAS, HeatCool) ---
    else:
        if not system_type: raise ValueError(f"system_type is required for {system_category}")
        
        HvacClass, final_sys_key = _get_hvac_class_and_key(system_category, system_type)
        sys_id_base = name if name else f"{system_category}_{final_sys_key}"
        sys_id = clean_and_id_ep_string(sys_id_base)
        
        hvac_obj = HvacClass(identifier=sys_id, vintage=selected_vintage, equipment_type=final_sys_key)
        
        # 1. Apply Standard Properties
        if name: hvac_obj.display_name = name
        if sensible_heat_recovery is not None: hvac_obj.sensible_heat_recovery = sensible_heat_recovery
        if latent_heat_recovery is not None: hvac_obj.latent_heat_recovery = latent_heat_recovery
        
        # 2. Apply Category Specifics
        if system_category == "AllAir":
            if economizer_type: hvac_obj.economizer_type = economizer_type
            if demand_controlled_ventilation: hvac_obj.demand_controlled_ventilation = True
        
        elif system_category == "DOAS":
            if demand_controlled_ventilation: hvac_obj.demand_controlled_ventilation = True
            if doas_sch: hvac_obj.doas_availability_schedule = doas_sch
            
        # 3. Apply Radiant Specifics (Duck Typing for Safety)
        # This works for both Radiant (HeatCool) and RadiantwithDOAS
        if radiant_type:
            if hasattr(hvac_obj, 'radiant_type'):
                hvac_obj.radiant_type = radiant_type
            else:
                warnings.append(f"radiant_type ignored: System '{final_sys_key}' is not a radiant system.")

        if radiant_switch_over_time is not None:
            if hasattr(hvac_obj, 'switch_over_time'):
                hvac_obj.switch_over_time = radiant_switch_over_time
            else:
                warnings.append(f"radiant_switch_over_time ignored: System '{final_sys_key}' does not support it.")

        final_hvac_name = hvac_obj.display_name

        for room in target_rooms:
            if room.properties.energy.is_conditioned:
                room.properties.energy.hvac = hvac_obj
                updated_count += 1
                
                if room.properties.energy.setpoint is None:
                    no_setpoint_rooms.append(room.display_name)
                
                vent_obj = room.properties.energy.ventilation
                if vent_obj is not None:
                    if hasattr(vent_obj, 'schedule') and vent_obj.schedule is not None:
                         vent_schedules.add(vent_obj.schedule.identifier)

        if system_category in ["AllAir", "DOAS"] and len(vent_schedules) > 1:
            warnings.append("Central system applied to rooms with differing ventilation schedules.")
        if no_setpoint_rooms:
            warnings.append(f"Rooms without setpoints: {', '.join(no_setpoint_rooms)}")

    if updated_count == 0:
        return {"status": "skipped", "message": "No valid target rooms found."}

    result = {
        "status": "success",
        "category": system_category,
        "system_type": final_sys_key,
        "system_name": final_hvac_name,
        "updated_room_count": updated_count,
        "warnings": warnings if warnings else None
    }
    
    auto_save_result = auto_save_to_shared_memory()
    if auto_save_result:
        result["auto_save"] = auto_save_result
    
    return result