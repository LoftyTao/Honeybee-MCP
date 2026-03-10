---
name: "honeybee-aperture-remover"
description: "Use when a task requires deleting apertures through the unified `remove` bus, either model-wide or face-scoped."
---

# Honeybee Aperture Remover

## Use This Skill When

- The user wants all windows removed
- The user wants apertures removed only from selected faces
- The user wants to clear glazing before re-adding apertures
- The user wants a facade reset without affecting the whole model

## Preferred Tool

### `remove`
**Description**
Unified removal bus. Aperture deletion mainly uses `all_apertures` and `face_objects`.

**Args**
- `operation: str`
- `identifiers: list | None = None`
- `options: dict | None = None`

**Returns**
- `success: bool`
- `message: str`
- operation-specific removal fields
- `auto_save: dict` when relevant

## Operation Selection

### `all_apertures`
Use when every aperture in the model should be removed.

```python
remove(operation="all_apertures")
```

### `face_objects`
Use when removal should be scoped to selected faces.

**Identifiers**
- Face identifiers

**Options**
- `apertures`
- `doors`
- `indoor_shades`
- `outdoor_shades`
- `sub_faces`

**Aperture-only example**
```python
remove(
    operation="face_objects",
    identifiers=["Face_1", "Face_2"],
    options={"apertures": True}
)
```

**Apertures plus attached objects example**
```python
remove(
    operation="face_objects",
    identifiers=["Face_3"],
    options={"apertures": True, "outdoor_shades": True}
)
```

**Subface reset example**
```python
remove(
    operation="face_objects",
    identifiers=["Face_4"],
    options={"sub_faces": True}
)
```

## Reset-and-Rebuild Pattern

A common pattern is to clear existing apertures and then re-add with new parameters:

```python
# 1. Query current state
query(target_type="face", identifiers=["Face_1"],
    fields=["identifier", "aperture_ratio", "apertures"])

# 2. Clear existing apertures
remove(operation="face_objects", identifiers=["Face_1"],
    options={"apertures": True})

# 3. Add new apertures with different parameters
add(operation="apertures_by_ratio", target_type="face",
    identifiers=["Face_1"], params={"ratio": 0.5})

# 4. Verify new state
query(target_type="face", identifiers=["Face_1"],
    fields=["identifier", "aperture_ratio", "apertures"])
```

## Return Guidance

- Use `message` for quick confirmation.
- Use `results` when explaining what happened on each face.
- Inspect `not_found` if identifiers may not exist in the current model.
- Mention `auto_save` when the source model came from shared memory.

## Workflow

1. Query faces first if the scope is uncertain.
2. Choose model-wide or face-scoped removal.
3. Re-query aperture counts or face aperture ratios after removal if verification is needed.
