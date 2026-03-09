def summarize_model(model) -> dict:
    """Build a compact summary for the currently loaded model."""
    return {
        "display_name": model.display_name,
        "identifier": model.identifier,
        "floor_area": sum(room.floor_area for room in model.rooms),
        "rooms_count": len(model.rooms),
        "outdoor_shades_count": len(model.outdoor_shades),
        "orphaned_faces_count": len(model.orphaned_faces),
        "orphaned_shades_count": len(model.orphaned_shades) + len(model.shade_meshes),
        "orphaned_apertures_count": len(model.orphaned_apertures),
        "orphaned_doors_count": len(model.orphaned_doors),
    }
