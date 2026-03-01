from .mcp_context import mcp
from tools.load_model import manager
from honeybee.aperture import  Aperture

@mcp.tool()
def add_louvers(
    aperture_identifiers: list,
    depth: float,
    louver_count: int = None,
    distance: float = None,
    offset: float = 0,
    angle: float = 0,
    contour_vector: list = None,
    flip_start_side: bool = False,
    indoor: bool = False,
    tolerance: float = 0.01,
    base_name: str = None
) -> dict:
    """
    Add a series of shading louvers to apertures.
    
    This tool creates horizontal or angled shading louvers on the specified
    apertures. Louvers can be specified by count or by spacing distance.
    
    Args:
        aperture_identifiers: List of aperture identifiers to add louvers to.
        depth: Depth of each louver in meters. Must be greater than 0.
        louver_count: Number of louvers to create. If specified with distance,
            louver_count takes priority.
        distance: Spacing between louvers in meters. Alternative to louver_count.
        offset: Distance to offset louvers from the aperture in meters. Default is 0.
        angle: Angle of louvers in degrees (0 = horizontal). Default is 0.
        contour_vector: 2D vector [x, y] defining louver direction. Default is [0, 1]
            (vertical arrangement, horizontal louvers).
        flip_start_side: If True, start louvers from the opposite side. Default is False.
        indoor: If True, create indoor shades (blinds). If False, create outdoor shades.
            Default is False.
        tolerance: Geometric tolerance for calculations in meters. Default is 0.01.
        base_name: Base name for generated shade identifiers. If not provided,
            names are auto-generated.
    
    Returns:
        dict: Dictionary containing:
            - success (bool): Whether the operation was successful
            - message (str): Summary of processed apertures
            - results (list): List of results for each aperture with:
                - aperture_identifier (str): Aperture ID
                - shade_count (int): Number of louvers created
                - shade_identifiers (list): IDs of created louvers
                - error (str): Error if creation failed
            - not_found (list): Aperture identifiers not found
    
    Example:
        add_louvers(["Window_1"], depth=0.3, louver_count=5)  # 5 louvers, 30cm deep
        add_louvers(["Window_2"], depth=0.2, distance=0.15)  # 15cm spacing
        add_louvers(["Window_3"], depth=0.25, louver_count=4, angle=30)  # 30° angle
    """
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded. Please use load_model to load a model first."
        }

    # Validate depth
    if depth <= 0:
        return {
            "success": False,
            "message": "depth must be greater than 0."
        }

    # Validate louver_count
    if louver_count is not None and louver_count <= 0:
        return {
            "success": False,
            "message": "louver_count must be a positive integer."
        }

    # Validate distance
    if distance is not None and distance <= 0:
        return {
            "success": False,
            "message": "distance must be greater than 0."
        }

    # Validate tolerance
    if tolerance <= 0:
        return {
            "success": False,
            "message": "Tolerance value must be greater than 0."
        }

    # Set default contour vector if not provided
    if contour_vector is None:
        contour_vector = [0.0, 1.0]

    # Validate contour_vector has exactly 2 elements
    if len(contour_vector) != 2:
        return {
            "success": False,
            "message": "contour_vector must be a list with exactly two elements."
        }

    # Import Vector2D for contour vector validation
    from ladybug_geometry.geometry2d import Vector2D

    # Create Vector2D object from contour vector
    try:
        contour_vector_2d = Vector2D(contour_vector[0], contour_vector[1])
    except Exception as e:
        return {
            "success": False,
            "message": f"Invalid contour_vector: {str(e)}"
        }

    results = []
    not_found = []

    # Process each aperture identifier in the list
    for aperture_id in aperture_identifiers:
        aperture = None

        # Search for aperture in rooms first
        for room in manager.model.rooms:
            for face in room.faces:
                for ap in face.apertures:
                    if ap.identifier == aperture_id:
                        aperture = ap
                        break
                if aperture is not None:
                    break
            if aperture is not None:
                break

        # If not found in rooms, search orphaned apertures
        if aperture is None:
            for ap in manager.model.orphaned_apertures:
                if ap.identifier == aperture_id:
                    aperture = ap
                    break

        # Handle case where aperture is not found
        if aperture is None:
            not_found.append(aperture_id)
            continue

        # Add louvers to the aperture
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
                base_name=base_name
            )

            shade_identifiers = [shade.identifier for shade in shades]

            results.append({
                "aperture_identifier": aperture_id,
                "depth": depth,
                "louver_count": louver_count,
                "distance": distance,
                "offset": offset,
                "angle": angle,
                "contour_vector": contour_vector,
                "flip_start_side": flip_start_side,
                "indoor": indoor,
                "shade_count": len(shade_identifiers),
                "shade_identifiers": shade_identifiers
            })
        except Exception as e:
            results.append({
                "aperture_identifier": aperture_id,
                "error": str(e)
            })

    return {
        "success": True,
        "message": f"Processed {len(results)} apertures, {len(not_found)} apertures not found.",
        "results": results,
        "not_found": not_found
    }


@mcp.tool()
def add_louvers_by_distance_between(
    aperture_identifiers: list,
    distance: float,
    depth: float,
    offset: float = 0,
    angle: float = 0,
    contour_vector: list = None,
    flip_start_side: bool = False,
    indoor: bool = False,
    tolerance: float = 0.01,
    max_count: int = None,
    base_name: str = None
) -> dict:
    """
    Add shading louvers to apertures to achieve target louver spacing.
    
    This tool creates louvers with a specified spacing between them.
    The number of louvers is calculated based on the aperture height and spacing.
    
    Args:
        aperture_identifiers: List of aperture identifiers to add louvers to.
        distance: Target spacing between louvers in meters. Must be greater than 0.
        depth: Depth of each louver in meters. Must be greater than 0.
        offset: Distance to offset louvers from the aperture in meters. Default is 0.
        angle: Angle of louvers in degrees (0 = horizontal). Default is 0.
        contour_vector: 2D vector [x, y] defining louver direction. Default is [0, 1].
        flip_start_side: If True, start louvers from the opposite side. Default is False.
        indoor: If True, create indoor shades. If False, create outdoor shades. Default is False.
        tolerance: Geometric tolerance in meters. Default is 0.01.
        max_count: Maximum number of louvers to create. Optional limit.
        base_name: Base name for generated shade identifiers.
    
    Returns:
        dict: Dictionary containing success status, results list, and not_found list.
    
    Example:
        add_louvers_by_distance_between(["Window_1"], distance=0.2, depth=0.3)
    """
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded. Please use load_model to load a model first."
        }

    # Validate distance
    if distance <= 0:
        return {
            "success": False,
            "message": "distance must be greater than 0."
        }

    # Validate depth
    if depth <= 0:
        return {
            "success": False,
            "message": "depth must be greater than 0."
        }

    # Validate tolerance
    if tolerance < 0:
        return {
            "success": False,
            "message": "Tolerance value cannot be negative."
        }

    # Validate max_count
    if max_count is not None and max_count <= 0:
        return {
            "success": False,
            "message": "max_count must be a positive integer."
        }

    # Set default contour vector if not provided
    if contour_vector is None:
        contour_vector = [0.0, 1.0]

    # Validate contour_vector has exactly 2 elements
    if len(contour_vector) != 2:
        return {
            "success": False,
            "message": "contour_vector must be a list with exactly two elements."
        }

    # Import Vector2D for contour vector validation
    from ladybug_geometry.geometry2d import Vector2D

    # Create Vector2D object from contour vector
    try:
        contour_vector_2d = Vector2D(contour_vector[0], contour_vector[1])
    except Exception as e:
        return {
            "success": False,
            "message": f"Invalid contour_vector: {str(e)}"
        }

    results = []
    not_found = []

    # Process each aperture identifier in the list
    for aperture_id in aperture_identifiers:
        aperture = None

        # Search for aperture in rooms first
        for room in manager.model.rooms:
            for face in room.faces:
                for ap in face.apertures:
                    if ap.identifier == aperture_id:
                        aperture = ap
                        break
                if aperture is not None:
                    break
            if aperture is not None:
                break

        # If not found in rooms, search orphaned apertures
        if aperture is None:
            for ap in manager.model.orphaned_apertures:
                if ap.identifier == aperture_id:
                    aperture = ap
                    break

        # Handle case where aperture is not found
        if aperture is None:
            not_found.append(aperture_id)
            continue

        # Add louvers to the aperture
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
                base_name=base_name
            )

            shade_identifiers = [shade.identifier for shade in shades]

            results.append({
                "aperture_identifier": aperture_id,
                "distance": distance,
                "depth": depth,
                "offset": offset,
                "angle": angle,
                "contour_vector": contour_vector,
                "flip_start_side": flip_start_side,
                "indoor": indoor,
                "max_count": max_count,
                "shade_count": len(shade_identifiers),
                "shade_identifiers": shade_identifiers
            })
        except Exception as e:
            results.append({
                "aperture_identifier": aperture_id,
                "error": str(e)
            })

    return {
        "success": True,
        "message": f"Processed {len(results)} apertures, {len(not_found)} apertures not found.",
        "results": results,
        "not_found": not_found
    }


@mcp.tool()
def add_louvers_by_count(
    aperture_identifiers: list,
    louver_count: int,
    depth: float,
    offset: float = 0,
    angle: float = 0,
    contour_vector: list = None,
    flip_start_side: bool = False,
    indoor: bool = False,
    tolerance: float = 0.01,
    base_name: str = None
) -> dict:
    """
    Add shading louvers to apertures to achieve target louver count.
    
    This tool creates a specific number of louvers evenly distributed across
    the aperture height.
    
    Args:
        aperture_identifiers: List of aperture identifiers to add louvers to.
        louver_count: Number of louvers to create. Must be a positive integer.
        depth: Depth of each louver in meters. Must be greater than 0.
        offset: Distance to offset louvers from the aperture in meters. Default is 0.
        angle: Angle of louvers in degrees (0 = horizontal). Default is 0.
        contour_vector: 2D vector [x, y] defining louver direction. Default is [0, 1].
        flip_start_side: If True, start louvers from the opposite side. Default is False.
        indoor: If True, create indoor shades. If False, create outdoor shades. Default is False.
        tolerance: Geometric tolerance in meters. Default is 0.01.
        base_name: Base name for generated shade identifiers.
    
    Returns:
        dict: Dictionary containing success status, results list, and not_found list.
    
    Example:
        add_louvers_by_count(["Window_1"], louver_count=5, depth=0.3)
    """
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded. Please use load_model to load a model first."
        }

    # Validate louver_count
    if louver_count <= 0:
        return {
            "success": False,
            "message": "louver_count must be a positive integer."
        }

    # Validate depth
    if depth <= 0:
        return {
            "success": False,
            "message": "depth must be greater than 0."
        }

    # Validate tolerance
    if tolerance <= 0:
        return {
            "success": False,
            "message": "Tolerance value must be greater than 0."
        }

    # Set default contour vector if not provided
    if contour_vector is None:
        contour_vector = [0.0, 1.0]

    # Validate contour_vector has exactly 2 elements
    if len(contour_vector) != 2:
        return {
            "success": False,
            "message": "contour_vector must be a list with exactly two elements."
        }

    # Import Vector2D for contour vector validation
    from ladybug_geometry.geometry2d import Vector2D

    # Create Vector2D object from contour vector
    try:
        contour_vector_2d = Vector2D(contour_vector[0], contour_vector[1])
    except Exception as e:
        return {
            "success": False,
            "message": f"Invalid contour_vector: {str(e)}"
        }

    results = []
    not_found = []

    # Process each aperture identifier in the list
    for aperture_id in aperture_identifiers:
        aperture = None

        # Search for aperture in rooms first
        for room in manager.model.rooms:
            for face in room.faces:
                for ap in face.apertures:
                    if ap.identifier == aperture_id:
                        aperture = ap
                        break
                if aperture is not None:
                    break
            if aperture is not None:
                break

        # If not found in rooms, search orphaned apertures
        if aperture is None:
            for ap in manager.model.orphaned_apertures:
                if ap.identifier == aperture_id:
                    aperture = ap
                    break

        # Handle case where aperture is not found
        if aperture is None:
            not_found.append(aperture_id)
            continue

        # Add louvers to the aperture
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
                base_name=base_name
            )

            shade_identifiers = [shade.identifier for shade in shades]

            results.append({
                "aperture_identifier": aperture_id,
                "louver_count": louver_count,
                "depth": depth,
                "offset": offset,
                "angle": angle,
                "contour_vector": contour_vector,
                "flip_start_side": flip_start_side,
                "indoor": indoor,
                "shade_count": len(shade_identifiers),
                "shade_identifiers": shade_identifiers
            })
        except Exception as e:
            results.append({
                "aperture_identifier": aperture_id,
                "error": str(e)
            })

    return {
        "success": True,
        "message": f"Processed {len(results)} apertures, {len(not_found)} apertures not found.",
        "results": results,
        "not_found": not_found
    }
