---
name: honeybee-mcp
description: Use for routing Honeybee-MCP tasks to the correct sub-skill. Invoke when a request involves loading Honeybee models, querying geometry or Energy/Radiance data, managing HBJSON-native Energy/Radiance resources, applying properties, adding apertures or louvers, removing objects, synchronizing with Grasshopper, searching property libraries, creating visualization exports, or managing versions.
---

# Honeybee-MCP

## Purpose

This top-level skill is the routing guide for Honeybee-MCP.

Use it to decide:

- whether Honeybee-MCP is the correct skill family
- which sub-skill should handle the current request
- which tool pattern should be preferred

Do not treat this file as the full API reference. Detailed `Args` and `Returns` belong in the sub-skills.

## System Summary

Honeybee-MCP is now organized around four unified operation buses:

- `query`
- `apply`
- `add`
- `remove`

Supporting tools:

- `load_model`
- `load_model_from_dict`
- `save_model`
- `load_model_from_shared_memory`
- `save_model_to_shared_memory`
- `check_shared_memory_status`
- `clear_shared_memory_model`
- `search_properties`
- `visualization`
- `version_control`

The current system also includes model-bound resource preservation for:

- `honeybee-energy` reusable resources such as schedules, schedule type limits, materials, constructions, construction sets, program types, HVAC, and SHW
- `honeybee-radiance` reusable resources such as modifiers and modifier sets
- Radiance model objects such as `sensor_grid` and `view`

## Skill Routing

### Use `model-loader`

Use when the request is about:

- loading a model from file
- loading a model from shared memory
- restoring a model from dict data
- starting any workflow where no model is loaded yet

### Use `model-saver`

Use when the request is about:

- exporting HBJSON
- saving the current model to disk
- manually writing the current model back to shared memory

### Use `visualization`

Use when the request is about:

- exporting a loaded model as `VisualizationSet`
- generating `.vsf`, `.svg`, `.html`, or `.vtkjs`
- preparing local interactive previews
- creating presentation-ready geometry exports without editing the model

Preferred tool family:

- `visualization`

### Use `query`

Use when the request is about:

- inspecting model structure
- getting identifiers before editing
- reading geometry or topology
- checking Energy or Radiance properties
- inspecting Energy resources such as schedules or constructions
- inspecting Radiance resources such as modifiers or modifier sets
- inspecting Radiance analysis objects such as sensor grids or views
- counting objects

Preferred tool family:

- `query`

### Use `apply-properties`

Use when the request is about:

- applying room attributes
- applying HVAC
- applying room-level Energy load objects such as `people`, `lighting`, `electric_equipment`, `service_hot_water`, `setpoint`, `ventilation`, and `process_load`
- applying facade, window, or shade constructions
- applying custom Energy constructions and schedules
- applying Radiance modifiers, modifier sets, sensor grids, or views

Preferred tool family:

- `apply`

### Use `resource-management`

Use when the request is about:

- creating custom Energy schedules, schedule days, or schedule type limits
- creating custom Energy constructions or materials as reusable resources
- creating or editing Radiance modifiers or modifier sets
- adding or editing sensor grids or views
- deleting reusable Energy or Radiance resources with reference safety
- reasoning about `session_store` versus `model_attached` resources

Preferred tool families:

- `query`
- `search_properties`
- `add`
- `apply`
- `remove`

### Use `aperture-adder`

Use when the request is about:

- adding windows
- adding skylights
- adding apertures by ratio, size, or gridded pattern

Preferred tool family:

- `add`

### Use `louver-adder`

Use when the request is about:

- adding louvers
- adding aperture-attached shading
- adding blinds or count/spacing-based shades

Preferred tool family:

- `add`

### Use `aperture-remover`

Use when the request is about:

- removing all apertures
- removing apertures from selected faces
- clearing glazing before re-adding windows

Preferred tool family:

- `remove`

### Use `shade-remover`

Use when the request is about:

- removing shades
- removing shade meshes
- clearing room-level or face-level shading

Preferred tool family:

- `remove`

### Use `door-editor`

Use when the request is about:

- inspecting doors
- removing doors
- removing door-related face objects

Preferred tool families:

- `query`
- `remove`

### Use `model-editor`

Use when the request is about:

- broad cleanup operations
- removing multiple categories of objects
- model-wide reset-style edits

Preferred tool family:

- `remove`

### Use `grasshopper-sync`

Use when the request is about:

- shared memory status
- Grasshopper synchronization
- reading from or writing to Grasshopper
- clearing shared memory

### Use `search-lib`

Use when the request is about:

- finding valid construction identifiers
- finding program types
- finding schedule, schedule type limit, modifier, or modifier set identifiers
- finding construction sets before apply

### Use `version-control`

Use when the request is about:

- saving checkpoints
- undo / redo
- loading a previous version
- comparing model versions
- clearing version history

## Recommended Workflow

For most requests, follow this sequence:

1. Load model if needed.
2. Query current state if scope is unclear.
3. Search identifiers if apply targets are unknown.
4. Use `visualization` when a preview or export deliverable is needed.
5. Execute `apply`, `add`, or `remove`.
6. Query again to verify.
7. Save or sync if required.
8. Use version control before risky operations.

## Selection Heuristics

- If the request is primarily about reading, prefer `query`.
- If the request changes metadata or simulation properties, prefer `apply`.
- If the request is about reusable Energy or Radiance resources, prefer `query` first and then `add/apply/remove`.
- If the request creates geometry, prefer `add`.
- If the request creates reusable schedules, modifiers, modifier sets, sensor grids, or views, also prefer `add`.
- If the request deletes geometry or attached objects, prefer `remove`.
- If the request deletes reusable resources, check references before removal.
- If the request is about visual delivery, preview, reporting, or local interactive output, prefer `visualization`.
- If the request mentions Grasshopper explicitly, inspect `grasshopper-sync`.
- If the request mentions “what options exist”, inspect `search-lib`.

## Notes

- Prefer unified buses over legacy object-specific tool names.
- `visualization` is a read-only export tool and should not be treated as part of the model persistence chain.
- Use sub-skills for concrete call shapes, arguments, return fields, and examples.

## Common Pitfalls

These are frequent mistakes that lead to failed or unexpected results:

1. **Forgetting `target_type`**: Every `query`, `apply`, and `add` call requires an explicit `target_type`. Omitting it or mismatching it with `identifiers` causes silent failures.
2. **Resource creation order**: Energy schedule resources have strict dependencies: `ScheduleTypeLimit` → `ScheduleDay` → `ScheduleRuleset`. Creating them out of order will fail with a "not found" error.
3. **Deleting referenced resources**: Using `remove` on a schedule, modifier, or modifier set that is still assigned to a room or face will be **blocked**. Query references first, reassign or unassign, then delete.
4. **Applying to wrong scope**: Passing room identifiers when `target_type="face"` is expected (or vice versa) will result in zero matched targets.
5. **Missing model load**: All buses require a loaded model. Calling any tool before `load_model` returns `"No model loaded"`.
6. **Assuming face identifiers**: Face and aperture identifiers are auto-generated and non-obvious. Always `query` first to discover them rather than guessing.

## Multi-Step Composition

Complex user requests typically require chaining multiple tools. Follow this template:

### Pattern: Create-and-Assign Resource

```
1. query → confirm target rooms/faces exist
2. search_properties → check if a library resource already fits
3. add → create custom resource if needed (respect dependency order)
4. apply → assign resource to targets
5. query → verify the assignment
6. save_model or version_control → persist
```

### Pattern: Geometry Reset-and-Rebuild

```
1. query → discover current faces, apertures, shades
2. version_control("save") → checkpoint before destructive edits
3. remove → clear existing geometry (apertures, shades, etc.)
4. add → rebuild with new parameters
5. apply → assign properties to new geometry
6. query → verify final state
```

### Pattern: Exploratory Inspection

```
1. query(target_type="model") → get model overview
2. query(target_type="room", output_mode="list") → enumerate rooms
3. query(target_type="face", identifiers=[...]) → drill into specific faces
4. query with Energy/Radiance nested paths → inspect attached properties
```

## Error Recovery

When a tool returns `success=False` or `status="error"`:

1. **Read `error` and `hint`** fields — they usually contain actionable guidance.
2. **Check `available_operations`** — returned when an unknown operation string is passed.
3. **Check `missing`** — returned by `query` when some identifiers were not found.
4. **Check `blocked`** — returned by `remove` when a resource is still referenced.
5. **Retry after correction** — fix the root cause (load model, fix identifier, create dependency) and retry the same call.
