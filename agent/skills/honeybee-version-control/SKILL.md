---
name: "honeybee-version-control"
description: "Manages model version history for undo/redo operations. Invoke when user wants to save snapshots, undo changes, or restore previous versions of the model."
---

# Honeybee Version Control

This skill manages version history for Honeybee models, enabling undo/redo workflows.

## Tools

### save_version

Manually save current model as a version snapshot.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `description` | string | "" | Optional description for this version snapshot. Use this to document what changes were made or why this version is being saved. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the version was saved |
| `version_id` | str | Version identifier (e.g., "001", "002") |
| `model_name` | str | Name of the model |
| `timestamp` | str | When the version was saved |
| `total_versions` | int | Total number of versions for this model |
| `error` | str | Error message if saving failed |

**Example:**
```python
save_version("Added windows to south facade")
save_version()  # No description
```

---

### list_model_versions

List all saved versions for a model.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | string | None | Name of the model to list versions for. If not specified, lists all models with their version counts. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the operation was successful |
| `model_name` | str | Name of the model (if specified) |
| `versions` | list | List of version info dictionaries with version, timestamp, description, rooms_count, outdoor_shades_count |
| `total_versions` | int | Total number of versions |
| `max_versions` | int | Maximum versions allowed (10) |
| `models` | list | List of all models with version counts (if no model_name) |
| `error` | str | Error message if operation failed |

**Example:**
```python
list_model_versions("MyModel")  # List versions for specific model
list_model_versions()  # List all models with versions
```

---

### load_model_version

Load a specific version of a model.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | string | required | Name of the model to load a version from. |
| `version_id` | string | required | Version number to load (e.g., "001", "002", "010"). Use list_model_versions to see available versions. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the version was loaded |
| `message` | str | Status message |
| `model_name` | str | Name of the model |
| `version_id` | str | Version that was loaded |
| `timestamp` | str | When this version was saved |
| `description` | str | Version description |
| `rooms_count` | int | Number of rooms in the loaded model |
| `error` | str | Error message if loading failed |
| `available_versions` | list | List of available versions (if version not found) |

**Example:**
```python
load_model_version("MyModel", "001")
load_model_version("MyModel", "5")  # Will be padded to "005"
```

---

### undo_last_change

Undo to the previous version (restore before last change).

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | string | None | Name of the model to undo. If not specified, uses the currently loaded model. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the undo was successful |
| `message` | str | Status message |
| `model_name` | str | Name of the model |
| `version_id` | str | Version restored to |
| `timestamp` | str | When this version was saved |
| `rooms_count` | int | Number of rooms in the restored model |
| `error` | str | Error message if undo failed |
| `current_version` | str | Current version ID (if only one version exists) |

**Example:**
```python
undo_last_change()  # Undo current model
undo_last_change("MyModel")  # Undo specific model
```

---

### clear_version_history

Clear version history for a model or all models.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | string | None | Name of the model to clear versions for. If not specified, clears version history for ALL models. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the clear was successful |
| `message` | str | Status message with count of cleared models |
| `error` | str | Error message if clearing failed |

**Example:**
```python
clear_version_history("MyModel")  # Clear specific model
clear_version_history()  # Clear ALL models
```

---

### cleanup_cache

Clean up old shared memory cache files.

**Args:**
None

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether cleanup was successful |
| `kept_files` | int | Number of files kept |
| `removed_files` | int | Number of files removed |
| `removed_details` | list | Details of removed files |
| `error` | str | Error message if cleanup failed |

**Example:**
```python
cleanup_cache()
```

## Version Control Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  EDITING SESSION                                            │
├─────────────────────────────────────────────────────────────┤
│  1. load_model()           ← Load from Grasshopper          │
│  2. save_version("start")  ← Save initial state             │
│  3. [Make edits]           ← Add/remove elements            │
│  4. save_version("edit1")  ← Save after changes             │
│  5. [More edits]           ← Continue editing               │
│  6. undo_last_change()     ← Undo if needed                 │
│  7. save_model_to_shared_memory() ← Save back to GH         │
└─────────────────────────────────────────────────────────────┘
```

## Common Scenarios

### Save Before Risky Operation
```python
save_version("Before removing all windows")
remove_all_apertures()
```

### Undo Last Change
```python
undo_last_change()
```

### View Version History
```python
list_model_versions("MyModel")
```

### Restore Specific Version
```python
load_model_version("MyModel", "003")
```

## Version Limits

- Maximum **10 versions** per model
- Oldest versions are automatically removed when limit is reached
- Versions are stored in memory (not persistent between sessions)

## Best Practices

1. Save version before major changes
2. Use descriptive version names
3. Clear history when starting new project
4. Use undo for quick reverts

## Notes

- Versions are stored in memory only
- Clearing history is irreversible
- Cache cleanup frees disk space
- Auto-save happens on load and save operations
