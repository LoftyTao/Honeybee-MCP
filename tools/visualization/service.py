import os

import honeybee_display  # noqa: F401 - imports patch Honeybee classes with display methods
import ladybug_vtk  # noqa: F401 - imports patch VisualizationSet with vtk/html methods
from ladybug_display.visualization import VisualizationSet

from ..operations.common import resolve_targets
from ..state.energy_resources import dump_json
from ..state.manager import manager


SUPPORTED_TARGET_TYPES = ("model", "room", "face", "aperture", "door", "subface", "shade")
SUPPORTED_EXPORT_FORMATS = ("vsf", "svg", "html", "vtkjs")
COMMON_VIS_OPTION_KEYS = {"color_by", "include_wireframe"}
MODEL_VIS_OPTION_KEYS = {
    "use_mesh",
    "hide_color_by",
    "grid_display_mode",
    "hide_grid",
    "grid_data_path",
    "grid_data_display_mode",
    "active_grid_data",
}
OBJECT_VIS_OPTION_KEYS = {
    "room": {"include_sub_faces", "include_shades"},
    "face": {"include_sub_faces", "include_shades"},
    "aperture": {"include_shades"},
    "door": {"include_shades"},
    "subface": {"include_shades"},
    "shade": set(),
}
SVG_OPTION_KEYS = {
    "width",
    "height",
    "margin",
    "interactive",
    "render_3d_legend",
    "render_2d_legend",
    "view",
}


def visualization_service(
    target_type: str = "model",
    identifiers=None,
    vis_options: dict = None,
    export_formats=None,
    output_folder: str = None,
    name: str = None,
    svg_options: dict = None,
    return_visualization_set: bool = None,
) -> dict:
    target_type = (target_type or "model").lower().strip()
    if target_type not in SUPPORTED_TARGET_TYPES:
        return {
            "success": False,
            "error": "Unsupported visualization target_type '{}'".format(target_type),
            "available_target_types": list(SUPPORTED_TARGET_TYPES),
        }

    vis_options = vis_options or {}
    svg_options = svg_options or {}
    export_formats = _normalize_export_formats(export_formats)
    if isinstance(export_formats, dict):
        return export_formats

    vis_validation = _validate_vis_options(target_type, vis_options)
    if vis_validation is not None:
        return vis_validation

    svg_validation = _validate_svg_options(svg_options)
    if svg_validation is not None:
        return svg_validation

    if target_type == "model":
        objects = [manager.model]
        missing = []
    else:
        objects, missing = resolve_targets(target_type, identifiers)
        if len(objects) == 0:
            return {
                "success": False,
                "target_type": target_type,
                "count": 0,
                "missing": missing,
                "error": "No valid targets found for visualization.",
                "hint": "Check the provided identifiers or query the target type first.",
            }

    vis_set = _build_visualization_set(target_type, objects, vis_options, name)
    if vis_set is None:
        return {
            "success": False,
            "target_type": target_type,
            "count": len(objects),
            "missing": missing,
            "error": "Visualization produced no geometry.",
            "hint": "Adjust vis_options or include_wireframe to generate visible output.",
        }

    base_name = _resolve_export_name(name=name, target_type=target_type)
    exports = {}
    if export_formats:
        export_folder = output_folder or os.getcwd()
        os.makedirs(export_folder, exist_ok=True)
        exports = _export_visualization_set(vis_set, export_formats, export_folder, base_name, svg_options)

    include_vis_dict = _should_return_visualization_set(return_visualization_set, export_formats)
    result = {
        "success": True,
        "target_type": target_type,
        "count": len(objects),
        "missing": missing,
        "summary": _summarize_visualization_set(vis_set),
        "exports": exports,
    }
    if include_vis_dict:
        result["visualization_set"] = vis_set.to_dict()
    return result


def _normalize_export_formats(export_formats):
    if export_formats is None:
        return []
    if isinstance(export_formats, str):
        export_formats = [export_formats]
    if not isinstance(export_formats, (list, tuple, set)):
        return {
            "success": False,
            "error": "export_formats must be a string or a list of strings.",
            "available_export_formats": list(SUPPORTED_EXPORT_FORMATS),
        }

    normalized = []
    invalid = []
    for fmt in export_formats:
        value = str(fmt).lower().strip()
        if value not in SUPPORTED_EXPORT_FORMATS:
            invalid.append(value)
            continue
        if value not in normalized:
            normalized.append(value)
    if invalid:
        return {
            "success": False,
            "error": "Unsupported export format(s): {}".format(", ".join(invalid)),
            "available_export_formats": list(SUPPORTED_EXPORT_FORMATS),
        }
    return normalized


def _validate_vis_options(target_type: str, vis_options: dict):
    if not isinstance(vis_options, dict):
        return {"success": False, "error": "vis_options must be a dictionary."}

    allowed = set(COMMON_VIS_OPTION_KEYS)
    if target_type == "model":
        allowed.update(MODEL_VIS_OPTION_KEYS)
    else:
        allowed.update(OBJECT_VIS_OPTION_KEYS[target_type])

    invalid_keys = sorted(set(vis_options.keys()) - allowed)
    if invalid_keys:
        return {
            "success": False,
            "error": "Unsupported vis_options for target_type '{}': {}".format(
                target_type, ", ".join(invalid_keys)
            ),
            "allowed_vis_options": sorted(allowed),
        }

    color_by = str(vis_options.get("color_by", "type")).lower()
    if color_by not in ("type", "boundary_condition", "none"):
        return {
            "success": False,
            "error": "Unsupported color_by '{}'".format(color_by),
            "allowed_color_by": ["type", "boundary_condition", "none"],
        }
    return None


def _validate_svg_options(svg_options: dict):
    if not isinstance(svg_options, dict):
        return {"success": False, "error": "svg_options must be a dictionary."}
    invalid_keys = sorted(set(svg_options.keys()) - SVG_OPTION_KEYS)
    if invalid_keys:
        return {
            "success": False,
            "error": "Unsupported svg_options: {}".format(", ".join(invalid_keys)),
            "allowed_svg_options": sorted(SVG_OPTION_KEYS),
        }
    return None


def _build_visualization_set(target_type: str, objects, vis_options: dict, name: str = None):
    if target_type == "model":
        model_options = _model_vis_options(vis_options)
        return manager.model.to_vis_set(**model_options)

    color_by = str(vis_options.get("color_by", "type")).lower()
    include_wireframe = vis_options.get("include_wireframe", True)
    base_name = _resolve_export_name(name=name, target_type=target_type)
    vis_set = VisualizationSet(base_name, [], manager.model.units)
    vis_set.display_name = base_name

    added_geometry = 0
    for obj in objects:
        if color_by != "none":
            source_vis_set = obj.to_vis_set(color_by=color_by)
            added_geometry += _merge_vis_set(vis_set, source_vis_set, obj.identifier)

        if include_wireframe:
            wireframe_vis_set = _object_wireframe_vis_set(target_type, obj, vis_options)
            if wireframe_vis_set is not None:
                added_geometry += _merge_vis_set(vis_set, wireframe_vis_set, "{}_wireframe".format(obj.identifier))

    return vis_set if added_geometry > 0 else None


def _model_vis_options(vis_options: dict):
    options = {
        "color_by": str(vis_options.get("color_by", "type")).lower(),
        "include_wireframe": vis_options.get("include_wireframe", True),
    }
    for key in MODEL_VIS_OPTION_KEYS:
        if key in vis_options:
            options[key] = vis_options[key]
    return options


def _object_wireframe_vis_set(target_type: str, obj, vis_options: dict):
    include_sub_faces = vis_options.get("include_sub_faces", True)
    include_shades = vis_options.get("include_shades", True)

    if target_type in ("room", "face"):
        return obj.to_vis_set_wireframe(include_sub_faces=include_sub_faces, include_shades=include_shades, color=None)
    if target_type in ("aperture", "door", "subface"):
        return obj.to_vis_set_wireframe(include_shades=include_shades, color=None)
    if target_type == "shade":
        return obj.to_vis_set_wireframe(color=None)
    return None


def _merge_vis_set(target_vis_set: VisualizationSet, source_vis_set: VisualizationSet, prefix: str):
    added = 0
    for index, geometry in enumerate(source_vis_set.geometry):
        geo_copy = geometry.duplicate() if hasattr(geometry, "duplicate") else geometry
        geo_id = getattr(geo_copy, "identifier", "geometry_{}".format(index))
        geo_copy.identifier = "{}_{}_{}".format(prefix, geo_id, index)
        if getattr(geo_copy, "display_name", None) is None:
            geo_copy.display_name = geo_copy.identifier
        target_vis_set.add_geometry(geo_copy)
        added += 1
    return added


def _resolve_export_name(name: str = None, target_type: str = "model"):
    if name:
        return _strip_known_suffixes(name)
    if target_type == "model":
        return manager.model.identifier
    return "{}_{}_selection".format(manager.model.identifier, target_type)


def _strip_known_suffixes(name: str):
    for suffix in (".vsf", ".svg", ".html", ".vtkjs"):
        if name.lower().endswith(suffix):
            return name[: -len(suffix)]
    return name


def _export_visualization_set(
    vis_set: VisualizationSet,
    export_formats,
    output_folder: str,
    base_name: str,
    svg_options: dict,
):
    exports = {}
    if "vsf" in export_formats:
        vsf_path = os.path.join(output_folder, "{}.vsf".format(base_name))
        dump_json(vsf_path, vis_set.to_dict(), indent=2)
        exports["vsf"] = vsf_path
    if "svg" in export_formats:
        svg_path = os.path.join(output_folder, "{}.svg".format(base_name))
        svg_obj = vis_set.to_svg(**_svg_options(svg_options))
        with open(svg_path, "w", encoding="utf-8") as fp:
            fp.write(str(svg_obj))
        exports["svg"] = svg_path
    if "html" in export_formats:
        exports["html"] = vis_set.to_html(output_folder, base_name, open=False)
    if "vtkjs" in export_formats:
        exports["vtkjs"] = vis_set.to_vtkjs(output_folder, base_name)
    return exports


def _svg_options(svg_options: dict):
    options = {"width": 800, "height": 600}
    options.update(svg_options or {})
    return options


def _should_return_visualization_set(return_visualization_set, export_formats):
    if return_visualization_set is not None:
        return bool(return_visualization_set)
    return len(export_formats) == 0


def _summarize_visualization_set(vis_set: VisualizationSet):
    return {
        "type": "VisualizationSet",
        "identifier": vis_set.identifier,
        "display_name": vis_set.display_name,
        "geometry_count": len(vis_set.geometry),
        "units": vis_set.units,
    }
