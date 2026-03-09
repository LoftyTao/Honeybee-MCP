from ..state.manager import manager
from ..state.energy_resources import (
    RESOURCE_CATEGORIES,
    get_resource_record_index,
    get_resource_records,
)
from ..state.radiance_resources import (
    RADIANCE_RESOURCE_CATEGORIES,
    get_radiance_resource_records,
)


def get_nested_attr(obj, attr_path):
    try:
        current = obj
        for attr in attr_path.split("."):
            if current is None:
                return None
            if attr == "__class__":
                current = current.__class__
            elif attr == "__name__":
                current = current.__name__
            else:
                current = getattr(current, attr, None)
        return current
    except Exception:
        return None


def _serialize_point_like(value):
    xyz = []
    for axis in ("x", "y", "z"):
        if not hasattr(value, axis):
            return None
        xyz.append(getattr(value, axis))
    return xyz


def serialize_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [serialize_value(v) for v in value]

    point_like = _serialize_point_like(value)
    if point_like is not None:
        return point_like

    if hasattr(value, "to_dict") and not hasattr(value, "identifier"):
        return serialize_value(value.to_dict())
    if hasattr(value, "identifier"):
        return value.identifier
    if hasattr(value, "display_name"):
        return value.display_name
    return str(value)


def _all_faces():
    faces = []
    for room in manager.model.rooms:
        faces.extend(list(room.faces))
    faces.extend(list(manager.model.orphaned_faces))
    return faces


def _all_apertures():
    apertures = list(manager.model.orphaned_apertures)
    for face in _all_faces():
        apertures.extend(list(face.apertures))
    return apertures


def _all_doors():
    doors = list(manager.model.orphaned_doors)
    for face in _all_faces():
        doors.extend(list(face.doors))
    return doors


def _all_shades():
    shades = list(manager.model.orphaned_shades)
    shades.extend(list(manager.model.shade_meshes))
    for room in manager.model.rooms:
        shades.extend(list(room.indoor_shades))
        shades.extend(list(room.outdoor_shades))
        for face in room.faces:
            shades.extend(list(face.indoor_shades))
            shades.extend(list(face.outdoor_shades))
            for aperture in face.apertures:
                shades.extend(list(aperture.indoor_shades))
                shades.extend(list(aperture.outdoor_shades))
            for door in face.doors:
                shades.extend(list(door.indoor_shades))
                shades.extend(list(door.outdoor_shades))
    return shades


def get_objects_by_type(target_type: str):
    target_type = target_type.lower()
    if target_type == "schedule":
        return get_resource_records(manager, ("schedules",))
    if target_type == "schedule_day":
        return get_resource_records(manager, ("schedule_days",))
    if target_type == "schedule_type_limit":
        return get_resource_records(manager, ("schedule_type_limits",))
    if target_type == "energy_resource":
        return get_resource_records(manager, RESOURCE_CATEGORIES)
    if target_type == "modifier":
        return get_radiance_resource_records(manager, ("modifiers",))
    if target_type == "modifier_set":
        return get_radiance_resource_records(manager, ("modifier_sets",))
    if target_type == "radiance_resource":
        return get_radiance_resource_records(manager, RADIANCE_RESOURCE_CATEGORIES)
    if target_type == "sensor_grid":
        return list(manager.model.properties.radiance.sensor_grids)
    if target_type == "view":
        return list(manager.model.properties.radiance.views)
    if target_type == "model":
        return [manager.model]
    if target_type == "room":
        return list(manager.model.rooms)
    if target_type == "face":
        return _all_faces()
    if target_type == "aperture":
        return _all_apertures()
    if target_type == "door":
        return _all_doors()
    if target_type == "subface":
        return _all_apertures() + _all_doors()
    if target_type == "shade":
        return _all_shades()
    raise ValueError("Unsupported target_type '{}'".format(target_type))


def resolve_targets(target_type: str, identifiers=None, resource_category: str = None):
    objects = get_objects_by_type(target_type)
    if target_type == "energy_resource" and resource_category:
        objects = [obj for obj in objects if obj.resource_category == resource_category]
    if target_type == "model":
        return objects, []
    if not identifiers:
        return objects, []

    if target_type in ("schedule", "schedule_day", "schedule_type_limit", "energy_resource"):
        index = get_resource_record_index(
            manager,
            None if target_type == "energy_resource" else (
                "schedules",
                "schedule_days",
                "schedule_type_limits",
            ),
        )
        if target_type == "energy_resource" and resource_category:
            index = {key: value for key, value in index.items() if value.resource_category == resource_category}
        elif target_type != "energy_resource":
            index = {key: value for key, value in index.items() if value in objects}
    elif target_type in ("modifier", "modifier_set", "radiance_resource"):
        records = (
            get_radiance_resource_records(manager, None)
            if target_type == "radiance_resource"
            else get_radiance_resource_records(
                manager,
                ("modifiers",) if target_type == "modifier" else ("modifier_sets",),
            )
        )
        index = {record.identifier: record for record in records}
        if target_type == "radiance_resource" and resource_category:
            index = {key: value for key, value in index.items() if value.resource_category == resource_category}
    else:
        index = {obj.identifier: obj for obj in objects if hasattr(obj, "identifier")}
    found = []
    missing = []
    for identifier in identifiers:
        obj = index.get(identifier)
        if obj is None:
            missing.append(identifier)
        else:
            found.append(obj)
    return found, missing
