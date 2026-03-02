---
name: "honeybee-model-saver"
description: "Saves Honeybee models to Grasshopper shared memory or HBJSON files. Invoke when user wants to export/save a model after editing."
---

# Honeybee Model Saver

This skill saves Honeybee models after editing, either back to Grasshopper or to file.

## Tools

### save_model

Save the current model to an HBJSON file.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | None | File name for the HBJSON file. If not provided, uses the model's display_name or identifier. The .hbjson extension is added automatically. |
| `folder` | string | None | Directory path to save the file. If not provided, saves to the current working directory. |
| `indent` | int | None | Number of spaces for JSON indentation. If not provided, the JSON is compact (no indentation). Use for human-readable files. |
| `included_prop` | list | None | List of property types to include in the export. If None, all properties are included. Options: "energy", "radiance", "doe2". Example: ["energy", "radiance"] |
| `triangulate_sub_faces` | boolean | False | If True, triangulate all sub-faces (apertures, doors) before export. Useful for compatibility with some simulation engines. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `file_path` | str | Absolute path to the saved HBJSON file |
| `error` | str | Error message if save failed (if applicable) |

**Example:**
```python
# Save with default name to current directory
save_model()

# Save with custom name and folder
save_model(name="my_model", folder="/path/to/output")

# Save with only energy properties
save_model(name="energy_model", included_prop=["energy"])

# Save with human-readable formatting
save_model(name="readable", indent=2)
```

---

### save_model_to_shared_memory

Save the current model to shared memory for Grasshopper to read.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | "hb_model_shared" | Shared memory name (must match the name used in Grasshopper). |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the model was saved successfully |
| `message` | str | Status message with file size |
| `display_name` | str | Model display name |
| `rooms_count` | int | Number of rooms in the model |
| `hint` | str | Instructions for reading in Grasshopper |
| `error` | str | Error message if saving failed |

**Example:**
```python
# Save with default name
save_model_to_shared_memory()

# Save with custom name
save_model_to_shared_memory("my_model")
```

## Workflow

1. Load model from Grasshopper or file
2. Perform editing operations
3. Save model back to Grasshopper or export to file
4. Verify save was successful

## Notes

- Use the same shared memory name when updating an existing Grasshopper model
- HBJSON files can be loaded back later or shared with others
- Use `included_prop` to reduce file size when only specific properties are needed
- `triangulate_sub_faces=True` improves compatibility with some simulation engines
