from ..mcp_context import mcp
from ..state.hooks import ensure_model_loaded
from importlib import import_module


REMOVE_REGISTRY = {
    "all_apertures": (".remove_service", "remove_all_apertures_impl"),
    "all_doors": (".remove_service", "remove_all_doors_impl"),
    "all_shades": (".remove_service", "remove_all_shades_impl"),
    "face_objects": (".remove_service", "remove_face_objects_impl"),
    "room_shades": (".remove_service", "remove_room_shades_impl"),
    "process_loads": (".energy_resource_service", "remove_process_loads_impl"),
    "schedule": (".energy_resource_service", "remove_schedule_resources_impl"),
    "schedule_day": (".energy_resource_service", "remove_schedule_resources_impl"),
    "schedule_type_limit": (".energy_resource_service", "remove_schedule_resources_impl"),
    "modifier": (".radiance_resource_service", "remove_modifier_resources_impl"),
    "modifier_set": (".radiance_resource_service", "remove_modifier_resources_impl"),
    "sensor_grid": (".radiance_resource_service", "remove_sensor_grids_impl"),
    "view": (".radiance_resource_service", "remove_views_impl"),
}


def _with_identifiers(operation: str, identifiers, options: dict):
    kwargs = dict(options or {})
    if identifiers is None:
        return kwargs
    if operation == "all_apertures":
        kwargs["aperture_ids"] = identifiers
    elif operation == "all_doors":
        kwargs["door_ids"] = identifiers
    elif operation == "all_shades":
        kwargs["shade_ids"] = identifiers
    elif operation == "face_objects":
        kwargs["face_identifiers"] = identifiers
    elif operation == "room_shades":
        kwargs["room_identifiers"] = identifiers
    elif operation == "process_loads":
        kwargs["room_identifiers"] = identifiers
    elif operation == "schedule":
        kwargs["schedule_ids"] = identifiers
    elif operation == "schedule_day":
        kwargs["schedule_day_ids"] = identifiers
    elif operation == "schedule_type_limit":
        kwargs["schedule_type_limit_ids"] = identifiers
    elif operation == "modifier":
        kwargs["modifier_ids"] = identifiers
    elif operation == "modifier_set":
        kwargs["modifier_set_ids"] = identifiers
    elif operation == "sensor_grid":
        kwargs["sensor_grid_ids"] = identifiers
    elif operation == "view":
        kwargs["view_ids"] = identifiers
    return kwargs


@mcp.tool()
def remove(
    operation: str,
    identifiers: list = None,
    options: dict = None,
) -> dict:
    """
    Unified remove bus for Honeybee object deletion.
    """
    ensure_model_loaded()
    registry_entry = REMOVE_REGISTRY.get(operation)
    if registry_entry is None:
        return {
            "success": False,
            "error": "Unknown remove operation '{}'".format(operation),
            "available_operations": sorted(REMOVE_REGISTRY.keys()),
        }

    module_name, func_name = registry_entry
    module = import_module(module_name, package=__package__)
    func = getattr(module, func_name)
    kwargs = _with_identifiers(operation, identifiers, options)
    return func(**kwargs)
