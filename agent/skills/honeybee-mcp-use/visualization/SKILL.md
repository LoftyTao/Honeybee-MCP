---
name: "honeybee-visualization"
description: "Use when a task requires exporting a loaded Honeybee model or selected Honeybee geometry objects as a VisualizationSet or related visual deliverables such as `.vsf`, `.svg`, `.html`, or `.vtkjs` through the `visualization` tool."
---

# Honeybee Visualization

## Use This Skill When

- The user wants a visual preview of the current model
- The user wants `.vsf`, `.svg`, `.html`, or `.vtkjs` output
- The user wants selected rooms, faces, apertures, doors, subfaces, or shades exported as a display package
- The user wants a local interactive deliverable without editing the model
- The task is about presentation, reporting, review, or geometry handoff rather than simulation-property editing

## Preferred Tool

### `visualization`

**Description**
Read-only visualization export tool for Honeybee geometry and model display data.

**Args**
- `target_type: str = "model"`
  Allowed: `model`, `room`, `face`, `aperture`, `door`, `subface`, `shade`
- `identifiers: list | None = None`
  Optional identifier scope for non-model targets. Omit to export all objects of the target type.
- `vis_options: dict | None = None`
  Common options:
  - `color_by`: `type | boundary_condition | none`
  - `include_wireframe`: `bool`
  Model-only options:
  - `use_mesh`
  - `hide_color_by`
  - `grid_display_mode`
  - `hide_grid`
  - `grid_data_path`
  - `grid_data_display_mode`
  - `active_grid_data`
  Object-level options:
  - `include_sub_faces`
  - `include_shades`
- `export_formats: list | None = None`
  Allowed: `vsf`, `svg`, `html`, `vtkjs`
- `output_folder: str | None = None`
- `name: str | None = None`
- `svg_options: dict | None = None`
  Allowed:
  - `width`
  - `height`
  - `margin`
  - `interactive`
  - `render_3d_legend`
  - `render_2d_legend`
  - `view`
- `return_visualization_set: bool | None = None`

**Returns**
- `success: bool`
- `target_type: str`
- `count: int`
- `missing: list`
- `summary: dict`
- `exports: dict`
- `visualization_set: dict` when requested or when no export file is requested

## Tool Choice

- Use `visualization` for visual deliverables.
- Use `save_model` only for HBJSON persistence.
- Use `query` before `visualization` when the user does not yet know target identifiers.
- Prefer `target_type="model"` when the user wants a whole-building export.
- Prefer object-level targets when the user wants isolated visual output for selected geometry.

## Export Patterns

### Whole-model export

Use for:

- design review snapshots
- full-scene SVG output
- local interactive HTML handoff
- vtkjs export for downstream viewing workflows

Example:

```python
visualization(
    target_type="model",
    export_formats=["vsf", "svg", "html"],
    output_folder="C:/output",
    name="MyModel_Review",
    vis_options={"color_by": "boundary_condition", "include_wireframe": True},
    svg_options={"width": 1600, "height": 900, "view": "Top"}
)
```

### Selected object export

Use for:

- room-level presentation
- facade subset review
- aperture or shade detail exports

Example:

```python
visualization(
    target_type="room",
    identifiers=["Room_1", "Room_2"],
    vis_options={
        "color_by": "type",
        "include_wireframe": True,
        "include_sub_faces": True,
        "include_shades": True
    },
    export_formats=["svg"],
    output_folder="C:/output"
)
```

### Return-only visualization set

Use when the caller wants structured visualization data without writing files.

```python
visualization(
    target_type="face",
    identifiers=["Face_1"],
    vis_options={"color_by": "type", "include_wireframe": True},
    return_visualization_set=True
)
```

## Return Guidance

- Surface `exports` when files are written.
- Surface `missing` when the user supplied identifiers.
- Use `summary.geometry_count` to confirm non-empty output.
- If the user asked for a file deliverable and no files were requested, recommend `export_formats`.
- If the user asked for an HBJSON file instead of a visual package, route to `model-saver`.

## Important Notes

- `visualization` is read-only and does not modify the model.
- It does not trigger shared-memory auto-save.
- It does not create version snapshots.
- `.vsf` is the canonical VisualizationSet file output for this project.
- High-level `room_attrs` / `face_attrs` analysis packaging and object-level `sensor_grid` / `view` export remain future work and should not be implied as currently supported.
