import copy
import inspect
import json
from dataclasses import dataclass

from honeybee_energy.lib.schedules import schedule_by_identifier
from honeybee_energy.lib.scheduletypelimits import schedule_type_limit_by_identifier
from honeybee_energy.properties.model import ModelEnergyProperties
from honeybee_energy.schedule.day import ScheduleDay
from honeybee_energy.schedule.fixedinterval import ScheduleFixedInterval
from honeybee_energy.schedule.ruleset import ScheduleRuleset
from honeybee_energy.schedule.typelimit import ScheduleTypeLimit


CUSTOM_SCHEDULE_DAYS_KEY = "_mcp_schedule_days"
RESOURCE_CATEGORIES = (
    "schedule_type_limits",
    "schedule_days",
    "schedules",
    "materials",
    "constructions",
    "construction_sets",
    "program_types",
    "hvacs",
    "shws",
)
HBJSON_RESOURCE_CATEGORIES = (
    "schedule_type_limits",
    "schedules",
    "materials",
    "constructions",
    "construction_sets",
    "program_types",
    "hvacs",
    "shws",
)
RESOURCE_CATEGORY_LABELS = {
    "schedule_type_limits": "schedule_type_limit",
    "schedule_days": "schedule_day",
    "schedules": "schedule",
    "materials": "material",
    "constructions": "construction",
    "construction_sets": "construction_set",
    "program_types": "program_type",
    "hvacs": "hvac",
    "shws": "shw",
}


@dataclass
class ResourceRecord:
    resource: object
    resource_category: str
    resource_source: str

    @property
    def identifier(self):
        return getattr(self.resource, "identifier", None)

    def __getattr__(self, item):
        return getattr(self.resource, item)


def empty_energy_resource_store():
    return {category: {} for category in RESOURCE_CATEGORIES}


def _copy_model_dict(model_dict):
    return copy.deepcopy(model_dict)


def _get_energy_root(model_dict, create=False):
    if create:
        model_dict.setdefault("properties", {})
        model_dict["properties"].setdefault("energy", {"type": "ModelEnergyProperties"})
    return model_dict.get("properties", {}).get("energy")


def strip_custom_energy_fields(model_dict):
    clean_dict = _copy_model_dict(model_dict)
    energy = _get_energy_root(clean_dict)
    if not energy:
        return clean_dict
    for key in list(energy.keys()):
        if key.startswith("_mcp_"):
            del energy[key]
    return clean_dict


def _add_resource(bucket, obj):
    identifier = getattr(obj, "identifier", None)
    if identifier:
        bucket[identifier] = obj


def _collect_schedule_days_from_schedule(schedule):
    days = {}
    if not isinstance(schedule, ScheduleRuleset):
        return days

    for day in (
        schedule.default_day_schedule,
        schedule.holiday_schedule,
        schedule.summer_designday_schedule,
        schedule.winter_designday_schedule,
    ):
        if day is not None:
            days[day.identifier] = day

    for rule in schedule.schedule_rules:
        if rule.schedule_day is not None:
            days[rule.schedule_day.identifier] = rule.schedule_day
    return days


def _serialize_resource(obj):
    if obj is None:
        return None
    if hasattr(obj, "to_dict"):
        try:
            signature = inspect.signature(obj.to_dict)
            if "abridged" in signature.parameters:
                return obj.to_dict(abridged=True)
        except (TypeError, ValueError):
            pass
        return obj.to_dict()
    raise TypeError("Resource '{}' does not support to_dict().".format(type(obj).__name__))


def _merge_resource_array(existing, additions):
    merged = []
    index = {}

    for item in existing or []:
        identifier = item.get("identifier")
        if identifier is None or identifier in index:
            continue
        index[identifier] = len(merged)
        merged.append(item)

    for item in additions or []:
        identifier = item.get("identifier")
        if identifier is None:
            continue
        if identifier in index:
            merged[index[identifier]] = item
        else:
            index[identifier] = len(merged)
            merged.append(item)
    return merged


def collect_attached_energy_resources(model):
    store = empty_energy_resource_store()
    if model is None:
        return store

    energy_props = model.properties.energy
    for category in HBJSON_RESOURCE_CATEGORIES:
        for obj in getattr(energy_props, category):
            _add_resource(store[category], obj)

    for schedule in store["schedules"].values():
        store["schedule_days"].update(_collect_schedule_days_from_schedule(schedule))
    return store


def get_effective_energy_resource_store(model, base_store):
    combined = empty_energy_resource_store()
    base_store = base_store or empty_energy_resource_store()
    for category in RESOURCE_CATEGORIES:
        combined[category].update(base_store.get(category, {}))

    attached = collect_attached_energy_resources(model)
    for category in RESOURCE_CATEGORIES:
        combined[category].update(attached[category])
    return combined


def load_energy_resource_store(model_dict, model=None):
    store = empty_energy_resource_store()
    if not model_dict:
        return store

    energy_root = _get_energy_root(model_dict)
    if not energy_root:
        return store

    clean_dict = strip_custom_energy_fields(model_dict)
    (
        materials,
        constructions,
        construction_sets,
        schedule_type_limits,
        schedules,
        program_types,
        hvacs,
        shws,
    ) = ModelEnergyProperties.load_properties_from_dict(clean_dict, skip_invalid=True)

    store["materials"].update(materials)
    store["constructions"].update(constructions)
    store["construction_sets"].update(construction_sets)
    store["schedule_type_limits"].update(schedule_type_limits)
    store["schedules"].update(schedules)
    store["program_types"].update(program_types)
    store["hvacs"].update(hvacs)
    store["shws"].update(shws)

    for schedule in schedules.values():
        store["schedule_days"].update(_collect_schedule_days_from_schedule(schedule))

    for day_dict in energy_root.get(CUSTOM_SCHEDULE_DAYS_KEY, []) or []:
        day = ScheduleDay.from_dict(day_dict)
        store["schedule_days"][day.identifier] = day

    attached = collect_attached_energy_resources(model)
    for category in RESOURCE_CATEGORIES:
        store[category].update(attached[category])
    return store


def merge_model_dict_with_energy_resources(model_dict, base_store):
    merged_dict = _copy_model_dict(model_dict)
    energy_root = _get_energy_root(merged_dict, create=True)
    energy_root.setdefault("type", "ModelEnergyProperties")

    effective_store = get_effective_energy_resource_store(None, base_store)
    for category in HBJSON_RESOURCE_CATEGORIES:
        existing = energy_root.get(category, []) or []
        additions = [_serialize_resource(obj) for obj in effective_store[category].values()]
        energy_root[category] = _merge_resource_array(existing, additions)

    schedule_days = [_serialize_resource(obj) for obj in effective_store["schedule_days"].values()]
    if schedule_days:
        energy_root[CUSTOM_SCHEDULE_DAYS_KEY] = _merge_resource_array(
            energy_root.get(CUSTOM_SCHEDULE_DAYS_KEY, []) or [],
            schedule_days,
        )
    elif CUSTOM_SCHEDULE_DAYS_KEY in energy_root:
        del energy_root[CUSTOM_SCHEDULE_DAYS_KEY]
    return merged_dict


def build_serializable_model_dict(model, base_store):
    if model is None:
        return None
    base_dict = model.to_dict()
    effective_store = get_effective_energy_resource_store(model, base_store)
    return merge_model_dict_with_energy_resources(base_dict, effective_store)


def get_model_resource_store_from_manager(manager):
    return get_effective_energy_resource_store(manager.model, manager.energy_resource_store)


def get_resources_for_category(manager, category):
    store = get_model_resource_store_from_manager(manager)
    return store.get(category, {})


def get_resource_records(manager, categories=None):
    store = get_model_resource_store_from_manager(manager)
    records = []
    category_list = categories or RESOURCE_CATEGORIES

    attached = collect_attached_energy_resources(manager.model)
    for category in category_list:
        attached_ids = set(attached.get(category, {}).keys())
        for identifier, obj in store.get(category, {}).items():
            source = "model_attached" if identifier in attached_ids else "session_store"
            records.append(ResourceRecord(obj, category, source))
    return records


def get_resource_record_index(manager, categories=None):
    return {record.identifier: record for record in get_resource_records(manager, categories)}


def register_resource(manager, category, obj):
    manager.energy_resource_store.setdefault(category, {})
    manager.energy_resource_store[category][obj.identifier] = obj
    if category == "schedules":
        manager.energy_resource_store.setdefault("schedule_days", {})
        manager.energy_resource_store["schedule_days"].update(_collect_schedule_days_from_schedule(obj))
    return obj


def unregister_resource(manager, category, identifier):
    bucket = manager.energy_resource_store.get(category, {})
    return bucket.pop(identifier, None)


def _library_schedule(identifier):
    try:
        return schedule_by_identifier(identifier)
    except Exception:
        return None


def _library_schedule_type_limit(identifier):
    try:
        return schedule_type_limit_by_identifier(identifier)
    except Exception:
        return None


def resolve_schedule(manager, identifier):
    if not identifier:
        return None
    schedule = get_resources_for_category(manager, "schedules").get(identifier)
    return schedule if schedule is not None else _library_schedule(identifier)


def resolve_schedule_type_limit(manager, identifier):
    if not identifier:
        return None
    type_limit = get_resources_for_category(manager, "schedule_type_limits").get(identifier)
    return type_limit if type_limit is not None else _library_schedule_type_limit(identifier)


def resolve_schedule_day(manager, identifier):
    if not identifier:
        return None
    return get_resources_for_category(manager, "schedule_days").get(identifier)


def resource_identifier_taken(manager, category, identifier):
    if not identifier:
        return False
    if identifier in get_resources_for_category(manager, category):
        return True
    if category == "schedules" and _library_schedule(identifier) is not None:
        return True
    if category == "schedule_type_limits" and _library_schedule_type_limit(identifier) is not None:
        return True
    return False


def serialize_resource_value(value):
    if value is None:
        return None
    if isinstance(value, ResourceRecord):
        return {
            "identifier": value.identifier,
            "resource_category": value.resource_category,
            "resource_source": value.resource_source,
        }
    if hasattr(value, "to_dict") and not hasattr(value, "identifier"):
        return value.to_dict()
    return value


def dump_json(path, data, indent=None):
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=indent)
