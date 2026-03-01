---
name: "honeybee-model-loader"
description: "Loads Honeybee models from Grasshopper shared memory or HBJSON files. Invoke when user wants to load/import a model for editing or analysis."
---

# Honeybee Model Loader

This skill loads Honeybee models into the current session for editing or analysis.

## Tools

### load_model

Load a Honeybee model from HBJSON/HBpkl file or Grasshopper shared memory.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hb_file` | string | None | Path to HBJSON or HBpkl file. Can also be "latest" to auto-load the most recent Grasshopper model from shared memory. Optional if Grasshopper model exists in shared memory. |
| `cleanup_irrational` | boolean | False | Boolean to clean irrational geometry from the model. Typical cases removed include Face3Ds with fewer than 3 vertices, Rooms with no Face geometry, etc. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the model was loaded successfully |
| `source` | str | "grasshopper" or "file" indicating load source |
| `display_name` | str | Model display name |
| `floor_area` | float | Total floor area in m² |
| `rooms_count` | int | Number of rooms in the model |
| `outdoor_shades_count` | int | Number of outdoor shades |
| `orphaned_faces_count` | int | Number of orphaned faces |
| `orphaned_shades_count` | int | Number of orphaned shades |
| `orphaned_apertures_count` | int | Number of orphaned apertures |
| `orphaned_doors_count` | int | Number of orphaned doors |
| `available_grasshopper_models` | list | List of available GH models (if any) |
| `cache_cleanup` | dict | Cache cleanup results (if cleanup occurred) |
| `error` | str | Error message if loading failed |

**Priority:**
1. If Grasshopper has written a model to shared memory, load from there first
2. Otherwise, load from the specified hb_file

**Example:**
```python
# Load from Grasshopper (auto-detect)
load_model()

# Load latest GH model
load_model("latest")

# Load from file
load_model("/path/to/model.hbjson")

# Load with geometry cleanup
load_model(cleanup_irrational=True)
```

---

### load_model_from_dict

Load a Honeybee model from a dictionary representation.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | dict | required | A dictionary representation of a Honeybee Model object. This should follow the Honeybee Model schema with keys like "type", "identifier", "display_name", "rooms", "orphaned_faces", etc. |
| `cleanup_irrational` | boolean | False | Boolean to note whether common types of irrational objects should be cleaned or removed from the dictionary before serializing the model to Python. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the model was loaded successfully |
| `display_name` | str | Model display name |
| `floor_area` | float | Total floor area in m² |
| `rooms_count` | int | Number of rooms in the model |
| `outdoor_shades_count` | int | Number of outdoor shades |
| `orphaned_faces_count` | int | Number of orphaned faces |
| `orphaned_shades_count` | int | Number of orphaned shades |
| `orphaned_apertures_count` | int | Number of orphaned apertures |
| `orphaned_doors_count` | int | Number of orphaned doors |
| `error` | str | Error message if loading failed |

**Example:**
```python
load_model_from_dict({"type": "Model", "identifier": "my_model", ...})
```

## Workflow

1. Load model using one of the methods above
2. Review model information (rooms, shades, area)
3. Proceed with editing operations
4. Save changes back to Grasshopper or file

## Notes

- Grasshopper models are stored in shared memory
- Multiple models may be available in shared memory
- Use `cleanup_irrational=True` to remove invalid geometry automatically
- Always load a model before performing any editing operations
