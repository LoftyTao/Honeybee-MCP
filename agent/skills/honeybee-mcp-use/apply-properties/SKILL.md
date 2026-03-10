---
name: "honeybee-apply-properties"
description: "Use when a task requires applying Honeybee Energy or Radiance properties through the unified `apply` bus, including room attributes, HVAC, room loads, schedules, modifiers, modifier sets, sensor grids, views, and facade constructions."
---

# Honeybee Apply Properties

## Use This Skill When

- The user wants room-level Energy or Radiance attributes assigned
- The user wants HVAC applied or inspected through controlled inputs
- The user wants room load objects or schedule resources updated
- The user wants facade, window, or shade properties assigned
- The user wants Radiance modifiers, modifier sets, sensor grids, or views updated
- The exact identifier is known or can be found using `search_properties`

## Preferred Tool

### `apply`
**Description**
Unified property application bus for Honeybee, Energy, and Radiance operations.

**Args**
- `operation: str`
- `target_type: str`
- `identifiers: list | None = None`
- `values: dict | None = None`

**Returns**
- operation-specific dict
- usually `status`
- often `updated_count` or `updated_room_count`
- optional `warnings`
- optional `auto_save`

## Supported Operations

### `room_attributes`
**Typical `values`**
- `construction_set_identifier`
- `modifier_set_identifier`
- `program_type_identifier`
- `is_conditioned`
- `reset_loads`

**Simple example**
```python
apply(
    operation="room_attributes",
    target_type="room",
    values={"program_type_identifier": "Office_Open"}
)
```

**Scoped example**
```python
apply(
    operation="room_attributes",
    target_type="room",
    identifiers=["Room_1", "Room_2"],
    values={
        "construction_set_identifier": "Office_Construction_Set",
        "is_conditioned": True
    }
)
```

### `hvac`
**Typical `values`**
- `system_category`
- `system_type`
- `vintage`
- `name`
- `list_options`
- `economizer_type`
- `sensible_heat_recovery`
- `latent_heat_recovery`
- `demand_controlled_ventilation`
- `heating_limit`
- `cooling_limit`
- `radiant_type`

**Simple example**
```python
apply(
    operation="hvac",
    target_type="room",
    values={"system_category": "Ideal"}
)
```

**Options example**
```python
apply(
    operation="hvac",
    target_type="room",
    values={"system_category": "AllAir", "list_options": True}
)
```

**More complex example**
```python
apply(
    operation="hvac",
    target_type="room",
    identifiers=["Room_1", "Room_2"],
    values={
        "system_category": "AllAir",
        "system_type": "VAV",
        "vintage": "ASHRAE_2019",
        "sensible_heat_recovery": 0.7
    }
)
```

### `opaque_attributes`
**Typical `target_type`**
- `face`
- `door`
- `room`

**Typical `values`**
- `construction_identifiers` — list of library construction identifiers to apply
- `modifier_identifiers` — list of Radiance modifier identifiers to apply
- `custom_construction` — dict for creating and assigning a new opaque construction inline

**Library construction example**
```python
apply(
    operation="opaque_attributes",
    target_type="face",
    identifiers=["Face_1"],
    values={"construction_identifiers": ["Generic Exterior Wall"]}
)
```

**Custom construction example**

Create and assign a custom opaque construction in one step. Provide the `custom_construction` dict with `name`, `layers` (list of material dicts with `name`, `thickness`, `conductivity`, `density`, `specific_heat`):

```python
apply(
    operation="opaque_attributes",
    target_type="face",
    identifiers=["Face_1"],
    values={
        "custom_construction": {
            "name": "HighInsulation_Wall",
            "layers": [
                {
                    "name": "InsulationMat",
                    "thickness": 0.1,
                    "conductivity": 0.04,
                    "density": 30,
                    "specific_heat": 1000
                }
            ]
        }
    }
)
```

### `window_attributes`
**Typical `target_type`**
- `aperture`
- `door`
- `face`
- `room`

**Typical `values`**
- `construction_identifiers`
- `modifier_identifiers`
- `custom_construction`
- optional cross-scope identifiers

**Orientation-based example**
```python
apply(
    operation="window_attributes",
    target_type="room",
    values={
        "construction_identifiers": ["NorthGlass", "EastGlass", "SouthGlass", "WestGlass"]
    }
)
```

### `shade_attributes`
**Typical `target_type`**
- `shade`
- `aperture`
- `door`
- `face`
- `room`

> **Known Issue (B-01)**: Applying `modifier_identifiers` to shades via `shade_attributes` may trigger a `TypeError: unhashable type: 'dict'` in certain scenarios when the shade was created via `add` (louvers). If this occurs, the underlying bug is in the apply service and needs a code fix.

**Direct shade example**
```python
apply(
    operation="shade_attributes",
    target_type="shade",
    identifiers=["Shade_1", "Shade_2"],
    values={"modifier_identifiers": ["MetalModifier"]}
)
```

## Room Load Operations

Each operation uses `target_type="room"` and accepts specific `values`:

### `people`
| Parameter | Type | Description |
|-----------|------|-------------|
| `people_per_area` | float | People density (people/m²) |
| `occupancy_schedule_identifier` | str | Schedule for occupancy fraction |
| `activity_schedule_identifier` | str | Schedule for metabolic rate |
| `radiant_fraction` | float | Fraction of sensible heat radiant |
| `latent_fraction` | float | Fraction of gains that are latent |

```python
apply(
    operation="people",
    target_type="room",
    identifiers=["Room_1"],
    values={
        "people_per_area": 0.2,
        "occupancy_schedule_identifier": "Office_Occ_Schedule"
    }
)
```

### `lighting`
| Parameter | Type | Description |
|-----------|------|-------------|
| `watts_per_area` | float | Lighting power density (W/m²) |
| `schedule_identifier` | str | Lighting schedule |
| `return_air_fraction` | float | Fraction to return air |
| `radiant_fraction` | float | Radiant fraction |
| `visible_fraction` | float | Visible fraction |

```python
apply(
    operation="lighting",
    target_type="room",
    identifiers=["Room_1"],
    values={"watts_per_area": 10.0}
)
```

### `electric_equipment`
| Parameter | Type | Description |
|-----------|------|-------------|
| `watts_per_area` | float | Equipment power density (W/m²) |
| `schedule_identifier` | str | Equipment schedule |
| `radiant_fraction` | float | Radiant fraction |
| `latent_fraction` | float | Latent fraction |
| `lost_fraction` | float | Lost fraction |

```python
apply(
    operation="electric_equipment",
    target_type="room",
    identifiers=["Room_1"],
    values={"watts_per_area": 12.0}
)
```

### `service_hot_water`
| Parameter | Type | Description |
|-----------|------|-------------|
| `flow_per_area` | float | Hot water flow rate (L/h/m²) |
| `schedule_identifier` | str | Hot water usage schedule |
| `target_temperature` | float | Target temperature (°C) |
| `sensible_fraction` | float | Sensible fraction |
| `latent_fraction` | float | Latent fraction |

```python
apply(
    operation="service_hot_water",
    target_type="room",
    identifiers=["Room_1"],
    values={"flow_per_area": 0.1}
)
```

### `setpoint`
| Parameter | Type | Description |
|-----------|------|-------------|
| `heating_setpoint` | float | Heating setpoint (°C) |
| `cooling_setpoint` | float | Cooling setpoint (°C) |
| `heating_schedule_identifier` | str | Heating setpoint schedule |
| `cooling_schedule_identifier` | str | Cooling setpoint schedule |

```python
apply(
    operation="setpoint",
    target_type="room",
    identifiers=["Room_1"],
    values={"heating_setpoint": 20, "cooling_setpoint": 26}
)
```

### `ventilation`
| Parameter | Type | Description |
|-----------|------|-------------|
| `flow_per_person` | float | Flow per person (m³/s/person) |
| `flow_per_area` | float | Flow per area (m³/s/m²) |
| `air_changes_per_hour` | float | Air changes per hour |
| `flow_per_zone` | float | Flow per zone (m³/s) |
| `schedule_identifier` | str | Ventilation schedule |

```python
apply(
    operation="ventilation",
    target_type="room",
    identifiers=["Room_1"],
    values={"flow_per_person": 0.006}
)
```

### `process_load`
| Parameter | Type | Description |
|-----------|------|-------------|
| `process_identifier` | str | Identifier of existing process load to edit |
| `watts` | float | Process load power (W) |
| `schedule_identifier` | str | Process load schedule |
| `fuel_type` | str | Fuel type |
| `end_use_category` | str | End use category |
| `radiant_fraction` | float | Radiant fraction |
| `latent_fraction` | float | Latent fraction |
| `lost_fraction` | float | Lost fraction |

```python
apply(
    operation="process_load",
    target_type="room",
    identifiers=["Room_1"],
    values={
        "process_identifier": "Process_A",
        "watts": 600
    }
)
```

## Schedule Resource Operations

Update existing schedule resources. Use `add` to create new ones first.

### `schedule_type_limit`
```python
apply(
    operation="schedule_type_limit",
    target_type="schedule_type_limit",
    identifiers=["MyTypeLimit"],
    values={"upper_limit": 2.0, "numeric_type": "Continuous"}
)
```

### `schedule_day`
```python
apply(
    operation="schedule_day",
    target_type="schedule_day",
    identifiers=["MyDay"],
    values={"values": [0, 1, 0.5], "times": [[0, 0], [8, 0], [18, 0]]}
)
```

### `schedule_ruleset`
```python
apply(
    operation="schedule_ruleset",
    target_type="schedule",
    identifiers=["MySchedule"],
    values={"default_day_identifier": "NewDefaultDay"}
)
```

### `schedule_fixed_interval`
```python
apply(
    operation="schedule_fixed_interval",
    target_type="schedule",
    identifiers=["MyFixedSchedule"],
    values={"values": [0.5] * 8760}
)
```

## Radiance Resource and Analysis Operations

Update existing Radiance resources. Use `add` to create new ones first.

### `modifier`
```python
apply(
    operation="modifier",
    target_type="modifier",
    identifiers=["TestPlastic"],
    values={"r_reflectance": 0.6, "g_reflectance": 0.6, "b_reflectance": 0.6}
)
```

### `modifier_set`
```python
apply(
    operation="modifier_set",
    target_type="modifier_set",
    identifiers=["TestModSet"],
    values={"wall_modifier_identifier": "NewWallMod"}
)
```

### `sensor_grid`
```python
apply(
    operation="sensor_grid",
    target_type="sensor_grid",
    identifiers=["Grid_01"],
    values={"sensors": [{"pos": [2, 0, 0.8], "dir": [0, 0, 1]}]}
)
```

### `view`
```python
apply(
    operation="view",
    target_type="view",
    identifiers=["View_01"],
    values={"direction": [0, 1, 0]}
)
```

## Return Guidance

- Report `updated_room_count` for room or HVAC operations.
- Report `updated_count` for opaque, window, and shade operations.
- Surface `resource_changes` when schedules, constructions, modifiers, or modifier sets are created or updated as part of the operation.
- If `status="skipped"`, explain why no valid targets or values were applied.
- If `warnings` exist, surface them explicitly.
- If `auto_save` exists, mention shared-memory writeback.

## Error Handling

- If `success=False`, check the `error` field for details.
- Common failures: identifier not found, invalid `values` key, resource does not exist yet (use `add` first).
- For HVAC, use `list_options=True` first to discover valid `system_type` values before applying.

## Workflow

1. Query current state or search identifiers first.
2. If the work involves reusable resources, check whether it should be `add` first and `apply` second.
3. Apply the narrowest valid scope.
4. Re-query to verify the applied result.
