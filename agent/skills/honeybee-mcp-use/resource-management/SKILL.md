---
name: "honeybee-resource-management"
description: "Use when a task requires creating, querying, updating, or removing reusable Honeybee Energy or Radiance resources such as schedules, schedule type limits, constructions, materials, modifiers, modifier sets, sensor grids, or views through the unified buses."
---

# Honeybee Resource Management

## Use This Skill When

- The user is working directly with reusable Energy resources
- The user is working directly with reusable Radiance resources
- The user wants custom schedules, schedule days, or schedule type limits
- The user wants custom modifiers or modifier sets
- The user wants sensor grids or views added or edited
- The user wants resource-safe deletion with reference checks

## Core Idea

Honeybee-MCP now treats reusable Energy and Radiance objects as HBJSON-native resources.

This means a resource workflow should usually follow:

1. `query` existing resources or host objects
2. `search_properties` if a library identifier may already exist
3. `add` a custom resource when needed
4. `apply` the resource to rooms, faces, apertures, doors, shades, or model-level analysis objects
5. `query` again to verify both the resource and the host assignment
6. `save_model` or shared-memory sync when persistence matters

## Preferred Tools

### `query`

Use for direct resource inspection.

Important `target_type` values:

- `schedule`
- `schedule_day`
- `schedule_type_limit`
- `energy_resource`
- `modifier`
- `modifier_set`
- `radiance_resource`
- `sensor_grid`
- `view`

Useful fields:

- `identifier`
- `resource_category`
- `resource_source`
- `schedule_kind`
- `default_day_schedule`
- `schedule_type_limit`
- `modifier_type`
- `sensor_count`
- `view_type`

### `add`

Use for creating resources or analysis objects.

Important `operation` values:

- `schedule_type_limit`
- `schedule_day`
- `schedule_ruleset`
- `schedule_fixed_interval`
- `process_load`
- `modifier`
- `modifier_set`
- `sensor_grid`
- `view`

### `apply`

Use for updating existing resources or assigning them to host objects.

Important `operation` values:

- `people`
- `lighting`
- `electric_equipment`
- `service_hot_water`
- `setpoint`
- `ventilation`
- `process_load`
- `schedule_type_limit`
- `schedule_day`
- `schedule_ruleset`
- `schedule_fixed_interval`
- `modifier`
- `modifier_set`
- `sensor_grid`
- `view`
- `opaque_attributes`
- `window_attributes`
- `shade_attributes`

### `remove`

Use for deleting resources or analysis objects.

Important `operation` values:

- `process_loads`
- `schedule`
- `schedule_day`
- `schedule_type_limit`
- `modifier`
- `modifier_set`
- `sensor_grid`
- `view`

## Resource Patterns

### Energy Schedule Resources

Use `add` to create:

- `ScheduleTypeLimit`
- `ScheduleDay`
- `ScheduleRuleset`
- `ScheduleFixedInterval`

Then use `apply` to assign them to:

- `people`
- `lighting`
- `electric_equipment`
- `service_hot_water`
- `setpoint`
- `ventilation`
- `process_load`

Example:

```python
add(
    operation="schedule_ruleset",
    target_type="model",
    params={
        "identifier": "Office_Occ_Schedule",
        "default_day_identifier": "Office_Day",
        "schedule_type_limit_identifier": "Fractional"
    }
)

apply(
    operation="people",
    target_type="room",
    identifiers=["Room_1"],
    values={"occupancy_schedule_identifier": "Office_Occ_Schedule"}
)
```

### Energy Construction Resources

Use `apply` with `custom_construction` when a resource should be created and assigned in one step.

Important operations:

- `opaque_attributes`
- `window_attributes`
- `shade_attributes`

These workflows also write custom materials and constructions into serialized HBJSON.

### Radiance Resources

Use `add` to create:

- `modifier`
- `modifier_set`
- `sensor_grid`
- `view`

Use `apply` to:

- update a modifier or modifier set
- update a sensor grid or view
- assign `modifier_set_identifier` to rooms via `room_attributes`
- assign `modifier_identifiers` to faces, apertures, doors, or shades via facade attribute operations

Example:

```python
add(
    operation="modifier",
    target_type="model",
    params={
        "identifier": "TestPlastic",
        "modifier_type": "plastic",
        "r_reflectance": 0.5,
        "g_reflectance": 0.5,
        "b_reflectance": 0.5
    }
)

apply(
    operation="opaque_attributes",
    target_type="face",
    identifiers=["Face_1"],
    values={"modifier_identifiers": ["TestPlastic"]}
)
```

## Query-First Guidance

Before creating a resource, check:

- whether a library identifier already exists
- whether the model already has an attached equivalent
- whether a session resource with the same identifier already exists

Use `resource_source` to distinguish:

- `library`
- `model_attached`
- `session_store`

## Safe Deletion Guidance

Reusable resources should not be removed blindly.

When deleting:

- expect `blocked` results if the resource is still referenced
- inspect returned reference summaries
- remove or reassign host references first, then retry deletion

This is especially important for:

- schedules
- schedule days
- schedule type limits
- modifiers
- modifier sets

## Persistence Reminder

These resources are now part of the HBJSON-oriented persistence path.

If they are serialized into the model, they survive:

- `save_model`
- `load_model`
- shared-memory auto-save
- version control restore

When the user cares about persistence, always finish with a save or a verification query after save/reload.
