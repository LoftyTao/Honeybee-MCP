---
name: "honeybee-query"
description: "Use when a task requires inspecting Honeybee geometry, hierarchy, Energy attributes, Radiance attributes, or HBJSON-native Energy/Radiance resources through the unified `query` bus."
---

# Honeybee Query

## Use This Skill When

- The user asks what exists in the model
- The user needs identifiers before editing
- The user needs geometry, topology, or area data
- The user needs Energy or Radiance inspection
- The user needs reusable Energy or Radiance resource inspection
- The user needs sensor grid or view inspection
- The user only needs counts

## Preferred Tool

### `query`
**Description**
Unified query bus for Honeybee, Energy, and Radiance properties.

**Args**
- `target_type: str`
  Allowed: `model`, `room`, `face`, `aperture`, `door`, `subface`, `shade`, `schedule`, `schedule_day`, `schedule_type_limit`, `energy_resource`, `modifier`, `modifier_set`, `radiance_resource`, `sensor_grid`, `view`
- `identifiers: list | None = None`
  Optional identifier scope. Omit to query all objects of the target type.
- `fields: list | None = None`
  Field names or nested attribute paths. Defaults to `["identifier", "display_name"]`.
- `output_mode: str = "records"`
  Allowed: `records`, `list`, `count`
- `resource_category: str | None = None`
  Used with aggregated resource targets such as `energy_resource` or `radiance_resource`.

**Returns**
- `success: bool`
- `target_type: str`
- `count: int` when relevant
- `data: dict | list`
- `missing: list`

## Field Families

### Model summary fields
- `identifier`
- `display_name`
- `rooms`
- `faces`
- `apertures`
- `doors`
- `shades`
- `shade_meshes`
- `stories`
- `floor_area`
- `volume`
- `exposed_area`

### Geometry and topology fields
- `type`
- `boundary_condition`
- `area`
- `perimeter`
- `normal`
- `center`
- `vertices`
- `aperture_ratio`
- `is_exterior`

### Relationship fields
- `parent`
- `top_level_parent`
- `has_parent`
- `sub_faces`
- `indoor_shades`
- `outdoor_shades`

### Energy / Radiance path examples
- `properties.energy.program_type.display_name`
- `properties.energy.hvac.display_name`
- `properties.energy.construction.display_name`
- `properties.radiance.modifier_set.display_name`
- `properties.radiance.modifier.display_name`

### Resource query examples
- `schedule_kind`
- `resource_category`
- `resource_source`
- `default_day_schedule`
- `schedule_type_limit`
- `modifier_type`
- `sensor_count`
- `view_type`

## Examples

### Simple overview
```python
query(
    target_type="model",
    fields=["identifier", "display_name", "rooms", "floor_area"]
)
```

### Count-only query
```python
query(
    target_type="aperture",
    fields=["identifier"],
    output_mode="count"
)
```

### Face inspection before editing
```python
query(
    target_type="face",
    identifiers=["Face_1", "Face_2"],
    fields=["identifier", "type", "boundary_condition", "area", "aperture_ratio"]
)
```

### Energy and Radiance inspection
```python
query(
    target_type="room",
    identifiers=["Room_1"],
    fields=[
        "identifier",
        "properties.energy.program_type.display_name",
        "properties.energy.hvac.display_name",
        "properties.radiance.modifier_set.display_name"
    ]
)
```

### Energy resource inspection
```python
query(
    target_type="schedule",
    identifiers=["Office_Occ_Schedule"],
    fields=["identifier", "schedule_kind", "default_day_schedule", "schedule_type_limit"],
    output_mode="list"
)
```

```python
query(
    target_type="energy_resource",
    resource_category="constructions",
    fields=["identifier", "resource_category", "resource_source"],
    output_mode="list"
)
```

### Radiance resource inspection
```python
query(
    target_type="modifier",
    identifiers=["TestPlastic"],
    fields=["identifier", "modifier_type", "resource_source"],
    output_mode="list"
)
```

```python
query(
    target_type="sensor_grid",
    fields=["identifier", "sensor_count"],
    output_mode="list"
)
```

### Batch reporting
```python
query(
    target_type="room",
    fields=[
        "identifier",
        "floor_area",
        "properties.energy.program_type.display_name"
    ],
    output_mode="list"
)
```

## Return Guidance

- For `target_type="model"`, `data` is a single dict.
- For `output_mode="records"`, `data` is identifier-keyed.
- For `output_mode="list"`, `data` is a list of row dicts.
- For `output_mode="count"`, use `count` directly.
- Inspect `missing` when identifiers are provided.
- For reusable resources, inspect `resource_source` to distinguish `model_attached` from `session_store`.

## Workflow

1. Start broad with model summary fields.
2. Narrow scope using identifiers.
3. Use resource targets when the user is asking about schedules, constructions, modifiers, modifier sets, sensor grids, or views directly.
4. Add nested Energy or Radiance paths only when needed.
5. Query again after `apply`, `add`, or `remove` to confirm results.
