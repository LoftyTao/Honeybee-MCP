from honeybee_radiance.modifierset import ModifierSet
from honeybee_radiance.mutil import dict_to_modifier
from honeybee_radiance.sensor import Sensor
from honeybee_radiance.sensorgrid import SensorGrid
from honeybee_radiance.view import View

from ..state.hooks import post_edit_pipeline
from ..state.manager import manager
from ..state.radiance_resources import (
    get_radiance_resources_for_category,
    radiance_identifier_taken,
    register_radiance_resource,
    resolve_modifier,
    resolve_modifier_set,
    unregister_radiance_resource,
)


def _result(success=True, **kwargs):
    data = {"success": success}
    data.update(kwargs)
    return post_edit_pipeline(data) if success else data


def _modifier_payload_to_dict(values, default_identifier=None):
    if values.get("modifier_dict"):
        return values["modifier_dict"]
    modifier_type = values.get("modifier_type")
    identifier = values.get("identifier") or default_identifier
    if not modifier_type or not identifier:
        raise ValueError("modifier_type and identifier are required for Radiance modifier creation.")

    modifier_type = modifier_type.lower()
    if modifier_type == "plastic":
        return {
            "modifier": "void",
            "type": "Plastic",
            "identifier": identifier,
            "r_reflectance": values.get("r_reflectance", 0.0),
            "g_reflectance": values.get("g_reflectance", values.get("r_reflectance", 0.0)),
            "b_reflectance": values.get("b_reflectance", values.get("r_reflectance", 0.0)),
            "specularity": values.get("specularity", 0.0),
            "roughness": values.get("roughness", 0.0),
        }
    if modifier_type == "glass":
        return {
            "modifier": "void",
            "type": "Glass",
            "identifier": identifier,
            "r_transmissivity": values.get("r_transmissivity", 0.0),
            "g_transmissivity": values.get("g_transmissivity", values.get("r_transmissivity", 0.0)),
            "b_transmissivity": values.get("b_transmissivity", values.get("r_transmissivity", 0.0)),
            "refraction_index": values.get("refraction_index"),
        }
    if modifier_type == "trans":
        return {
            "modifier": "void",
            "type": "Trans",
            "identifier": identifier,
            "r_reflectance": values.get("r_reflectance", 0.0),
            "g_reflectance": values.get("g_reflectance", values.get("r_reflectance", 0.0)),
            "b_reflectance": values.get("b_reflectance", values.get("r_reflectance", 0.0)),
            "specularity": values.get("specularity", 0.0),
            "roughness": values.get("roughness", 0.0),
            "transmitted_diff": values.get("transmitted_diff", 0.0),
            "transmitted_spec": values.get("transmitted_spec", 0.0),
        }
    if modifier_type == "metal":
        return {
            "modifier": "void",
            "type": "Metal",
            "identifier": identifier,
            "r_reflectance": values.get("r_reflectance", 0.0),
            "g_reflectance": values.get("g_reflectance", values.get("r_reflectance", 0.0)),
            "b_reflectance": values.get("b_reflectance", values.get("r_reflectance", 0.0)),
            "specularity": values.get("specularity", 0.9),
            "roughness": values.get("roughness", 0.0),
        }
    if modifier_type == "mirror":
        return {
            "modifier": "void",
            "type": "Mirror",
            "identifier": identifier,
            "r_reflectance": values.get("r_reflectance", 1.0),
            "g_reflectance": values.get("g_reflectance", values.get("r_reflectance", 1.0)),
            "b_reflectance": values.get("b_reflectance", values.get("r_reflectance", 1.0)),
        }
    if modifier_type == "glow":
        return {
            "modifier": "void",
            "type": "Glow",
            "identifier": identifier,
            "r_emittance": values.get("r_emittance", 0.0),
            "g_emittance": values.get("g_emittance", values.get("r_emittance", 0.0)),
            "b_emittance": values.get("b_emittance", values.get("r_emittance", 0.0)),
            "max_radius": values.get("max_radius", 0.0),
        }
    raise ValueError("Unsupported modifier_type '{}'.".format(values.get("modifier_type")))


def _build_modifier(values, default_identifier=None):
    return dict_to_modifier(_modifier_payload_to_dict(values, default_identifier))


def _resolve_modifier_required(identifier):
    modifier = resolve_modifier(manager, identifier)
    if modifier is None:
        raise ValueError("Modifier '{}' was not found.".format(identifier))
    return modifier


def _build_modifier_set(values, default_identifier=None):
    if values.get("modifier_set_dict"):
        modifier_dict = {identifier: modifier for identifier, modifier in get_radiance_resources_for_category(manager, "modifiers").items()}
        return ModifierSet.from_dict_abridged(values["modifier_set_dict"], modifier_dict)

    identifier = values.get("identifier") or default_identifier
    if not identifier:
        raise ValueError("ModifierSet identifier is required.")

    def _slot_dict(slot_type, payload):
        data = {"type": slot_type}
        for key, modifier_id in (payload or {}).items():
            data[key] = modifier_id
        return data

    modifier_set_dict = {
        "type": "ModifierSetAbridged",
        "identifier": identifier,
        "wall_set": _slot_dict("WallModifierSetAbridged", values.get("wall_set")),
        "floor_set": _slot_dict("FloorModifierSetAbridged", values.get("floor_set")),
        "roof_ceiling_set": _slot_dict("RoofCeilingModifierSetAbridged", values.get("roof_ceiling_set")),
        "aperture_set": _slot_dict("ApertureModifierSetAbridged", values.get("aperture_set")),
        "door_set": _slot_dict("DoorModifierSetAbridged", values.get("door_set")),
        "shade_set": _slot_dict("ShadeModifierSetAbridged", values.get("shade_set")),
        "air_boundary_modifier": values.get("air_boundary_modifier"),
    }
    modifier_ids = set()
    for slot_name in ("wall_set", "floor_set", "roof_ceiling_set", "aperture_set", "door_set", "shade_set"):
        modifier_ids.update([value for value in modifier_set_dict[slot_name].values() if value and not str(value).endswith("Abridged")])
    if modifier_set_dict["air_boundary_modifier"]:
        modifier_ids.add(modifier_set_dict["air_boundary_modifier"])

    modifier_dict = {modifier_id: _resolve_modifier_required(modifier_id) for modifier_id in modifier_ids}
    return ModifierSet.from_dict_abridged(modifier_set_dict, modifier_dict)


def _sensor_dict(sensor_payload):
    return {
        "pos": tuple(sensor_payload.get("pos", (0, 0, 0))),
        "dir": tuple(sensor_payload.get("dir", (0, 0, 1))),
    }


def _build_sensor_grid(values, default_identifier=None):
    if values.get("sensor_grid_dict"):
        return SensorGrid.from_dict(values["sensor_grid_dict"])
    identifier = values.get("identifier") or default_identifier
    if not identifier:
        raise ValueError("SensorGrid identifier is required.")
    sensors = [Sensor.from_dict(_sensor_dict(sensor)) for sensor in values.get("sensors", [])]
    if not sensors:
        raise ValueError("SensorGrid sensors are required.")
    return SensorGrid(identifier, sensors)


def _build_view(values, default_identifier=None):
    if values.get("view_dict"):
        return View.from_dict(values["view_dict"])
    identifier = values.get("identifier") or default_identifier
    if not identifier:
        raise ValueError("View identifier is required.")
    return View(
        identifier,
        position=values.get("position"),
        direction=values.get("direction"),
        up_vector=values.get("up_vector"),
        type=values.get("view_type", "v"),
        h_size=values.get("h_size", 60),
        v_size=values.get("v_size", 60),
        shift=values.get("shift"),
        lift=values.get("lift"),
    )


def add_modifier_impl(**values):
    modifier = _build_modifier(values)
    if radiance_identifier_taken(manager, "modifiers", modifier.identifier):
        return {"success": False, "error": "Modifier '{}' already exists.".format(modifier.identifier)}
    register_radiance_resource(manager, "modifiers", modifier)
    return _result(True, message="Created modifier '{}'.".format(modifier.identifier), results=[modifier.identifier], resource_changes=[{"action": "created", "resource_category": "modifier", "identifier": modifier.identifier}])


def add_modifier_set_impl(**values):
    modifier_set = _build_modifier_set(values)
    if radiance_identifier_taken(manager, "modifier_sets", modifier_set.identifier):
        return {"success": False, "error": "ModifierSet '{}' already exists.".format(modifier_set.identifier)}
    register_radiance_resource(manager, "modifier_sets", modifier_set)
    return _result(True, message="Created modifier set '{}'.".format(modifier_set.identifier), results=[modifier_set.identifier], resource_changes=[{"action": "created", "resource_category": "modifier_set", "identifier": modifier_set.identifier}])


def add_sensor_grid_impl(**values):
    grid = _build_sensor_grid(values)
    manager.model.properties.radiance.add_sensor_grid(grid)
    return _result(True, message="Created sensor grid '{}'.".format(grid.identifier), results=[grid.identifier])


def add_view_impl(**values):
    view = _build_view(values)
    manager.model.properties.radiance.add_view(view)
    return _result(True, message="Created view '{}'.".format(view.identifier), results=[view.identifier])


def _replace_modifier_on_host_objects(old_identifier, new_modifier):
    for face in manager.model.faces:
        explicit = face.properties.radiance._modifier
        if explicit is not None and explicit.identifier == old_identifier:
            face.properties.radiance.modifier = new_modifier
        blk = face.properties.radiance._modifier_blk
        if blk is not None and blk.identifier == old_identifier:
            face.properties.radiance.modifier_blk = new_modifier
    for aperture in manager.model.apertures:
        explicit = aperture.properties.radiance._modifier
        if explicit is not None and explicit.identifier == old_identifier:
            aperture.properties.radiance.modifier = new_modifier
        blk = aperture.properties.radiance._modifier_blk
        if blk is not None and blk.identifier == old_identifier:
            aperture.properties.radiance.modifier_blk = new_modifier
    for door in manager.model.doors:
        explicit = door.properties.radiance._modifier
        if explicit is not None and explicit.identifier == old_identifier:
            door.properties.radiance.modifier = new_modifier
        blk = door.properties.radiance._modifier_blk
        if blk is not None and blk.identifier == old_identifier:
            door.properties.radiance.modifier_blk = new_modifier
    for shade in manager.model.shades + manager.model.shade_meshes:
        explicit = shade.properties.radiance._modifier
        if explicit is not None and explicit.identifier == old_identifier:
            shade.properties.radiance.modifier = new_modifier
        blk = shade.properties.radiance._modifier_blk
        if blk is not None and blk.identifier == old_identifier:
            shade.properties.radiance.modifier_blk = new_modifier


def _replace_modifier_set_on_rooms(old_identifier, new_modifier_set):
    for room in manager.model.rooms:
        if room.properties.radiance._modifier_set is not None and room.properties.radiance._modifier_set.identifier == old_identifier:
            room.properties.radiance.modifier_set = new_modifier_set


def apply_modifier_impl(modifier_identifiers=None, **values):
    bucket = get_radiance_resources_for_category(manager, "modifiers")
    identifiers = modifier_identifiers or list(bucket.keys())
    results = []
    changes = []
    for identifier in identifiers:
        if bucket.get(identifier) is None:
            results.append({"identifier": identifier, "error": "Modifier not found."})
            continue
        payload = dict(values)
        payload.setdefault("identifier", values.get("identifier") or identifier)
        modifier = _build_modifier(payload)
        register_radiance_resource(manager, "modifiers", modifier)
        if identifier != modifier.identifier:
            unregister_radiance_resource(manager, "modifiers", identifier)
        _replace_modifier_on_host_objects(identifier, modifier)
        results.append({"identifier": identifier, "updated_identifier": modifier.identifier})
        changes.append({"action": "updated", "resource_category": "modifier", "identifier": modifier.identifier})
    return _result(True, message="Updated modifiers.", results=results, resource_changes=changes)


def apply_modifier_set_impl(modifier_set_identifiers=None, **values):
    bucket = get_radiance_resources_for_category(manager, "modifier_sets")
    identifiers = modifier_set_identifiers or list(bucket.keys())
    results = []
    changes = []
    for identifier in identifiers:
        if bucket.get(identifier) is None:
            results.append({"identifier": identifier, "error": "ModifierSet not found."})
            continue
        payload = dict(values)
        payload.setdefault("identifier", values.get("identifier") or identifier)
        modifier_set = _build_modifier_set(payload)
        register_radiance_resource(manager, "modifier_sets", modifier_set)
        if identifier != modifier_set.identifier:
            unregister_radiance_resource(manager, "modifier_sets", identifier)
        _replace_modifier_set_on_rooms(identifier, modifier_set)
        results.append({"identifier": identifier, "updated_identifier": modifier_set.identifier})
        changes.append({"action": "updated", "resource_category": "modifier_set", "identifier": modifier_set.identifier})
    return _result(True, message="Updated modifier sets.", results=results, resource_changes=changes)


def _replace_by_identifier(items, identifier, new_item):
    result = []
    replaced = False
    for item in items:
        if item.identifier == identifier:
            result.append(new_item)
            replaced = True
        else:
            result.append(item)
    return result, replaced


def apply_sensor_grid_impl(sensor_grid_identifiers=None, **values):
    grids = list(manager.model.properties.radiance.sensor_grids)
    identifiers = sensor_grid_identifiers or [grid.identifier for grid in grids]
    results = []
    for identifier in identifiers:
        payload = dict(values)
        payload.setdefault("identifier", values.get("identifier") or identifier)
        new_grid = _build_sensor_grid(payload)
        grids, replaced = _replace_by_identifier(grids, identifier, new_grid)
        if not replaced:
            results.append({"identifier": identifier, "error": "SensorGrid not found."})
        else:
            results.append({"identifier": identifier, "updated_identifier": new_grid.identifier})
    manager.model.properties.radiance.sensor_grids = grids
    return _result(True, message="Updated sensor grids.", results=results)


def apply_view_impl(view_identifiers=None, **values):
    views = list(manager.model.properties.radiance.views)
    identifiers = view_identifiers or [view.identifier for view in views]
    results = []
    for identifier in identifiers:
        payload = dict(values)
        payload.setdefault("identifier", values.get("identifier") or identifier)
        new_view = _build_view(payload)
        views, replaced = _replace_by_identifier(views, identifier, new_view)
        if not replaced:
            results.append({"identifier": identifier, "error": "View not found."})
        else:
            results.append({"identifier": identifier, "updated_identifier": new_view.identifier})
    manager.model.properties.radiance.views = views
    return _result(True, message="Updated views.", results=results)


def remove_modifier_resources_impl(modifier_ids=None, modifier_set_ids=None):
    removed = {"modifier": [], "modifier_set": []}
    blocked = []
    for identifier in modifier_ids or []:
        refs = []
        for face in manager.model.faces:
            if face.properties.radiance._modifier is not None and face.properties.radiance._modifier.identifier == identifier:
                refs.append("face:{}".format(face.identifier))
        for shade in list(manager.model.shades) + list(manager.model.shade_meshes):
            if shade.properties.radiance._modifier is not None and shade.properties.radiance._modifier.identifier == identifier:
                refs.append("shade:{}".format(shade.identifier))
        for aperture in manager.model.apertures:
            if aperture.properties.radiance._modifier is not None and aperture.properties.radiance._modifier.identifier == identifier:
                refs.append("aperture:{}".format(aperture.identifier))
        for door in manager.model.doors:
            if door.properties.radiance._modifier is not None and door.properties.radiance._modifier.identifier == identifier:
                refs.append("door:{}".format(door.identifier))
        if refs:
            blocked.append({"identifier": identifier, "resource_category": "modifier", "references": refs})
            continue
        if unregister_radiance_resource(manager, "modifiers", identifier) is not None:
            removed["modifier"].append(identifier)

    for identifier in modifier_set_ids or []:
        refs = [room.identifier for room in manager.model.rooms if room.properties.radiance._modifier_set is not None and room.properties.radiance._modifier_set.identifier == identifier]
        if refs:
            blocked.append({"identifier": identifier, "resource_category": "modifier_set", "references": refs})
            continue
        if unregister_radiance_resource(manager, "modifier_sets", identifier) is not None:
            removed["modifier_set"].append(identifier)
    return _result(True, message="Processed radiance resource removal.", removed=removed, blocked=blocked or None)


def remove_sensor_grids_impl(sensor_grid_ids=None):
    grids = list(manager.model.properties.radiance.sensor_grids)
    kept = []
    removed = []
    for grid in grids:
        if sensor_grid_ids is None or grid.identifier in sensor_grid_ids:
            removed.append(grid.identifier)
        else:
            kept.append(grid)
    manager.model.properties.radiance.sensor_grids = kept
    return _result(True, message="Removed sensor grids.", removed_ids=removed)


def remove_views_impl(view_ids=None):
    views = list(manager.model.properties.radiance.views)
    kept = []
    removed = []
    for view in views:
        if view_ids is None or view.identifier in view_ids:
            removed.append(view.identifier)
        else:
            kept.append(view)
    manager.model.properties.radiance.views = kept
    return _result(True, message="Removed views.", removed_ids=removed)
