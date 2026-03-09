---
name: "honeybee-aperture-adder"
description: "Use when a task requires adding parameterized apertures to faces through the unified `add` bus."
---

# Honeybee Aperture Adder

## Use This Skill When

- The user wants windows or skylights added
- Apertures are parameterized, not freeform modeled
- The scope is face-based

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
- `width`
- `height`
- `sill_height`
- `aperture_identifier`

### `apertures_by_ratio`
Use for quick WWR-driven glazing.

**Params**
- `ratio`
- `tolerance`
- `rect_split`

### `apertures_by_ratio_rectangle`
Use when WWR and rectangular window behavior both matter.

**Params**
- `ratio`
- `aperture_height`
- `sill_height`
- `horizontal_separation`
- `vertical_separation`
- `tolerance`

### `apertures_by_ratio_gridded`
Use for modular or repetitive facade grids.

**Params**
- `ratio`
- `x_dim`
- `y_dim`
- `tolerance`

### `apertures_by_width_height_rectangle`
Use for repeated equal-size windows.

**Params**
- `aperture_height`
- `aperture_width`
- `sill_height`
- `horizontal_separation`
- `tolerance`

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

## Return Guidance

- Inspect `not_found` when face identifiers may be incomplete.
- Use `results` to report what was added on each face.
- Surface aperture identifiers if later `apply` or `query` steps will target them.
