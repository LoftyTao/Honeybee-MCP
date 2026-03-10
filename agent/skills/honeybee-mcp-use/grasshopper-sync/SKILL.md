---
name: "honeybee-grasshopper-sync"
description: "Use when a task requires reading from, writing to, checking, or clearing Grasshopper shared memory for Honeybee models, including custom Energy and Radiance resources that serialize into HBJSON."
---

# Honeybee Grasshopper Sync

## Use This Skill When

- The user explicitly mentions Grasshopper
- The model should be pulled from or pushed to shared memory
- Shared-memory status or cleanup is required
- The user needs confirmation that custom Energy/Radiance resources will survive shared-memory writeback

## Tools

### `load_model_from_shared_memory`
**Args**
- `name: str | None = None`
- `cleanup_irrational: bool = False`

**Returns**
- `success: bool`
- `message: str`
- model summary fields
- optional `writer_signal`
- optional `cleared`

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

### `check_shared_memory_status`
**Args**
- `name: str = "hb_model_shared"`

**Returns**
- `exists: bool`
- `signal_type: str | None`
- size and status metadata

### `clear_shared_memory_model`
**Args**
- `name: str = "hb_model_shared"`

**Returns**
- `success: bool`
- `message: str`

### `cleanup_shared_memory_cache`
**Description**
Removes stale cache files from the shared-memory temp directory. Does not affect the active shared-memory model.

**Args**
- none

**Returns**
- `success: bool`
- `kept_files: int`
- `removed_files: int`
- optional `removed_details`

## Auto-Save Behavior

When a model is loaded from shared memory, many edit operations (`apply`, `add`, `remove`) will **automatically write the model back** to shared memory after each operation. This is indicated by the `auto_save` field in the operation's return value.

This means:
- **Grasshopper picks up changes immediately** without a manual `save_model_to_shared_memory` call.
- Manual save is only needed when: the model was loaded from file (not shared memory), or auto-save was not triggered.
- The `auto_save` field contains `{"shared_memory": True, "name": "..."}` when writeback occurred.

## Examples

### Inspect-before-load
```python
check_shared_memory_status(name="hb_model_shared")
load_model_from_shared_memory(name="hb_model_shared")
```

### Read-modify-write loop
```python
load_model_from_shared_memory()
query(target_type="model", fields=["identifier", "rooms"])
# ... make edits (auto_save handles writeback)
# OR manually write back:
save_model_to_shared_memory()
```

### Resource-aware shared-memory workflow
```python
load_model_from_shared_memory()
add(operation="schedule_ruleset", target_type="model", params={...})
apply(operation="people", target_type="room", identifiers=["Room_1"],
      values={"occupancy_schedule_identifier": "CustomSchedule"})
# auto_save writeback includes the new schedule resource
```

If the model source is shared memory, many edit operations already write back automatically through `auto_save`.

### Cleanup
```python
clear_shared_memory_model(name="hb_model_shared")
cleanup_shared_memory_cache()
```

## Return Guidance

- If `writer_signal=True`, a Grasshopper writer updated the model.
- If `cleared=True`, shared-memory clear state was detected.
- Use `hint` from save results when instructing a user how to reconnect Reader/Writer components.
- Custom schedules, constructions, modifiers, modifier sets, sensor grids, and views that are part of serialized model data are preserved in shared-memory writeback.
- Check `auto_save` in edit operation returns to confirm whether writeback already happened.
