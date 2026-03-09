from honeybee.face import Face
from ladybug_geometry.geometry2d import Vector2D

from ..state.hooks import ensure_model_loaded, post_edit_pipeline
from ..state.manager import manager


def _resolve_horizontal_separation(face, horizontal_separation, tolerance=0.01):
    """Return a valid separation for Honeybee rectangle-based aperture methods."""
    if horizontal_separation is not None:
        return horizontal_separation
    # Honeybee requires a positive number here. Using the face perimeter ensures
    # the value is larger than any individual rectangle width, yielding one span.
    return max(face.perimeter, tolerance * 2)


def _find_faces(face_identifiers):
    results = []
    not_found = []
    face_map = {}
    for room in manager.model.rooms:
        for face in room.faces:
            face_map[face.identifier] = face
    for face in manager.model.orphaned_faces:
        face_map[face.identifier] = face

    for face_id in face_identifiers:
        face = face_map.get(face_id)
        if face is None:
            not_found.append(face_id)
        else:
            results.append(face)
    return results, not_found


def _find_apertures(aperture_identifiers):
    results = []
    not_found = []
    aperture_map = {}
    for room in manager.model.rooms:
        for face in room.faces:
            for aperture in face.apertures:
                aperture_map[aperture.identifier] = aperture
    for aperture in manager.model.orphaned_apertures:
        aperture_map[aperture.identifier] = aperture

    for aperture_id in aperture_identifiers:
        aperture = aperture_map.get(aperture_id)
        if aperture is None:
            not_found.append(aperture_id)
        else:
            results.append(aperture)
    return results, not_found


def add_aperture_by_width_height_impl(
    face_identifiers, width, height, sill_height=1.0, aperture_identifier=None
):
    ensure_model_loaded()
    if width <= 0 or height <= 0:
        return {"success": False, "message": "Aperture width and height must be greater than 0."}
    if sill_height < 0:
        return {"success": False, "message": "Sill height cannot be negative."}

    faces, not_found = _find_faces(face_identifiers)
    results = []
    for face in faces:
        try:
            aperture = face.aperture_by_width_height(
                width=width,
                height=height,
                sill_height=sill_height,
                aperture_identifier=aperture_identifier,
            )
            results.append(
                {
                    "face_identifier": face.identifier,
                    "aperture_identifier": aperture.identifier,
                    "width": width,
                    "height": height,
                    "sill_height": sill_height,
                }
            )
        except Exception as e:
            results.append({"face_identifier": face.identifier, "error": str(e)})
    return post_edit_pipeline(
        {
            "success": True,
            "message": f"Processed {len(results)} faces, {len(not_found)} faces not found.",
            "results": results,
            "not_found": not_found,
        }
    )


def add_apertures_by_ratio_rectangle_impl(
    face_identifiers,
    ratio,
    aperture_height=None,
    sill_height=0.9,
    horizontal_separation=None,
    vertical_separation=0,
    tolerance=0.01,
):
    ensure_model_loaded()
    if ratio <= 0 or ratio >= 0.95:
        return {"success": False, "message": "Ratio must be between 0 and 0.95."}
    if aperture_height is not None and aperture_height <= 0:
        return {"success": False, "message": "aperture_height must be greater than 0."}
    if sill_height < 0:
        return {"success": False, "message": "sill_height cannot be negative."}
    if horizontal_separation is not None and horizontal_separation <= 0:
        return {"success": False, "message": "horizontal_separation must be greater than 0."}
    if vertical_separation < 0:
        return {"success": False, "message": "vertical_separation cannot be negative."}
    if tolerance <= 0:
        return {"success": False, "message": "Tolerance value must be greater than 0."}

    faces, not_found = _find_faces(face_identifiers)
    results = []
    for face in faces:
        try:
            resolved_horizontal_separation = _resolve_horizontal_separation(
                face, horizontal_separation, tolerance
            )
            face.apertures_by_ratio_rectangle(
                ratio=ratio,
                aperture_height=aperture_height,
                sill_height=sill_height,
                horizontal_separation=resolved_horizontal_separation,
                vertical_separation=vertical_separation,
                tolerance=tolerance,
            )
            results.append(
                {
                    "face_identifier": face.identifier,
                    "ratio": ratio,
                    "horizontal_separation": resolved_horizontal_separation,
                    "aperture_count": len(face.apertures),
                    "aperture_identifiers": [ap.identifier for ap in face.apertures],
                }
            )
        except Exception as e:
            results.append({"face_identifier": face.identifier, "error": str(e)})
    return post_edit_pipeline(
        {
            "success": True,
            "message": f"Processed {len(results)} faces, {len(not_found)} faces not found.",
            "results": results,
            "not_found": not_found,
        }
    )


def add_apertures_by_ratio_impl(face_identifiers, ratio, tolerance=0.01, rect_split=True):
    ensure_model_loaded()
    if ratio <= 0 or ratio >= 1:
        return {"success": False, "message": "Ratio must be between 0 and 1 (cannot equal 0 or 1)."}
    if tolerance <= 0:
        return {"success": False, "message": "Tolerance value must be greater than 0."}
    faces, not_found = _find_faces(face_identifiers)
    results = []
    for face in faces:
        try:
            face.apertures_by_ratio(ratio=ratio, tolerance=tolerance, rect_split=rect_split)
            results.append(
                {
                    "face_identifier": face.identifier,
                    "ratio": ratio,
                    "aperture_count": len(face.apertures),
                    "aperture_identifiers": [ap.identifier for ap in face.apertures],
                }
            )
        except Exception as e:
            results.append({"face_identifier": face.identifier, "error": str(e)})
    return post_edit_pipeline(
        {
            "success": True,
            "message": f"Processed {len(results)} faces, {len(not_found)} faces not found.",
            "results": results,
            "not_found": not_found,
        }
    )


def add_apertures_by_ratio_gridded_impl(face_identifiers, ratio, x_dim, y_dim=None, tolerance=0.01):
    ensure_model_loaded()
    if ratio <= 0 or ratio >= 1:
        return {"success": False, "message": "Ratio must be between 0 and 1 (cannot equal 0 or 1)."}
    if x_dim <= 0:
        return {"success": False, "message": "x_dim must be greater than 0."}
    if y_dim is not None and y_dim <= 0:
        return {"success": False, "message": "y_dim must be greater than 0."}
    if tolerance <= 0:
        return {"success": False, "message": "Tolerance value must be greater than 0."}

    faces, not_found = _find_faces(face_identifiers)
    results = []
    for face in faces:
        try:
            face.apertures_by_ratio_gridded(ratio=ratio, x_dim=x_dim, y_dim=y_dim, tolerance=tolerance)
            results.append(
                {
                    "face_identifier": face.identifier,
                    "ratio": ratio,
                    "x_dim": x_dim,
                    "y_dim": y_dim,
                    "aperture_count": len(face.apertures),
                    "aperture_identifiers": [ap.identifier for ap in face.apertures],
                }
            )
        except Exception as e:
            results.append({"face_identifier": face.identifier, "error": str(e)})
    return post_edit_pipeline(
        {
            "success": True,
            "message": f"Processed {len(results)} faces, {len(not_found)} faces not found.",
            "results": results,
            "not_found": not_found,
        }
    )


def add_apertures_by_width_height_rectangle_impl(
    face_identifiers,
    aperture_height,
    aperture_width,
    sill_height=0.9,
    horizontal_separation=None,
    tolerance=0.01,
):
    ensure_model_loaded()
    if aperture_height <= 0:
        return {"success": False, "message": "aperture_height must be greater than 0."}
    if aperture_width <= 0:
        return {"success": False, "message": "aperture_width must be greater than 0."}
    if sill_height < 0:
        return {"success": False, "message": "sill_height cannot be negative."}
    if horizontal_separation is not None and horizontal_separation <= 0:
        return {"success": False, "message": "horizontal_separation must be greater than 0."}
    if tolerance <= 0:
        return {"success": False, "message": "Tolerance value must be greater than 0."}

    faces, not_found = _find_faces(face_identifiers)
    results = []
    for face in faces:
        try:
            resolved_horizontal_separation = _resolve_horizontal_separation(
                face, horizontal_separation, tolerance
            )
            face.apertures_by_width_height_rectangle(
                aperture_height=aperture_height,
                aperture_width=aperture_width,
                sill_height=sill_height,
                horizontal_separation=resolved_horizontal_separation,
                tolerance=tolerance,
            )
            results.append(
                {
                    "face_identifier": face.identifier,
                    "aperture_height": aperture_height,
                    "aperture_width": aperture_width,
                    "sill_height": sill_height,
                    "horizontal_separation": resolved_horizontal_separation,
                    "aperture_count": len(face.apertures),
                    "aperture_identifiers": [ap.identifier for ap in face.apertures],
                }
            )
        except Exception as e:
            results.append({"face_identifier": face.identifier, "error": str(e)})
    return post_edit_pipeline(
        {
            "success": True,
            "message": f"Processed {len(results)} faces, {len(not_found)} faces not found.",
            "results": results,
            "not_found": not_found,
        }
    )


def _normalize_contour_vector(contour_vector):
    contour_vector = contour_vector or [0.0, 1.0]
    if len(contour_vector) != 2:
        raise ValueError("contour_vector must be a list with exactly two elements.")
    return Vector2D(contour_vector[0], contour_vector[1]), contour_vector


def add_louvers_impl(
    aperture_identifiers,
    depth,
    louver_count=None,
    distance=None,
    offset=0,
    angle=0,
    contour_vector=None,
    flip_start_side=False,
    indoor=False,
    tolerance=0.01,
    base_name=None,
):
    ensure_model_loaded()
    if depth <= 0:
        return {"success": False, "message": "depth must be greater than 0."}
    if louver_count is not None and louver_count <= 0:
        return {"success": False, "message": "louver_count must be a positive integer."}
    if distance is not None and distance <= 0:
        return {"success": False, "message": "distance must be greater than 0."}
    if tolerance <= 0:
        return {"success": False, "message": "Tolerance value must be greater than 0."}
    try:
        contour_vector_2d, contour_vector = _normalize_contour_vector(contour_vector)
    except Exception as e:
        return {"success": False, "message": str(e)}

    apertures, not_found = _find_apertures(aperture_identifiers)
    results = []
    for aperture in apertures:
        try:
            shades = aperture.louvers(
                depth=depth,
                louver_count=louver_count,
                distance=distance,
                offset=offset,
                angle=angle,
                contour_vector=contour_vector_2d,
                flip_start_side=flip_start_side,
                indoor=indoor,
                tolerance=tolerance,
                base_name=base_name,
            )
            results.append(
                {
                    "aperture_identifier": aperture.identifier,
                    "depth": depth,
                    "louver_count": louver_count,
                    "distance": distance,
                    "offset": offset,
                    "angle": angle,
                    "contour_vector": contour_vector,
                    "flip_start_side": flip_start_side,
                    "indoor": indoor,
                    "shade_count": len(shades),
                    "shade_identifiers": [shade.identifier for shade in shades],
                }
            )
        except Exception as e:
            results.append({"aperture_identifier": aperture.identifier, "error": str(e)})
    return post_edit_pipeline(
        {
            "success": True,
            "message": f"Processed {len(results)} apertures, {len(not_found)} apertures not found.",
            "results": results,
            "not_found": not_found,
        }
    )


def add_louvers_by_distance_between_impl(
    aperture_identifiers,
    distance,
    depth,
    offset=0,
    angle=0,
    contour_vector=None,
    flip_start_side=False,
    indoor=False,
    tolerance=0.01,
    max_count=None,
    base_name=None,
):
    ensure_model_loaded()
    if distance <= 0:
        return {"success": False, "message": "distance must be greater than 0."}
    if depth <= 0:
        return {"success": False, "message": "depth must be greater than 0."}
    if tolerance < 0:
        return {"success": False, "message": "Tolerance value cannot be negative."}
    if max_count is not None and max_count <= 0:
        return {"success": False, "message": "max_count must be a positive integer."}
    try:
        contour_vector_2d, contour_vector = _normalize_contour_vector(contour_vector)
    except Exception as e:
        return {"success": False, "message": str(e)}

    apertures, not_found = _find_apertures(aperture_identifiers)
    results = []
    for aperture in apertures:
        try:
            shades = aperture.louvers_by_distance_between(
                distance=distance,
                depth=depth,
                offset=offset,
                angle=angle,
                contour_vector=contour_vector_2d,
                flip_start_side=flip_start_side,
                indoor=indoor,
                tolerance=tolerance,
                max_count=max_count,
                base_name=base_name,
            )
            results.append(
                {
                    "aperture_identifier": aperture.identifier,
                    "distance": distance,
                    "depth": depth,
                    "offset": offset,
                    "angle": angle,
                    "contour_vector": contour_vector,
                    "flip_start_side": flip_start_side,
                    "indoor": indoor,
                    "max_count": max_count,
                    "shade_count": len(shades),
                    "shade_identifiers": [shade.identifier for shade in shades],
                }
            )
        except Exception as e:
            results.append({"aperture_identifier": aperture.identifier, "error": str(e)})
    return post_edit_pipeline(
        {
            "success": True,
            "message": f"Processed {len(results)} apertures, {len(not_found)} apertures not found.",
            "results": results,
            "not_found": not_found,
        }
    )


def add_louvers_by_count_impl(
    aperture_identifiers,
    louver_count,
    depth,
    offset=0,
    angle=0,
    contour_vector=None,
    flip_start_side=False,
    indoor=False,
    tolerance=0.01,
    base_name=None,
):
    ensure_model_loaded()
    if louver_count <= 0:
        return {"success": False, "message": "louver_count must be a positive integer."}
    if depth <= 0:
        return {"success": False, "message": "depth must be greater than 0."}
    if tolerance <= 0:
        return {"success": False, "message": "Tolerance value must be greater than 0."}
    try:
        contour_vector_2d, contour_vector = _normalize_contour_vector(contour_vector)
    except Exception as e:
        return {"success": False, "message": str(e)}

    apertures, not_found = _find_apertures(aperture_identifiers)
    results = []
    for aperture in apertures:
        try:
            shades = aperture.louvers_by_count(
                louver_count=louver_count,
                depth=depth,
                offset=offset,
                angle=angle,
                contour_vector=contour_vector_2d,
                flip_start_side=flip_start_side,
                indoor=indoor,
                tolerance=tolerance,
                base_name=base_name,
            )
            results.append(
                {
                    "aperture_identifier": aperture.identifier,
                    "louver_count": louver_count,
                    "depth": depth,
                    "offset": offset,
                    "angle": angle,
                    "contour_vector": contour_vector,
                    "flip_start_side": flip_start_side,
                    "indoor": indoor,
                    "shade_count": len(shades),
                    "shade_identifiers": [shade.identifier for shade in shades],
                }
            )
        except Exception as e:
            results.append({"aperture_identifier": aperture.identifier, "error": str(e)})
    return post_edit_pipeline(
        {
            "success": True,
            "message": f"Processed {len(results)} apertures, {len(not_found)} apertures not found.",
            "results": results,
            "not_found": not_found,
        }
    )
