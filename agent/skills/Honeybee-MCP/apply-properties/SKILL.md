---
name: "honeybee-apply-properties"
description: "Applies energy and radiance properties to model elements including constructions, modifiers, program types, and HVAC systems. Invoke when user wants to assign or modify building properties."
---

# Honeybee Apply Properties

This skill applies energy and radiance properties to Honeybee model elements.

## Tools

### apply_room_attributes

Apply Construction Set, Modifier Set, Program Type, or conditioning status to specific rooms.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `construction_set_identifier` | string | None | Name of the Construction Set to apply. |
| `modifier_set_identifier` | string | None | Name of the Modifier Set to apply for Radiance. |
| `program_type_identifier` | string | None | Name of the Program Type to apply. |
| `is_conditioned` | bool | None | Control HVAC conditioning status: True=add Ideal Air, False=remove HVAC, None=no change. |
| `reset_loads` | bool | False | If True and program_type_identifier is set, reset all room loads to match the program type. |
| `room_identifiers` | list | None | List of room IDs to apply changes to. If None or empty, applies to all rooms. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `status` | str | "success" or "skipped" |
| `updated_room_count` | int | Number of rooms modified |
| `conditioning_changes` | int | Number of rooms with HVAC changes |
| `applied_attributes` | dict | Attributes that were applied |
| `warnings` | list | Any warnings about overridden loads |
| `target_scope` | str | "specific_rooms" or "all_rooms" |

**Example:**
```python
apply_room_attributes(program_type_identifier="Office_Open")
apply_room_attributes(construction_set_identifier="Default", room_identifiers=["Room_1"])
apply_room_attributes(is_conditioned=True, reset_loads=True)
```

---

### apply_hvac

Unified tool to apply ANY HVAC system (Ideal, AllAir, DOAS, HeatCool, SHW) to rooms.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `system_category` | string | "Ideal" | HVAC system category: "Ideal", "AllAir", "DOAS", "HeatCool", "SHW". |
| `system_type` | string | None | Specific system type within the category. Required for AllAir, DOAS, HeatCool, SHW. |
| `vintage` | string | "ASHRAE_2019" | Standard year for equipment efficiency. |
| `name` | string | None | Display name for the HVAC system. Auto-generated if not provided. |
| `room_identifiers` | list | None | List of room IDs to apply HVAC to. If None, applies to all rooms. |
| `list_options` | bool | False | If True, return available system types and vintages instead of applying. |
| `economizer_type` | string | None | Economizer type for AllAir/DOAS: "NoEconomizer", "DifferentialDryBulb", etc. |
| `sensible_heat_recovery` | float | None | Sensible heat recovery effectiveness (0-1). |
| `latent_heat_recovery` | float | None | Latent heat recovery effectiveness (0-1). |
| `demand_controlled_ventilation` | bool | False | Enable DCV based on CO2 levels. |
| `heating_air_temperature` | float | None | Supply air temperature for heating (°C). Ideal Air only. |
| `cooling_air_temperature` | float | None | Supply air temperature for cooling (°C). Ideal Air only. |
| `heating_limit` | string | None | Maximum heating capacity: number (W), "Autosize", "NoLimit". |
| `cooling_limit` | string | None | Maximum cooling capacity: number (W), "Autosize", "NoLimit". |
| `radiant_type` | string | None | Radiant panel type: "Floor", "Ceiling", "FloorWithCarpet", etc. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `status` | str | "success", "skipped", "info", or "error" |
| `category` | str | System category applied |
| `system_type` | str | Specific system type |
| `system_name` | str | Display name of the system |
| `updated_room_count` | int | Number of rooms updated |
| `available_types` | list | Available system types (if list_options=True) |

**Example:**
```python
apply_hvac()  # Apply Ideal Air to all rooms
apply_hvac(system_category="AllAir", system_type="VAV", list_options=True)
apply_hvac(system_category="AllAir", system_type="VAV", room_identifiers=["Room_1"])
apply_hvac(system_category="HeatCool", system_type="Radiant", radiant_type="Floor")
```

---

### apply_opaque_attributes

Apply Opaque Constructions (Energy) or Modifiers (Radiance).

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `construction_identifiers` | list | None | List of opaque construction names to apply. |
| `modifier_identifiers` | list | None | List of Radiance modifier names to apply. |
| `face_identifiers` | list | None | List of face identifiers to apply properties to. |
| `door_identifiers` | list | None | List of door identifiers to apply properties to. |
| `room_identifiers` | list | None | List of room identifiers. Applies to exterior walls only. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `status` | str | "success" or "skipped" |
| `updated_count` | int | Number of objects updated |
| `message` | str | Status message (if skipped) |

**Example:**
```python
apply_opaque_attributes(construction_identifiers=["ConcreteWall"])
apply_opaque_attributes(construction_identifiers=["NorthWall", "SouthWall", "EastWall", "WestWall"])
apply_opaque_attributes(room_identifiers=["Room_1"], construction_identifiers=["BrickWall"])
```

---

### apply_window_attributes

Apply Window Constructions (Energy) or Modifiers (Radiance).

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `construction_identifiers` | list | None | List of window construction names to apply. |
| `modifier_identifiers` | list | None | List of Radiance modifier names for glass. |
| `aperture_identifiers` | list | None | List of aperture identifiers to apply properties to. |
| `door_identifiers` | list | None | List of glass door identifiers to apply properties to. |
| `face_identifiers` | list | None | List of face identifiers. Applies to child apertures. |
| `room_identifiers` | list | None | List of room identifiers. Applies to apertures on exterior walls. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `status` | str | "success" or "skipped" |
| `updated_count` | int | Number of objects updated |
| `message` | str | Status message (if skipped) |

**Example:**
```python
apply_window_attributes(construction_identifiers=["DoubleGlazed"])
apply_window_attributes(construction_identifiers=["NorthGlazing", "SouthGlazing", "EastGlazing", "WestGlazing"])
apply_window_attributes(room_identifiers=["Room_1"], construction_identifiers=["LowEWindow"])
```

---

### apply_shade_attributes

Apply Shade Constructions (Energy) or Modifiers (Radiance).

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `construction_identifiers` | list | None | List of shade construction names to apply. |
| `modifier_identifiers` | list | None | List of Radiance modifier names for shades. |
| `shade_identifiers` | list | None | List of shade identifiers to apply properties to directly. |
| `aperture_identifiers` | list | None | List of aperture identifiers. Applies to attached shades. |
| `door_identifiers` | list | None | List of door identifiers. Applies to attached shades. |
| `face_identifiers` | list | None | List of face identifiers. Applies to attached shades. |
| `room_identifiers` | list | None | List of room identifiers. Applies to all attached shades. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `status` | str | "success" or "skipped" |
| `updated_count` | int | Number of objects updated |
| `message` | str | Status message (if skipped) |

**Example:**
```python
apply_shade_attributes(construction_identifiers=["MetalShade"])
apply_shade_attributes(shade_identifiers=["Overhang_1"], modifier_identifiers=["MetalMaterial"])
apply_shade_attributes(room_identifiers=["Room_1"], construction_identifiers=["LouverConstruction"])
```

## Orientation-Based Assignment

When multiple constructions/modifiers are provided, they are applied by orientation:
- 1 item: Applied to all
- 2 items: North, South
- 4 items: North, East, South, West
- 8 items: N, NE, E, SE, S, SW, W, NW

## Workflow

```
1. Load model
2. Search for available properties (optional): search_properties()
3. Apply properties to targets
4. Save model back to Grasshopper
```

## Notes

- Use `search_properties` to find valid identifiers
- Properties are applied to all rooms if no targets specified
- Orientation-based assignment uses face azimuth
- HVAC changes require conditioned rooms
