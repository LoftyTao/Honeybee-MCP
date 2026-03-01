---
name: "honeybee-aperture-remover"
description: "Removes apertures (windows/skylights) from Honeybee models. Invoke when user wants to delete/remove windows or glazing from faces."
---

# Honeybee Aperture Remover

This skill removes apertures (windows, skylights) from Honeybee models.

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
| `error` | str | Error message if operation failed |

**Example:**
```python
remove_all_apertures()
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
| `results` | list | List of results for each face with face_identifier and removed_objects |
| `not_found` | list | Face identifiers not found |

**Example:**
```python
# Remove windows only
remove_face_objects(["Face_1"], apertures=True)
# Remove windows and doors
remove_face_objects(["Face_2"], sub_faces=True)
# Remove outdoor shades and indoor shades
remove_face_objects(["Face_3"], outdoor_shades=True, indoor_shades=True)
```

## Complete Workflow

```
1. load_model()
2. remove_all_apertures()
3. save_model_to_shared_memory()
```

## Notes

- Removing apertures also removes any attached shades (indoor/outdoor)
- Operation is irreversible - save a backup if needed
- Use face-specific removal for selective editing
- Always save the model after removal operations
