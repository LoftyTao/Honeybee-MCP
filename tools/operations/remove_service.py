from ..state.hooks import ensure_model_loaded, post_edit_pipeline
from ..state.manager import manager


def _ordered_matches(requested_ids, found_ids):
    return [item_id for item_id in requested_ids if item_id in found_ids]


def _filter_objects_by_identifier(objects, identifier_set, detach=None):
    kept = []
    found_ids = set()
    for obj in list(objects):
        if obj.identifier in identifier_set:
            found_ids.add(obj.identifier)
            if detach is not None:
                detach(obj)
        else:
            kept.append(obj)
    return kept, found_ids


def _detach_subface(subface):
    subface._parent = None


def _detach_indoor_shade(shade):
    shade._parent = None
    shade._is_indoor = False


def _detach_outdoor_shade(shade):
    shade._parent = None


def _all_faces():
    faces = []
    for room in manager.model.rooms:
        faces.extend(list(room.faces))
    faces.extend(list(manager.model.orphaned_faces))
    return faces


def _remove_specific_apertures(aperture_ids):
    requested_ids = list(aperture_ids or [])
    if not requested_ids:
        return set()

    identifier_set = set(requested_ids)
    found_ids = set()

    for face in _all_faces():
        filtered, removed = _filter_objects_by_identifier(
            face._apertures,
            identifier_set,
            detach=_detach_subface,
        )
        if removed:
            face._apertures = filtered
            face._punched_geometry = None
            found_ids.update(removed)

    filtered, removed = _filter_objects_by_identifier(
        manager.model._orphaned_apertures,
        identifier_set,
    )
    if removed:
        manager.model._orphaned_apertures = filtered
        found_ids.update(removed)

    return found_ids


def _remove_specific_doors(door_ids):
    requested_ids = list(door_ids or [])
    if not requested_ids:
        return set()

    identifier_set = set(requested_ids)
    found_ids = set()

    for face in _all_faces():
        filtered, removed = _filter_objects_by_identifier(
            face._doors,
            identifier_set,
            detach=_detach_subface,
        )
        if removed:
            face._doors = filtered
            face._punched_geometry = None
            found_ids.update(removed)

    filtered, removed = _filter_objects_by_identifier(
        manager.model._orphaned_doors,
        identifier_set,
    )
    if removed:
        manager.model._orphaned_doors = filtered
        found_ids.update(removed)

    return found_ids


def _remove_shades_from_parent(parent, identifier_set):
    found_ids = set()

    filtered, removed = _filter_objects_by_identifier(
        parent._indoor_shades,
        identifier_set,
        detach=_detach_indoor_shade,
    )
    if removed:
        parent._indoor_shades = filtered
        found_ids.update(removed)

    filtered, removed = _filter_objects_by_identifier(
        parent._outdoor_shades,
        identifier_set,
        detach=_detach_outdoor_shade,
    )
    if removed:
        parent._outdoor_shades = filtered
        found_ids.update(removed)

    return found_ids


def _remove_specific_shades(shade_ids):
    requested_ids = list(shade_ids or [])
    if not requested_ids:
        return set(), set()

    identifier_set = set(requested_ids)
    removed_shade_ids = set()
    removed_shade_mesh_ids = set()

    filtered, removed = _filter_objects_by_identifier(
        manager.model._orphaned_shades,
        identifier_set,
    )
    if removed:
        manager.model._orphaned_shades = filtered
        removed_shade_ids.update(removed)

    filtered, removed = _filter_objects_by_identifier(
        manager.model._shade_meshes,
        identifier_set,
    )
    if removed:
        manager.model._shade_meshes = filtered
        removed_shade_mesh_ids.update(removed)

    for room in manager.model.rooms:
        removed_shade_ids.update(_remove_shades_from_parent(room, identifier_set))
        for face in room.faces:
            removed_shade_ids.update(_remove_shades_from_parent(face, identifier_set))
            for aperture in face.apertures:
                removed_shade_ids.update(_remove_shades_from_parent(aperture, identifier_set))
            for door in face.doors:
                removed_shade_ids.update(_remove_shades_from_parent(door, identifier_set))

    return removed_shade_ids, removed_shade_mesh_ids


def remove_all_apertures_impl(aperture_ids=None):
    ensure_model_loaded()
    if aperture_ids is not None:
        removed_ids = _ordered_matches(aperture_ids, _remove_specific_apertures(aperture_ids))
        not_found = [aperture_id for aperture_id in aperture_ids if aperture_id not in removed_ids]
        return post_edit_pipeline(
            {
                "success": True,
                "message": "Removed {} aperture(s) from the model.".format(len(removed_ids)),
                "removed_count": len(removed_ids),
                "removed_ids": removed_ids,
                "not_found": not_found,
            }
        )

    manager.model.remove_all_apertures()
    return post_edit_pipeline(
        {
            "success": True,
            "message": "All apertures (Aperture) have been removed from the model.",
        }
    )


def remove_all_doors_impl(door_ids=None):
    ensure_model_loaded()
    if door_ids is not None:
        removed_ids = _ordered_matches(door_ids, _remove_specific_doors(door_ids))
        not_found = [door_id for door_id in door_ids if door_id not in removed_ids]
        return post_edit_pipeline(
            {
                "success": True,
                "message": "Removed {} door(s) from the model.".format(len(removed_ids)),
                "removed_count": len(removed_ids),
                "removed_ids": removed_ids,
                "not_found": not_found,
            }
        )

    manager.model.remove_all_doors()
    return post_edit_pipeline(
        {
            "success": True,
            "message": "All doors (Door) have been removed from the model.",
        }
    )


def remove_all_shades_impl(shade_ids=None, shade_mesh_ids=None):
    ensure_model_loaded()
    requested_ids = []
    if shade_ids:
        requested_ids.extend(shade_ids)
    if shade_mesh_ids:
        requested_ids.extend(shade_mesh_ids)

    if not requested_ids:
        outdoor_count = len(manager.model.outdoor_shades)
        indoor_count = len(manager.model.indoor_shades)
        orphaned_count = len(manager.model.orphaned_shades)
        mesh_count = len(manager.model.shade_meshes)
        total_count = outdoor_count + indoor_count + orphaned_count + mesh_count
        manager.model.remove_all_shades()
        manager.model.remove_shade_meshes()
        return post_edit_pipeline(
            {
                "success": True,
                "message": "All shading elements have been removed from the model.",
                "removed": {
                    "outdoor_shades": outdoor_count,
                    "indoor_shades": indoor_count,
                    "orphaned_shades": orphaned_count,
                    "shade_meshes": mesh_count,
                    "total": total_count,
                },
            }
        )

    removed_shade_ids, removed_shade_mesh_ids = _remove_specific_shades(requested_ids)
    removed_lookup = removed_shade_ids | removed_shade_mesh_ids
    removed_ids = _ordered_matches(requested_ids, removed_lookup)
    not_found = [shade_id for shade_id in requested_ids if shade_id not in removed_lookup]
    return post_edit_pipeline(
        {
            "success": True,
            "message": "Removed {} shading object(s) from the model.".format(len(removed_ids)),
            "removed_count": len(removed_ids),
            "removed_ids": removed_ids,
            "removed_shade_ids": _ordered_matches(requested_ids, removed_shade_ids),
            "removed_shade_mesh_ids": _ordered_matches(requested_ids, removed_shade_mesh_ids),
            "not_found": not_found,
            "remaining_count": len(manager.model.shades) + len(manager.model.shade_meshes),
        }
    )


def remove_face_objects_impl(
    face_identifiers,
    apertures=False,
    doors=False,
    indoor_shades=False,
    outdoor_shades=False,
    sub_faces=False,
):
    ensure_model_loaded()
    if not any([apertures, doors, indoor_shades, outdoor_shades, sub_faces]):
        return {"success": False, "message": "At least one object type must be selected for removal."}

    face_map = {}
    for room in manager.model.rooms:
        for face in room.faces:
            face_map[face.identifier] = face
    for face in manager.model.orphaned_faces:
        face_map[face.identifier] = face

    results = []
    not_found = []
    for face_id in face_identifiers:
        face = face_map.get(face_id)
        if face is None:
            not_found.append(face_id)
            continue
        removed_objects = []
        if sub_faces:
            removed_count = len(face.apertures) + len(face.doors)
            face.remove_sub_faces()
            removed_objects.append(f"Sub-faces ({removed_count})")
        else:
            if apertures:
                removed_count = len(face.apertures)
                face.remove_apertures()
                removed_objects.append(f"Apertures ({removed_count})")
            if doors:
                removed_count = len(face.doors)
                face.remove_doors()
                removed_objects.append(f"Doors ({removed_count})")
        if indoor_shades:
            removed_count = len(face.indoor_shades)
            face.remove_indoor_shades()
            removed_objects.append(f"Indoor shades ({removed_count})")
        if outdoor_shades:
            removed_count = len(face.outdoor_shades)
            face.remove_outdoor_shades()
            removed_objects.append(f"Outdoor shades ({removed_count})")
        results.append({"face_identifier": face_id, "removed_objects": removed_objects})

    return post_edit_pipeline(
        {
            "success": True,
            "message": f"Processed {len(results)} faces, {len(not_found)} faces not found.",
            "results": results,
            "not_found": not_found,
        }
    )


def remove_room_shades_impl(room_identifiers, indoor_shades=True, outdoor_shades=True):
    ensure_model_loaded()
    if not indoor_shades and not outdoor_shades:
        return {
            "success": False,
            "message": "At least one of indoor_shades or outdoor_shades must be True.",
        }

    room_map = {room.identifier: room for room in manager.model.rooms}
    results = []
    not_found = []
    for room_id in room_identifiers:
        room = room_map.get(room_id)
        if room is None:
            not_found.append(room_id)
            continue
        removed_count = 0
        shade_types = []
        if indoor_shades:
            removed_count += len(room.indoor_shades)
            room.remove_indoor_shades()
            shade_types.append("indoor")
        if outdoor_shades:
            removed_count += len(room.outdoor_shades)
            room.remove_outdoor_shades()
            shade_types.append("outdoor")
        results.append(
            {
                "room_identifier": room_id,
                "removed_count": removed_count,
                "shade_type": ", ".join(shade_types),
            }
        )

    return post_edit_pipeline(
        {
            "success": True,
            "message": f"Processed {len(results)} rooms, {len(not_found)} rooms not found.",
            "results": results,
            "not_found": not_found,
        }
    )
