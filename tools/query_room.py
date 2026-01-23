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
def query_room(
    room_identifiers: list[str] = None,
    general_properties: bool = False,
    load_properties: bool = False,
    schedule_properties: bool = False,
    setpoint_properties: bool = False,
    hvac_properties: bool = False,
    radiance_properties: bool = False
) -> dict:
    """
    Query detailed Energy and Radiance attributes for specific rooms.
    
    Args:
        room_identifiers: List of room IDs to query. If None, queries all rooms.
        general_properties: Includes Program, Construction Set, Is Conditioned.
        load_properties: Includes People, Lighting, Equipment, Ventilation, Infiltration densities.
        schedule_properties: Includes all operation schedules (Occupancy, Lighting, HVAC, etc.).
        setpoint_properties: Includes Heating/Cooling setpoints, setbacks, and humidity thresholds.
        hvac_properties: Includes HVAC type, system names, efficiencies, and SHW.
        radiance_properties: Includes Modifier Set.
    """
    if not manager.model:
        raise ValueError("Model is not loaded.")

    # Determine target rooms
    target_rooms = []
    if room_identifiers:
        room_map = {r.identifier: r for r in manager.model.rooms}
        for r_id in room_identifiers:
            if r_id in room_map:
                target_rooms.append(room_map[r_id])
    else:
        target_rooms = list(manager.model.rooms)

    results = {}

    for room in target_rooms:
        room_data = {}

        # 1. General Energy Properties
        if general_properties:
            room_data.update({
                "program_type": _get_nested_attr(room, "properties.energy.program_type.display_name"),
                "construction_set": _get_nested_attr(room, "properties.energy.construction_set.display_name"),
                "is_conditioned": _get_nested_attr(room, "properties.energy.is_conditioned")
            })

        # 2. Load Properties (Densities & Flow)
        if load_properties:
            room_data.update({
                "people_per_area": _get_nested_attr(room, "properties.energy.people.people_per_area"),
                "area_per_person": _get_nested_attr(room, "properties.energy.people.area_per_person"),
                "lighting_per_area": _get_nested_attr(room, "properties.energy.lighting.watts_per_area"),
                "electric_equipment_per_area": _get_nested_attr(room, "properties.energy.electric_equipment.watts_per_area"),
                "gas_equipment_per_area": _get_nested_attr(room, "properties.energy.gas_equipment.watts_per_area"),
                "hot_water_per_area": _get_nested_attr(room, "properties.energy.service_hot_water.flow_per_area"),
                "infiltration_per_ext_area": _get_nested_attr(room, "properties.energy.infiltration.flow_per_exterior_area"),
                "ventilation_per_person": _get_nested_attr(room, "properties.energy.ventilation.flow_per_person"),
                "ventilation_per_area": _get_nested_attr(room, "properties.energy.ventilation.flow_per_area"),
                "ventilation_ach": _get_nested_attr(room, "properties.energy.ventilation.air_changes_per_hour"),
                "ventilation_absolute": _get_nested_attr(room, "properties.energy.ventilation.flow_per_zone"),
                "total_fan_flow": _get_nested_attr(room, "properties.energy.total_fan_flow"),
                "total_process_load": _get_nested_attr(room, "properties.energy.total_process_load")
            })

        # 3. Schedule Properties
        if schedule_properties:
            room_data.update({
                "occupancy_schedule": _get_nested_attr(room, "properties.energy.people.occupancy_schedule.display_name"),
                "activity_schedule": _get_nested_attr(room, "properties.energy.people.activity_schedule.display_name"),
                "lighting_schedule": _get_nested_attr(room, "properties.energy.lighting.schedule.display_name"),
                "electric_equipment_schedule": _get_nested_attr(room, "properties.energy.electric_equipment.schedule.display_name"),
                "gas_equipment_schedule": _get_nested_attr(room, "properties.energy.gas_equipment.schedule.display_name"),
                "hot_water_schedule": _get_nested_attr(room, "properties.energy.service_hot_water.schedule.display_name"),
                "infiltration_schedule": _get_nested_attr(room, "properties.energy.infiltration.schedule.display_name"),
                "ventilation_schedule": _get_nested_attr(room, "properties.energy.ventilation.schedule.display_name"),
                "heating_schedule": _get_nested_attr(room, "properties.energy.setpoint.heating_schedule.display_name"),
                "cooling_schedule": _get_nested_attr(room, "properties.energy.setpoint.cooling_schedule.display_name")
            })

        # 4. Setpoint Properties
        if setpoint_properties:
            room_data.update({
                "heating_setpoint": _get_nested_attr(room, "properties.energy.setpoint.heating_setpoint"),
                "cooling_setpoint": _get_nested_attr(room, "properties.energy.setpoint.cooling_setpoint"),
                "heating_setback": _get_nested_attr(room, "properties.energy.setpoint.heating_setback"),
                "cooling_setback": _get_nested_attr(room, "properties.energy.setpoint.cooling_setback"),
                "humidifying_setpoint": _get_nested_attr(room, "properties.energy.setpoint.humidifying_setpoint"),
                "dehumidifying_setpoint": _get_nested_attr(room, "properties.energy.setpoint.dehumidifying_setpoint")
            })

        # 5. HVAC & SHW Properties
        if hvac_properties:
            room_data.update({
                "hvac_type": _get_nested_attr(room, "properties.energy.hvac.__class__.__name__"),
                "hvac_equipment_type": _get_nested_attr(room, "properties.energy.hvac.equipment_type"),
                "hvac_name": _get_nested_attr(room, "properties.energy.hvac.display_name"),
                "economizer_type": _get_nested_attr(room, "properties.energy.hvac.economizer_type"),
                "demand_controlled_ventilation": _get_nested_attr(room, "properties.energy.hvac.demand_controlled_ventilation"),
                "sensible_heat_recovery": _get_nested_attr(room, "properties.energy.hvac.sensible_heat_recovery"),
                "latent_heat_recovery": _get_nested_attr(room, "properties.energy.hvac.latent_heat_recovery"),
                "shw_equipment_type": _get_nested_attr(room, "properties.energy.shw.equipment_type"),
                "shw_heater_efficiency": _get_nested_attr(room, "properties.energy.shw.heater_efficiency"),
                "shw_ambient_condition": _get_nested_attr(room, "properties.energy.shw.ambient_condition"),
                "shw_ambient_loss_coefficient": _get_nested_attr(room, "properties.energy.shw.ambient_loss_coefficient"),
                "daylight_illuminance_setpoint": _get_nested_attr(room, "properties.energy.daylighting_control.illuminance_setpoint"),
                "daylight_sensor_position": _get_nested_attr(room, "properties.energy.daylighting_control.sensor_position")
            })

        # 6. Radiance Properties
        if radiance_properties:
            room_data.update({
                "modifier_set": _get_nested_attr(room, "properties.radiance.modifier_set.display_name")
            })

        if room_data:
            results[room.identifier] = room_data

    return {
        "status": "success",
        "room_count": len(results),
        "data": results
    }