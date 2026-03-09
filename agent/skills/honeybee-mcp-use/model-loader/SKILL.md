---
name: "honeybee-model-loader"
description: "Use when a task requires loading a Honeybee model from file, dict, or Grasshopper shared memory before any query, apply, add, or remove operation, including restoration of custom Energy and Radiance resources."
---

# Honeybee Model Loader

## Use This Skill When

- No model is currently loaded
- The user wants to import an HBJSON or HBpkl
- The user is working from Grasshopper shared memory
- A model dictionary must be restored from version history or external input

## Preferred Tools

### `load_model`
**Args**
- `hb_file: str | None = None`
- `cleanup_irrational: bool = False`

**Returns**
- `success: bool`
- `source: str`
- `display_name: str`
- `identifier: str`
- `floor_area: float`
- `rooms_count: int`
- `outdoor_shades_count: int`
- `orphaned_faces_count: int`
- `orphaned_shades_count: int`
- `orphaned_apertures_count: int`
- `orphaned_doors_count: int`
- optional `available_grasshopper_models`
- optional `cache_cleanup`

### `load_model_from_dict`
**Args**
- `data: dict`
- `cleanup_irrational: bool = False`

**Returns**
- `success: bool`
- model summary fields

## Tool Choice

- Use `load_model()` for normal file or auto-detected Grasshopper workflows.
- Use `load_model("latest")` when the newest shared-memory model is intended.
- Use `load_model_from_dict()` for version restore or API-provided model data.

## Example

```python
load_model()
load_model("latest")
load_model("C:/path/to/model.hbjson")
load_model_from_dict(model_dict)
```

## Return Guidance

- If `success=False`, inspect `error` and `hint`.
- If the source is Grasshopper, mention `source="grasshopper"` or shared-memory origin in your response.
- Custom MCP-managed Energy and Radiance resources are restored together with the HBJSON model when present in serialized model data.
