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

## Complete Field Reference

### Model fields

| Field | Description |
|-------|-------------|
| `identifier` | Model identifier |
| `display_name` | Display name |
| `rooms` | List of room identifiers |
| `faces` | List of face identifiers |
| `apertures` | List of aperture identifiers |
| `doors` | List of door identifiers |
| `shades` | List of shade identifiers |
| `shade_meshes` | List of shade mesh identifiers |
| `indoor_shades` | List of indoor shade identifiers |
| `outdoor_shades` | List of outdoor shade identifiers |
| `orphaned_faces` | List of orphaned face identifiers |
| `orphaned_shades` | List of orphaned shade identifiers |
| `orphaned_apertures` | List of orphaned aperture identifiers |
| `orphaned_doors` | List of orphaned door identifiers |
| `stories` | Story list |
| `volume` | Total model volume |
| `floor_area` | Total floor area |
| `exposed_area` | Total exposed area |
| `exterior_wall_area` | Total exterior wall area |
| `exterior_roof_area` | Total exterior roof area |
| `exterior_aperture_area` | Total exterior aperture area |
| `exterior_wall_aperture_area` | Exterior wall aperture area only |
| `exterior_skylight_aperture_area` | Exterior skylight aperture area only |

### Room fields

| Field | Description |
|-------|-------------|
| `identifier` | Room identifier |
| `display_name` | Display name |
| `story` | Story assignment |
| `multiplier` | Room multiplier |
| `floor_area` | Floor area (m²) |
| `volume` | Volume (m³) |
| `exposed_area` | Exposed surface area |
| `exterior_wall_area` | Exterior wall area for this room |
| `exterior_aperture_area` | Exterior aperture area for this room |

### Face fields

| Field | Description |
|-------|-------------|
| `identifier` | Face identifier |
| `display_name` | Display name |
| `type` | Face type (Wall, Floor, RoofCeiling, AirBoundary) |
| `boundary_condition` | Boundary condition string |
| `apertures` | List of child aperture identifiers |
| `doors` | List of child door identifiers |
| `sub_faces` | Combined aperture + door identifiers |
| `indoor_shades` | Indoor shade identifiers |
| `outdoor_shades` | Outdoor shade identifiers |
| `parent` | Parent room identifier |
| `has_parent` | Whether the face has a parent |
| `has_sub_faces` | Whether the face has sub-faces |
| `can_be_ground` | Whether the face can be ground |
| `is_exterior` | Whether the face is exterior |
| `vertices` | Vertex coordinates |
| `punched_vertices` | Vertices with holes punched for sub-faces |
| `upper_left_vertices` | Upper-left vertex ordering |
| `normal` | Face normal vector |
| `center` | Face center point |
| `area` | Face area (m²) |
| `perimeter` | Face perimeter (m) |
| `aperture_area` | Total area of child apertures |
| `aperture_ratio` | Window-to-wall ratio |
| `tilt` | Tilt angle from horizontal (degrees) |
| `altitude` | Altitude angle |
| `azimuth` | Azimuth angle from north (degrees, 0=N, 90=E, 180=S, 270=W) |

### Aperture fields

| Field | Description |
|-------|-------------|
| `identifier` | Aperture identifier |
| `display_name` | Display name |
| `boundary_condition` | Boundary condition string |
| `is_operable` | Whether the aperture is operable |
| `is_exterior` | Whether the aperture is exterior |
| `has_parent` | Whether the aperture has a parent |
| `parent` | Parent face identifier |
| `top_level_parent` | Top-level parent (room) identifier |
| `vertices` | Vertex coordinates |
| `upper_left_vertices` | Upper-left vertex ordering |
| `normal` | Normal vector |
| `center` | Center point |
| `area` | Area (m²) |
| `perimeter` | Perimeter (m) |
| `tilt` | Tilt angle (degrees) |
| `altitude` | Altitude angle |
| `azimuth` | Azimuth from north (degrees) |
| `indoor_shades` | Indoor shade identifiers |
| `outdoor_shades` | Outdoor shade identifiers |

### Door fields

| Field | Description |
|-------|-------------|
| `identifier` | Door identifier |
| `display_name` | Display name |
| `boundary_condition` | Boundary condition string |
| `is_glass` | Whether the door is glass |
| `is_exterior` | Whether the door is exterior |
| `has_parent` | Whether the door has a parent |
| `parent` | Parent face identifier |
| `top_level_parent` | Top-level parent (room) identifier |
| `vertices` | Vertex coordinates |
| `normal` | Normal vector |
| `center` | Center point |
| `area` | Area (m²) |
| `perimeter` | Perimeter (m) |
| `tilt` | Tilt angle (degrees) |
| `altitude` | Altitude angle |
| `azimuth` | Azimuth from north (degrees) |
| `indoor_shades` | Indoor shade identifiers |
| `outdoor_shades` | Outdoor shade identifiers |

### Shade fields

| Field | Description |
|-------|-------------|
| `identifier` | Shade identifier |
| `display_name` | Display name |
| `is_detached` | Whether the shade is detached |
| `is_indoor` | Whether the shade is indoor |
| `has_parent` | Whether the shade has a parent |
| `parent` | Parent object identifier |
| `top_level_parent` | Top-level parent identifier |
| `vertices` | Vertex coordinates |
| `normal` | Normal vector |
| `center` | Center point |
| `area` | Area (m²) |
| `perimeter` | Perimeter (m) |
| `tilt` | Tilt angle (degrees) |
| `altitude` | Altitude angle |
| `azimuth` | Azimuth from north (degrees) |

### Schedule fields

| Field | Description |
|-------|-------------|
| `identifier` | Schedule identifier |
| `resource_category` | Category (e.g. `schedules`) |
| `resource_source` | Source: `library`, `model_attached`, or `session_store` |
| `schedule_kind` | Class name without "Schedule" prefix (e.g. `Ruleset`, `FixedInterval`) |
| `schedule_type_limit` | Linked ScheduleTypeLimit identifier |
| `default_day_schedule` | Default ScheduleDay identifier |
| `holiday_schedule` | Holiday ScheduleDay identifier |
| `summer_designday_schedule` | Summer design day ScheduleDay identifier |
| `winter_designday_schedule` | Winter design day ScheduleDay identifier |
| `schedule_rules` | Schedule rules list |
| `values` | Value list (FixedInterval) |
| `times` | Time list (FixedInterval) |
| `timestep` | Timestep (FixedInterval) |
| `interpolate` | Interpolation setting |

### ScheduleDay fields

| Field | Description |
|-------|-------------|
| `identifier` | ScheduleDay identifier |
| `resource_category` | Category |
| `resource_source` | Source |
| `values` | Value list |
| `times` | Time breakpoints |
| `interpolate` | Interpolation flag |

### ScheduleTypeLimit fields

| Field | Description |
|-------|-------------|
| `identifier` | ScheduleTypeLimit identifier |
| `resource_category` | Category |
| `resource_source` | Source |
| `lower_limit` | Lower bound value |
| `upper_limit` | Upper bound value |
| `numeric_type` | Continuous or Discrete |
| `unit_type` | Unit type (e.g. Dimensionless, Temperature) |

### Modifier fields

| Field | Description |
|-------|-------------|
| `identifier` | Modifier identifier |
| `resource_category` | Category |
| `resource_source` | Source |
| `modifier_type` | Modifier class name (e.g. Plastic, Glass, Trans) |
| `display_name` | Display name |

### ModifierSet fields

| Field | Description |
|-------|-------------|
| `identifier` | ModifierSet identifier |
| `resource_category` | Category |
| `resource_source` | Source |
| `display_name` | Display name |
| `wall_set` | Wall modifier sub-set object |
| `floor_set` | Floor modifier sub-set object |
| `roof_ceiling_set` | Roof/ceiling modifier sub-set object |
| `aperture_set` | Aperture modifier sub-set object |
| `door_set` | Door modifier sub-set object |
| `shade_set` | Shade modifier sub-set object |
| `air_boundary_modifier` | Air boundary modifier identifier |

### SensorGrid fields

| Field | Description |
|-------|-------------|
| `identifier` | Grid identifier |
| `display_name` | Display name |
| `sensor_count` | Number of sensor points |
| `room_identifier` | Associated room identifier |
| `mesh` | Underlying mesh object |
| `sensors` | List of sensor objects |

### View fields

| Field | Description |
|-------|-------------|
| `identifier` | View identifier |
| `position` | Viewpoint position (x, y, z) |
| `direction` | View direction vector |
| `up_vector` | Up direction vector |
| `view_type` | View projection type |
| `h_size` | Horizontal size |
| `v_size` | Vertical size |
| `shift` | Horizontal shift |
| `lift` | Vertical lift |

### Energy / Radiance nested path examples

Access deep properties using dot-separated paths:

- `properties.energy.program_type.display_name`
- `properties.energy.program_type.identifier`
- `properties.energy.hvac.display_name`
- `properties.energy.construction.display_name`
- `properties.energy.construction.identifier`
- `properties.energy.construction_set.identifier`
- `properties.energy.is_conditioned`
- `properties.radiance.modifier_set.display_name`
- `properties.radiance.modifier_set.identifier`
- `properties.radiance.modifier.display_name`
- `properties.radiance.modifier.identifier`

## Examples

### Model overview
```python
query(
    target_type="model",
    fields=["identifier", "display_name", "rooms", "floor_area",
            "exterior_wall_area", "exterior_aperture_area"]
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

### Finding exterior walls by orientation

Use this pattern before adding apertures or assigning constructions:

```python
query(
    target_type="face",
    fields=["identifier", "display_name", "type", "boundary_condition",
            "azimuth", "area", "aperture_ratio", "parent"],
    output_mode="list"
)
```

Then filter client-side for `type == "Wall"` and `boundary_condition` containing `"Outdoors"`, and use `azimuth` to determine orientation (0=North, 90=East, 180=South, 270=West).

### Face inspection before editing
```python
query(
    target_type="face",
    identifiers=["Face_1", "Face_2"],
    fields=["identifier", "type", "boundary_condition", "area",
            "aperture_ratio", "has_sub_faces", "azimuth"]
)
```

### Room Energy and Radiance inspection
```python
query(
    target_type="room",
    identifiers=["Room_1"],
    fields=[
        "identifier",
        "properties.energy.program_type.display_name",
        "properties.energy.hvac.display_name",
        "properties.energy.construction_set.identifier",
        "properties.energy.is_conditioned",
        "properties.radiance.modifier_set.display_name"
    ]
)
```

### Energy resource inspection
```python
query(
    target_type="schedule",
    identifiers=["Office_Occ_Schedule"],
    fields=["identifier", "schedule_kind", "default_day_schedule",
            "schedule_type_limit", "holiday_schedule"],
    output_mode="list"
)
```

```python
query(
    target_type="energy_resource",
    resource_category="constructions",
    fields=["identifier", "resource_category", "resource_source", "type"],
    output_mode="list"
)
```

### ScheduleTypeLimit inspection
```python
query(
    target_type="schedule_type_limit",
    identifiers=["Fractional"],
    fields=["identifier", "lower_limit", "upper_limit", "numeric_type", "unit_type"]
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
    target_type="modifier_set",
    identifiers=["TestModSet"],
    fields=["identifier", "wall_set", "floor_set", "roof_ceiling_set",
            "aperture_set", "resource_source"]
)
```

### SensorGrid and View inspection
```python
query(
    target_type="sensor_grid",
    fields=["identifier", "sensor_count", "room_identifier"],
    output_mode="list"
)
```

```python
query(
    target_type="view",
    fields=["identifier", "position", "direction", "up_vector", "view_type"],
    output_mode="list"
)
```

### Aggregated Radiance resource overview
```python
query(
    target_type="radiance_resource",
    fields=["identifier", "resource_category", "resource_source", "type"],
    output_mode="list"
)
```

### Batch room reporting
```python
query(
    target_type="room",
    fields=[
        "identifier",
        "display_name",
        "story",
        "floor_area",
        "volume",
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
6. Use `azimuth`/`type`/`boundary_condition` to help find specific faces when the user describes orientation or location rather than providing identifiers.
