---
name: "honeybee-louver-adder"
description: "Use when a task requires adding aperture-attached louvers or blinds through the unified `add` bus."
---

# Honeybee Louver Adder

## Use This Skill When

- The user wants louvers, blinds, or repeated aperture-attached shades
- The target objects are apertures
- The geometry is count-based or spacing-based

## Prerequisites

- **Apertures must already exist** on the target faces. If no apertures exist, use `aperture-adder` first.
- Query aperture identifiers before calling add: `query(target_type="aperture", fields=["identifier", "parent"], output_mode="list")`

## Preferred Tool

### `add`
**Args**
- `operation: str`
- `target_type: str` — Must be `"aperture"`
- `identifiers: list | None = None`
- `params: dict | None = None`

**Returns**
- `success: bool`
- `message: str`
- `results: list` — Each item has `shade_identifiers` listing the created shades
- `not_found: list`
- `auto_save: dict` when relevant

## Operation Matrix

### `louvers`
General louver constructor. Most flexible.

**Params**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `depth` | float | required | Louver depth (m) |
| `louver_count` | int | None | Number of louvers |
| `distance` | float | None | Distance between louvers (alternative to count) |
| `offset` | float | 0 | Distance from aperture edge |
| `angle` | float | 0 | Tilt angle (degrees) |
| `contour_vector` | list | None | Direction for louver layout |
| `flip_start_side` | bool | False | Start from opposite side |
| `indoor` | bool | False | Place louvers on indoor side |
| `tolerance` | float | None | Geometry tolerance |
| `base_name` | str | None | Base name for shade identifiers |

### `louvers_by_count`
Use when the number of louvers is known.

**Params**
- `louver_count` — Number of louvers
- `depth` — Depth (m)
- Plus all optional params from `louvers`

### `louvers_by_distance_between`
Use when spacing is known.

**Params**
- `distance` — Spacing between louvers (m)
- `depth` — Depth (m)
- `max_count` — Optional maximum count
- Plus all optional params from `louvers`

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

- Surface `shade_identifiers` from `results[i]` when later shade query or removal is likely.
- Use `results` to explain per-aperture success when processing many apertures.
- The created shades can later be queried via `query(target_type="shade", ...)` or removed via `remove(operation="all_shades")`.
