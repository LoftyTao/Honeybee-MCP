from ..mcp_context import mcp
from .service import search_properties_service


@mcp.tool()
def search_properties(
    category: str,
    keywords: list = None,
    vintage: str = None,
    climate_zone: str = None,
    construction_type: str = None,
    building_program: str = None,
    exact_match: bool = False,
) -> dict:
    """
    Search for Honeybee properties including Constructions, Modifiers, Program Types, and Construction Sets.
    """
    return search_properties_service(
        category=category,
        keywords=keywords,
        vintage=vintage,
        climate_zone=climate_zone,
        construction_type=construction_type,
        building_program=building_program,
        exact_match=exact_match,
    )
