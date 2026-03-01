---
name: "honeybee-shade-remover"
description: "Removes shading elements from Honeybee models. Invoke when user wants to delete/remove shades, louvers, or overhangs."
---

# Honeybee Shade Remover

This skill removes shading elements from Honeybee models.

## Tools

### remove_all_shades

Remove all shades from the model.

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
remove_all_shades()
```

---

### remove_room_shades

Remove shades from specified rooms.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `room_identifiers` | list | required | List of room identifiers to remove shades from. |
| `indoor_shades` | boolean | True | If True, remove indoor shades (blinds, curtains). |
| `outdoor_shades` | boolean | True | If True, remove outdoor shades (overhangs, fins, louvers). |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the operation was successful |
| `message` | str | Summary of processed rooms |
| `results` | list | List of results for each room with room_identifier, removed_count, shade_type |
| `not_found` | list | Room identifiers not found |

**Example:**
```python
# Remove all shades
remove_room_shades(["Room_1", "Room_2"])
# Outdoor only
remove_room_shades(["Room_3"], indoor_shades=False)
# Indoor only
remove_room_shades(["Room_4"], outdoor_shades=False)
```

---

### remove_face_objects

Remove shades from specific faces.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `face_identifiers` | list | required | List of face identifiers to remove objects from. |
| `indoor_shades` | boolean | False | If True, remove all indoor shades from the faces. |
| `outdoor_shades` | boolean | False | If True, remove all outdoor shades from the faces. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the operation was successful |
| `message` | str | Summary of processed faces |
| `results` | list | List of results for each face |
| `not_found` | list | Face identifiers not found |

**Example:**
```python
remove_face_objects(["South_Face"], outdoor_shades=True)
```

## Complete Workflow

```
1. load_model()
2. remove_all_shades()
3. save_model_to_shared_memory()
```

## Notes

- Shades are often attached to apertures (windows)
- Removing apertures will also remove their attached shades
- Use room-specific removal for selective editing
- Operation is irreversible - save a backup if needed
