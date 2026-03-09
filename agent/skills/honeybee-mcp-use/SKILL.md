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
