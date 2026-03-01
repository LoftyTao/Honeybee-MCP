---
name: "honeybee-louver-adder"
description: "Adds shading louvers to apertures in Honeybee models. Invoke when user wants to add overhangs, fins, or blinds to windows."
---

# Honeybee Louver Adder

This skill adds shading louvers to apertures (windows) in Honeybee models.

## Tools

### add_louvers

Add a series of shading louvers to apertures.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `aperture_identifiers` | list | required | List of aperture identifiers to add louvers to. |
| `depth` | float | required | Depth of each louver in meters. Must be greater than 0. |
| `louver_count` | int | None | Number of louvers to create. If specified with distance, louver_count takes priority. |
| `distance` | float | None | Spacing between louvers in meters. Alternative to louver_count. |
| `offset` | float | 0 | Distance to offset louvers from the aperture in meters. |
| `angle` | float | 0 | Angle of louvers in degrees (0 = horizontal). |
| `contour_vector` | list | [0, 1] | 2D vector [x, y] defining louver direction. Default is vertical arrangement, horizontal louvers. |
| `flip_start_side` | boolean | False | If True, start louvers from the opposite side. |
| `indoor` | boolean | False | If True, create indoor shades (blinds). If False, create outdoor shades. |
| `tolerance` | float | 0.01 | Geometric tolerance for calculations in meters. |
| `base_name` | string | None | Base name for generated shade identifiers. If not provided, names are auto-generated. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the operation was successful |
| `message` | str | Summary of processed apertures |
| `results` | list | List of results for each aperture with aperture_identifier, shade_count, shade_identifiers, error |
| `not_found` | list | Aperture identifiers not found |

**Example:**
```python
# 5 louvers, 30cm deep
add_louvers(["Window_1"], depth=0.3, louver_count=5)
# 15cm spacing
add_louvers(["Window_2"], depth=0.2, distance=0.15)
# 30° angle
add_louvers(["Window_3"], depth=0.25, louver_count=4, angle=30)
```

---

### add_louvers_by_count

Add a specific number of shading louvers to apertures.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `aperture_identifiers` | list | required | List of aperture identifiers to add louvers to. |
| `louver_count` | int | required | Number of louvers to create. Must be a positive integer. |
| `depth` | float | required | Depth of each louver in meters. Must be greater than 0. |
| `offset` | float | 0 | Distance to offset louvers from the aperture in meters. |
| `angle` | float | 0 | Angle of louvers in degrees (0 = horizontal). |
| `contour_vector` | list | [0, 1] | 2D vector [x, y] defining louver direction. |
| `flip_start_side` | boolean | False | If True, start louvers from the opposite side. |
| `indoor` | boolean | False | If True, create indoor shades. If False, create outdoor shades. |
| `tolerance` | float | 0.01 | Geometric tolerance in meters. |
| `base_name` | string | None | Base name for generated shade identifiers. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the operation was successful |
| `message` | str | Summary of processed apertures |
| `results` | list | List of results for each aperture |
| `not_found` | list | Aperture identifiers not found |

**Example:**
```python
add_louvers_by_count(["Window_1"], louver_count=5, depth=0.3)
```

---

### add_louvers_by_distance_between

Add shading louvers to apertures with target spacing between them.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `aperture_identifiers` | list | required | List of aperture identifiers to add louvers to. |
| `distance` | float | required | Target spacing between louvers in meters. Must be greater than 0. |
| `depth` | float | required | Depth of each louver in meters. Must be greater than 0. |
| `offset` | float | 0 | Distance to offset louvers from the aperture in meters. |
| `angle` | float | 0 | Angle of louvers in degrees (0 = horizontal). |
| `contour_vector` | list | [0, 1] | 2D vector [x, y] defining louver direction. |
| `flip_start_side` | boolean | False | If True, start louvers from the opposite side. |
| `indoor` | boolean | False | If True, create indoor shades. If False, create outdoor shades. |
| `tolerance` | float | 0.01 | Geometric tolerance in meters. |
| `max_count` | int | None | Maximum number of louvers to create. Optional limit. |
| `base_name` | string | None | Base name for generated shade identifiers. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the operation was successful |
| `message` | str | Summary of processed apertures |
| `results` | list | List of results for each aperture |
| `not_found` | list | Aperture identifiers not found |

**Example:**
```python
add_louvers_by_distance_between(["Window_1"], distance=0.2, depth=0.3)
```

## Complete Workflow

```
1. load_model()
2. add_louvers(["Window_1"], depth=0.3, louver_count=5)
3. save_model_to_shared_memory()
```

## Notes

- Louver depth typically ranges from 0.15m to 0.5m
- Use `indoor=True` for blinds/curtains
- Angle affects both shading performance and aesthetics
- Offset moves louvers away from the aperture plane
- Use aperture identifiers from the loaded model
- Louvers are created as shade objects attached to apertures
