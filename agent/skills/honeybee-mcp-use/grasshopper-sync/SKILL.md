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
**Args**
- none

**Returns**
- `success: bool`
- `kept_files: int`
- `removed_files: int`
- optional `removed_details`

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
save_model_to_shared_memory()
```

### Resource-aware shared-memory workflow
```python
load_model_from_shared_memory()
add(operation="schedule_ruleset", target_type="model", params={...})
apply(operation="people", target_type="room", identifiers=["Room_1"], values={"occupancy_schedule_identifier": "CustomSchedule"})
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
