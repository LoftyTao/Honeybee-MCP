from ..mcp_context import mcp
from ..state.hooks import ensure_model_loaded
from ..state.manager import manager
from .common import get_nested_attr, resolve_targets, serialize_value


def _identifier_list(items):
    return [item.identifier for item in items]


QUERY_FIELD_REGISTRY = {
    "model": {
        "identifier": lambda model: model.identifier,
        "display_name": lambda model: model.display_name,
        "rooms": lambda model: _identifier_list(model.rooms),
        "faces": lambda model: _identifier_list(model.faces),
        "apertures": lambda model: _identifier_list(model.apertures),
        "doors": lambda model: _identifier_list(model.doors),
        "shades": lambda model: _identifier_list(model.shades),
        "shade_meshes": lambda model: _identifier_list(model.shade_meshes),
        "indoor_shades": lambda model: _identifier_list(model.indoor_shades),
        "outdoor_shades": lambda model: _identifier_list(model.outdoor_shades),
        "orphaned_faces": lambda model: _identifier_list(model.orphaned_faces),
        "orphaned_shades": lambda model: _identifier_list(model.orphaned_shades),
        "orphaned_apertures": lambda model: _identifier_list(model.orphaned_apertures),
        "orphaned_doors": lambda model: _identifier_list(model.orphaned_doors),
        "stories": lambda model: model.stories,
        "volume": lambda model: model.volume,
        "floor_area": lambda model: model.floor_area,
        "exposed_area": lambda model: model.exposed_area,
        "exterior_wall_area": lambda model: model.exterior_wall_area,
        "exterior_roof_area": lambda model: model.exterior_roof_area,
        "exterior_aperture_area": lambda model: model.exterior_aperture_area,
        "exterior_wall_aperture_area": lambda model: model.exterior_wall_aperture_area,
        "exterior_skylight_aperture_area": lambda model: model.exterior_skylight_aperture_area,
    },
    "room": {
        "identifier": lambda room: room.identifier,
        "display_name": lambda room: room.display_name,
        "story": lambda room: room.story,
        "multiplier": lambda room: room.multiplier,
        "floor_area": lambda room: room.floor_area,
        "volume": lambda room: room.volume,
        "exposed_area": lambda room: room.exposed_area,
        "exterior_wall_area": lambda room: room.exterior_wall_area,
        "exterior_aperture_area": lambda room: room.exterior_aperture_area,
    },
    "face": {
        "identifier": lambda face: face.identifier,
        "display_name": lambda face: face.display_name,
        "type": lambda face: str(face.type),
        "boundary_condition": lambda face: str(face.boundary_condition),
        "apertures": lambda face: _identifier_list(face.apertures),
        "doors": lambda face: _identifier_list(face.doors),
        "sub_faces": lambda face: _identifier_list(face.sub_faces),
        "indoor_shades": lambda face: _identifier_list(face.indoor_shades),
        "outdoor_shades": lambda face: _identifier_list(face.outdoor_shades),
        "parent": lambda face: face.parent.identifier if face.parent else None,
        "has_parent": lambda face: face.has_parent,
        "has_sub_faces": lambda face: face.has_sub_faces,
        "can_be_ground": lambda face: face.can_be_ground,
        "geometry": lambda face: str(face.geometry),
        "punched_geometry": lambda face: str(face.punched_geometry),
        "vertices": lambda face: face.vertices,
        "punched_vertices": lambda face: face.punched_vertices,
        "upper_left_vertices": lambda face: face.upper_left_vertices,
        "normal": lambda face: face.normal,
        "center": lambda face: face.center,
        "area": lambda face: face.area,
        "perimeter": lambda face: face.perimeter,
        "min": lambda face: face.min,
        "max": lambda face: face.max,
        "aperture_area": lambda face: face.aperture_area,
        "aperture_ratio": lambda face: face.aperture_ratio,
        "tilt": lambda face: face.tilt,
        "altitude": lambda face: face.altitude,
        "azimuth": lambda face: face.azimuth,
        "is_exterior": lambda face: face.is_exterior,
        "type_color": lambda face: face.type_color,
        "bc_color": lambda face: face.bc_color,
    },
    "aperture": {
        "identifier": lambda aperture: aperture.identifier,
        "display_name": lambda aperture: aperture.display_name,
        "boundary_condition": lambda aperture: str(aperture.boundary_condition),
        "is_operable": lambda aperture: aperture.is_operable,
        "is_exterior": lambda aperture: aperture.is_exterior,
        "has_parent": lambda aperture: aperture.has_parent,
        "parent": lambda aperture: aperture.parent.identifier if aperture.parent else None,
        "top_level_parent": lambda aperture: aperture.top_level_parent.identifier if aperture.top_level_parent else None,
        "geometry": lambda aperture: str(aperture.geometry),
        "vertices": lambda aperture: aperture.vertices,
        "upper_left_vertices": lambda aperture: aperture.upper_left_vertices,
        "normal": lambda aperture: aperture.normal,
        "center": lambda aperture: aperture.center,
        "area": lambda aperture: aperture.area,
        "perimeter": lambda aperture: aperture.perimeter,
        "min": lambda aperture: aperture.min,
        "max": lambda aperture: aperture.max,
        "tilt": lambda aperture: aperture.tilt,
        "altitude": lambda aperture: aperture.altitude,
        "azimuth": lambda aperture: aperture.azimuth,
        "indoor_shades": lambda aperture: _identifier_list(aperture.indoor_shades),
        "outdoor_shades": lambda aperture: _identifier_list(aperture.outdoor_shades),
        "type_color": lambda aperture: aperture.type_color,
        "bc_color": lambda aperture: aperture.bc_color,
        "triangulated_mesh3d": lambda aperture: str(aperture.triangulated_mesh3d),
    },
    "door": {
        "identifier": lambda door: door.identifier,
        "display_name": lambda door: door.display_name,
        "boundary_condition": lambda door: str(door.boundary_condition),
        "is_glass": lambda door: door.is_glass,
        "is_exterior": lambda door: door.is_exterior,
        "has_parent": lambda door: door.has_parent,
        "parent": lambda door: door.parent.identifier if door.parent else None,
        "top_level_parent": lambda door: door.top_level_parent.identifier if door.top_level_parent else None,
        "geometry": lambda door: str(door.geometry),
        "vertices": lambda door: door.vertices,
        "upper_left_vertices": lambda door: door.upper_left_vertices,
        "normal": lambda door: door.normal,
        "center": lambda door: door.center,
        "area": lambda door: door.area,
        "perimeter": lambda door: door.perimeter,
        "min": lambda door: door.min,
        "max": lambda door: door.max,
        "tilt": lambda door: door.tilt,
        "altitude": lambda door: door.altitude,
        "azimuth": lambda door: door.azimuth,
        "indoor_shades": lambda door: _identifier_list(door.indoor_shades),
        "outdoor_shades": lambda door: _identifier_list(door.outdoor_shades),
        "type_color": lambda door: door.type_color,
        "bc_color": lambda door: door.bc_color,
    },
    "subface": {},
    "shade": {
        "identifier": lambda shade: shade.identifier,
        "display_name": lambda shade: shade.display_name,
        "is_detached": lambda shade: getattr(shade, "is_detached", None),
        "is_indoor": lambda shade: getattr(shade, "is_indoor", None),
        "has_parent": lambda shade: getattr(shade, "has_parent", None),
        "parent": lambda shade: shade.parent.identifier if getattr(shade, "parent", None) else None,
        "top_level_parent": lambda shade: shade.top_level_parent.identifier if getattr(shade, "top_level_parent", None) else None,
        "geometry": lambda shade: str(shade.geometry) if hasattr(shade, "geometry") else None,
        "vertices": lambda shade: shade.vertices if hasattr(shade, "vertices") else None,
        "upper_left_vertices": lambda shade: shade.upper_left_vertices if hasattr(shade, "upper_left_vertices") else None,
        "normal": lambda shade: shade.normal if hasattr(shade, "normal") else None,
        "center": lambda shade: shade.center if hasattr(shade, "center") else None,
        "area": lambda shade: shade.area if hasattr(shade, "area") else None,
        "perimeter": lambda shade: shade.perimeter if hasattr(shade, "perimeter") else None,
        "min": lambda shade: shade.min if hasattr(shade, "min") else None,
        "max": lambda shade: shade.max if hasattr(shade, "max") else None,
        "tilt": lambda shade: shade.tilt if hasattr(shade, "tilt") else None,
        "altitude": lambda shade: shade.altitude if hasattr(shade, "altitude") else None,
        "azimuth": lambda shade: shade.azimuth if hasattr(shade, "azimuth") else None,
        "type_color": lambda shade: getattr(shade, "type_color", None),
        "bc_color": lambda shade: getattr(shade, "bc_color", None),
    },
    "schedule": {
        "identifier": lambda record: record.identifier,
        "resource_category": lambda record: record.resource_category,
        "resource_source": lambda record: record.resource_source,
        "schedule_kind": lambda record: record.resource.__class__.__name__.replace("Schedule", ""),
        "schedule_type_limit": lambda record: getattr(getattr(record.resource, "schedule_type_limit", None), "identifier", None),
        "default_day_schedule": lambda record: getattr(getattr(record.resource, "default_day_schedule", None), "identifier", None),
        "holiday_schedule": lambda record: getattr(getattr(record.resource, "holiday_schedule", None), "identifier", None),
        "summer_designday_schedule": lambda record: getattr(getattr(record.resource, "summer_designday_schedule", None), "identifier", None),
        "winter_designday_schedule": lambda record: getattr(getattr(record.resource, "winter_designday_schedule", None), "identifier", None),
        "schedule_rules": lambda record: getattr(record.resource, "schedule_rules", None),
        "values": lambda record: getattr(record.resource, "values", None),
        "times": lambda record: getattr(record.resource, "times", None),
        "timestep": lambda record: getattr(record.resource, "timestep", None),
        "start_date": lambda record: getattr(record.resource, "start_date", None),
        "interpolate": lambda record: getattr(record.resource, "interpolate", None),
    },
    "schedule_day": {
        "identifier": lambda record: record.identifier,
        "resource_category": lambda record: record.resource_category,
        "resource_source": lambda record: record.resource_source,
        "values": lambda record: record.resource.values,
        "times": lambda record: record.resource.times,
        "interpolate": lambda record: record.resource.interpolate,
    },
    "schedule_type_limit": {
        "identifier": lambda record: record.identifier,
        "resource_category": lambda record: record.resource_category,
        "resource_source": lambda record: record.resource_source,
        "lower_limit": lambda record: record.resource.lower_limit,
        "upper_limit": lambda record: record.resource.upper_limit,
        "numeric_type": lambda record: record.resource.numeric_type,
        "unit_type": lambda record: record.resource.unit_type,
    },
    "energy_resource": {
        "identifier": lambda record: record.identifier,
        "resource_category": lambda record: record.resource_category,
        "resource_source": lambda record: record.resource_source,
        "type": lambda record: record.resource.__class__.__name__,
    },
    "modifier": {
        "identifier": lambda record: record.identifier,
        "resource_category": lambda record: record.resource_category,
        "resource_source": lambda record: record.resource_source,
        "modifier_type": lambda record: record.resource.__class__.__name__,
        "display_name": lambda record: getattr(record.resource, "display_name", record.identifier),
    },
    "modifier_set": {
        "identifier": lambda record: record.identifier,
        "resource_category": lambda record: record.resource_category,
        "resource_source": lambda record: record.resource_source,
        "display_name": lambda record: getattr(record.resource, "display_name", record.identifier),
        "wall_set": lambda record: record.resource.wall_set,
        "floor_set": lambda record: record.resource.floor_set,
        "roof_ceiling_set": lambda record: record.resource.roof_ceiling_set,
        "aperture_set": lambda record: record.resource.aperture_set,
        "door_set": lambda record: record.resource.door_set,
        "shade_set": lambda record: record.resource.shade_set,
        "air_boundary_modifier": lambda record: getattr(record.resource.air_boundary_modifier, "identifier", None),
    },
    "radiance_resource": {
        "identifier": lambda record: record.identifier,
        "resource_category": lambda record: record.resource_category,
        "resource_source": lambda record: record.resource_source,
        "type": lambda record: record.resource.__class__.__name__,
    },
    "sensor_grid": {
        "identifier": lambda grid: grid.identifier,
        "display_name": lambda grid: getattr(grid, "display_name", grid.identifier),
        "sensor_count": lambda grid: len(grid.sensors),
        "room_identifier": lambda grid: getattr(grid, "room_identifier", None),
        "mesh": lambda grid: getattr(grid, "mesh", None),
        "sensors": lambda grid: grid.sensors,
    },
    "view": {
        "identifier": lambda view: view.identifier,
        "position": lambda view: view.position,
        "direction": lambda view: view.direction,
        "up_vector": lambda view: view.up_vector,
        "view_type": lambda view: view.type,
        "h_size": lambda view: view.h_size,
        "v_size": lambda view: view.v_size,
        "shift": lambda view: view.shift,
        "lift": lambda view: view.lift,
    },
}
QUERY_FIELD_REGISTRY["subface"] = dict(QUERY_FIELD_REGISTRY["aperture"], **QUERY_FIELD_REGISTRY["door"])


def _resolve_field(target_type: str, obj, field: str):
    registry = QUERY_FIELD_REGISTRY.get(target_type, {})
    getter = registry.get(field)
    if getter is not None:
        return getter(obj)
    return get_nested_attr(obj, field)


@mcp.tool()
def query(
    target_type: str,
    identifiers: list = None,
    fields: list = None,
    output_mode: str = "records",
    resource_category: str = None,
) -> dict:
    """
    Unified query bus for Honeybee, Energy, and Radiance properties.
    """
    ensure_model_loaded()

    if fields is None or len(fields) == 0:
        fields = ["identifier", "display_name"]

    objects, missing = resolve_targets(target_type, identifiers, resource_category=resource_category)
    if output_mode == "count":
        return {
            "success": True,
            "target_type": target_type,
            "count": len(objects),
            "missing": missing,
            "resource_category": resource_category,
        }

    if target_type == "model":
        model = manager.model
        data = {field: serialize_value(_resolve_field("model", model, field)) for field in fields}
        return {
            "success": True,
            "target_type": target_type,
            "data": data,
            "resource_category": resource_category,
        }

    records = {}
    list_data = []
    for obj in objects:
        row = {field: serialize_value(_resolve_field(target_type, obj, field)) for field in fields}
        records[obj.identifier] = row
        list_data.append(row)

    return {
        "success": True,
        "target_type": target_type,
        "count": len(objects),
        "data": list_data if output_mode == "list" else records,
        "missing": missing,
        "resource_category": resource_category,
    }
