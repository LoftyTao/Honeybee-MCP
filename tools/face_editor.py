from .mcp_context import mcp
from tools.load_model import manager
from honeybee.face import Face

@mcp.tool()
def add_aperture_by_width_height(
    face_identifiers: list,
    width: float,
    height: float,
    sill_height: float = 1.0,
    aperture_identifier: str = None
) -> dict:
    """
    Add a rectangular aperture (window) at the center of each face.
    
    This tool creates a single rectangular aperture centered on each specified face.
    The aperture is positioned with the specified sill height from the bottom
    of the face.
    
    Args:
        face_identifiers: List of face identifiers to add apertures to.
            Faces can be from rooms or orphaned faces.
        width: Width of the aperture in meters. Must be greater than 0.
        height: Height of the aperture in meters. Must be greater than 0.
        sill_height: Height of the sill from the face bottom in meters.
            Default is 1.0m (typical window sill height).
        aperture_identifier: Optional base identifier for the aperture.
            If not provided, an identifier will be auto-generated.
    
    Returns:
        dict: Dictionary containing:
            - success (bool): Whether the operation was successful
            - message (str): Summary of processed faces
            - results (list): List of results for each face with:
                - face_identifier (str): Face ID
                - aperture_identifier (str): Created aperture ID
                - width, height, sill_height (float): Aperture dimensions
                - error (str): Error if aperture creation failed
            - not_found (list): Face identifiers that were not found
    
    Example:
        add_aperture_by_width_height(["Face_1", "Face_2"], 1.5, 2.0)
        add_aperture_by_width_height(["South_Face"], 2.0, 1.5, 0.9)
    """
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded. Please use load_model to load a model first."
        }

    # Validate aperture dimensions
    if width <= 0 or height <= 0:
        return {
            "success": False,
            "message": "Aperture width and height must be greater than 0."
        }

    if sill_height < 0:
        return {
            "success": False,
            "message": "Sill height cannot be negative."
        }

    results = []
    not_found = []

    # Process each face identifier in the list
    for face_id in face_identifiers:
        face = None

        # Search for face in rooms first
        for room in manager.model.rooms:
            for f in room.faces:
                if f.identifier == face_id:
                    face = f
                    break
            if face is not None:
                break

        # If not found in rooms, search orphaned faces
        if face is None:
            for f in manager.model.orphaned_faces:
                if f.identifier == face_id:
                    face = f
                    break

        # Handle case where face is not found
        if face is None:
            not_found.append(face_id)
            continue

        # Add aperture to the face
        try:
            aperture = face.aperture_by_width_height(
                width=width,
                height=height,
                sill_height=sill_height,
                aperture_identifier=aperture_identifier
            )

            results.append({
                "face_identifier": face_id,
                "aperture_identifier": aperture.identifier,
                "width": width,
                "height": height,
                "sill_height": sill_height
            })
        except Exception as e:
            results.append({
                "face_identifier": face_id,
                "error": str(e)
            })

    return {
        "success": True,
        "message": f"Processed {len(results)} faces, {len(not_found)} faces not found.",
        "results": results,
        "not_found": not_found
    }


@mcp.tool()
def add_apertures_by_ratio_rectangle(
    face_identifiers: list,
    ratio: float,
    aperture_height: float = None,
    sill_height: float = 0.9,
    horizontal_separation: float = None,
    vertical_separation: float = 0,
    tolerance: float = 0.01
) -> dict:
    """
    Add rectangular apertures to faces based on area ratio.
    
    This tool creates multiple rectangular apertures on each specified face,
    with the total area equal to the specified ratio of the face area.
    Apertures are distributed across the face with optional separation.
    
    Args:
        face_identifiers: List of face identifiers to add apertures to.
        ratio: Window-to-wall ratio (WWR) as a decimal (e.g., 0.4 for 40%).
            Must be between 0 and 0.95.
        aperture_height: Height of each aperture in meters. If not specified,
            apertures will be sized automatically based on face dimensions.
        sill_height: Height of the sill from the face bottom in meters.
            Default is 0.9m.
        horizontal_separation: Horizontal distance between apertures in meters.
            If not specified, separation is calculated automatically.
        vertical_separation: Vertical distance between rows of apertures.
            Default is 0 (single row).
        tolerance: Geometric tolerance for calculations in meters. Default is 0.01.
    
    Returns:
        dict: Dictionary containing:
            - success (bool): Whether the operation was successful
            - message (str): Summary of processed faces
            - results (list): List of results for each face with:
                - face_identifier (str): Face ID
                - ratio (float): Applied WWR
                - aperture_count (int): Number of apertures created
                - aperture_identifiers (list): IDs of created apertures
                - error (str): Error if creation failed
            - not_found (list): Face identifiers not found
    
    Example:
        add_apertures_by_ratio_rectangle(["South_Face"], 0.4)  # 40% WWR
        add_apertures_by_ratio_rectangle(["Face_1"], 0.3, aperture_height=1.5)
    """
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded. Please use load_model to load a model first."
        }

    # Validate ratio
    if ratio <= 0 or ratio >= 0.95:
        return {
            "success": False,
            "message": "Ratio must be between 0 and 0.95."
        }

    # Validate optional parameters
    if aperture_height is not None and aperture_height <= 0:
        return {
            "success": False,
            "message": "aperture_height must be greater than 0."
        }

    if sill_height < 0:
        return {
            "success": False,
            "message": "sill_height cannot be negative."
        }

    if horizontal_separation is not None and horizontal_separation <= 0:
        return {
            "success": False,
            "message": "horizontal_separation must be greater than 0."
        }

    if vertical_separation < 0:
        return {
            "success": False,
            "message": "vertical_separation cannot be negative."
        }

    if tolerance <= 0:
        return {
            "success": False,
            "message": "Tolerance value must be greater than 0."
        }

    results = []
    not_found = []

    # Process each face identifier in the list
    for face_id in face_identifiers:
        face = None

        # Search for face in rooms first
        for room in manager.model.rooms:
            for f in room.faces:
                if f.identifier == face_id:
                    face = f
                    break
            if face is not None:
                break

        # If not found in rooms, search orphaned faces
        if face is None:
            for f in manager.model.orphaned_faces:
                if f.identifier == face_id:
                    face = f
                    break

        # Handle case where face is not found
        if face is None:
            not_found.append(face_id)
            continue

        # Add apertures to the face
        try:
            face.apertures_by_ratio_rectangle(
                ratio=ratio,
                aperture_height=aperture_height,
                sill_height=sill_height,
                horizontal_separation=horizontal_separation,
                vertical_separation=vertical_separation,
                tolerance=tolerance
            )

            aperture_identifiers = [ap.identifier for ap in face.apertures]

            results.append({
                "face_identifier": face_id,
                "ratio": ratio,
                "aperture_count": len(aperture_identifiers),
                "aperture_identifiers": aperture_identifiers
            })
        except Exception as e:
            results.append({
                "face_identifier": face_id,
                "error": str(e)
            })

    return {
        "success": True,
        "message": f"Processed {len(results)} faces, {len(not_found)} faces not found.",
        "results": results,
        "not_found": not_found
    }


@mcp.tool()
def add_apertures_by_ratio(
    face_identifiers: list,
    ratio: float,
    tolerance: float = 0.01,
    rect_split: bool = True
) -> dict:
    """
    Add apertures to faces based on area ratio.
    
    This tool creates apertures on each specified face with the total area
    equal to the specified ratio of the face area. Apertures can be split
    into multiple rectangular windows or created as a single polygon.
    
    Args:
        face_identifiers: List of face identifiers to add apertures to.
        ratio: Window-to-wall ratio (WWR) as a decimal (e.g., 0.4 for 40%).
            Must be between 0 and 1 (exclusive).
        tolerance: Geometric tolerance for calculations in meters. Default is 0.01.
        rect_split: If True, split apertures into rectangular windows.
            If False, create single polygon apertures. Default is True.
    
    Returns:
        dict: Dictionary containing:
            - success (bool): Whether the operation was successful
            - message (str): Summary of processed faces
            - results (list): List of results for each face
            - not_found (list): Face identifiers not found
    
    Example:
        add_apertures_by_ratio(["Face_1"], 0.4)  # 40% WWR, rectangular
        add_apertures_by_ratio(["Face_2"], 0.3, rect_split=False)  # Single polygon
    """
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded. Please use load_model to load a model first."
        }

    # Validate ratio
    if ratio <= 0 or ratio >= 1:
        return {
            "success": False,
            "message": "Ratio must be between 0 and 1 (cannot equal 0 or 1)."
        }

    # Validate tolerance
    if tolerance <= 0:
        return {
            "success": False,
            "message": "Tolerance value must be greater than 0."
        }

    results = []
    not_found = []

    # Process each face identifier in the list
    for face_id in face_identifiers:
        face = None

        # Search for face in rooms first
        for room in manager.model.rooms:
            for f in room.faces:
                if f.identifier == face_id:
                    face = f
                    break
            if face is not None:
                break

        # If not found in rooms, search orphaned faces
        if face is None:
            for f in manager.model.orphaned_faces:
                if f.identifier == face_id:
                    face = f
                    break

        # Handle case where face is not found
        if face is None:
            not_found.append(face_id)
            continue

        # Add apertures to the face
        try:
            face.apertures_by_ratio(
                ratio=ratio,
                tolerance=tolerance,
                rect_split=rect_split
            )

            aperture_identifiers = [ap.identifier for ap in face.apertures]

            results.append({
                "face_identifier": face_id,
                "ratio": ratio,
                "aperture_count": len(aperture_identifiers),
                "aperture_identifiers": aperture_identifiers
            })
        except Exception as e:
            results.append({
                "face_identifier": face_id,
                "error": str(e)
            })

    return {
        "success": True,
        "message": f"Processed {len(results)} faces, {len(not_found)} faces not found.",
        "results": results,
        "not_found": not_found
    }


@mcp.tool()
def add_apertures_by_ratio_gridded(
    face_identifiers: list,
    ratio: float,
    x_dim: float,
    y_dim: float = None,
    tolerance: float = 0.01
) -> dict:
    """
    Add apertures to faces in a grid pattern based on area ratio.
    
    This tool creates a grid of rectangular apertures on each specified face.
    The total aperture area equals the specified ratio of the face area.
    Apertures are arranged in a regular grid pattern.
    
    Args:
        face_identifiers: List of face identifiers to add apertures to.
        ratio: Window-to-wall ratio (WWR) as a decimal (e.g., 0.4 for 40%).
            Must be between 0 and 1 (exclusive).
        x_dim: Horizontal dimension of each aperture in meters.
        y_dim: Vertical dimension of each aperture in meters. If not specified,
            uses x_dim value (square apertures).
        tolerance: Geometric tolerance for calculations in meters. Default is 0.01.
    
    Returns:
        dict: Dictionary containing:
            - success (bool): Whether the operation was successful
            - message (str): Summary of processed faces
            - results (list): List of results for each face
            - not_found (list): Face identifiers not found
    
    Example:
        add_apertures_by_ratio_gridded(["Face_1"], 0.4, 1.0, 1.5)  # 1m x 1.5m grid
        add_apertures_by_ratio_gridded(["Face_2"], 0.3, 0.6)  # 0.6m square grid
    """
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded. Please use load_model to load a model first."
        }

    # Validate ratio
    if ratio <= 0 or ratio >= 1:
        return {
            "success": False,
            "message": "Ratio must be between 0 and 1 (cannot equal 0 or 1)."
        }

    # Validate dimensions
    if x_dim <= 0:
        return {
            "success": False,
            "message": "x_dim must be greater than 0."
        }

    if y_dim is not None and y_dim <= 0:
        return {
            "success": False,
            "message": "y_dim must be greater than 0."
        }

    # Validate tolerance
    if tolerance <= 0:
        return {
            "success": False,
            "message": "Tolerance value must be greater than 0."
        }

    results = []
    not_found = []

    # Process each face identifier in the list
    for face_id in face_identifiers:
        face = None

        # Search for face in rooms first
        for room in manager.model.rooms:
            for f in room.faces:
                if f.identifier == face_id:
                    face = f
                    break
            if face is not None:
                break

        # If not found in rooms, search orphaned faces
        if face is None:
            for f in manager.model.orphaned_faces:
                if f.identifier == face_id:
                    face = f
                    break

        # Handle case where face is not found
        if face is None:
            not_found.append(face_id)
            continue

        # Add apertures to the face
        try:
            face.apertures_by_ratio_gridded(
                ratio=ratio,
                x_dim=x_dim,
                y_dim=y_dim,
                tolerance=tolerance
            )

            aperture_identifiers = [ap.identifier for ap in face.apertures]

            results.append({
                "face_identifier": face_id,
                "ratio": ratio,
                "x_dim": x_dim,
                "y_dim": y_dim,
                "aperture_count": len(aperture_identifiers),
                "aperture_identifiers": aperture_identifiers
            })
        except Exception as e:
            results.append({
                "face_identifier": face_id,
                "error": str(e)
            })

    return {
        "success": True,
        "message": f"Processed {len(results)} faces, {len(not_found)} faces not found.",
        "results": results,
        "not_found": not_found
    }


@mcp.tool()
def add_apertures_by_width_height_rectangle(
    face_identifiers: list,
    aperture_height: float,
    aperture_width: float,
    sill_height: float = 0.9,
    horizontal_separation: float = None,
    tolerance: float = 0.01
) -> dict:
    """
    Add repeated rectangular apertures to faces based on width and height.
    
    This tool creates multiple rectangular apertures across each specified face.
    Apertures are repeated horizontally across the face with the specified
    dimensions and separation.
    
    Args:
        face_identifiers: List of face identifiers to add apertures to.
        aperture_height: Height of each aperture in meters. Must be greater than 0.
        aperture_width: Width of each aperture in meters. Must be greater than 0.
        sill_height: Height of the sill from the face bottom in meters.
            Default is 0.9m.
        horizontal_separation: Horizontal distance between apertures in meters.
            If not specified, apertures are evenly distributed.
        tolerance: Geometric tolerance for calculations in meters. Default is 0.01.
    
    Returns:
        dict: Dictionary containing:
            - success (bool): Whether the operation was successful
            - message (str): Summary of processed faces
            - results (list): List of results for each face
            - not_found (list): Face identifiers not found
    
    Example:
        add_apertures_by_width_height_rectangle(["Face_1"], 1.5, 1.0)  # 1.5m x 1m windows
        add_apertures_by_width_height_rectangle(["Face_2"], 2.0, 1.2, 0.8, 0.5)  # With separation
    """
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded. Please use load_model to load a model first."
        }

    # Validate dimensions
    if aperture_height <= 0:
        return {
            "success": False,
            "message": "aperture_height must be greater than 0."
        }

    if aperture_width <= 0:
        return {
            "success": False,
            "message": "aperture_width must be greater than 0."
        }

    if sill_height < 0:
        return {
            "success": False,
            "message": "sill_height cannot be negative."
        }

    if horizontal_separation is not None and horizontal_separation <= 0:
        return {
            "success": False,
            "message": "horizontal_separation must be greater than 0."
        }

    # Validate tolerance
    if tolerance <= 0:
        return {
            "success": False,
            "message": "Tolerance value must be greater than 0."
        }

    results = []
    not_found = []

    # Process each face identifier in the list
    for face_id in face_identifiers:
        face = None

        # Search for face in rooms first
        for room in manager.model.rooms:
            for f in room.faces:
                if f.identifier == face_id:
                    face = f
                    break
            if face is not None:
                break

        # If not found in rooms, search orphaned faces
        if face is None:
            for f in manager.model.orphaned_faces:
                if f.identifier == face_id:
                    face = f
                    break

        # Handle case where face is not found
        if face is None:
            not_found.append(face_id)
            continue

        # Add apertures to the face
        try:
            face.apertures_by_width_height_rectangle(
                aperture_height=aperture_height,
                aperture_width=aperture_width,
                sill_height=sill_height,
                horizontal_separation=horizontal_separation,
                tolerance=tolerance
            )

            aperture_identifiers = [ap.identifier for ap in face.apertures]

            results.append({
                "face_identifier": face_id,
                "aperture_height": aperture_height,
                "aperture_width": aperture_width,
                "sill_height": sill_height,
                "horizontal_separation": horizontal_separation,
                "aperture_count": len(aperture_identifiers),
                "aperture_identifiers": aperture_identifiers
            })
        except Exception as e:
            results.append({
                "face_identifier": face_id,
                "error": str(e)
            })

    return {
        "success": True,
        "message": f"Processed {len(results)} faces, {len(not_found)} faces not found.",
        "results": results,
        "not_found": not_found
    }


@mcp.tool()
def remove_face_objects(
    face_identifiers: list,
    apertures: bool = False,
    doors: bool = False,
    indoor_shades: bool = False,
    outdoor_shades: bool = False,
    sub_faces: bool = False
) -> dict:
    """
    Remove objects from specified faces.
    
    This tool removes apertures, doors, and/or shades from the specified faces.
    Multiple object types can be removed in a single call by setting multiple
    flags to True.
    
    Args:
        face_identifiers: List of face identifiers to remove objects from.
        apertures: If True, remove all apertures from the faces. Default is False.
        doors: If True, remove all doors from the faces. Default is False.
        indoor_shades: If True, remove all indoor shades from the faces. Default is False.
        outdoor_shades: If True, remove all outdoor shades from the faces. Default is False.
        sub_faces: If True, remove all sub-faces (apertures AND doors). This is a
            shortcut that overrides apertures and doors flags. Default is False.
    
    Returns:
        dict: Dictionary containing:
            - success (bool): Whether the operation was successful
            - message (str): Summary of processed faces
            - results (list): List of results for each face with:
                - face_identifier (str): Face ID
                - removed_objects (list): List of removed object types with counts
            - not_found (list): Face identifiers not found
    
    Example:
        remove_face_objects(["Face_1"], apertures=True)  # Remove windows only
        remove_face_objects(["Face_2"], sub_faces=True)  # Remove windows and doors
        remove_face_objects(["Face_3"], outdoor_shades=True, indoor_shades=True)
    """
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded. Please use load_model to load a model first."
        }

    # Validate that at least one object type is selected
    if not any([apertures, doors, indoor_shades, outdoor_shades, sub_faces]):
        return {
            "success": False,
            "message": "At least one object type must be selected for removal."
        }

    results = []
    not_found = []

    # Process each face identifier in the list
    for face_id in face_identifiers:
        face = None

        # Search for face in rooms first
        for room in manager.model.rooms:
            for f in room.faces:
                if f.identifier == face_id:
                    face = f
                    break
            if face is not None:
                break

        # If not found in rooms, search orphaned faces
        if face is None:
            for f in manager.model.orphaned_faces:
                if f.identifier == face_id:
                    face = f
                    break

        # Handle case where face is not found
        if face is None:
            not_found.append(face_id)
            continue

        # Track removed objects
        removed_objects = []

        # Remove sub-faces if requested
        if sub_faces:
            removed_count = len(face.apertures) + len(face.doors)
            face.remove_sub_faces()
            removed_objects.append(f"Sub-faces ({removed_count})")
        else:
            # Remove apertures if requested
            if apertures:
                removed_count = len(face.apertures)
                face.remove_apertures()
                removed_objects.append(f"Apertures ({removed_count})")

            # Remove doors if requested
            if doors:
                removed_count = len(face.doors)
                face.remove_doors()
                removed_objects.append(f"Doors ({removed_count})")

        # Remove indoor shades if requested
        if indoor_shades:
            removed_count = len(face.indoor_shades)
            face.remove_indoor_shades()
            removed_objects.append(f"Indoor shades ({removed_count})")

        # Remove outdoor shades if requested
        if outdoor_shades:
            removed_count = len(face.outdoor_shades)
            face.remove_outdoor_shades()
            removed_objects.append(f"Outdoor shades ({removed_count})")

        # Add result for this face
        results.append({
            "face_identifier": face_id,
            "removed_objects": removed_objects
        })

    return {
        "success": True,
        "message": f"Processed {len(results)} faces, {len(not_found)} faces not found.",
        "results": results,
        "not_found": not_found
    }
