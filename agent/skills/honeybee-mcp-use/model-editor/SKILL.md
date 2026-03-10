---
name: "honeybee-model-editor"
description: "Use when a task requires model-wide cleanup, scoped deletion, mixed removal workflows, or safe removal of reusable Energy and Radiance resources through the unified `remove` bus, usually with `query` for scope confirmation."
---

# Honeybee Model Editor

## Use This Skill When

- The user wants a model-wide cleanup
- The user wants to remove several object categories together
- The user wants reset-like editing before rebuilding geometry
- The user wants scoped deletion on faces or rooms
- The user needs a general deletion workflow rather than a single narrow object type
- The user wants reusable schedules, modifiers, modifier sets, process loads, sensor grids, or views removed safely

## Preferred Tools

### `query`
**Description**
Use first when the deletion scope is unclear.

**Args**
- `target_type: str`
- `identifiers: list | None = None`
- `fields: list | None = None`
- `output_mode: str = "records"`

**Returns**
- `success: bool`
- `data: dict | list`
- `count: int` when relevant
- `missing: list`

### `remove`
**Description**
Primary editing tool for destructive object cleanup.

**Args**
- `operation: str`
- `identifiers: list | None = None`
- `options: dict | None = None`

**Returns**
- `success: bool`
- `message: str`
- operation-specific result fields
- `auto_save: dict` when relevant

## Removal Matrix

### Model-wide cleanup
- `remove(operation="all_apertures")`
- `remove(operation="all_doors")`
- `remove(operation="all_shades")`

### Face-scoped cleanup
- `remove(operation="face_objects", identifiers=[...], options={...})`

Use `options` for:
- `apertures`
- `doors`
- `indoor_shades`
- `outdoor_shades`
- `sub_faces`

### Room-scoped cleanup
- `remove(operation="room_shades", identifiers=[...], options={...})`
- `remove(operation="process_loads", identifiers=[...], options={...})`

Room shades `options`:
- `indoor_shades: bool`
- `outdoor_shades: bool`

Process loads `options`:
- `process_ids: list` — List of process load identifiers to delete from the room. Omit to delete all process loads from the room.

### Resource-aware cleanup
- `remove(operation="schedule", identifiers=[...])`
- `remove(operation="schedule_day", identifiers=[...])`
- `remove(operation="schedule_type_limit", identifiers=[...])`
- `remove(operation="modifier", identifiers=[...])`
- `remove(operation="modifier_set", identifiers=[...])`
- `remove(operation="sensor_grid", identifiers=[...])`
- `remove(operation="view", identifiers=[...])`

These operations may return blocked references instead of deleting immediately.

## Examples

### Reset all openings
```python
remove(operation="all_apertures")
remove(operation="all_doors")
```

### Remove all shading
```python
remove(operation="all_shades")
```

### Mixed face cleanup
```python
remove(
    operation="face_objects",
    identifiers=["Face_1", "Face_2"],
    options={"apertures": True, "doors": True, "outdoor_shades": True}
)
```

### Room-scoped shade cleanup
```python
remove(
    operation="room_shades",
    identifiers=["Room_1"],
    options={"outdoor_shades": True}
)
```

### Remove specific process loads from a room
```python
remove(
    operation="process_loads",
    identifiers=["Room_1"],
    options={"process_ids": ["Process_A", "Process_B"]}
)
```

### Remove all process loads from a room
```python
remove(
    operation="process_loads",
    identifiers=["Room_1"]
)
```

### Remove a custom schedule resource
```python
remove(operation="schedule", identifiers=["Office_Occ_Schedule"])
```

### Remove a sensor grid
```python
remove(operation="sensor_grid", identifiers=["Grid_01"])
```

### Resource deletion with blocked references

When a resource is still referenced, deletion is blocked:

```python
# Step 1: Attempt deletion
result = remove(operation="schedule", identifiers=["OfficeOccupancy"])
# result may contain "blocked" with a list of referencing objects

# Step 2: Reassign the referencing rooms/loads to a different schedule
apply(operation="people", target_type="room", identifiers=["Room_1"],
      values={"occupancy_schedule_identifier": "AlternativeSchedule"})

# Step 3: Retry deletion
remove(operation="schedule", identifiers=["OfficeOccupancy"])
```

### Query before delete
```python
query(
    target_type="face",
    identifiers=["Face_1"],
    fields=["identifier", "apertures", "doors", "indoor_shades", "outdoor_shades"]
)
```

## Return Guidance

- Use `message` for quick operation confirmation.
- Use `results` for per-face or per-room detail.
- Use `removed`, `removed_count`, or `remaining_count` when returned by model-wide operations.
- Use `blocked` and reference summaries when removal is denied for reusable resources.
- Mention `auto_save` when shared-memory writeback occurs.

## Notes

- Prefer the narrowest valid deletion scope.
- Save a version first when the cleanup is broad or destructive.
- For reusable resources, query first and expect safe-block behavior if the resource is still referenced.
- Re-query after cleanup if the user wants confirmation or downstream editing depends on clean state.
