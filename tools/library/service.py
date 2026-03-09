try:
    from honeybee.search import filter_array_by_keywords
except ImportError:
    filter_array_by_keywords = None

try:
    from honeybee_energy.lib.programtypes import STANDARDS_REGISTRY, PROGRAM_TYPES
    from honeybee_energy.lib.schedules import SCHEDULES
    from honeybee_energy.lib.scheduletypelimits import SCHEDULE_TYPE_LIMITS
    from honeybee_energy.lib.constructions import (
        OPAQUE_CONSTRUCTIONS,
        SHADE_CONSTRUCTIONS,
        WINDOW_CONSTRUCTIONS,
    )
except ImportError:
    STANDARDS_REGISTRY = {}
    PROGRAM_TYPES = []
    SCHEDULES = []
    SCHEDULE_TYPE_LIMITS = []
    OPAQUE_CONSTRUCTIONS = []
    WINDOW_CONSTRUCTIONS = []
    SHADE_CONSTRUCTIONS = []

try:
    from honeybee_radiance.lib.modifiers import MODIFIERS
    from honeybee_radiance.lib.modifiersets import MODIFIER_SETS
except ImportError:
    MODIFIERS = []
    MODIFIER_SETS = []

from ..state.energy_resources import get_resources_for_category
from ..state.radiance_resources import get_radiance_resources_for_category
from ..state.manager import manager


CONSTRUCTION_TYPES = ("SteelFramed", "WoodFramed", "Mass", "Metal Building")


def _keyword_match(values, search_terms, split_words):
    if not search_terms:
        return sorted(values)
    return sorted(filter_array_by_keywords(sorted(values), search_terms, split_words))


def _build_resource_results(category, library_values, model_values, search_terms, split_words):
    rows = []
    for source_name, values in (
        ("library", library_values),
        ("model_resource", model_values.get("model_attached", [])),
        ("session_resource", model_values.get("session_store", [])),
    ):
        filtered = _keyword_match(values, search_terms, split_words)
        rows.extend([{"identifier": identifier, "source": source_name} for identifier in filtered])
    return rows


def search_properties_service(
    category: str,
    keywords: list = None,
    vintage: str = None,
    climate_zone: str = None,
    construction_type: str = None,
    building_program: str = None,
    exact_match: bool = False,
) -> dict:
    if filter_array_by_keywords is None:
        return {"status": "error", "message": "Honeybee libraries not installed."}

    search_terms = keywords if keywords else []
    split_words = not exact_match
    category_lower = category.lower()
    effective_store = {
        "schedules": get_resources_for_category(manager, "schedules"),
        "schedule_type_limits": get_resources_for_category(manager, "schedule_type_limits"),
        "constructions": get_resources_for_category(manager, "constructions"),
        "modifiers": get_radiance_resources_for_category(manager, "modifiers"),
        "modifier_sets": get_radiance_resources_for_category(manager, "modifier_sets"),
    }

    if category_lower == "constructionset":
        sel_vintage = vintage if vintage else "2019"
        sel_type = construction_type if construction_type else "SteelFramed"
        if sel_vintage not in STANDARDS_REGISTRY:
            return {
                "status": "error",
                "message": f"Vintage '{sel_vintage}' not valid. Options: {list(STANDARDS_REGISTRY.keys())}",
            }
        if sel_type not in CONSTRUCTION_TYPES:
            return {
                "status": "error",
                "message": f"Construction Type '{sel_type}' not valid. Options: {CONSTRUCTION_TYPES}",
            }
        if not climate_zone:
            return {"status": "error", "message": "climate_zone is required for ConstructionSet search."}
        try:
            cz_str = str(climate_zone).strip()
            cz_num = int(cz_str[0])
            if not (1 <= cz_num <= 8):
                raise ValueError
        except (ValueError, IndexError):
            return {
                "status": "error",
                "message": f"Climate Zone '{climate_zone}' must start with 1-8.",
            }
        identifier = f"{sel_vintage}::ClimateZone{cz_num}::{sel_type}"
        return {
            "status": "success",
            "category": "ConstructionSet",
            "results": [identifier],
            "note": "Construction Sets are generated based on inputs, not searched from a list.",
        }

    if category_lower == "programtype":
        results = []
        if building_program:
            sel_vintage = vintage if vintage else "2019"
            if sel_vintage not in STANDARDS_REGISTRY:
                return {
                    "status": "error",
                    "message": f"Vintage '{sel_vintage}' invalid. Options: {list(STANDARDS_REGISTRY.keys())}",
                }
            vintage_subset = STANDARDS_REGISTRY[sel_vintage]
            if building_program not in vintage_subset:
                return {
                    "status": "error",
                    "message": f"Building '{building_program}' not found in {sel_vintage}. Options: {list(vintage_subset.keys())[:10]}...",
                }
            room_programs = vintage_subset[building_program]
            if search_terms:
                room_programs = filter_array_by_keywords(room_programs, search_terms, split_words)
            results = [f"{sel_vintage}::{building_program}::{rp}" for rp in room_programs]
        else:
            base_list = sorted(PROGRAM_TYPES)
            if vintage:
                base_list = filter_array_by_keywords(base_list, [vintage], False)
            if search_terms:
                base_list = filter_array_by_keywords(base_list, search_terms, split_words)
            results = base_list
        return {
            "status": "success",
            "category": "ProgramType",
            "count": len(results),
            "results": results,
        }

    if category_lower == "construction":
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
                "shade": res_shade,
            },
            "total_count": len(res_opaque) + len(res_window) + len(res_shade),
        }

    if category_lower == "schedule":
        attached_schedule_ids = {schedule.identifier for schedule in manager.model.properties.energy.schedules} if manager.model else set()
        model_values = {
            "model_attached": sorted(attached_schedule_ids),
            "session_store": sorted(set(effective_store["schedules"].keys()) - attached_schedule_ids),
        }
        results = _build_resource_results("Schedule", sorted(SCHEDULES), model_values, search_terms, split_words)
        return {
            "status": "success",
            "category": "Schedule",
            "count": len(results),
            "results": results,
        }

    if category_lower == "scheduletypelimit":
        attached_type_limit_ids = {obj.identifier for obj in manager.model.properties.energy.schedule_type_limits} if manager.model else set()
        model_values = {
            "model_attached": sorted(attached_type_limit_ids),
            "session_store": sorted(set(effective_store["schedule_type_limits"].keys()) - attached_type_limit_ids),
        }
        results = _build_resource_results(
            "ScheduleTypeLimit",
            sorted(SCHEDULE_TYPE_LIMITS),
            model_values,
            search_terms,
            split_words,
        )
        return {
            "status": "success",
            "category": "ScheduleTypeLimit",
            "count": len(results),
            "results": results,
        }

    if category_lower == "modifierset":
        attached_ids = {obj.identifier for obj in manager.model.properties.radiance.modifier_sets} if manager.model else set()
        model_values = {
            "model_attached": sorted(attached_ids),
            "session_store": sorted(set(effective_store["modifier_sets"].keys()) - attached_ids),
        }
        results = _build_resource_results("ModifierSet", sorted(MODIFIER_SETS), model_values, search_terms, split_words)
        return {"status": "success", "category": "ModifierSet", "count": len(results), "results": results}

    if category_lower == "modifier":
        attached_ids = {obj.identifier for obj in manager.model.properties.radiance.modifiers} if manager.model else set()
        model_values = {
            "model_attached": sorted(attached_ids),
            "session_store": sorted(set(effective_store["modifiers"].keys()) - attached_ids),
        }
        results = _build_resource_results("Modifier", sorted(MODIFIERS), model_values, search_terms, split_words)
        return {"status": "success", "category": "Modifier", "count": len(results), "results": results}

    return {
        "status": "error",
        "message": f"Unknown category '{category}'. Valid: Construction, ConstructionSet, ProgramType, Schedule, ScheduleTypeLimit, Modifier, ModifierSet",
    }
