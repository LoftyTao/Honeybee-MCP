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
- `construction_identifiers`
- `modifier_identifiers`
- `custom_construction`
- optional cross-scope identifiers

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

**Direct shade example**
```python
apply(
    operation="shade_attributes",
    target_type="shade",
    identifiers=["Shade_1", "Shade_2"],
    values={"modifier_identifiers": ["MetalModifier"]}
)
```

### Room Load Operations

Supported `operation` values include:

- `people`
- `lighting`
- `electric_equipment`
- `service_hot_water`
- `setpoint`
- `ventilation`
- `process_load`

These operations are primarily used with `target_type="room"`.

Typical patterns:

- update a room-level Energy load object
- reset an overridden object back to default
- attach a custom schedule by identifier
- edit an existing process load by `process_identifier`

Example:

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

### Schedule Resource Operations

Supported `operation` values include:

- `schedule_type_limit`
- `schedule_day`
- `schedule_ruleset`
- `schedule_fixed_interval`

These are resource-oriented update operations. Use them when the resource already exists and must be edited rather than created.

Typical patterns:

- update a custom `ScheduleDay`
- replace rules in a `ScheduleRuleset`
- update values in a `ScheduleFixedInterval`

### Radiance Resource and Analysis Operations

Supported `operation` values include:

- `modifier`
- `modifier_set`
- `sensor_grid`
- `view`

Use these when a custom Radiance resource or analysis object already exists and needs to be updated.

Example:

```python
apply(
    operation="modifier",
    target_type="modifier",
    identifiers=["TestPlastic"],
    values={"r_reflectance": 0.6, "g_reflectance": 0.6, "b_reflectance": 0.6}
)
```

## Return Guidance

- Report `updated_room_count` for room or HVAC operations.
- Report `updated_count` for opaque, window, and shade operations.
- Surface `resource_changes` when schedules, constructions, modifiers, or modifier sets are created or updated as part of the operation.
- If `status="skipped"`, explain why no valid targets or values were applied.
- If `warnings` exist, surface them explicitly.
- If `auto_save` exists, mention shared-memory writeback.

## Workflow

1. Query current state or search identifiers first.
2. If the work involves reusable resources, check whether it should be `add` first and `apply` second.
3. Apply the narrowest valid scope.
4. Re-query to verify the applied result.
