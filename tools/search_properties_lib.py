import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .mcp_context import mcp

# --- Safe Imports for Honeybee Dependencies ---
try:
    from honeybee.search import filter_array_by_keywords
except ImportError:
    filter_array_by_keywords = None

try:
    from honeybee_energy.lib.programtypes import STANDARDS_REGISTRY, PROGRAM_TYPES
    from honeybee_energy.lib.constructions import OPAQUE_CONSTRUCTIONS, \
        WINDOW_CONSTRUCTIONS, SHADE_CONSTRUCTIONS
except ImportError:
    STANDARDS_REGISTRY = {}
    PROGRAM_TYPES = []
    OPAQUE_CONSTRUCTIONS = []
    WINDOW_CONSTRUCTIONS = []
    SHADE_CONSTRUCTIONS = []

try:
    from honeybee_radiance.lib.modifiers import MODIFIERS
    from honeybee_radiance.lib.modifiersets import MODIFIER_SETS
except ImportError:
    MODIFIERS = []
    MODIFIER_SETS = []


# Constants for Construction Sets
CONSTRUCTION_TYPES = ('SteelFramed', 'WoodFramed', 'Mass', 'Metal Building')


@mcp.tool()
def search_properties(
    category: str,
    keywords: list[str] = None,
    vintage: str = None,
    climate_zone: str = None,
    construction_type: str = None,
    building_program: str = None,
    exact_match: bool = False
) -> dict:
    """
    Search for various Honeybee properties including Constructions, Modifiers, 
    Program Types, and Construction Sets.

    Args:
        category: Search target. Options: 
                  'Construction', 'ConstructionSet', 'ProgramType', 
                  'Modifier', 'ModifierSet'.
        keywords: List of words to filter results (e.g. ["Office", "Open"]).
        vintage: Standard year (e.g. 'ASHRAE_2019', '2019'). Used for ConstrSet/Program.
        climate_zone: Climate zone number (1-8). Used for ConstructionSet.
        construction_type: 'SteelFramed', 'WoodFramed', 'Mass', 'Metal Building'.
        building_program: Building type (e.g. 'Office', 'School'). Used for ProgramType.
        exact_match: If True, treats keywords as a joined phrase.
    """
    
    if filter_array_by_keywords is None:
        return {"status": "error", "message": "Honeybee libraries not installed."}

    # Normalize inputs
    search_terms = keywords if keywords else []
    split_words = not exact_match
    
    # -------------------------------------------------------------------------
    # 1. Construction Sets (Logic: Construct Identifier)
    # -------------------------------------------------------------------------
    if category.lower() == "constructionset":
        # Defaults
        sel_vintage = vintage if vintage else '2019'
        sel_type = construction_type if construction_type else 'SteelFramed'
        
        # Validation: Vintage
        if sel_vintage not in STANDARDS_REGISTRY:
            return {
                "status": "error", 
                "message": f"Vintage '{sel_vintage}' not valid. Options: {list(STANDARDS_REGISTRY.keys())}"
            }
        
        # Validation: Construction Type
        if sel_type not in CONSTRUCTION_TYPES:
            return {
                "status": "error",
                "message": f"Construction Type '{sel_type}' not valid. Options: {CONSTRUCTION_TYPES}"
            }

        # Validation: Climate Zone
        if not climate_zone:
            return {"status": "error", "message": "climate_zone is required for ConstructionSet search."}
        
        # Parse Climate Zone (strip qualifiers like '4A' -> '4')
        try:
            cz_str = str(climate_zone).strip()
            cz_num = int(cz_str[0])
            if not (1 <= cz_num <= 8): raise ValueError
        except (ValueError, IndexError):
            return {"status": "error", "message": f"Climate Zone '{climate_zone}' must start with 1-8."}

        # Format Result
        identifier = f"{sel_vintage}::ClimateZone{cz_num}::{sel_type}"
        return {
            "status": "success",
            "category": "ConstructionSet",
            "results": [identifier],
            "note": "Construction Sets are generated based on inputs, not searched from a list."
        }

    # -------------------------------------------------------------------------
    # 2. Program Types (Logic: Registry Lookup OR Global Search)
    # -------------------------------------------------------------------------
    elif category.lower() == "programtype":
        results = []
        
        # Sub-mode A: Specific Building Hierarchy Search
        if building_program:
            sel_vintage = vintage if vintage else '2019'
            
            # 1. Validate Vintage
            if sel_vintage not in STANDARDS_REGISTRY:
                return {
                    "status": "error", 
                    "message": f"Vintage '{sel_vintage}' invalid. Options: {list(STANDARDS_REGISTRY.keys())}"
                }
            
            vintage_subset = STANDARDS_REGISTRY[sel_vintage]
            
            # 2. Validate Building Program
            if building_program not in vintage_subset:
                return {
                    "status": "error",
                    "message": f"Building '{building_program}' not found in {sel_vintage}. Options: {list(vintage_subset.keys())[:10]}..."
                }
            
            # 3. Get Room Programs & Filter
            room_programs = vintage_subset[building_program]
            if search_terms:
                room_programs = filter_array_by_keywords(room_programs, search_terms, split_words)
            
            # 4. Construct Identifiers
            results = [f"{sel_vintage}::{building_program}::{rp}" for rp in room_programs]
            
        # Sub-mode B: Global Library Search
        else:
            base_list = sorted(PROGRAM_TYPES)
            # Filter by vintage if provided
            if vintage:
                base_list = filter_array_by_keywords(base_list, [vintage], False)
            # Filter by keywords
            if search_terms:
                base_list = filter_array_by_keywords(base_list, search_terms, split_words)
            results = base_list

        return {
            "status": "success",
            "category": "ProgramType",
            "count": len(results),
            "results": results
        }

    # -------------------------------------------------------------------------
    # 3. Constructions (Logic: Filter Global Lists)
    # -------------------------------------------------------------------------
    elif category.lower() == "construction":
        # Determine scope based on keywords or return all
        res_opaque = sorted(OPAQUE_CONSTRUCTIONS)
        res_window = sorted(WINDOW_CONSTRUCTIONS)
        res_shade = sorted(SHADE_CONSTRUCTIONS)

        if search_terms:
            res_opaque = sorted(filter_array_by_keywords(res_opaque, search_terms, split_words))
            res_window = sorted(filter_array_by_keywords(res_window, search_terms, split_words))
            res_shade = sorted(filter_array_by_keywords(res_shade, search_terms, split_words))

        return {
            "status": "success",
            "category": "Construction",
            "results": {
                "opaque": res_opaque,
                "window": res_window,
                "shade": res_shade
            },
            "total_count": len(res_opaque) + len(res_window) + len(res_shade)
        }

    # -------------------------------------------------------------------------
    # 4. Modifiers & Modifier Sets (Logic: Filter Global Lists)
    # -------------------------------------------------------------------------
    elif category.lower() == "modifierset":
        source = sorted(MODIFIER_SETS)
        if search_terms:
            source = sorted(filter_array_by_keywords(source, search_terms, split_words))
        return {"status": "success", "category": "ModifierSet", "count": len(source), "results": source}

    elif category.lower() == "modifier":
        source = sorted(MODIFIERS)
        if search_terms:
            source = sorted(filter_array_by_keywords(source, search_terms, split_words))
        return {"status": "success", "category": "Modifier", "count": len(source), "results": source}

    else:
        return {
            "status": "error", 
            "message": f"Unknown category '{category}'. Valid: Construction, ConstructionSet, ProgramType, Modifier, ModifierSet"
        }