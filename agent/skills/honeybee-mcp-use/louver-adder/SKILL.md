---
name: "honeybee-louver-adder"
description: "Use when a task requires adding aperture-attached louvers or blinds through the unified `add` bus."
---

# Honeybee Louver Adder

## Use This Skill When

- The user wants louvers, blinds, or repeated aperture-attached shades
- The target objects are apertures
- The geometry is count-based or spacing-based

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

### `louvers`
General louver constructor.

**Params**
- `depth`
- `louver_count`
- `distance`
- `offset`
- `angle`
- `contour_vector`
- `flip_start_side`
- `indoor`
- `tolerance`
- `base_name`

### `louvers_by_count`
Use when the number of louvers is known.

### `louvers_by_distance_between`
Use when spacing is known.

## Examples

### Count-based louvers
```python
add(
    operation="louvers_by_count",
    target_type="aperture",
    identifiers=["Aperture_1"],
    params={"louver_count": 5, "depth": 0.5}
)
```

### Distance-based louvers
```python
add(
    operation="louvers_by_distance_between",
    target_type="aperture",
    identifiers=["Aperture_1", "Aperture_2"],
    params={"distance": 0.3, "depth": 0.4}
)
```

### Angled indoor blinds
```python
add(
    operation="louvers",
    target_type="aperture",
    identifiers=["Aperture_3"],
    params={
        "depth": 0.25,
        "louver_count": 4,
        "angle": 30,
        "indoor": True
    }
)
```

## Return Guidance

- Surface `shade_identifiers` when later shade query or removal is likely.
- Use `results` to explain per-aperture success when processing many apertures.
