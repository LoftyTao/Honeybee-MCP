from honeybee.typing import clean_and_id_ep_string
from honeybee_energy.load.equipment import ElectricEquipment
from honeybee_energy.load.hotwater import ServiceHotWater
from honeybee_energy.load.lighting import Lighting
from honeybee_energy.load.people import People
from honeybee_energy.load.process import Process
from honeybee_energy.load.setpoint import Setpoint
from honeybee_energy.load.ventilation import Ventilation
from honeybee_energy.schedule.day import ScheduleDay
from honeybee_energy.schedule.fixedinterval import ScheduleFixedInterval
from honeybee_energy.schedule.rule import ScheduleRule
from honeybee_energy.schedule.ruleset import ScheduleRuleset
from honeybee_energy.schedule.typelimit import ScheduleTypeLimit

from ..state.energy_resources import (
    get_resources_for_category,
    register_resource,
    resolve_schedule,
    resolve_schedule_day,
    resolve_schedule_type_limit,
    resource_identifier_taken,
    unregister_resource,
)
from ..state.hooks import post_edit_pipeline
from ..state.manager import manager


ROOM_LOAD_METADATA = {
    "people": {
        "private_attr": "_people",
        "public_attr": "people",
        "class": People,
        "default_suffix": "People",
        "schedule_fields": {
            "occupancy_schedule": ("occupancy_schedule_identifier", "occupancy_schedule_definition"),
            "activity_schedule": ("activity_schedule_identifier", "activity_schedule_definition"),
        },
    },
    "lighting": {
        "private_attr": "_lighting",
        "public_attr": "lighting",
        "class": Lighting,
        "default_suffix": "Lighting",
        "schedule_fields": {"schedule": ("schedule_identifier", "schedule_definition")},
    },
    "electric_equipment": {
        "private_attr": "_electric_equipment",
        "public_attr": "electric_equipment",
        "class": ElectricEquipment,
        "default_suffix": "Equipment",
        "schedule_fields": {"schedule": ("schedule_identifier", "schedule_definition")},
    },
    "service_hot_water": {
        "private_attr": "_service_hot_water",
        "public_attr": "service_hot_water",
        "class": ServiceHotWater,
        "default_suffix": "SHW",
        "schedule_fields": {"schedule": ("schedule_identifier", "schedule_definition")},
    },
    "setpoint": {
        "private_attr": "_setpoint",
        "public_attr": "setpoint",
        "class": Setpoint,
        "default_suffix": "Setpoint",
        "schedule_fields": {
            "heating_schedule": ("heating_schedule_identifier", "heating_schedule_definition"),
            "cooling_schedule": ("cooling_schedule_identifier", "cooling_schedule_definition"),
            "humidifying_schedule": ("humidifying_schedule_identifier", "humidifying_schedule_definition"),
            "dehumidifying_schedule": ("dehumidifying_schedule_identifier", "dehumidifying_schedule_definition"),
        },
    },
    "ventilation": {
        "private_attr": "_ventilation",
        "public_attr": "ventilation",
        "class": Ventilation,
        "default_suffix": "Ventilation",
        "schedule_fields": {"schedule": ("schedule_identifier", "schedule_definition")},
    },
}


def _ensure_model():
    if manager.model is None:
        raise ValueError("No model loaded. Please use load_model to load a model first.")


def _result(success=True, **kwargs):
    data = {"success": success}
    data.update(kwargs)
    return post_edit_pipeline(data) if success else data


def _target_rooms(room_identifiers=None):
    _ensure_model()
    if not room_identifiers:
        return list(manager.model.rooms), []
    room_map = {room.identifier: room for room in manager.model.rooms}
    rooms = []
    missing = []
    for room_id in room_identifiers:
        room = room_map.get(room_id)
        if room is None:
            missing.append(room_id)
        else:
            rooms.append(room)
    return rooms, missing


def _parse_time_tuple(value):
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return int(value[0]), int(value[1])
    if isinstance(value, str):
        hour, minute = value.split(":")
        return int(hour), int(minute)
    raise ValueError("Invalid time value '{}'. Expected 'HH:MM' or [hour, minute].".format(value))


def _parse_date_tuple(value):
    if value is None:
        return None
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return int(value[0]), int(value[1])
    if isinstance(value, str):
        month, day = value.split("-")
        return int(month), int(day)
    raise ValueError("Invalid date value '{}'. Expected 'MM-DD' or [month, day].".format(value))


def _schedule_day_dict_from_payload(payload, default_identifier=None):
    if payload is None:
        raise ValueError("ScheduleDay payload is required.")
    if payload.get("schedule_day_dict"):
        return payload["schedule_day_dict"]

    identifier = payload.get("identifier") or default_identifier
    if not identifier:
        raise ValueError("ScheduleDay identifier is required.")
    values = payload.get("values")
    if values is None:
        raise ValueError("ScheduleDay values are required.")
    times = payload.get("times")
    if times is not None:
        times = [_parse_time_tuple(value) for value in times]
    return {
        "type": "ScheduleDay",
        "identifier": identifier,
        "values": values,
        "times": times,
        "interpolate": bool(payload.get("interpolate", False)),
    }


def _make_schedule_day(payload, default_identifier=None):
    return ScheduleDay.from_dict(_schedule_day_dict_from_payload(payload, default_identifier))


def _schedule_type_limit_dict_from_payload(payload, default_identifier=None):
    if payload is None:
        raise ValueError("ScheduleTypeLimit payload is required.")
    if payload.get("schedule_type_limit_dict"):
        return payload["schedule_type_limit_dict"]

    identifier = payload.get("identifier") or default_identifier
    if not identifier:
        raise ValueError("ScheduleTypeLimit identifier is required.")
    return {
        "type": "ScheduleTypeLimit",
        "identifier": identifier,
        "lower_limit": payload.get("lower_limit", "NoLimit"),
        "upper_limit": payload.get("upper_limit", "NoLimit"),
        "numeric_type": payload.get("numeric_type", "Continuous"),
        "unit_type": payload.get("unit_type", "Dimensionless"),
    }


def _make_schedule_type_limit(payload, default_identifier=None):
    return ScheduleTypeLimit.from_dict(_schedule_type_limit_dict_from_payload(payload, default_identifier))


def _resolve_or_create_type_limit(identifier=None, definition=None, default_identifier=None, allow_library=True):
    if definition:
        return _make_schedule_type_limit(definition, default_identifier)
    if identifier:
        type_limit = resolve_schedule_type_limit(manager, identifier)
        if type_limit is None and not allow_library:
            raise ValueError("ScheduleTypeLimit '{}' was not found.".format(identifier))
        return type_limit
    return None


def _resolve_or_create_day(identifier=None, definition=None, default_identifier=None):
    if definition:
        return _make_schedule_day(definition, default_identifier)
    if identifier:
        day = resolve_schedule_day(manager, identifier)
        if day is None:
            raise ValueError("ScheduleDay '{}' was not found.".format(identifier))
        return day
    return None


def _normalize_rule_dict(rule_data, schedule_identifier, index):
    if "day_identifier" in rule_data:
        day = resolve_schedule_day(manager, rule_data["day_identifier"])
        if day is None:
            raise ValueError("ScheduleDay '{}' was not found.".format(rule_data["day_identifier"]))
        day_dict = day.to_dict()
    elif "day" in rule_data or "schedule_day" in rule_data:
        payload = rule_data.get("day") or rule_data.get("schedule_day")
        default_identifier = "{}_RuleDay_{}".format(schedule_identifier, index + 1)
        if isinstance(payload, dict) and payload.get("type") == "ScheduleDay":
            day_dict = payload
            day_dict.setdefault("identifier", default_identifier)
        else:
            day_dict = _schedule_day_dict_from_payload(payload, default_identifier)
    else:
        raise ValueError("Each schedule rule must provide day_identifier or day.")

    return {
        "type": "ScheduleRule",
        "schedule_day": day_dict,
        "apply_sunday": bool(rule_data.get("apply_sunday", False)),
        "apply_monday": bool(rule_data.get("apply_monday", False)),
        "apply_tuesday": bool(rule_data.get("apply_tuesday", False)),
        "apply_wednesday": bool(rule_data.get("apply_wednesday", False)),
        "apply_thursday": bool(rule_data.get("apply_thursday", False)),
        "apply_friday": bool(rule_data.get("apply_friday", False)),
        "apply_saturday": bool(rule_data.get("apply_saturday", False)),
        "start_date": _parse_date_tuple(rule_data.get("start_date")) or (1, 1),
        "end_date": _parse_date_tuple(rule_data.get("end_date")) or (12, 31),
    }


def _collect_days(schedule):
    days = []
    if isinstance(schedule, ScheduleRuleset):
        for day in (
            schedule.default_day_schedule,
            schedule.holiday_schedule,
            schedule.summer_designday_schedule,
            schedule.winter_designday_schedule,
        ):
            if day is not None:
                days.append(day)
        for rule in schedule.schedule_rules:
            if rule.schedule_day is not None:
                days.append(rule.schedule_day)
    return days


def _register_day_if_new(day_obj, resource_changes):
    if not resource_identifier_taken(manager, "schedule_days", day_obj.identifier):
        register_resource(manager, "schedule_days", day_obj)
        resource_changes.append(
            {"action": "created", "resource_category": "schedule_day", "identifier": day_obj.identifier}
        )


def _register_type_limit_if_new(type_limit_obj, resource_changes):
    if not resource_identifier_taken(manager, "schedule_type_limits", type_limit_obj.identifier):
        register_resource(manager, "schedule_type_limits", type_limit_obj)
        resource_changes.append(
            {
                "action": "created",
                "resource_category": "schedule_type_limit",
                "identifier": type_limit_obj.identifier,
            }
        )


def _build_schedule_ruleset(values):
    if values.get("schedule_dict"):
        schedule = ScheduleRuleset.from_dict(values["schedule_dict"])
        resource_changes = []
        for day_obj in _collect_days(schedule):
            _register_day_if_new(day_obj, resource_changes)
        if schedule.schedule_type_limit is not None:
            _register_type_limit_if_new(schedule.schedule_type_limit, resource_changes)
        return schedule, resource_changes

    identifier = values.get("identifier")
    if not identifier:
        raise ValueError("ScheduleRuleset identifier is required.")
    default_day = _resolve_or_create_day(
        values.get("default_day_identifier"),
        values.get("default_day"),
        "{}_DefaultDay".format(identifier),
    )
    if default_day is None:
        raise ValueError("default_day_identifier or default_day is required for ScheduleRuleset.")

    type_limit = _resolve_or_create_type_limit(
        values.get("schedule_type_limit_identifier"),
        values.get("schedule_type_limit"),
        "{}_TypeLimit".format(identifier),
    )
    holiday_day = _resolve_or_create_day(
        values.get("holiday_day_identifier"),
        values.get("holiday_day"),
        "{}_HolidayDay".format(identifier),
    )
    summer_day = _resolve_or_create_day(
        values.get("summer_designday_identifier"),
        values.get("summer_designday"),
        "{}_SummerDesignDay".format(identifier),
    )
    winter_day = _resolve_or_create_day(
        values.get("winter_designday_identifier"),
        values.get("winter_designday"),
        "{}_WinterDesignDay".format(identifier),
    )

    resource_changes = []
    for day_obj in (default_day, holiday_day, summer_day, winter_day):
        if day_obj is not None:
            _register_day_if_new(day_obj, resource_changes)
    if type_limit is not None:
        _register_type_limit_if_new(type_limit, resource_changes)

    schedule_rules = []
    for index, rule_data in enumerate(values.get("rules", []) or []):
        rule = ScheduleRule.from_dict(_normalize_rule_dict(rule_data, identifier, index))
        schedule_rules.append(rule)
        _register_day_if_new(rule.schedule_day, resource_changes)

    schedule = ScheduleRuleset(
        identifier,
        default_day,
        schedule_rules=schedule_rules,
        schedule_type_limit=type_limit,
        holiday_schedule=holiday_day,
        summer_designday_schedule=summer_day,
        winter_designday_schedule=winter_day,
    )
    return schedule, resource_changes


def _build_schedule_fixed_interval(values):
    if values.get("schedule_dict"):
        return ScheduleFixedInterval.from_dict(values["schedule_dict"]), []

    identifier = values.get("identifier")
    if not identifier:
        raise ValueError("ScheduleFixedInterval identifier is required.")
    raw_values = values.get("values")
    if raw_values is None:
        raise ValueError("ScheduleFixedInterval values are required.")

    type_limit = _resolve_or_create_type_limit(
        values.get("schedule_type_limit_identifier"),
        values.get("schedule_type_limit"),
        "{}_TypeLimit".format(identifier),
    )
    resource_changes = []
    if type_limit is not None:
        _register_type_limit_if_new(type_limit, resource_changes)

    schedule_dict = {
        "type": "ScheduleFixedInterval",
        "identifier": identifier,
        "values": raw_values,
        "timestep": int(values.get("timestep", 1)),
        "start_date": _parse_date_tuple(values.get("start_date")) or (1, 1),
        "placeholder_value": values.get("placeholder_value", 0),
        "interpolate": bool(values.get("interpolate", False)),
    }
    if type_limit is not None:
        schedule_dict["schedule_type_limit"] = type_limit.to_dict()
    return ScheduleFixedInterval.from_dict(schedule_dict), resource_changes


def _build_schedule_from_definition(definition, default_identifier=None):
    if definition is None:
        return None, []
    working = dict(definition)
    if default_identifier and "identifier" not in working:
        working["identifier"] = default_identifier
    if working.get("type") == "ScheduleRuleset" or working.get("schedule_kind") == "ruleset":
        return _build_schedule_ruleset(working)
    if working.get("type") == "ScheduleFixedInterval" or working.get("schedule_kind") == "fixed_interval":
        return _build_schedule_fixed_interval(working)
    raise ValueError("Unsupported schedule definition. Expected ScheduleRuleset or ScheduleFixedInterval.")


def _resolve_schedule_input(identifier=None, definition=None, default_identifier=None):
    if definition:
        schedule, resource_changes = _build_schedule_from_definition(definition, default_identifier)
        if not resource_identifier_taken(manager, "schedules", schedule.identifier):
            register_resource(manager, "schedules", schedule)
            resource_changes.append(
                {"action": "created", "resource_category": "schedule", "identifier": schedule.identifier}
            )
        return schedule, resource_changes
    if identifier:
        schedule = resolve_schedule(manager, identifier)
        if schedule is None:
            raise ValueError("Schedule '{}' was not found.".format(identifier))
        return schedule, []
    return None, []


def _default_load_identifier(room, load_key):
    suffix = ROOM_LOAD_METADATA[load_key]["default_suffix"]
    return clean_and_id_ep_string("{}_{}".format(room.identifier, suffix))


def _duplicate_effective_room_load(room, load_key):
    meta = ROOM_LOAD_METADATA[load_key]
    private_value = getattr(room.properties.energy, meta["private_attr"])
    if private_value is not None:
        return private_value.duplicate()

    effective_value = getattr(room.properties.energy, meta["public_attr"])
    if effective_value is None:
        return None
    duplicate = effective_value.duplicate()
    duplicate.identifier = _default_load_identifier(room, load_key)
    return duplicate


def _replace_schedule_fields(load_obj, meta, values, default_identifier_prefix):
    resource_changes = []
    for attr_name, (identifier_key, definition_key) in meta["schedule_fields"].items():
        schedule_identifier = values.get(identifier_key)
        schedule_definition = values.get(definition_key)
        if schedule_identifier is None and schedule_definition is None:
            continue
        schedule_obj, schedule_changes = _resolve_schedule_input(
            schedule_identifier,
            schedule_definition,
            "{}_{}".format(default_identifier_prefix, attr_name),
        )
        setattr(load_obj, attr_name, schedule_obj)
        resource_changes.extend(schedule_changes)
    return resource_changes


def _apply_room_load(room, load_key, values):
    meta = ROOM_LOAD_METADATA[load_key]
    if values.get("reset_to_default"):
        setattr(room.properties.energy, meta["private_attr"], None)
        return {"room_identifier": room.identifier, "action": "reset_to_default"}, []

    if load_key == "service_hot_water" and values.get("clear"):
        setattr(room.properties.energy, meta["private_attr"], None)
        return {"room_identifier": room.identifier, "action": "cleared"}, []

    load_obj = _duplicate_effective_room_load(room, load_key)
    if load_obj is None:
        raise ValueError("Room '{}' does not have a base '{}' object to update.".format(room.identifier, load_key))

    identifier = values.get("identifier")
    if identifier:
        load_obj.identifier = identifier

    resource_changes = _replace_schedule_fields(
        load_obj,
        meta,
        values,
        clean_and_id_ep_string("{}_{}".format(room.identifier, meta["default_suffix"])),
    )

    for key, value in values.items():
        if key in ("identifier", "reset_to_default", "clear"):
            continue
        if key.endswith("_identifier") or key.endswith("_definition"):
            continue
        if hasattr(load_obj, key) and value is not None:
            setattr(load_obj, key, value)

    setattr(room.properties.energy, meta["public_attr"], load_obj)
    return {"room_identifier": room.identifier, "action": "updated", "identifier": load_obj.identifier}, resource_changes


def _apply_room_load_impl(load_key, room_identifiers=None, **values):
    rooms, missing = _target_rooms(room_identifiers)
    results = []
    resource_changes = []
    for room in rooms:
        result, new_changes = _apply_room_load(room, load_key, values)
        results.append(result)
        resource_changes.extend(new_changes)
    return _result(
        True,
        message="Updated {} '{}' object(s).".format(len(results), load_key),
        updated_room_count=len(results),
        missing=missing,
        results=results,
        resource_changes=resource_changes or None,
    )


def _replace_schedule_in_room_explicit_objects(schedule_identifier, schedule_obj):
    for room in manager.model.rooms:
        for meta in ROOM_LOAD_METADATA.values():
            explicit_value = getattr(room.properties.energy, meta["private_attr"])
            if explicit_value is None:
                continue
            updated = False
            duplicate = explicit_value.duplicate()
            for attr_name in meta["schedule_fields"].keys():
                current_value = getattr(duplicate, attr_name, None)
                if current_value is not None and current_value.identifier == schedule_identifier:
                    setattr(duplicate, attr_name, schedule_obj)
                    updated = True
            if updated:
                setattr(room.properties.energy, meta["public_attr"], duplicate)

        if room.properties.energy._process_loads:
            new_processes = []
            updated_processes = False
            for process in room.properties.energy._process_loads:
                duplicate_process = process.duplicate()
                if duplicate_process.schedule.identifier == schedule_identifier:
                    duplicate_process.schedule = schedule_obj
                    updated_processes = True
                new_processes.append(duplicate_process)
            if updated_processes:
                room.properties.energy._process_loads = new_processes


def _update_dependent_schedules_for_day(day_identifier, updated_day):
    schedule_bucket = get_resources_for_category(manager, "schedules")
    updated_identifiers = []
    for identifier, schedule in list(schedule_bucket.items()):
        if not isinstance(schedule, ScheduleRuleset):
            continue
        schedule_dict = schedule.to_dict()
        changed = False
        for index, day_dict in enumerate(schedule_dict.get("day_schedules", []) or []):
            if day_dict.get("identifier") == day_identifier:
                schedule_dict["day_schedules"][index] = updated_day.to_dict()
                changed = True
        if changed:
            rebuilt = ScheduleRuleset.from_dict(schedule_dict)
            register_resource(manager, "schedules", rebuilt)
            _replace_schedule_in_room_explicit_objects(identifier, rebuilt)
            updated_identifiers.append(identifier)
    return updated_identifiers


def _update_dependent_schedules_for_type_limit(type_limit_identifier, updated_type_limit):
    schedule_bucket = get_resources_for_category(manager, "schedules")
    updated_identifiers = []
    for identifier, schedule in list(schedule_bucket.items()):
        current_type_limit = getattr(schedule, "schedule_type_limit", None)
        if current_type_limit is None or current_type_limit.identifier != type_limit_identifier:
            continue
        schedule_dict = schedule.to_dict()
        schedule_dict["schedule_type_limit"] = updated_type_limit.to_dict()
        rebuilt = (
            ScheduleRuleset.from_dict(schedule_dict)
            if schedule_dict.get("type") == "ScheduleRuleset"
            else ScheduleFixedInterval.from_dict(schedule_dict)
        )
        register_resource(manager, "schedules", rebuilt)
        _replace_schedule_in_room_explicit_objects(identifier, rebuilt)
        updated_identifiers.append(identifier)
    return updated_identifiers


def add_schedule_type_limit_impl(**values):
    type_limit = _make_schedule_type_limit(values)
    if resource_identifier_taken(manager, "schedule_type_limits", type_limit.identifier):
        return {"success": False, "error": "ScheduleTypeLimit '{}' already exists.".format(type_limit.identifier)}
    register_resource(manager, "schedule_type_limits", type_limit)
    return _result(True, message="Created ScheduleTypeLimit '{}'.".format(type_limit.identifier), results=[type_limit.identifier], resource_changes=[{"action": "created", "resource_category": "schedule_type_limit", "identifier": type_limit.identifier}])


def add_schedule_day_impl(**values):
    day = _make_schedule_day(values)
    if resource_identifier_taken(manager, "schedule_days", day.identifier):
        return {"success": False, "error": "ScheduleDay '{}' already exists.".format(day.identifier)}
    register_resource(manager, "schedule_days", day)
    return _result(True, message="Created ScheduleDay '{}'.".format(day.identifier), results=[day.identifier], resource_changes=[{"action": "created", "resource_category": "schedule_day", "identifier": day.identifier}])


def add_schedule_ruleset_impl(**values):
    schedule, resource_changes = _build_schedule_ruleset(values)
    if resource_identifier_taken(manager, "schedules", schedule.identifier):
        return {"success": False, "error": "Schedule '{}' already exists.".format(schedule.identifier)}
    register_resource(manager, "schedules", schedule)
    resource_changes.append({"action": "created", "resource_category": "schedule", "identifier": schedule.identifier})
    return _result(True, message="Created ScheduleRuleset '{}'.".format(schedule.identifier), results=[schedule.identifier], resource_changes=resource_changes)


def add_schedule_fixed_interval_impl(**values):
    schedule, resource_changes = _build_schedule_fixed_interval(values)
    if resource_identifier_taken(manager, "schedules", schedule.identifier):
        return {"success": False, "error": "Schedule '{}' already exists.".format(schedule.identifier)}
    register_resource(manager, "schedules", schedule)
    resource_changes.append({"action": "created", "resource_category": "schedule", "identifier": schedule.identifier})
    return _result(True, message="Created ScheduleFixedInterval '{}'.".format(schedule.identifier), results=[schedule.identifier], resource_changes=resource_changes)


def add_process_load_impl(room_identifiers=None, identifier=None, watts=None, schedule_identifier=None, schedule_definition=None, fuel_type=None, end_use_category="Process", radiant_fraction=0, latent_fraction=0, lost_fraction=0):
    rooms, missing = _target_rooms(room_identifiers)
    if watts is None or fuel_type is None:
        return {"success": False, "error": "watts and fuel_type are required for process_load."}

    results = []
    resource_changes = []
    for room in rooms:
        process_identifier = identifier or clean_and_id_ep_string("{}_Process_{}".format(room.identifier, len(room.properties.energy._process_loads) + 1))
        if any(proc.identifier == process_identifier for proc in room.properties.energy._process_loads):
            results.append({"room_identifier": room.identifier, "error": "Duplicate process identifier '{}'.".format(process_identifier)})
            continue
        schedule_obj, schedule_changes = _resolve_schedule_input(schedule_identifier, schedule_definition, "{}_ProcessSchedule".format(process_identifier))
        if schedule_obj is None:
            results.append({"room_identifier": room.identifier, "error": "A process schedule is required."})
            continue
        process = Process(process_identifier, watts, schedule_obj, fuel_type, end_use_category=end_use_category, radiant_fraction=radiant_fraction, latent_fraction=latent_fraction, lost_fraction=lost_fraction)
        room.properties.energy.add_process_load(process)
        results.append({"room_identifier": room.identifier, "identifier": process.identifier, "action": "created"})
        resource_changes.extend(schedule_changes)

    return _result(True, message="Processed {} room(s) for process loads.".format(len(rooms)), results=results, missing=missing, resource_changes=resource_changes or None)


def apply_people_impl(room_identifiers=None, **values):
    return _apply_room_load_impl("people", room_identifiers=room_identifiers, **values)


def apply_lighting_impl(room_identifiers=None, **values):
    return _apply_room_load_impl("lighting", room_identifiers=room_identifiers, **values)


def apply_electric_equipment_impl(room_identifiers=None, **values):
    return _apply_room_load_impl("electric_equipment", room_identifiers=room_identifiers, **values)


def apply_service_hot_water_impl(room_identifiers=None, **values):
    return _apply_room_load_impl("service_hot_water", room_identifiers=room_identifiers, **values)


def apply_setpoint_impl(room_identifiers=None, **values):
    return _apply_room_load_impl("setpoint", room_identifiers=room_identifiers, **values)


def apply_ventilation_impl(room_identifiers=None, **values):
    return _apply_room_load_impl("ventilation", room_identifiers=room_identifiers, **values)


def apply_process_load_impl(room_identifiers=None, process_identifier=None, identifier=None, schedule_identifier=None, schedule_definition=None, **values):
    rooms, missing = _target_rooms(room_identifiers)
    results = []
    resource_changes = []
    for room in rooms:
        processes = list(room.properties.energy._process_loads)
        matched = False
        new_processes = []
        for process in processes:
            if process.identifier != process_identifier:
                new_processes.append(process)
                continue
            duplicate = process.duplicate()
            if identifier:
                duplicate.identifier = identifier
            schedule_obj, schedule_changes = _resolve_schedule_input(schedule_identifier, schedule_definition, "{}_Schedule".format(duplicate.identifier))
            if schedule_obj is not None:
                duplicate.schedule = schedule_obj
                resource_changes.extend(schedule_changes)
            for key, value in values.items():
                if hasattr(duplicate, key) and value is not None:
                    setattr(duplicate, key, value)
            new_processes.append(duplicate)
            matched = True
            results.append({"room_identifier": room.identifier, "identifier": duplicate.identifier, "action": "updated"})
        if matched:
            room.properties.energy._process_loads = new_processes
        else:
            results.append({"room_identifier": room.identifier, "error": "Process '{}' not found.".format(process_identifier)})
    return _result(True, message="Processed {} room(s) for process load update.".format(len(rooms)), results=results, missing=missing, resource_changes=resource_changes or None)


def apply_schedule_type_limit_impl(schedule_type_limit_identifiers=None, **values):
    bucket = get_resources_for_category(manager, "schedule_type_limits")
    identifiers = schedule_type_limit_identifiers or list(bucket.keys())
    results = []
    resource_changes = []
    for identifier in identifiers:
        if bucket.get(identifier) is None:
            results.append({"identifier": identifier, "error": "ScheduleTypeLimit not found."})
            continue
        payload = dict(values)
        payload.setdefault("identifier", values.get("identifier") or identifier)
        updated = _make_schedule_type_limit(payload)
        register_resource(manager, "schedule_type_limits", updated)
        if identifier != updated.identifier:
            unregister_resource(manager, "schedule_type_limits", identifier)
        affected = _update_dependent_schedules_for_type_limit(identifier, updated)
        resource_changes.append({"action": "updated", "resource_category": "schedule_type_limit", "identifier": updated.identifier})
        results.append({"identifier": identifier, "updated_identifier": updated.identifier, "affected_schedules": affected})
    return _result(True, message="Updated schedule type limits.", results=results, resource_changes=resource_changes)


def apply_schedule_day_impl(schedule_day_identifiers=None, **values):
    bucket = get_resources_for_category(manager, "schedule_days")
    identifiers = schedule_day_identifiers or list(bucket.keys())
    results = []
    resource_changes = []
    for identifier in identifiers:
        if bucket.get(identifier) is None:
            results.append({"identifier": identifier, "error": "ScheduleDay not found."})
            continue
        payload = dict(values)
        payload.setdefault("identifier", values.get("identifier") or identifier)
        updated = _make_schedule_day(payload)
        register_resource(manager, "schedule_days", updated)
        if identifier != updated.identifier:
            unregister_resource(manager, "schedule_days", identifier)
        affected = _update_dependent_schedules_for_day(identifier, updated)
        resource_changes.append({"action": "updated", "resource_category": "schedule_day", "identifier": updated.identifier})
        results.append({"identifier": identifier, "updated_identifier": updated.identifier, "affected_schedules": affected})
    return _result(True, message="Updated schedule days.", results=results, resource_changes=resource_changes)


def _apply_rule_changes_to_dict(schedule_dict, rule_changes):
    for change in rule_changes or []:
        action = change.get("action")
        if action == "add":
            new_rule = _normalize_rule_dict(change, schedule_dict["identifier"], len(schedule_dict.get("schedule_rules", [])))
            schedule_dict.setdefault("day_schedules", []).append(new_rule["schedule_day"])
            abridged_rule = dict(new_rule)
            abridged_rule["type"] = "ScheduleRuleAbridged"
            abridged_rule["schedule_day"] = new_rule["schedule_day"]["identifier"]
            schedule_dict.setdefault("schedule_rules", []).append(abridged_rule)
        elif action in ("replace", "remove"):
            rule_index = change.get("rule_index")
            if rule_index is None or rule_index < 0 or rule_index >= len(schedule_dict.get("schedule_rules", [])):
                raise ValueError("Invalid rule_index '{}'.".format(rule_index))
            if action == "remove":
                del schedule_dict["schedule_rules"][rule_index]
            else:
                new_rule = _normalize_rule_dict(change, schedule_dict["identifier"], rule_index)
                schedule_dict.setdefault("day_schedules", []).append(new_rule["schedule_day"])
                abridged_rule = dict(new_rule)
                abridged_rule["type"] = "ScheduleRuleAbridged"
                abridged_rule["schedule_day"] = new_rule["schedule_day"]["identifier"]
                schedule_dict["schedule_rules"][rule_index] = abridged_rule
        else:
            raise ValueError("Unsupported rule_changes action '{}'.".format(action))
    return schedule_dict


def apply_schedule_ruleset_impl(schedule_identifiers=None, **values):
    bucket = get_resources_for_category(manager, "schedules")
    identifiers = schedule_identifiers or list(bucket.keys())
    results = []
    resource_changes = []
    for identifier in identifiers:
        current = bucket.get(identifier)
        if not isinstance(current, ScheduleRuleset):
            continue
        schedule_dict = current.to_dict()
        schedule_dict["identifier"] = values.get("identifier") or identifier

        direct_mapping = {
            "default_day_identifier": "default_day_schedule",
            "holiday_day_identifier": "holiday_schedule",
            "summer_designday_identifier": "summer_designday_schedule",
            "winter_designday_identifier": "winter_designday_schedule",
        }
        for input_key, schedule_key in direct_mapping.items():
            ref_identifier = values.get(input_key)
            if ref_identifier:
                day_obj = resolve_schedule_day(manager, ref_identifier)
                if day_obj is None:
                    raise ValueError("ScheduleDay '{}' was not found.".format(ref_identifier))
                schedule_dict[schedule_key] = day_obj.identifier
                schedule_dict.setdefault("day_schedules", []).append(day_obj.to_dict())

        if values.get("schedule_type_limit_identifier"):
            type_limit = resolve_schedule_type_limit(manager, values["schedule_type_limit_identifier"])
            if type_limit is None:
                raise ValueError("ScheduleTypeLimit '{}' was not found.".format(values["schedule_type_limit_identifier"]))
            schedule_dict["schedule_type_limit"] = type_limit.to_dict()

        schedule_dict = _apply_rule_changes_to_dict(schedule_dict, values.get("rule_changes"))
        rebuilt = ScheduleRuleset.from_dict(schedule_dict)
        register_resource(manager, "schedules", rebuilt)
        if identifier != rebuilt.identifier:
            unregister_resource(manager, "schedules", identifier)
        _replace_schedule_in_room_explicit_objects(identifier, rebuilt)
        resource_changes.append({"action": "updated", "resource_category": "schedule", "identifier": rebuilt.identifier})
        results.append({"identifier": identifier, "updated_identifier": rebuilt.identifier})
    return _result(True, message="Updated schedule rulesets.", results=results, resource_changes=resource_changes)


def apply_schedule_fixed_interval_impl(schedule_identifiers=None, **values):
    bucket = get_resources_for_category(manager, "schedules")
    identifiers = schedule_identifiers or list(bucket.keys())
    results = []
    resource_changes = []
    for identifier in identifiers:
        current = bucket.get(identifier)
        if not isinstance(current, ScheduleFixedInterval):
            continue
        schedule_dict = current.to_dict()
        for key in ("identifier", "values", "timestep", "placeholder_value", "interpolate"):
            if key in values and values[key] is not None:
                schedule_dict[key] = values[key]
        if values.get("start_date") is not None:
            schedule_dict["start_date"] = _parse_date_tuple(values["start_date"])
        if values.get("schedule_type_limit_identifier"):
            type_limit = resolve_schedule_type_limit(manager, values["schedule_type_limit_identifier"])
            if type_limit is None:
                raise ValueError("ScheduleTypeLimit '{}' was not found.".format(values["schedule_type_limit_identifier"]))
            schedule_dict["schedule_type_limit"] = type_limit.to_dict()
        rebuilt = ScheduleFixedInterval.from_dict(schedule_dict)
        register_resource(manager, "schedules", rebuilt)
        if identifier != rebuilt.identifier:
            unregister_resource(manager, "schedules", identifier)
        _replace_schedule_in_room_explicit_objects(identifier, rebuilt)
        resource_changes.append({"action": "updated", "resource_category": "schedule", "identifier": rebuilt.identifier})
        results.append({"identifier": identifier, "updated_identifier": rebuilt.identifier})
    return _result(True, message="Updated schedule fixed intervals.", results=results, resource_changes=resource_changes)


def _scan_schedule_references(identifier):
    references = []
    for room in manager.model.rooms:
        energy = room.properties.energy
        if energy._people is not None:
            if energy._people.occupancy_schedule.identifier == identifier:
                references.append("room:{}:people.occupancy_schedule".format(room.identifier))
            if energy._people.activity_schedule.identifier == identifier:
                references.append("room:{}:people.activity_schedule".format(room.identifier))
        if energy._lighting is not None and energy._lighting.schedule.identifier == identifier:
            references.append("room:{}:lighting.schedule".format(room.identifier))
        if energy._electric_equipment is not None and energy._electric_equipment.schedule.identifier == identifier:
            references.append("room:{}:electric_equipment.schedule".format(room.identifier))
        if energy._service_hot_water is not None and energy._service_hot_water.schedule.identifier == identifier:
            references.append("room:{}:service_hot_water.schedule".format(room.identifier))
        if energy._ventilation is not None and energy._ventilation.schedule is not None and energy._ventilation.schedule.identifier == identifier:
            references.append("room:{}:ventilation.schedule".format(room.identifier))
        if energy._setpoint is not None:
            for attr in ("heating_schedule", "cooling_schedule", "humidifying_schedule", "dehumidifying_schedule"):
                schedule = getattr(energy._setpoint, attr)
                if schedule is not None and schedule.identifier == identifier:
                    references.append("room:{}:setpoint.{}".format(room.identifier, attr))
        for process in energy._process_loads:
            if process.schedule.identifier == identifier:
                references.append("room:{}:process:{}".format(room.identifier, process.identifier))
    return references


def remove_schedule_resources_impl(schedule_ids=None, schedule_day_ids=None, schedule_type_limit_ids=None):
    removed = {"schedule": [], "schedule_day": [], "schedule_type_limit": []}
    blocked = []

    for identifier in schedule_ids or []:
        refs = _scan_schedule_references(identifier)
        if refs:
            blocked.append({"identifier": identifier, "resource_category": "schedule", "references": refs})
            continue
        if unregister_resource(manager, "schedules", identifier) is not None:
            removed["schedule"].append(identifier)

    for identifier in schedule_day_ids or []:
        refs = [
            "schedule:{}".format(schedule_id)
            for schedule_id, schedule in get_resources_for_category(manager, "schedules").items()
            if identifier in [day.identifier for day in _collect_days(schedule)]
        ]
        if refs:
            blocked.append({"identifier": identifier, "resource_category": "schedule_day", "references": refs})
            continue
        if unregister_resource(manager, "schedule_days", identifier) is not None:
            removed["schedule_day"].append(identifier)

    for identifier in schedule_type_limit_ids or []:
        refs = [
            "schedule:{}".format(schedule_id)
            for schedule_id, schedule in get_resources_for_category(manager, "schedules").items()
            if getattr(getattr(schedule, "schedule_type_limit", None), "identifier", None) == identifier
        ]
        if refs:
            blocked.append({"identifier": identifier, "resource_category": "schedule_type_limit", "references": refs})
            continue
        if unregister_resource(manager, "schedule_type_limits", identifier) is not None:
            removed["schedule_type_limit"].append(identifier)

    return _result(True, message="Processed energy resource removal.", removed=removed, blocked=blocked or None, resource_changes=[{"action": "removed", "resource_category": category, "identifier": item} for category, items in removed.items() for item in items] or None)


def remove_process_loads_impl(room_identifiers=None, process_ids=None):
    rooms, missing = _target_rooms(room_identifiers)
    results = []
    for room in rooms:
        if not process_ids:
            removed_ids = [proc.identifier for proc in room.properties.energy._process_loads]
            room.properties.energy._process_loads = []
        else:
            kept = []
            removed_ids = []
            for process in room.properties.energy._process_loads:
                if process.identifier in process_ids:
                    removed_ids.append(process.identifier)
                else:
                    kept.append(process)
            room.properties.energy._process_loads = kept
        results.append({"room_identifier": room.identifier, "removed_ids": removed_ids})
    return _result(True, message="Processed process load removal for {} room(s).".format(len(rooms)), results=results, missing=missing)
