import json
import os

from honeybee.altnumber import autosize, no_limit
from honeybee.aperture import Aperture
from honeybee.boundarycondition import Outdoors
from honeybee.door import Door
from honeybee.face import Face
from honeybee.facetype import Wall
from honeybee.orientation import angles_from_num_orient, face_orient_index
from honeybee.room import Room
from honeybee.shade import Shade
from honeybee.typing import clean_and_id_ep_string
from honeybee_energy.hvac.allair import EQUIPMENT_TYPES_DICT as AA_TYPES
from honeybee_energy.hvac.doas import EQUIPMENT_TYPES_DICT as DOAS_TYPES
from honeybee_energy.hvac.heatcool import EQUIPMENT_TYPES_DICT as HC_TYPES
from honeybee_energy.hvac.idealair import IdealAirSystem
from honeybee_energy.material.glazing import EnergyWindowMaterialSimpleGlazSys
from honeybee_energy.material.opaque import EnergyMaterial
from honeybee_energy.construction.opaque import OpaqueConstruction
from honeybee_energy.construction.window import WindowConstruction
from honeybee_energy.construction.shade import ShadeConstruction
from honeybee_energy.lib.constructionsets import construction_set_by_identifier
from honeybee_energy.lib.programtypes import (
    building_program_type_by_identifier,
    program_type_by_identifier,
)
from honeybee_energy.lib.schedules import schedule_by_identifier
from honeybee_energy.shw import SHWSystem
from honeybee_radiance.lib.modifiersets import modifier_set_by_identifier

from ..state.hooks import post_edit_pipeline
from ..state.manager import manager
from ..state.energy_resources import register_resource, resolve_schedule, resource_identifier_taken
from ..state.radiance_resources import resolve_modifier, resolve_modifier_set

try:
    from honeybee_energy.lib.constructions import (
        opaque_construction_by_identifier,
        shade_construction_by_identifier,
        window_construction_by_identifier,
    )
except ImportError:
    opaque_construction_by_identifier = None
    shade_construction_by_identifier = None
    window_construction_by_identifier = None

try:
    from honeybee_radiance.lib.modifiers import modifier_by_identifier
except ImportError:
    modifier_by_identifier = None


def _load_registry():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "hvac_config.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"HVAC configuration file not found at: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


REGISTRY = _load_registry()
VINTAGE_MAPPING = REGISTRY.get("vintages", {})
HVAC_MAPPINGS = REGISTRY.get("mappings", {})
VALID_RADIANT_TYPES = [
    "Floor",
    "Ceiling",
    "FloorWithCarpet",
    "CeilingMetalPanel",
    "FloorWithHardwood",
]


def _ensure_model():
    if not manager.model:
        raise ValueError("Model is not loaded.")


def _get_target_rooms(room_identifiers):
    _ensure_model()
    if room_identifiers:
        room_map = {r.identifier: r for r in manager.model.rooms}
        return [room_map[rid] for rid in room_identifiers if rid in room_map]
    return list(manager.model.rooms)


def _parse_alt_number(value):
    if value is None:
        return None
    str_val = str(value).lower().strip()
    if str_val == "autosize":
        return autosize
    if str_val == "nolimit":
        return no_limit
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid limit: '{value}'. Expected number, 'Autosize', or 'NoLimit'.")


def _parse_shw_condition(value, room_map):
    if value is None:
        return 22.0
    try:
        return float(value)
    except (ValueError, TypeError):
        pass
    str_val = str(value)
    return str_val if str_val in room_map else str_val


def _resolve_schedule_reference(identifier):
    if not identifier:
        return None
    schedule = resolve_schedule(manager, identifier)
    if schedule is not None:
        return schedule
    return schedule_by_identifier(identifier)


def _register_materials_and_construction(materials, construction):
    for material in materials:
        if not resource_identifier_taken(manager, "materials", material.identifier):
            register_resource(manager, "materials", material)
    if not resource_identifier_taken(manager, "constructions", construction.identifier):
        register_resource(manager, "constructions", construction)


def _build_custom_opaque_construction(custom_construction):
    materials = []
    for material_data in custom_construction.get("materials", []) or []:
        material = EnergyMaterial(
            material_data["identifier"],
            material_data["thickness"],
            material_data["conductivity"],
            material_data["density"],
            material_data["specific_heat"],
            roughness=material_data.get("roughness", "MediumRough"),
            thermal_absorptance=material_data.get("thermal_absorptance", 0.9),
            solar_absorptance=material_data.get("solar_absorptance", 0.7),
            visible_absorptance=material_data.get("visible_absorptance"),
        )
        materials.append(material)
    construction = OpaqueConstruction(custom_construction["identifier"], materials)
    _register_materials_and_construction(materials, construction)
    return construction


def _build_custom_window_construction(custom_construction):
    simple_glazing = custom_construction.get("simple_glazing")
    if simple_glazing is None:
        raise ValueError("custom_construction.simple_glazing is required for window_attributes.")
    material = EnergyWindowMaterialSimpleGlazSys(
        simple_glazing["identifier"],
        simple_glazing["u_factor"],
        simple_glazing["shgc"],
        simple_glazing.get("vt", 0.6),
    )
    construction = WindowConstruction(custom_construction["identifier"], [material])
    _register_materials_and_construction([material], construction)
    return construction


def _build_custom_shade_construction(custom_construction):
    construction = ShadeConstruction(
        custom_construction["identifier"],
        solar_reflectance=custom_construction.get("solar_reflectance", 0.2),
        visible_reflectance=custom_construction.get("visible_reflectance", 0.2),
        is_specular=custom_construction.get("is_specular", False),
    )
    if not resource_identifier_taken(manager, "constructions", construction.identifier):
        register_resource(manager, "constructions", construction)
    return construction


def _get_hvac_class_and_key(category, system_type):
    if category not in HVAC_MAPPINGS:
        raise ValueError(f"Unknown category '{category}'")

    mapping = HVAC_MAPPINGS[category]
    sys_key = mapping.get(system_type, system_type)

    if category == "SHW":
        if sys_key not in mapping.values() and sys_key not in mapping:
            raise ValueError(f"SHW Type '{system_type}' not found in library.")
        return SHWSystem, sys_key

    type_dict = None
    if category == "AllAir":
        type_dict = AA_TYPES
    elif category == "DOAS":
        type_dict = DOAS_TYPES
    elif category == "HeatCool":
        type_dict = HC_TYPES

    if sys_key not in type_dict:
        raise ValueError(f"System Type '{system_type}' not found in {category} library.")

    return type_dict[sys_key], sys_key


def _is_exterior_wall(face):
    return isinstance(face.boundary_condition, Outdoors) and isinstance(face.type, Wall)


def _get_model_objects(identifier_list, obj_type_class):
    if not identifier_list:
        return []
    _ensure_model()

    found_objs = []
    ids_set = set(identifier_list)
    for room in manager.model.rooms:
        if obj_type_class == Room:
            if room.identifier in ids_set:
                found_objs.append(room)
            continue

        for face in room.faces:
            if obj_type_class == Face and face.identifier in ids_set:
                found_objs.append(face)

            if obj_type_class in [Aperture, Door, Shade]:
                if obj_type_class == Aperture:
                    for ap in face.apertures:
                        if ap.identifier in ids_set:
                            found_objs.append(ap)
                elif obj_type_class == Door:
                    for dr in face.doors:
                        if dr.identifier in ids_set:
                            found_objs.append(dr)
                if obj_type_class == Shade:
                    for shd in face.shades:
                        if shd.identifier in ids_set:
                            found_objs.append(shd)
                    for ap in face.apertures:
                        for shd in ap.shades:
                            if shd.identifier in ids_set:
                                found_objs.append(shd)
                    for dr in face.doors:
                        for shd in dr.shades:
                            if shd.identifier in ids_set:
                                found_objs.append(shd)

        if obj_type_class == Shade:
            for shd in room.shades:
                if shd.identifier in ids_set:
                    found_objs.append(shd)

    if obj_type_class == Face:
        for face in manager.model.orphaned_faces:
            if face.identifier in ids_set:
                found_objs.append(face)
    elif obj_type_class == Shade:
        for shd in manager.model.orphaned_shades:
            if shd.identifier in ids_set:
                found_objs.append(shd)

    return found_objs


def _apply_properties_by_orientation(targets, constructions, modifiers, prop_check_func, get_children_func):
    updated = 0

    def _set_props(obj, c, m):
        did_set = False
        if c and hasattr(obj.properties.energy, "construction"):
            obj.properties.energy.construction = c
            did_set = True
        if m and hasattr(obj.properties.radiance, "modifier"):
            obj.properties.radiance.modifier = m
            did_set = True
        return 1 if did_set else 0

    if (constructions and len(constructions) == 1) or (modifiers and len(modifiers) == 1):
        c_single = constructions[0] if constructions else None
        m_single = modifiers[0] if modifiers else None
        for obj in targets:
            if prop_check_func(obj):
                updated += _set_props(obj, c_single, m_single)
            for child in get_children_func(obj):
                updated += _set_props(child, c_single, m_single)
    else:
        count = max(len(constructions) if constructions else 0, len(modifiers) if modifiers else 0)
        angles = angles_from_num_orient(count)
        for obj in targets:
            if prop_check_func(obj):
                orient_i = face_orient_index(obj, angles)
                if orient_i is not None:
                    c = constructions[orient_i] if constructions else None
                    m = modifiers[orient_i] if modifiers else None
                    updated += _set_props(obj, c, m)
            for child in get_children_func(obj):
                orient_i = face_orient_index(child, angles)
                if orient_i is not None:
                    c = constructions[orient_i] if constructions else None
                    m = modifiers[orient_i] if modifiers else None
                    updated += _set_props(child, c, m)
    return updated


def apply_room_attributes_impl(
    construction_set_identifier=None,
    modifier_set_identifier=None,
    program_type_identifier=None,
    is_conditioned=None,
    reset_loads=False,
    room_identifiers=None,
):
    _ensure_model()
    if all(v is None for v in [construction_set_identifier, modifier_set_identifier, program_type_identifier, is_conditioned]):
        return {"status": "skipped", "message": "No attributes provided to apply."}

    con_set = None
    mod_set = None
    prog_type = None
    if construction_set_identifier:
        con_set = construction_set_by_identifier(construction_set_identifier)
        if not con_set:
            raise ValueError(f"Construction Set '{construction_set_identifier}' not found.")
    if modifier_set_identifier:
        mod_set = resolve_modifier_set(manager, modifier_set_identifier) or modifier_set_by_identifier(modifier_set_identifier)
        if not mod_set:
            raise ValueError(f"Modifier Set '{modifier_set_identifier}' not found.")
    if program_type_identifier:
        try:
            prog_type = building_program_type_by_identifier(program_type_identifier)
        except ValueError:
            try:
                prog_type = program_type_by_identifier(program_type_identifier)
            except ValueError:
                raise ValueError(f"Program Type '{program_type_identifier}' not found.")

    target_rooms = _get_target_rooms(room_identifiers)
    warnings = []
    updated_conditioned_status = 0
    for room in target_rooms:
        if is_conditioned is not None:
            if is_conditioned:
                if not room.properties.energy.is_conditioned:
                    room.properties.energy.add_default_ideal_air()
                    updated_conditioned_status += 1
            else:
                if room.properties.energy.is_conditioned:
                    room.properties.energy.hvac = None
                    updated_conditioned_status += 1
        if con_set:
            room.properties.energy.construction_set = con_set
        if mod_set:
            room.properties.radiance.modifier_set = mod_set
        if prog_type:
            room.properties.energy.program_type = prog_type
            if reset_loads:
                room.properties.energy.reset_loads_to_program()
            elif room.properties.energy.has_overridden_loads:
                warnings.append(
                    f"Room '{room.display_name}' has overridden loads. Set reset_loads=True to force update."
                )

    return post_edit_pipeline(
        {
            "status": "success",
            "updated_room_count": len(target_rooms),
            "conditioning_changes": updated_conditioned_status if is_conditioned is not None else 0,
            "applied_attributes": {
                "is_conditioned": is_conditioned,
                "construction_set": con_set.identifier if con_set else None,
                "modifier_set": mod_set.identifier if mod_set else None,
                "program_type": prog_type.identifier if prog_type else None,
            },
            "warnings": warnings if warnings else None,
            "target_scope": "specific_rooms" if room_identifiers else "all_rooms",
        }
    )


def apply_hvac_impl(
    system_category="Ideal",
    system_type=None,
    vintage="ASHRAE_2019",
    name=None,
    room_identifiers=None,
    list_options=False,
    economizer_type=None,
    sensible_heat_recovery=None,
    latent_heat_recovery=None,
    demand_controlled_ventilation=False,
    heating_air_temperature=None,
    cooling_air_temperature=None,
    heating_limit=None,
    cooling_limit=None,
    heating_availability_schedule=None,
    cooling_availability_schedule=None,
    doas_availability_schedule=None,
    shw_efficiency=None,
    shw_ambient_condition=None,
    shw_loss_coefficient=None,
    radiant_type=None,
    radiant_switch_over_time=None,
):
    valid_cats = ["AllAir", "DOAS", "HeatCool", "SHW"]
    if list_options:
        if system_category == "Ideal":
            return {"status": "info", "message": "Ideal Air System does not have subtypes."}
        if system_category not in valid_cats:
            return {"status": "error", "message": f"Invalid category. Choose from: {valid_cats}"}
        cat_mapping = HVAC_MAPPINGS.get(system_category, {})
        vintages = sorted(list(set(VINTAGE_MAPPING.keys()) - {None, "null"}))
        return {
            "status": "info",
            "category": system_category,
            "available_types": list(cat_mapping.keys()),
            "available_vintages": vintages,
            "available_radiant_types": VALID_RADIANT_TYPES,
        }

    _ensure_model()
    target_rooms = _get_target_rooms(room_identifiers)
    selected_vintage = VINTAGE_MAPPING.get(vintage, vintage)
    if selected_vintage == "null":
        selected_vintage = "ASHRAE_2019"

    heat_sch = _resolve_schedule_reference(heating_availability_schedule) if heating_availability_schedule else None
    cool_sch = _resolve_schedule_reference(cooling_availability_schedule) if cooling_availability_schedule else None
    doas_sch = _resolve_schedule_reference(doas_availability_schedule) if doas_availability_schedule else None
    if radiant_type and radiant_type not in VALID_RADIANT_TYPES:
        raise ValueError(f"Invalid radiant_type '{radiant_type}'. Options: {VALID_RADIANT_TYPES}")

    updated_count = 0
    warnings = []
    vent_schedules = set()
    no_setpoint_rooms = []
    final_hvac_name = ""
    final_sys_key = "IdealAirSystem"

    if system_category.lower() == "ideal":
        for room in target_rooms:
            if not room.properties.energy.is_conditioned:
                continue
            if not isinstance(room.properties.energy.hvac, IdealAirSystem):
                room.properties.energy.add_default_ideal_air()
            hvac_obj = room.properties.energy.hvac.duplicate()
            if economizer_type:
                hvac_obj.economizer_type = economizer_type
            if sensible_heat_recovery is not None:
                hvac_obj.sensible_heat_recovery = sensible_heat_recovery
            if latent_heat_recovery is not None:
                hvac_obj.latent_heat_recovery = latent_heat_recovery
            if demand_controlled_ventilation is not None:
                hvac_obj.demand_controlled_ventilation = demand_controlled_ventilation
            if heating_air_temperature:
                hvac_obj.heating_air_temperature = heating_air_temperature
            if cooling_air_temperature:
                hvac_obj.cooling_air_temperature = cooling_air_temperature
            if heating_limit:
                hvac_obj.heating_limit = _parse_alt_number(heating_limit)
            if cooling_limit:
                hvac_obj.cooling_limit = _parse_alt_number(cooling_limit)
            if heat_sch:
                hvac_obj.heating_availability = heat_sch
            if cool_sch:
                hvac_obj.cooling_availability = cool_sch
            if name:
                hvac_obj.display_name = name
            room.properties.energy.hvac = hvac_obj
            updated_count += 1
        final_hvac_name = "Custom Ideal Air"
    elif system_category == "SHW":
        if not system_type:
            raise ValueError(f"system_type is required for {system_category}")
        _, final_sys_key = _get_hvac_class_and_key("SHW", system_type)
        sys_id_base = name if name else f"SHW_{final_sys_key}"
        sys_id = clean_and_id_ep_string(sys_id_base)
        room_map_full = {r.identifier: r for r in manager.model.rooms}
        cond = _parse_shw_condition(shw_ambient_condition, room_map_full)
        loss_coeff = shw_loss_coefficient if shw_loss_coefficient is not None else 6.0
        shw_obj = SHWSystem(
            identifier=sys_id,
            equipment_type=final_sys_key,
            heater_efficiency=shw_efficiency,
            ambient_condition=cond,
            ambient_loss_coefficient=loss_coeff,
        )
        if name:
            shw_obj.display_name = name
        final_hvac_name = shw_obj.display_name
        skipped_no_load = 0
        for room in target_rooms:
            if room.properties.energy.service_hot_water is not None:
                room.properties.energy.shw = shw_obj
                updated_count += 1
            else:
                skipped_no_load += 1
        if skipped_no_load > 0:
            warnings.append(f"{skipped_no_load} rooms skipped (no SHW load).")
    else:
        if not system_type:
            raise ValueError(f"system_type is required for {system_category}")
        HvacClass, final_sys_key = _get_hvac_class_and_key(system_category, system_type)
        sys_id_base = name if name else f"{system_category}_{final_sys_key}"
        sys_id = clean_and_id_ep_string(sys_id_base)
        hvac_obj = HvacClass(identifier=sys_id, vintage=selected_vintage, equipment_type=final_sys_key)
        if name:
            hvac_obj.display_name = name
        if sensible_heat_recovery is not None:
            hvac_obj.sensible_heat_recovery = sensible_heat_recovery
        if latent_heat_recovery is not None:
            hvac_obj.latent_heat_recovery = latent_heat_recovery
        if system_category == "AllAir":
            if economizer_type:
                hvac_obj.economizer_type = economizer_type
            if demand_controlled_ventilation:
                hvac_obj.demand_controlled_ventilation = True
        elif system_category == "DOAS":
            if demand_controlled_ventilation:
                hvac_obj.demand_controlled_ventilation = True
            if doas_sch:
                hvac_obj.doas_availability_schedule = doas_sch
        if radiant_type:
            if hasattr(hvac_obj, "radiant_type"):
                hvac_obj.radiant_type = radiant_type
            else:
                warnings.append(f"radiant_type ignored: System '{final_sys_key}' is not a radiant system.")
        if radiant_switch_over_time is not None:
            if hasattr(hvac_obj, "switch_over_time"):
                hvac_obj.switch_over_time = radiant_switch_over_time
            else:
                warnings.append(
                    f"radiant_switch_over_time ignored: System '{final_sys_key}' does not support it."
                )
        final_hvac_name = hvac_obj.display_name
        for room in target_rooms:
            if room.properties.energy.is_conditioned:
                room.properties.energy.hvac = hvac_obj
                updated_count += 1
                if room.properties.energy.setpoint is None:
                    no_setpoint_rooms.append(room.display_name)
                vent_obj = room.properties.energy.ventilation
                if vent_obj is not None and hasattr(vent_obj, "schedule") and vent_obj.schedule is not None:
                    vent_schedules.add(vent_obj.schedule.identifier)
        if system_category in ["AllAir", "DOAS"] and len(vent_schedules) > 1:
            warnings.append("Central system applied to rooms with differing ventilation schedules.")
        if no_setpoint_rooms:
            warnings.append(f"Rooms without setpoints: {', '.join(no_setpoint_rooms)}")

    if updated_count == 0:
        return {"status": "skipped", "message": "No valid target rooms found."}
    return post_edit_pipeline(
        {
            "status": "success",
            "category": system_category,
            "system_type": final_sys_key,
            "system_name": final_hvac_name,
            "updated_room_count": updated_count,
            "warnings": warnings if warnings else None,
        }
    )


def apply_opaque_attributes_impl(
    construction_identifiers=None,
    modifier_identifiers=None,
    custom_construction=None,
    face_identifiers=None,
    door_identifiers=None,
    room_identifiers=None,
):
    _ensure_model()
    if custom_construction and construction_identifiers:
        raise ValueError("custom_construction and construction_identifiers cannot be used together.")
    constrs = [opaque_construction_by_identifier(cid) for cid in construction_identifiers] if construction_identifiers else []
    if custom_construction:
        constrs = [_build_custom_opaque_construction(custom_construction)]
    mods = [resolve_modifier(manager, mid) or modifier_by_identifier(mid) for mid in modifier_identifiers] if modifier_identifiers else []
    if not constrs and not mods:
        return {"status": "skipped", "message": "No constructions or modifiers provided."}
    t_faces = _get_model_objects(face_identifiers, Face)
    t_doors = _get_model_objects(door_identifiers, Door)
    t_rooms = _get_model_objects(room_identifiers, Room)
    if not any([face_identifiers, door_identifiers, room_identifiers]):
        t_rooms = list(manager.model.rooms)
    all_targets = t_faces + t_doors + t_rooms

    def _can_have_props(obj):
        return isinstance(obj, (Face, Door))

    def _get_children(obj):
        if isinstance(obj, Room):
            return [f for f in obj.faces if _is_exterior_wall(f)]
        return []

    updated = _apply_properties_by_orientation(all_targets, constrs, mods, _can_have_props, _get_children)
    return post_edit_pipeline({"status": "success", "updated_count": updated})


def apply_window_attributes_impl(
    construction_identifiers=None,
    modifier_identifiers=None,
    custom_construction=None,
    aperture_identifiers=None,
    door_identifiers=None,
    face_identifiers=None,
    room_identifiers=None,
):
    _ensure_model()
    if custom_construction and construction_identifiers:
        raise ValueError("custom_construction and construction_identifiers cannot be used together.")
    constrs = [window_construction_by_identifier(cid) for cid in construction_identifiers] if construction_identifiers else []
    if custom_construction:
        constrs = [_build_custom_window_construction(custom_construction)]
    mods = [resolve_modifier(manager, mid) or modifier_by_identifier(mid) for mid in modifier_identifiers] if modifier_identifiers else []
    if not constrs and not mods:
        return {"status": "skipped", "message": "No constructions or modifiers provided."}
    t_aps = _get_model_objects(aperture_identifiers, Aperture)
    t_drs = _get_model_objects(door_identifiers, Door)
    t_faces = _get_model_objects(face_identifiers, Face)
    t_rooms = _get_model_objects(room_identifiers, Room)
    if not any([aperture_identifiers, door_identifiers, face_identifiers, room_identifiers]):
        t_rooms = list(manager.model.rooms)
    all_targets = t_aps + t_drs + t_faces + t_rooms

    def _can_have_props(obj):
        return isinstance(obj, (Aperture, Door))

    def _get_children(obj):
        if isinstance(obj, Face):
            return list(obj.apertures)
        if isinstance(obj, Room):
            aps = []
            for f in obj.faces:
                if _is_exterior_wall(f):
                    aps.extend(list(f.apertures))
            return aps
        return []

    updated = _apply_properties_by_orientation(all_targets, constrs, mods, _can_have_props, _get_children)
    return post_edit_pipeline({"status": "success", "updated_count": updated})


def apply_shade_attributes_impl(
    construction_identifiers=None,
    modifier_identifiers=None,
    custom_construction=None,
    shade_identifiers=None,
    aperture_identifiers=None,
    door_identifiers=None,
    face_identifiers=None,
    room_identifiers=None,
):
    _ensure_model()
    if custom_construction and construction_identifiers:
        raise ValueError("custom_construction and construction_identifiers cannot be used together.")
    constrs = [shade_construction_by_identifier(cid) for cid in construction_identifiers] if construction_identifiers else []
    if custom_construction:
        constrs = [_build_custom_shade_construction(custom_construction)]
    mods = [resolve_modifier(manager, mid) or modifier_by_identifier(mid) for mid in modifier_identifiers] if modifier_identifiers else []
    if not constrs and not mods:
        return {"status": "skipped", "message": "No constructions or modifiers provided."}
    t_shds = _get_model_objects(shade_identifiers, Shade)
    t_aps = _get_model_objects(aperture_identifiers, Aperture)
    t_drs = _get_model_objects(door_identifiers, Door)
    t_faces = _get_model_objects(face_identifiers, Face)
    t_rooms = _get_model_objects(room_identifiers, Room)
    if not any([shade_identifiers, aperture_identifiers, door_identifiers, face_identifiers, room_identifiers]):
        t_rooms = list(manager.model.rooms)
        t_shds.extend(manager.model.orphaned_shades)
    all_targets = t_shds + t_aps + t_drs + t_faces + t_rooms

    def _can_have_props(obj):
        return isinstance(obj, Shade)

    def _get_children(obj):
        shades = []
        if hasattr(obj, "shades"):
            shades.extend(list(obj.shades))
        if isinstance(obj, Face):
            for ap in obj.apertures:
                shades.extend(list(ap.shades))
            for dr in obj.doors:
                shades.extend(list(dr.shades))
        elif isinstance(obj, Room):
            for f in obj.faces:
                shades.extend(list(f.shades))
                for ap in f.apertures:
                    shades.extend(list(ap.shades))
                for dr in f.doors:
                    shades.extend(list(dr.shades))
        return shades

    updated = _apply_properties_by_orientation(all_targets, constrs, mods, _can_have_props, _get_children)
    return post_edit_pipeline({"status": "success", "updated_count": updated})
