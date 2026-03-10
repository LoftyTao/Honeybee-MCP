---
name: "honeybee-door-editor"
description: "Use when a task requires inspecting door properties or deleting doors through the unified `query` and `remove` buses."
---

# Honeybee Door Editor

## Use This Skill When

- The user asks what doors exist in the model
- The user wants to inspect glass vs opaque doors
- The user wants to remove all doors
- The user wants to remove doors from selected faces
- The user wants to remove both doors and apertures together from selected faces

## Preferred Tools

### `query`
**Description**
Use for door inspection, door counts, geometric properties, and related shade relationships.

**Args**
- `target_type: str` — Use `"door"`
- `identifiers: list | None = None`
- `fields: list | None = None`
- `output_mode: str = "records"`

**Available fields for doors**

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

### `remove`
**Description**
Use for deleting doors either model-wide or face-scoped.

**Args**
- `operation: str`
- `identifiers: list | None = None`
- `options: dict | None = None`

**Returns**
- `success: bool`
- `message: str`
- operation-specific removal fields
- `auto_save: dict` when relevant

## Query Patterns

### Quick door inventory
```python
query(
    target_type="door",
    fields=["identifier"],
    output_mode="count"
)
```

### Door property inspection
```python
query(
    target_type="door",
    identifiers=["Door_1"],
    fields=["identifier", "boundary_condition", "is_glass", "area",
            "parent", "top_level_parent", "azimuth"]
)
```

### Batch reporting
```python
query(
    target_type="door",
    fields=["identifier", "is_glass", "boundary_condition", "area",
            "tilt", "azimuth", "parent"],
    output_mode="list"
)
```

## Remove Patterns

### Remove all doors
```python
remove(operation="all_doors")
```

### Remove doors from selected faces
```python
remove(
    operation="face_objects",
    identifiers=["Face_1", "Face_2"],
    options={"doors": True}
)
```

### Remove all subfaces from selected faces
```python
remove(
    operation="face_objects",
    identifiers=["Face_3"],
    options={"sub_faces": True}
)
```

## Return Guidance

- For `query`, use `data` and `missing`.
- For `remove`, use `message` for quick confirmation and `results` for per-face detail.
- Mention `auto_save` when shared-memory writeback happens after deletion.

## Notes

- `sub_faces=True` removes both apertures and doors from selected faces.
- Door inspection should usually precede door deletion if the user has not named exact targets.
