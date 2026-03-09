from ..mcp_context import mcp
from ..state.hooks import ensure_model_loaded
from .service import visualization_service


@mcp.tool()
def visualization(
    target_type: str = "model",
    identifiers: list = None,
    vis_options: dict = None,
    export_formats: list = None,
    output_folder: str = None,
    name: str = None,
    svg_options: dict = None,
    return_visualization_set: bool = None,
) -> dict:
    """
    Export the current Honeybee model or selected objects as a VisualizationSet and optional files.
    """
    try:
        ensure_model_loaded()
        return visualization_service(
            target_type=target_type,
            identifiers=identifiers,
            vis_options=vis_options,
            export_formats=export_formats,
            output_folder=output_folder,
            name=name,
            svg_options=svg_options,
            return_visualization_set=return_visualization_set,
        )
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}
