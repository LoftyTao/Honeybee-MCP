from ..mcp_context import mcp
from ..state.hooks import ensure_model_loaded
from importlib import import_module


def _with_identifiers(target_type: str, identifiers, values: dict):
    kwargs = dict(values or {})
    if identifiers is None:
        return kwargs

    mapping = {
        "room": "room_identifiers",
        "face": "face_identifiers",
        "aperture": "aperture_identifiers",
        "door": "door_identifiers",
        "shade": "shade_identifiers",
        "subface": "aperture_identifiers",
        "schedule": "schedule_identifiers",
        "schedule_day": "schedule_day_identifiers",
        "schedule_type_limit": "schedule_type_limit_identifiers",
        "modifier": "modifier_identifiers",
        "modifier_set": "modifier_set_identifiers",
        "sensor_grid": "sensor_grid_identifiers",
        "view": "view_identifiers",
    }
    identifier_key = mapping.get(target_type)
    if identifier_key:
        kwargs[identifier_key] = identifiers
    return kwargs


APPLY_REGISTRY = {
    "room_attributes": (".apply_service", "apply_room_attributes_impl"),
    "hvac": (".apply_service", "apply_hvac_impl"),
    "opaque_attributes": (".apply_service", "apply_opaque_attributes_impl"),
    "window_attributes": (".apply_service", "apply_window_attributes_impl"),
    "shade_attributes": (".apply_service", "apply_shade_attributes_impl"),
    "people": (".energy_resource_service", "apply_people_impl"),
    "lighting": (".energy_resource_service", "apply_lighting_impl"),
    "electric_equipment": (".energy_resource_service", "apply_electric_equipment_impl"),
    "service_hot_water": (".energy_resource_service", "apply_service_hot_water_impl"),
    "setpoint": (".energy_resource_service", "apply_setpoint_impl"),
    "ventilation": (".energy_resource_service", "apply_ventilation_impl"),
    "process_load": (".energy_resource_service", "apply_process_load_impl"),
    "schedule_type_limit": (".energy_resource_service", "apply_schedule_type_limit_impl"),
    "schedule_day": (".energy_resource_service", "apply_schedule_day_impl"),
    "schedule_ruleset": (".energy_resource_service", "apply_schedule_ruleset_impl"),
    "schedule_fixed_interval": (".energy_resource_service", "apply_schedule_fixed_interval_impl"),
    "modifier": (".radiance_resource_service", "apply_modifier_impl"),
    "modifier_set": (".radiance_resource_service", "apply_modifier_set_impl"),
    "sensor_grid": (".radiance_resource_service", "apply_sensor_grid_impl"),
    "view": (".radiance_resource_service", "apply_view_impl"),
}


@mcp.tool()
def apply(
    operation: str,
    target_type: str,
    identifiers: list = None,
    values: dict = None,
) -> dict:
    """
    Unified apply bus for Honeybee, Energy, and Radiance attributes.
    """
    ensure_model_loaded()
    registry_entry = APPLY_REGISTRY.get(operation)
    if registry_entry is None:
        return {
            "success": False,
            "error": "Unknown apply operation '{}'".format(operation),
            "available_operations": sorted(APPLY_REGISTRY.keys()),
        }

    module_name, func_name = registry_entry
    module = import_module(module_name, package=__package__)
    func = getattr(module, func_name)
    kwargs = _with_identifiers(target_type, identifiers, values)
    return func(**kwargs)
