---
name: "honeybee-aperture-adder"
description: "Use when a task requires adding parameterized apertures to faces through the unified `add` bus."
---

# Honeybee Aperture Adder

## Use This Skill When

- The user wants windows or skylights added
- Apertures are parameterized, not freeform modeled
- The scope is face-based

## Prerequisites

Before adding apertures, you must:

1. **Know the face identifiers** — Use `query` to discover them. Face identifiers are auto-generated and cannot be guessed.
2. **Confirm faces are exterior walls** — Filter by `type == "Wall"` and `boundary_condition` containing `"Outdoors"`. Interior faces and floors cannot receive meaningful window ratios.
3. **Clear existing apertures if needed** — If a face already has apertures, adding more may fail or produce unexpected results. Use `remove(operation="face_objects", ...)` first.

### Face discovery pattern

```python
# Step 1: Query all faces
query(
    target_type="face",
    fields=["identifier", "type", "boundary_condition", "azimuth",
            "area", "aperture_ratio", "parent"],
    output_mode="list"
)

# Step 2: Filter client-side for exterior walls
# type == "Wall" AND boundary_condition contains "Outdoors"
# Use azimuth for orientation: 0=N, 90=E, 180=S, 270=W

# Step 3: Clear existing apertures if any
remove(
    operation="face_objects",
    identifiers=["Face_1", "Face_2"],
    options={"apertures": True}
)
```

## Preferred Tool

### `add`
**Args**
- `operation: str`
- `target_type: str`
- `identifiers: list | None = None`
- `params: dict | None = None`

**Returns**
- `success: bool`
- `message: str`
- `results: list`
- `not_found: list`
- `auto_save: dict` when relevant

## Operation Matrix

### `aperture_by_width_height`
Use for one centered aperture per face.

**Params**
- `width` — Window width (m)
- `height` — Window height (m)
- `sill_height` — Distance from face bottom to window bottom (m, default 0.8)
- `aperture_identifier` — Optional custom identifier

### `apertures_by_ratio`
Use for quick WWR-driven glazing. Simplest method.

**Params**
- `ratio` — Window-to-wall ratio (0.0–1.0)
- `tolerance` — Geometry tolerance (default from model)
- `rect_split` — Whether to split into rectangular sub-apertures

### `apertures_by_ratio_rectangle`
Use when WWR and rectangular window behavior both matter.

**Params**
- `ratio` — Window-to-wall ratio
- `aperture_height` — Height of each window (m)
- `sill_height` — Sill height (m)
- `horizontal_separation` — Horizontal gap between windows (m)
- `vertical_separation` — Vertical gap (m, if stacked)
- `tolerance` — Geometry tolerance

### `apertures_by_ratio_gridded`
Use for modular or repetitive facade grids.

**Params**
- `ratio` — Window-to-wall ratio
- `x_dim` — Grid cell width (m)
- `y_dim` — Grid cell height (m)
- `tolerance` — Geometry tolerance

### `apertures_by_width_height_rectangle`
Use for repeated equal-size windows.

**Params**
- `aperture_height` — Height of each window (m)
- `aperture_width` — Width of each window (m)
- `sill_height` — Sill height (m)
- `horizontal_separation` — Horizontal gap between windows (m)
- `tolerance` — Geometry tolerance

## Examples

### Single-window example
```python
add(
    operation="aperture_by_width_height",
    target_type="face",
    identifiers=["Face_1"],
    params={"width": 2.0, "height": 1.5, "sill_height": 0.9}
)
```

### Fast WWR example
```python
add(
    operation="apertures_by_ratio",
    target_type="face",
    identifiers=["Face_1", "Face_2"],
    params={"ratio": 0.4}
)
```

### Gridded facade example
```python
add(
    operation="apertures_by_ratio_gridded",
    target_type="face",
    identifiers=["Face_1", "Face_2"],
    params={"ratio": 0.35, "x_dim": 1.2, "y_dim": 1.5}
)
```

### Complete workflow: query → remove → add → verify
```python
# 1. Find south-facing exterior walls
faces = query(target_type="face",
    fields=["identifier", "type", "boundary_condition", "azimuth", "area"],
    output_mode="list")
# Filter for: type=="Wall", boundary_condition containing "Outdoors", azimuth ~180

# 2. Clear existing apertures
remove(operation="face_objects", identifiers=south_face_ids,
    options={"apertures": True})

# 3. Add new apertures by ratio
add(operation="apertures_by_ratio", target_type="face",
    identifiers=south_face_ids, params={"ratio": 0.4})

# 4. Verify
query(target_type="face", identifiers=south_face_ids,
    fields=["identifier", "aperture_ratio", "apertures"])
```

## Return Guidance

- Inspect `not_found` when face identifiers may be incomplete.
- Use `results` to report what was added on each face.
- Surface aperture identifiers if later `apply` or `query` steps will target them.
- Check `results[i].error` for per-face failure messages.
