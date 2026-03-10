---
name: "honeybee-version-control"
description: "Use when a task requires snapshotting, undoing, redoing, comparing, clearing, or loading Honeybee model versions, including custom Energy and Radiance resources."
---

# Honeybee Version Control

## Use This Skill When

- A risky edit is about to happen
- The user wants undo or redo
- The user wants to compare model states
- The user wants to restore a specific version
- The user wants to delete a specific version
- The user wants to clear all version history

## Tool

### `version_control`
**Args**
- `action: str` — Required. One of: `save`, `undo`, `redo`, `list`, `info`, `load`, `compare`, `delete`, `clear`
- `model_name: str | None = None` — Model identifier (auto-detected from current model if omitted)
- `version_id: str | None = None` — Version identifier for targeted actions
- `version_id_2: str | None = None` — Second version identifier (for `compare`)
- `description: str = ""` — Description for `save` action

**Returns**
- action-specific dict
- usually includes `success`
- may include `models`, `versions`, `version_id`, `timestamp`, `description`, `model_dict`

## Action Reference

### `save`
Create a named checkpoint. Use before any risky or destructive operations.

**Required params**: none (auto-detects model)
**Optional params**: `description`
**Returns**: `version_id`, `timestamp`, `description`

```python
version_control("save", description="Before adding windows")
```

### `list`
List all versions for a model.

**Optional params**: `model_name`
**Returns**: `versions` (list of version summaries)

```python
version_control("list", model_name="MyModel")
```

### `info`
Get details of a specific version.

**Required params**: `model_name`, `version_id`
**Returns**: Version metadata including `timestamp`, `description`

```python
version_control("info", model_name="MyModel", version_id="002")
```

### `load`
Restore a specific version as the current model.

**Required params**: `model_name`, `version_id`
**Returns**: `model_dict` (the restored model state becomes active)

```python
version_control("load", model_name="MyModel", version_id="002")
```

### `undo`
Step back one version.

**Optional params**: `model_name`
**Returns**: Restored model state

```python
version_control("undo")
```

### `redo`
Step forward one version (after undo).

**Optional params**: `model_name`

```python
version_control("redo")
```

### `compare`
Compare two versions to see differences.

**Required params**: `model_name`, `version_id`, `version_id_2`
**Returns**: `has_changes`, diff details

```python
version_control("compare", model_name="MyModel",
    version_id="001", version_id_2="003")
```

### `delete`
Delete a specific version.

**Required params**: `model_name`, `version_id`

```python
version_control("delete", model_name="MyModel", version_id="001")
```

### `clear`
Clear all version history for a model.

**Required params**: `model_name`

```python
version_control("clear", model_name="MyModel")
```

## Multi-Step Versioned Editing Workflow

```python
# 1. Save initial state
version_control("save", description="Original state")

# 2. Make edits (e.g., add apertures)
remove(operation="all_apertures")
add(operation="apertures_by_ratio", target_type="face",
    identifiers=wall_ids, params={"ratio": 0.6})
version_control("save", description="Large window scheme")

# 3. Undo and try different parameters
version_control("undo")
add(operation="apertures_by_ratio", target_type="face",
    identifiers=wall_ids, params={"ratio": 0.2})
version_control("save", description="Small window scheme")

# 4. Compare schemes
version_control("compare", model_name="MyModel",
    version_id="002", version_id_2="003")

# 5. Choose and load preferred version
version_control("load", model_name="MyModel", version_id="002")
```

## Return Guidance

- Surface `version_id` and `timestamp` when restoring or comparing.
- If `model_dict` is returned by a load-like action, the current model state has changed and follow-up `query` calls should reflect the restored version.
- Version restore now includes custom Energy and Radiance resources that were serialized into the model snapshot.
- After `undo`/`redo`/`load`, always re-query to confirm the model state matches expectations.
