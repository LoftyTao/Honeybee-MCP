from ..mcp_context import mcp
from ..state.hooks import ensure_model_loaded
from importlib import import_module


ADD_REGISTRY = {
    "aperture_by_width_height": (".add_service", "add_aperture_by_width_height_impl"),
    "apertures_by_ratio_rectangle": (".add_service", "add_apertures_by_ratio_rectangle_impl"),
    "apertures_by_ratio": (".add_service", "add_apertures_by_ratio_impl"),
    "apertures_by_ratio_gridded": (".add_service", "add_apertures_by_ratio_gridded_impl"),
    "apertures_by_width_height_rectangle": (".add_service", "add_apertures_by_width_height_rectangle_impl"),
    "louvers": (".add_service", "add_louvers_impl"),
    "louvers_by_count": (".add_service", "add_louvers_by_count_impl"),
    "louvers_by_distance_between": (".add_service", "add_louvers_by_distance_between_impl"),
    "schedule_type_limit": (".energy_resource_service", "add_schedule_type_limit_impl"),
    "schedule_day": (".energy_resource_service", "add_schedule_day_impl"),
    "schedule_ruleset": (".energy_resource_service", "add_schedule_ruleset_impl"),
    "schedule_fixed_interval": (".energy_resource_service", "add_schedule_fixed_interval_impl"),
    "process_load": (".energy_resource_service", "add_process_load_impl"),
    "modifier": (".radiance_resource_service", "add_modifier_impl"),
    "modifier_set": (".radiance_resource_service", "add_modifier_set_impl"),
    "sensor_grid": (".radiance_resource_service", "add_sensor_grid_impl"),
    "view": (".radiance_resource_service", "add_view_impl"),
}


def _with_identifiers(target_type: str, identifiers, params: dict):
    kwargs = dict(params or {})
    mapping = {
        "face": "face_identifiers",
        "aperture": "aperture_identifiers",
        "subface": "aperture_identifiers",
        "room": "room_identifiers",
    }
    identifier_key = mapping.get(target_type)
    if identifier_key and identifiers is not None:
        kwargs[identifier_key] = identifiers
    return kwargs


@mcp.tool()
def add(
    operation: str,
    target_type: str,
    identifiers: list = None,
    params: dict = None,
) -> dict:
    """
    Unified add bus for parameterized Honeybee object creation.
    """
    ensure_model_loaded()
    registry_entry = ADD_REGISTRY.get(operation)
    if registry_entry is None:
        return {
            "success": False,
            "error": "Unknown add operation '{}'".format(operation),
            "available_operations": sorted(ADD_REGISTRY.keys()),
        }

    module_name, func_name = registry_entry
    module = import_module(module_name, package=__package__)
    func = getattr(module, func_name)
    kwargs = _with_identifiers(target_type, identifiers, params)
    return func(**kwargs)
