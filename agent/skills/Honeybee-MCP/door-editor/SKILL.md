---
name: "honeybee-door-editor"
description: "Edits doors in Honeybee models including adding, removing, and querying door properties. Invoke when user wants to modify or inspect doors."
---

# Honeybee Door Editor

This skill manages doors in Honeybee models.

## Tools

### remove_all_doors

Remove all doors from the model.

**Args:**
None

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the operation was successful |
| `message` | str | Status message |
| `error` | str | Error message if operation failed |

**Example:**
```python
remove_all_doors()
```

---

### remove_face_objects

Remove doors from specific faces.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `face_identifiers` | list | required | List of face identifiers to remove objects from. |
| `doors` | boolean | False | If True, remove all doors from the faces. |
| `sub_faces` | boolean | False | If True, remove all sub-faces (apertures AND doors). |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the operation was successful |
| `message` | str | Summary of processed faces |
| `results` | list | List of results for each face |
| `not_found` | list | Face identifiers not found |

**Example:**
```python
# Remove doors from specific faces
remove_face_objects(["Face_1"], doors=True)
# Remove doors and windows
remove_face_objects(["Face_1"], sub_faces=True)
```

---

### query_doors

Query various properties for multiple doors.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `door_identifiers` | list | required | List of door identifiers to query. |
| `identifier` | bool | False | Return the door identifier string. |
| `display_name` | bool | False | Return the door display name. |
| `boundary_condition` | bool | False | Return the boundary condition (Outdoors, Surface). |
| `is_glass` | bool | False | Return True if door is a glass door (has glazing). |
| `is_exterior` | bool | False | Return True if door is on an exterior face. |
| `has_parent` | bool | False | Return True if door has a parent face. |
| `parent` | bool | False | Return the parent face identifier. |
| `top_level_parent` | bool | False | Return the top-level parent (room) identifier. |
| `geometry` | bool | False | Return the door geometry string representation. |
| `vertices` | bool | False | Return list of vertex coordinates [[x,y,z], ...]. |
| `normal` | bool | False | Return the normal vector [x, y, z]. |
| `center` | bool | False | Return the center point [x, y, z]. |
| `area` | bool | False | Return the door area in m². |
| `perimeter` | bool | False | Return the door perimeter in m. |
| `tilt` | bool | False | Return the tilt angle in degrees. |
| `azimuth` | bool | False | Return the azimuth angle in degrees. |
| `indoor_shades` | bool | False | Return indoor shade identifiers or count. |
| `outdoor_shades` | bool | False | Return outdoor shade identifiers or count. |
| `return_count` | bool | False | If True, return counts instead of identifier lists for shades. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| dict | dict | Dictionary mapping door identifiers to their queried properties. |

**Example:**
```python
query_doors(["Door_1"], area=True, is_glass=True)
query_doors(["Door_1", "Door_2"], boundary_condition=True)
```

## Door Properties

| Property | Description |
|----------|-------------|
| `is_glass` | True if door has glazing |
| `is_exterior` | True if on exterior face |
| `area` | Door area in m² |
| `boundary_condition` | Outdoors or Surface |
| `indoor_shades` | Attached indoor shades |
| `outdoor_shades` | Attached outdoor shades |

## Workflow

```
1. Load model
2. Query doors: query_doors()
3. Modify: remove or apply properties
4. Save model
```

## Notes

- Doors can be glass or opaque
- Glass doors accept window constructions
- Removing doors also removes attached shades
- Use `sub_faces=True` to remove both doors and windows
