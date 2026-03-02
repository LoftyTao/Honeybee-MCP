---
name: "honeybee-model-editor"
description: "Edits Honeybee models from Grasshopper. Invoke when user wants to load, modify (add/remove apertures, doors, shades), and save models back to Grasshopper."
---

# Honeybee Model Editor

This skill provides comprehensive model editing capabilities for Honeybee models.

## Tools

### remove_all_apertures

Remove all apertures from the model.

**Args:**
None

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the operation was successful |
| `message` | str | Status message |
| `auto_save` | dict | Auto-save information (if model from shared memory) |
| `error` | str | Error message if operation failed |

**Example:**
```python
remove_all_apertures()
```

---

### remove_all_doors

Remove all doors from the model.

**Args:**
None

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the operation was successful |
| `message` | str | Status message |
| `auto_save` | dict | Auto-save information (if model from shared memory) |
| `error` | str | Error message if operation failed |

**Example:**
```python
remove_all_doors()
```

---

### remove_all_shades

Remove all shades from the model.

**Args:**
None

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the operation was successful |
| `message` | str | Status message |
| `auto_save` | dict | Auto-save information (if model from shared memory) |
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
| `results` | list | List of results for each room |
| `not_found` | list | Room identifiers not found |
| `auto_save` | dict | Auto-save information (if model from shared memory) |

**Example:**
```python
remove_room_shades(["Room_1", "Room_2"])  # Remove all shades
remove_room_shades(["Room_3"], indoor_shades=False)  # Outdoor only
```

---

### remove_face_objects

Remove objects from specified faces.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `face_identifiers` | list | required | List of face identifiers to remove objects from. |
| `apertures` | boolean | False | If True, remove all apertures from the faces. |
| `doors` | boolean | False | If True, remove all doors from the faces. |
| `indoor_shades` | boolean | False | If True, remove all indoor shades from the faces. |
| `outdoor_shades` | boolean | False | If True, remove all outdoor shades from the faces. |
| `sub_faces` | boolean | False | If True, remove all sub-faces (apertures AND doors). This is a shortcut that overrides apertures and doors flags. |

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
remove_face_objects(["Face_1"], apertures=True)  # Remove windows only
remove_face_objects(["Face_2"], sub_faces=True)  # Remove windows and doors
remove_face_objects(["Face_3"], outdoor_shades=True, indoor_shades=True)
```

## Complete Editing Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│  TYPICAL EDITING SESSION                                            │
├─────────────────────────────────────────────────────────────────────┤
│  1. load_model()              ← Load from Grasshopper/File          │
│  2. query_model(rooms=True)   ← Inspect model structure             │
│  3. [Edit operations]         ← Add/remove elements                 │
│     - add_apertures_by_ratio()                                      │
│     - add_louvers()                                                 │
│     - remove_face_objects()                                         │
│     - apply_room_attributes()                                       │
│     Note: Auto-save triggers automatically for shared memory models!  │
│  4. VERIFY CHANGES                                          │
│     └─► query_model() to confirm                            │
│  5. (Optional) save_model_to_shared_memory() ← Manual backup       │
└─────────────────────────────────────────────────────────────────────┘
```

## Common Editing Scenarios

### Remove All Glazing
```python
load_model()
remove_all_apertures()
# Auto-save triggers automatically for shared memory models
```

### Remove Windows from Specific Faces
```python
load_model()
remove_face_objects(["South_Face", "North_Face"], apertures=True)
# Auto-save triggers automatically for shared memory models
```

### Clear All Shades from Rooms
```python
load_model()
remove_room_shades(["Room_1", "Room_2"])
# Auto-save triggers automatically for shared memory models
```

### Reset Model (Remove All Openings)
```python
load_model()
remove_all_apertures()
remove_all_doors()
remove_all_shades()
# Auto-save triggers automatically for shared memory models
```

## Notes

- Always load a model before editing
- Removing apertures also removes attached shades
- Use query tools to identify target identifiers
- Save version before major changes for undo capability
- **Auto-save**: When model is loaded from Grasshopper shared memory, all editing operations automatically save changes back to shared memory. No manual save required for normal workflow!
- Manual save is still available for creating backups or saving to different shared memory names
