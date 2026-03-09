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

## Tool

### `version_control`
**Args**
- `action: str`
- `model_name: str | None = None`
- `version_id: str | None = None`
- `version_id_2: str | None = None`
- `description: str = ""`

**Returns**
- action-specific dict
- usually includes `success`
- may include `models`, `versions`, `version_id`, `timestamp`, `description`, `model_dict`

## Actions and Scenarios

### `save`
Use before major edits.

### `undo` / `redo`
Use during iterative design changes.

### `list` / `info`
Use when the user wants history visibility.

### `load`
Use when restoring a chosen checkpoint.

### `compare`
Use when the user wants to understand differences between snapshots.

### `clear`
Use only when version history should be intentionally reset.

## Examples

```python
version_control("save", description="Before adding windows")
version_control("undo")
version_control("redo")
```

```python
version_control("list", model_name="MyModel")
version_control("info", model_name="MyModel", version_id="002")
version_control("compare", model_name="MyModel", version_id="001", version_id_2="003")
```

```python
version_control("load", model_name="MyModel", version_id="002")
```

## Return Guidance

- Surface `version_id` and `timestamp` when restoring or comparing.
- If `model_dict` is returned by a load-like action, the current model state has changed and follow-up `query` calls should reflect the restored version.
- Version restore now includes custom Energy and Radiance resources that were serialized into the model snapshot.
