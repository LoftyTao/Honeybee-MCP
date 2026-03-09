from honeybee_radiance.lib.modifiers import modifier_by_identifier
from honeybee_radiance.lib.modifiersets import modifier_set_by_identifier
from honeybee_radiance.properties.model import ModelRadianceProperties

from .energy_resources import ResourceRecord


RADIANCE_RESOURCE_CATEGORIES = ("modifiers", "modifier_sets")
RADIANCE_RESOURCE_CATEGORY_LABELS = {
    "modifiers": "modifier",
    "modifier_sets": "modifier_set",
}


def empty_radiance_resource_store():
    return {category: {} for category in RADIANCE_RESOURCE_CATEGORIES}


def collect_attached_radiance_resources(model):
    store = empty_radiance_resource_store()
    if model is None:
        return store
    props = model.properties.radiance
    for modifier in props.modifiers:
        store["modifiers"][modifier.identifier] = modifier
    for modifier_set in props.modifier_sets:
        store["modifier_sets"][modifier_set.identifier] = modifier_set
    return store


def load_radiance_resource_store(model_dict, model=None):
    store = empty_radiance_resource_store()
    radiance_root = model_dict.get("properties", {}).get("radiance")
    if radiance_root:
        modifiers, modifier_sets = ModelRadianceProperties.load_properties_from_dict(model_dict)
        store["modifiers"].update(modifiers)
        store["modifier_sets"].update(modifier_sets)
    attached = collect_attached_radiance_resources(model)
    for category in RADIANCE_RESOURCE_CATEGORIES:
        store[category].update(attached[category])
    return store


def get_effective_radiance_resource_store(model, base_store):
    combined = empty_radiance_resource_store()
    base_store = base_store or empty_radiance_resource_store()
    for category in RADIANCE_RESOURCE_CATEGORIES:
        combined[category].update(base_store.get(category, {}))
    attached = collect_attached_radiance_resources(model)
    for category in RADIANCE_RESOURCE_CATEGORIES:
        combined[category].update(attached[category])
    return combined


def _serialize_resource(obj):
    if hasattr(obj, "to_dict"):
        try:
            return obj.to_dict(abridged=True)
        except TypeError:
            return obj.to_dict()
    raise TypeError("Radiance resource '{}' does not support to_dict().".format(type(obj).__name__))


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


def merge_model_dict_with_radiance_resources(model_dict, model, base_store):
    merged = dict(model_dict)
    merged.setdefault("properties", {})
    merged["properties"] = dict(merged["properties"])
    merged["properties"].setdefault("radiance", {"type": "ModelRadianceProperties"})
    radiance = dict(merged["properties"]["radiance"])
    merged["properties"]["radiance"] = radiance

    store = get_effective_radiance_resource_store(model, base_store)
    for category in RADIANCE_RESOURCE_CATEGORIES:
        existing = radiance.get(category, []) or []
        additions = [_serialize_resource(obj) for obj in store[category].values()]
        radiance[category] = _merge_resource_array(existing, additions)
    return merged


def get_radiance_resources_for_category(manager, category):
    store = get_effective_radiance_resource_store(manager.model, manager.radiance_resource_store)
    return store.get(category, {})


def get_radiance_resource_records(manager, categories=None):
    store = get_effective_radiance_resource_store(manager.model, manager.radiance_resource_store)
    attached = collect_attached_radiance_resources(manager.model)
    records = []
    for category in categories or RADIANCE_RESOURCE_CATEGORIES:
        attached_ids = set(attached.get(category, {}).keys())
        for identifier, obj in store.get(category, {}).items():
            source = "model_attached" if identifier in attached_ids else "session_store"
            records.append(ResourceRecord(obj, category, source))
    return records


def register_radiance_resource(manager, category, obj):
    manager.radiance_resource_store.setdefault(category, {})
    manager.radiance_resource_store[category][obj.identifier] = obj
    return obj


def unregister_radiance_resource(manager, category, identifier):
    return manager.radiance_resource_store.get(category, {}).pop(identifier, None)


def resolve_modifier(manager, identifier):
    if not identifier:
        return None
    modifier = get_radiance_resources_for_category(manager, "modifiers").get(identifier)
    if modifier is not None:
        return modifier
    try:
        return modifier_by_identifier(identifier)
    except Exception:
        return None


def resolve_modifier_set(manager, identifier):
    if not identifier:
        return None
    modifier_set = get_radiance_resources_for_category(manager, "modifier_sets").get(identifier)
    if modifier_set is not None:
        return modifier_set
    try:
        return modifier_set_by_identifier(identifier)
    except Exception:
        return None


def radiance_identifier_taken(manager, category, identifier):
    if identifier in get_radiance_resources_for_category(manager, category):
        return True
    if category == "modifiers" and resolve_modifier(manager, identifier) is not None:
        return True
    if category == "modifier_sets" and resolve_modifier_set(manager, identifier) is not None:
        return True
    return False
