---
name: "honeybee-aperture-adder"
description: "Adds apertures (windows/skylights) to Honeybee model faces. Invoke when user wants to add windows by dimensions, ratio (WWR), or grid pattern."
---

# Honeybee Aperture Adder

This skill adds apertures (windows, skylights) to Honeybee model faces.

## Tools

### add_aperture_by_width_height

Add a rectangular aperture (window) at the center of each face.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `face_identifiers` | list | required | List of face identifiers to add apertures to. Faces can be from rooms or orphaned faces. |
| `width` | float | required | Width of the aperture in meters. Must be greater than 0. |
| `height` | float | required | Height of the aperture in meters. Must be greater than 0. |
| `sill_height` | float | 1.0 | Height of the sill from the face bottom in meters. Default is 1.0m (typical window sill height). |
| `aperture_identifier` | string | None | Optional base identifier for the aperture. If not provided, an identifier will be auto-generated. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the operation was successful |
| `message` | str | Summary of processed faces |
| `results` | list | List of results for each face with face_identifier, aperture_identifier, width, height, sill_height, error |
| `not_found` | list | Face identifiers that were not found |
| `auto_save` | dict | Auto-save information (if model from shared memory) |

**Example:**
```python
add_aperture_by_width_height(["Face_1", "Face_2"], 1.5, 2.0)
add_aperture_by_width_height(["South_Face"], 2.0, 1.5, 0.9)
```

---

### add_apertures_by_ratio_rectangle

Add rectangular apertures to faces based on area ratio (WWR).

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `face_identifiers` | list | required | List of face identifiers to add apertures to. |
| `ratio` | float | required | Window-to-wall ratio (WWR) as a decimal (e.g., 0.4 for 40%). Must be between 0 and 0.95. |
| `aperture_height` | float | None | Height of each aperture in meters. If not specified, apertures will be sized automatically based on face dimensions. |
| `sill_height` | float | 0.9 | Height of the sill from the face bottom in meters. |
| `horizontal_separation` | float | None | Horizontal distance between apertures in meters. If not specified, separation is calculated automatically. |
| `vertical_separation` | float | 0 | Vertical distance between rows of apertures. Default is 0 (single row). |
| `tolerance` | float | 0.01 | Geometric tolerance for calculations in meters. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the operation was successful |
| `message` | str | Summary of processed faces |
| `results` | list | List of results for each face with face_identifier, ratio, aperture_count, aperture_identifiers, error |
| `not_found` | list | Face identifiers not found |
| `auto_save` | dict | Auto-save information (if model from shared memory) |

**Example:**
```python
# 40% WWR
add_apertures_by_ratio_rectangle(["South_Face"], 0.4)
add_apertures_by_ratio_rectangle(["Face_1"], 0.3, aperture_height=1.5)
```

---

### add_apertures_by_ratio

Add apertures to faces based on area ratio.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `face_identifiers` | list | required | List of face identifiers to add apertures to. |
| `ratio` | float | required | Window-to-wall ratio (WWR) as a decimal (e.g., 0.4 for 40%). Must be between 0 and 1 (exclusive). |
| `tolerance` | float | 0.01 | Geometric tolerance for calculations in meters. |
| `rect_split` | boolean | True | If True, split apertures into rectangular windows. If False, create single polygon apertures. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the operation was successful |
| `message` | str | Summary of processed faces |
| `results` | list | List of results for each face |
| `not_found` | list | Face identifiers not found |
| `auto_save` | dict | Auto-save information (if model from shared memory) |

**Example:**
```python
# 40% WWR, rectangular
add_apertures_by_ratio(["Face_1"], 0.4)
# Single polygon
add_apertures_by_ratio(["Face_2"], 0.3, rect_split=False)
```

---

### add_apertures_by_ratio_gridded

Add apertures to faces in a grid pattern based on area ratio.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `face_identifiers` | list | required | List of face identifiers to add apertures to. |
| `ratio` | float | required | Window-to-wall ratio (WWR) as a decimal (e.g., 0.4 for 40%). Must be between 0 and 1 (exclusive). |
| `x_dim` | float | required | Horizontal dimension of each aperture in meters. |
| `y_dim` | float | None | Vertical dimension of each aperture in meters. If not specified, uses x_dim value (square apertures). |
| `tolerance` | float | 0.01 | Geometric tolerance for calculations in meters. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the operation was successful |
| `message` | str | Summary of processed faces |
| `results` | list | List of results for each face |
| `not_found` | list | Face identifiers not found |
| `auto_save` | dict | Auto-save information (if model from shared memory) |

**Example:**
```python
# 1m x 1.5m grid
add_apertures_by_ratio_gridded(["Face_1"], 0.4, 1.0, 1.5)
# 0.6m square grid
add_apertures_by_ratio_gridded(["Face_2"], 0.3, 0.6)
```

---

### add_apertures_by_width_height_rectangle

Add repeated rectangular apertures to faces based on width and height.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `face_identifiers` | list | required | List of face identifiers to add apertures to. |
| `aperture_height` | float | required | Height of each aperture in meters. Must be greater than 0. |
| `aperture_width` | float | required | Width of each aperture in meters. Must be greater than 0. |
| `sill_height` | float | 0.9 | Height of the sill from the face bottom in meters. |
| `horizontal_separation` | float | None | Horizontal distance between apertures in meters. If not specified, apertures are evenly distributed. |
| `tolerance` | float | 0.01 | Geometric tolerance for calculations in meters. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the operation was successful |
| `message` | str | Summary of processed faces |
| `results` | list | List of results for each face |
| `not_found` | list | Face identifiers not found |
| `auto_save` | dict | Auto-save information (if model from shared memory) |

**Example:**
```python
# 1.5m x 1m windows
add_apertures_by_width_height_rectangle(["Face_1"], 1.5, 1.0)
# With separation
add_apertures_by_width_height_rectangle(["Face_2"], 2.0, 1.2, 0.8, 0.5)
```

## Complete Workflow

```
1. load_model()
2. add_apertures_by_ratio(["South_Face"], 0.4)
   Note: Auto-save triggers automatically for shared memory models
3. (Optional) save_model_to_shared_memory() - for backup only
```

## Notes

- Ratio must be between 0 and 1 (exclusive for some methods)
- Dimensions are in meters
- Typical sill height is 0.9m (office) or 1.0m (residential)
- Existing apertures on the face are not affected
- Use face identifiers from the loaded model
- **Auto-save**: When model is loaded from Grasshopper shared memory, all aperture addition operations automatically save changes back to shared memory. No manual save required for normal workflow!
- Manual save is still available for creating backups or saving to different shared memory names
