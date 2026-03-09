---
name: "honeybee-shade-remover"
description: "Use when a task requires deleting attached shades, room-level shades, face-level shades, or shade meshes through the unified `remove` bus."
---

# Honeybee Shade Remover

## Use This Skill When

- The user wants to remove all shading elements
- The user wants to remove only shade meshes
- The user wants to clear room-level shades
- The user wants to clear face-level indoor or outdoor shades
- The user wants to reset louvers or other attached shading before re-adding new shading

## Preferred Tool

### `remove`
**Description**
Unified removal bus for Honeybee objects. Shade workflows mainly use `all_shades`, `room_shades`, and `face_objects`.

**Args**
- `operation: str`
- `identifiers: list | None = None`
- `options: dict | None = None`

**Returns**
- `success: bool`
- `message: str`
- operation-specific removal fields
- `auto_save: dict` when the model source is shared memory

## Operation Selection

### `all_shades`
Use when the user wants every attached shade and shade mesh removed, or only specific shade meshes removed.

**Identifiers behavior**
- Omit `identifiers` to remove all attached shades and all shade meshes.
- Pass `identifiers=["Tree_1", "Building_2"]` to remove only selected shade meshes.

**Typical returns**
- `removed`
- `removed_count`
- `removed_ids`
- `remaining_count`
- `not_found`

### `room_shades`
Use when the user wants to clear shades attached at room scope.

**Identifiers**
- Room identifiers

**Options**
- `indoor_shades: bool`
- `outdoor_shades: bool`

**Typical returns**
- `results`
- `not_found`
- per-room `removed_count`

### `face_objects`
Use when the user wants to clear indoor or outdoor shades from specific faces, or remove multiple categories together.

**Identifiers**
- Face identifiers

**Options**
- `indoor_shades: bool`
- `outdoor_shades: bool`
- optionally combine with `apertures`, `doors`, or `sub_faces`

**Typical returns**
- `results`
- `not_found`
- per-face `removed_objects`

## Examples

### Remove all shades and shade meshes
```python
remove(operation="all_shades")
```

### Remove only selected shade meshes
```python
remove(
    operation="all_shades",
    identifiers=["Tree_1", "Context_Building_2"]
)
```

### Remove outdoor shades from rooms
```python
remove(
    operation="room_shades",
    identifiers=["Room_1", "Room_2"],
    options={"outdoor_shades": True, "indoor_shades": False}
)
```

### Remove both indoor and outdoor shades from specific faces
```python
remove(
    operation="face_objects",
    identifiers=["Face_1", "Face_2"],
    options={"outdoor_shades": True, "indoor_shades": True}
)
```

### Mixed cleanup on selected faces
```python
remove(
    operation="face_objects",
    identifiers=["Face_3"],
    options={"apertures": True, "outdoor_shades": True}
)
```

## Return Guidance

- Use `message` for quick confirmation.
- Use `removed` or `removed_count` for high-level summaries.
- Use `results` when the user cares about which rooms or faces were affected.
- Use `not_found` when identifiers may be stale or incomplete.
- Mention `auto_save` when the model came from shared memory and writeback occurred.

## Workflow

1. Query first if the shade scope is unclear.
2. Distinguish between attached shades and shade meshes.
3. Choose the narrowest valid remove operation.
4. Re-query after deletion if the user needs verification.

## Notes

- `all_shades` is the broadest removal path.
- Shade mesh removal is identifier-based inside the same `all_shades` operation.
- Removing apertures or sub-faces may also remove attached shading indirectly.
