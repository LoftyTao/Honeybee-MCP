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

## Dependency Chain

Energy schedule resources must be created in dependency order:

```
ScheduleTypeLimit → ScheduleDay → ScheduleRuleset
```

- A `ScheduleRuleset` references a `ScheduleDay` as its default day.
- A `ScheduleRuleset` optionally references a `ScheduleTypeLimit`.
- A `ScheduleDay` is standalone but should match the value range of its eventual `ScheduleTypeLimit`.
- Creating a `ScheduleRuleset` before its `ScheduleDay` exists will fail.

## Add Operations — Complete `params` Reference

### `schedule_type_limit`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `identifier` | str | yes | Unique identifier |
| `lower_limit` | float | no | Lower bound (default 0) |
| `upper_limit` | float | no | Upper bound (default 1) |
| `numeric_type` | str | no | `Continuous` or `Discrete` |
| `unit_type` | str | no | e.g. `Dimensionless`, `Temperature`, `Power` |

```python
add(
    operation="schedule_type_limit",
    target_type="model",
    params={
        "identifier": "OfficeFraction",
        "lower_limit": 0,
        "upper_limit": 1,
        "numeric_type": "Continuous",
        "unit_type": "Dimensionless"
    }
)
```

### `schedule_day`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `identifier` | str | yes | Unique identifier |
| `values` | list[float] | yes | Value at each time breakpoint |
| `times` | list[list[int]] | no | Time breakpoints as `[hour, minute]` pairs. Default `[[0, 0]]` |
| `interpolate` | bool | no | Whether to interpolate between values |

```python
add(
    operation="schedule_day",
    target_type="model",
    params={
        "identifier": "OfficeDay",
        "values": [0, 1, 0.2],
        "times": [[0, 0], [8, 0], [18, 0]]
    }
)
```

### `schedule_ruleset`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `identifier` | str | yes | Unique identifier |
| `default_day_identifier` | str | yes | Existing ScheduleDay identifier |
| `schedule_type_limit_identifier` | str | no | Existing ScheduleTypeLimit identifier |

```python
add(
    operation="schedule_ruleset",
    target_type="model",
    params={
        "identifier": "OfficeOccupancy",
        "default_day_identifier": "OfficeDay",
        "schedule_type_limit_identifier": "OfficeFraction"
    }
)
```

### `schedule_fixed_interval`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `identifier` | str | yes | Unique identifier |
| `values` | list[float] | yes | Full list of values (e.g. 8760 for hourly) |
| `timestep` | int | no | Steps per hour (default 1) |
| `schedule_type_limit_identifier` | str | no | Existing ScheduleTypeLimit identifier |

```python
add(
    operation="schedule_fixed_interval",
    target_type="model",
    params={
        "identifier": "HourlyOccupancy",
        "values": [0.5] * 8760,
        "schedule_type_limit_identifier": "OfficeFraction"
    }
)
```

### `process_load`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `identifier` | str | yes | Unique identifier |
| `watts` | float | yes | Process load power (W) |
| `schedule_identifier` | str | no | Usage schedule |
| `fuel_type` | str | no | Fuel type |
| `end_use_category` | str | no | End use category |
| `radiant_fraction` | float | no | Radiant fraction |
| `latent_fraction` | float | no | Latent fraction |
| `lost_fraction` | float | no | Lost fraction |

```python
add(
    operation="process_load",
    target_type="room",
    identifiers=["Kitchen_1"],
    params={
        "identifier": "CookingEquipment",
        "watts": 500
    }
)
```

### `modifier`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `identifier` | str | yes | Unique identifier |
| `modifier_type` | str | yes | `plastic`, `glass`, `trans`, `metal`, `mirror`, `glow`, `light`, `bsdf` |
| `r_reflectance` | float | no | Red reflectance (plastic/metal) |
| `g_reflectance` | float | no | Green reflectance (plastic/metal) |
| `b_reflectance` | float | no | Blue reflectance (plastic/metal) |
| `specularity` | float | no | Specularity (plastic) |
| `roughness` | float | no | Roughness (plastic) |
| `r_transmittance` | float | no | Red transmittance (glass/trans) |
| `g_transmittance` | float | no | Green transmittance (glass/trans) |
| `b_transmittance` | float | no | Blue transmittance (glass/trans) |

```python
add(
    operation="modifier",
    target_type="model",
    params={
        "identifier": "WallPlastic",
        "modifier_type": "plastic",
        "r_reflectance": 0.5,
        "g_reflectance": 0.5,
        "b_reflectance": 0.5
    }
)
```

### `modifier_set`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `identifier` | str | yes | Unique identifier |
| `wall_interior_modifier` | str | no | Interior wall modifier identifier |
| `wall_exterior_modifier` | str | no | Exterior wall modifier identifier |
| `floor_interior_modifier` | str | no | Interior floor modifier identifier |
| `floor_exterior_modifier` | str | no | Exterior floor modifier identifier |
| `roof_ceiling_interior_modifier` | str | no | Interior roof/ceiling modifier identifier |
| `roof_ceiling_exterior_modifier` | str | no | Exterior roof/ceiling modifier identifier |
| `aperture_interior_modifier` | str | no | Interior aperture modifier identifier |
| `aperture_exterior_modifier` | str | no | Exterior aperture modifier identifier |
| `door_interior_modifier` | str | no | Interior door modifier identifier |
| `door_exterior_modifier` | str | no | Exterior door modifier identifier |
| `shade_exterior_modifier` | str | no | Exterior shade modifier identifier |
| `shade_interior_modifier` | str | no | Interior shade modifier identifier |

```python
add(
    operation="modifier_set",
    target_type="model",
    params={
        "identifier": "RoomModSet",
        "wall_interior_modifier": "WallPlastic",
        "wall_exterior_modifier": "WallPlastic",
        "floor_interior_modifier": "WallPlastic",
        "floor_exterior_modifier": "WallPlastic",
        "roof_ceiling_interior_modifier": "WallPlastic",
        "roof_ceiling_exterior_modifier": "WallPlastic"
    }
)
```

### `sensor_grid`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `identifier` | str | yes | Unique identifier |
| `sensors` | list[dict] | yes | Each sensor: `{"pos": [x,y,z], "dir": [dx,dy,dz]}` |
| `room_identifier` | str | no | Room to associate the grid with |

```python
add(
    operation="sensor_grid",
    target_type="model",
    params={
        "identifier": "Grid_01",
        "sensors": [
            {"pos": [0, 0, 0.8], "dir": [0, 0, 1]},
            {"pos": [1, 0, 0.8], "dir": [0, 0, 1]}
        ]
    }
)
```

### `view`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `identifier` | str | yes | Unique identifier |
| `position` | list[float] | yes | Viewpoint [x, y, z] |
| `direction` | list[float] | yes | View direction [dx, dy, dz] |
| `up_vector` | list[float] | no | Up vector (default [0, 0, 1]) |
| `view_type` | str | no | `v` (perspective), `h` (hemispherical), `l` (parallel) |
| `h_size` | float | no | Horizontal field of view |
| `v_size` | float | no | Vertical field of view |

```python
add(
    operation="view",
    target_type="model",
    params={
        "identifier": "View_01",
        "position": [0, 0, 1.6],
        "direction": [1, 0, 0],
        "up_vector": [0, 0, 1]
    }
)
```

## Assign Operations

After creating resources, assign them to host objects:

```python
# Assign schedule to room's People load
apply(
    operation="people",
    target_type="room",
    identifiers=["Room_1"],
    values={"occupancy_schedule_identifier": "OfficeOccupancy"}
)

# Assign modifier to face
apply(
    operation="opaque_attributes",
    target_type="face",
    identifiers=["Face_1"],
    values={"modifier_identifiers": ["WallPlastic"]}
)

# Assign modifier set to room
apply(
    operation="room_attributes",
    target_type="room",
    identifiers=["Room_1"],
    values={"modifier_set_identifier": "RoomModSet"}
)
```

## Remove Operations

### Resource removal with reference check

| Operation | Identifiers Type | Behavior |
|-----------|------------------|----------|
| `schedule` | Schedule identifiers | Blocked if referenced by loads |
| `schedule_day` | ScheduleDay identifiers | Blocked if referenced by rulesets |
| `schedule_type_limit` | ScheduleTypeLimit identifiers | Blocked if referenced by schedules |
| `modifier` | Modifier identifiers | Blocked if referenced by faces/modifier sets |
| `modifier_set` | ModifierSet identifiers | Blocked if referenced by rooms |
| `sensor_grid` | SensorGrid identifiers | Deleted directly |
| `view` | View identifiers | Deleted directly |
| `process_loads` | Room identifiers + `options.process_ids` | Deleted from rooms |

```python
remove(operation="schedule", identifiers=["OfficeOccupancy"])
remove(operation="modifier", identifiers=["WallPlastic"])
remove(operation="sensor_grid", identifiers=["Grid_01"])
remove(operation="view", identifiers=["View_01"])
remove(
    operation="process_loads",
    identifiers=["Kitchen_1"],
    options={"process_ids": ["CookingEquipment"]}
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

**Example: safe modifier deletion**

```python
# Step 1: Try to delete
result = remove(operation="modifier", identifiers=["WallPlastic"])
# If result contains "blocked" with references listed

# Step 2: Reassign the referencing faces to a different modifier
apply(
    operation="opaque_attributes",
    target_type="face",
    identifiers=["Face_1"],
    values={"modifier_identifiers": ["GenericWall"]}
)

# Step 3: Retry deletion
remove(operation="modifier", identifiers=["WallPlastic"])
```

## Round-Trip Verification Example

Complete create → assign → save → reload → verify workflow:

```python
# 1. Create resources in dependency order
add(operation="schedule_type_limit", target_type="model",
    params={"identifier": "TestFraction", "lower_limit": 0, "upper_limit": 1,
            "numeric_type": "Continuous", "unit_type": "Dimensionless"})

add(operation="schedule_day", target_type="model",
    params={"identifier": "TestDay", "values": [0, 1, 0],
            "times": [[0, 0], [8, 0], [18, 0]]})

add(operation="schedule_ruleset", target_type="model",
    params={"identifier": "TestSchedule", "default_day_identifier": "TestDay",
            "schedule_type_limit_identifier": "TestFraction"})

# 2. Assign to room
apply(operation="people", target_type="room", identifiers=["Bedroom_1"],
      values={"people_per_area": 0.2, "occupancy_schedule_identifier": "TestSchedule"})

# 3. Save
save_model(folder="output", name="roundtrip_test")

# 4. Reload
load_model("output/roundtrip_test.hbjson")

# 5. Verify resource survived
query(target_type="schedule", identifiers=["TestSchedule"],
      fields=["identifier", "schedule_kind", "default_day_schedule", "schedule_type_limit"])
```

## Persistence Reminder

These resources are now part of the HBJSON-oriented persistence path.

If they are serialized into the model, they survive:

- `save_model`
- `load_model`
- shared-memory auto-save
- version control restore

When the user cares about persistence, always finish with a save or a verification query after save/reload.
