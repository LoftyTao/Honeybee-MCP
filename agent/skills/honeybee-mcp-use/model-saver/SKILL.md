---
name: "honeybee-model-saver"
description: "Use when a task requires exporting a Honeybee model to file or sending the current model back to Grasshopper shared memory, including custom HBJSON-native Energy and Radiance resources."
---

# Honeybee Model Saver

## Use This Skill When

- The user wants an HBJSON output
- The current model should be written back to Grasshopper
- A backup is needed before further edits
- The current model contains custom Energy or Radiance resources that must survive save/reload

## Preferred Tools

### `save_model`
**Args**
- `name: str | None = None`
- `folder: str | None = None`
- `indent: int | None = None`
- `included_prop: list | None = None`
- `triangulate_sub_faces: bool = False`

**Returns**
- `success: bool`
- `file_path: str`

### `save_model_to_shared_memory`
**Args**
- `name: str | None = None`

**Returns**
- `success: bool`
- `message: str`
- `name: str`
- `display_name: str`
- `rooms_count: int`
- `hint: str`

## Tool Choice

- Use `save_model` for durable file export.
- Use `save_model_to_shared_memory` for Grasshopper round-trip workflows.
- `save_model` now serializes custom MCP-managed Energy and Radiance resources back into HBJSON.
- Use `visualization` instead when the user wants `.vsf`, `.svg`, `.html`, or `.vtkjs` visual deliverables rather than HBJSON persistence.

## Example

```python
save_model(folder="C:/output", name="my_model")
save_model_to_shared_memory()
```

## Return Guidance

- Surface `file_path` when exporting files.
- Surface `name` and `hint` when saving to shared memory.
- Remind the user that edit buses may already have auto-saved if the model source was shared memory.
- If the workflow introduced custom schedules, constructions, modifiers, modifier sets, sensor grids, or views, mention that save preserves them in the exported HBJSON.
