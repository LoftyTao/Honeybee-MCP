---
name: "honeybee-version-control"
description: "Manages model version history for undo/redo operations. Invoke when user wants to save snapshots, undo changes, or restore previous versions of the model."
---

# Honeybee Version Control

This skill manages version history for Honeybee models, enabling undo/redo workflows.

## Unified Tool: version_control

A single tool that handles all version control operations through the `action` parameter.

### Actions

| Action | Description | Required Parameters |
|--------|-------------|---------------------|
| `list` | List all versions for a model | model_name (optional) |
| `save` | Save current model as a version snapshot | description (optional) |
| `load` | Load a specific version | model_name, version_id |
| `undo` | Undo to previous version | model_name (optional) |
| `redo` | Redo last undone change | model_name (optional) |
| `compare` | Compare two versions | model_name, version_id, version_id_2 |
| `info` | Get detailed info about a version | model_name, version_id |
| `delete` | Delete a specific version | model_name, version_id |
| `clear` | Clear version history | model_name (optional) |
| `cleanup` | Clean up old cache files | none |

---

## Usage Examples

### List Versions
```python
# List all models with versions
version_control("list")

# List versions for specific model
version_control("list", model_name="MyModel")
```

### Save Version
```python
# Save with description
version_control("save", description="Before removing windows")

# Save without description
version_control("save")
```

### Load Specific Version
```python
# Load version 001
version_control("load", model_name="MyModel", version_id="001")
```

### Undo/Redo
```python
# Undo to previous version
version_control("undo")

# Redo last undone change
version_control("redo")
```

### Compare Versions
```python
# Compare version 001 and 003
version_control("compare", model_name="MyModel", version_id="001", version_id_2="003")
```

### Get Version Info
```python
# Get detailed info about version 002
version_control("info", model_name="MyModel", version_id="002")
```

### Delete Version
```python
# Delete version 002
version_control("delete", model_name="MyModel", version_id="002")
```

### Clear History
```python
# Clear specific model history
version_control("clear", model_name="MyModel")

# Clear ALL models history
version_control("clear")
```

---

## Version Control Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  EDITING SESSION                                            │
├─────────────────────────────────────────────────────────────┤
│  1. load_model()           ← Load from Grasshopper          │
│  2. version_control("save", description="start")            │
│  3. [Make edits]           ← Add/remove elements            │
│  4. version_control("save", description="edit1")            │
│  5. [More edits]           ← Continue editing               │
│  6. version_control("undo") ← Undo if needed                │
│  7. version_control("redo") ← Redo if needed                │
│  8. save_model_to_shared_memory() ← Sync with Grasshopper   │
└─────────────────────────────────────────────────────────────┘
```

---

## Version Data

Each version stores:
- `rooms_count` - Number of rooms
- `outdoor_shades_count` - Number of outdoor shades
- `apertures_count` - Number of windows
- `doors_count` - Number of doors
- `shade_meshes_count` - Number of shade meshes
- `timestamp` - When saved
- `description` - User description

---

## Version Limits

- Maximum **10 versions** per model
- Oldest versions are automatically removed when limit is reached
- Versions are stored in memory (not persistent between sessions)

---

## Best Practices

1. Save version before major changes
2. Use descriptive version names
3. Clear history when starting new project
4. Use undo for quick reverts
5. Compare versions to understand changes

---

## Notes

- Versions are stored in memory only
- Clearing history is irreversible
- Cache cleanup frees disk space
- Auto-save happens on load and save operations
- After loading a version, use `save_model_to_shared_memory()` to sync with Grasshopper
