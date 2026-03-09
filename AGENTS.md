# Honeybee-MCP Agent Working Guide

> This document helps AI IDE agents quickly understand the current Honeybee-MCP architecture, the unified tool surface, the working workflow, and the preferred extension strategy. It reflects the refactored implementation rather than the earlier object-specific tool layout.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Core Architecture](#2-core-architecture)
3. [Model State System](#3-model-state-system)
4. [Unified Tool System](#4-unified-tool-system)
5. [Shared Memory System](#5-shared-memory-system)
6. [Version Control System](#6-version-control-system)
7. [Skills System](#7-skills-system)
8. [Workflow Guide](#8-workflow-guide)
9. [Best Practices](#9-best-practices)
10. [Common Task Examples](#10-common-task-examples)
11. [Error Handling](#11-error-handling)
12. [Code Standards](#12-code-standards)
13. [HBJSON Resource Extension Pattern](#13-hbjson-resource-extension-pattern)
14. [Planning Lessons from Energy and Radiance Work](#14-planning-lessons-from-energy-and-radiance-work)

---

## 1. Project Overview

### 1.1 Project Positioning

**Honeybee-MCP** is an MCP server for the Honeybee ecosystem. Its purpose is to let an AI IDE load, inspect, edit, synchronize, and version Honeybee models in a stable and persistent way.

The project currently supports:

- `honeybee-core`
- `honeybee-energy`
- `honeybee-radiance`
- Grasshopper collaboration through shared memory

### 1.2 Current Refactor Status

The project has completed a clear restructuring of its tool system. The current implementation no longer treats a large set of object-specific tool files as the main architecture. Instead, it is organized around four unified operation buses:

- `query`
- `apply`
- `add`
- `remove`

State management, shared-memory synchronization, version control, and the bus execution core have been separated from the older wrapper-style tools and moved into clearer subsystems.

### 1.3 Project Structure

```text
Honeybee-MCP/
|-- server.py
|-- requirements.txt
|-- README.md
|-- AGENTS.md
|-- tools/
|   |-- __init__.py
|   |-- mcp_context.py
|   |-- load_model.py
|   |-- save_model.py
|   |-- state/
|   |   |-- manager.py
|   |   |-- hooks.py
|   |   |-- summary.py
|   |   |-- energy_resources.py
|   |   `-- radiance_resources.py
|   |-- operations/
|   |   |-- common.py
|   |   |-- query_bus.py
|   |   |-- apply_bus.py
|   |   |-- add_bus.py
|   |   |-- remove_bus.py
|   |   |-- apply_service.py
|   |   |-- add_service.py
|   |   |-- remove_service.py
|   |   |-- energy_resource_service.py
|   |   |-- radiance_resource_service.py
|   |   `-- hvac_config.json
|   |-- sync/
|   |   |-- bus.py
|   |   |-- service.py
|   |   `-- shared_memory.py
|   |-- library/
|   |   |-- bus.py
|   |   `-- service.py
|   |-- visualization/
|   |   |-- bus.py
|   |   `-- service.py
|   `-- versioning/
|       |-- bus.py
|       |-- service.py
|       `-- store.py
|-- grasshopper/
|-- agent/skills/
`-- src/
```

### 1.4 Current Tool Policy

The repository now treats the unified buses as the only primary public interface.

**Rule**: Extend `query`, `apply`, `add`, `remove`, `sync`, `library`, `visualization`, or `versioning` directly. Do not reintroduce object-specific wrapper files.

---

## 2. Core Architecture

### 2.1 Architecture Layers

The current architecture can be understood as four layers:

1. **State Layer**
   - current model state
   - model source tracking
   - post-edit hooks

2. **Sync Layer**
   - shared-memory protocol
   - cache cleanup
   - Grasshopper read/write collaboration

3. **Operation Layer**
   - the four unified buses: `query / apply / add / remove`
   - their service modules
   - target resolution, argument boundaries, and result formatting

4. **Library and Versioning Support**
   - Energy and Radiance library search
   - version snapshot storage and action dispatch

### 2.2 Design Principle

The current system follows a small set of architectural principles:

- concentrate the user-facing interface
- concentrate the internal implementation
- make input boundaries explicit
- make output boundaries explicit
- keep cross-cutting logic in one place

In other words, when adding a new capability, the preferred questions are:

- Is this a new `query` field registration?
- Is this a new `apply` operation?
- Is this a new `add` operation?
- Is this a new `remove` operation?

The preferred answer is not to create another scattered top-level tool file.

---

## 3. Model State System

### 3.1 Model Manager

Current model state is managed centrally by `tools/state/manager.py`.

```python
class ModelManager:
    def __init__(self):
        self.model = None
        self.source = None
        self.source_name = None
```

Global singleton:

```python
manager = ModelManager()
```

### 3.2 Model Source

`manager.source` currently records one of the following origins:

- `file`
- `dict`
- `shared_memory`

### 3.3 Post-Edit Pipeline

All edit operations should enter the unified post-edit pipeline after a successful change. This pipeline is handled by `tools/state/hooks.py`.

Its responsibilities include:

- automatically writing back to shared memory when appropriate
- attaching consistent `auto_save` information to tool responses

This means new business logic should not implement a separate private auto-save routine.

---

## 4. Unified Tool System

### 4.1 Public Tool Surface

The recommended public MCP interface is:

- `load_model`
- `load_model_from_dict`
- `save_model`
- `load_model_from_shared_memory`
- `save_model_to_shared_memory`
- `check_shared_memory_status`
- `clear_shared_memory_model`
- `cleanup_shared_memory_cache`
- `version_control`
- `search_properties`
- `visualization`
- `query`
- `apply`
- `add`
- `remove`

### 4.2 Query Bus

`query` is the unified read interface.

#### Args

- `target_type`
- `identifiers`
- `fields`
- `output_mode`

#### Supported Target Types

- `model`
- `room`
- `face`
- `aperture`
- `door`
- `subface`
- `shade`
- `schedule`
- `schedule_day`
- `schedule_type_limit`
- `energy_resource`
- `modifier`
- `modifier_set`
- `radiance_resource`
- `sensor_grid`
- `view`

#### Example

```python
query(
    target_type="face",
    identifiers=["Face_1"],
    fields=[
        "identifier",
        "area",
        "aperture_ratio",
        "properties.energy.construction.display_name"
    ]
)
```

### 4.3 Apply Bus

`apply` is the unified property-assignment interface.

#### Args

- `operation`
- `target_type`
- `identifiers`
- `values`

#### Current Operations

- `room_attributes`
- `hvac`
- `opaque_attributes`
- `window_attributes`
- `shade_attributes`
- `people`
- `lighting`
- `electric_equipment`
- `service_hot_water`
- `setpoint`
- `ventilation`
- `process_load`
- `schedule_type_limit`
- `schedule_day`
- `schedule_ruleset`
- `schedule_fixed_interval`
- `modifier`
- `modifier_set`
- `sensor_grid`
- `view`

#### Example

```python
apply(
    operation="room_attributes",
    target_type="room",
    values={"program_type_identifier": "Office_Open"}
)
```

### 4.4 Add Bus

`add` is the unified creation interface.

#### Current Operations

- `aperture_by_width_height`
- `apertures_by_ratio`
- `apertures_by_ratio_rectangle`
- `apertures_by_ratio_gridded`
- `apertures_by_width_height_rectangle`
- `louvers`
- `louvers_by_count`
- `louvers_by_distance_between`
- `schedule_type_limit`
- `schedule_day`
- `schedule_ruleset`
- `schedule_fixed_interval`
- `process_load`
- `modifier`
- `modifier_set`
- `sensor_grid`
- `view`

#### Example

```python
add(
    operation="apertures_by_ratio",
    target_type="face",
    identifiers=["Face_1"],
    params={"ratio": 0.4}
)
```

### 4.5 Remove Bus

`remove` is the unified deletion interface.

#### Current Operations

- `all_apertures`
- `all_doors`
- `all_shades`
- `face_objects`
- `room_shades`
- `process_loads`
- `schedule`
- `schedule_day`
- `schedule_type_limit`
- `modifier`
- `modifier_set`
- `sensor_grid`
- `view`

#### Example

```python
remove(
    operation="face_objects",
    identifiers=["Face_1"],
    options={"apertures": True, "doors": True}
)
```

### 4.6 Public Interface Policy

The unified buses are the only recommended public editing interface. If a compatibility wrapper is needed for an external ecosystem in the future, it should be treated as a separate compatibility strategy rather than the main architecture.

---

## 5. Shared Memory System

### 5.1 Purpose

The shared-memory system enables two-way model exchange between Grasshopper and an AI IDE.

### 5.2 Main Location

The current shared-memory implementation is concentrated in:

- `tools/sync/service.py`
- `tools/sync/bus.py`
- `tools/sync/shared_memory.py`

### 5.3 Behavior

The expected collaboration sequence is:

- Grasshopper Writer writes a model
- MCP loads the model
- MCP edits the model
- the post-edit pipeline writes updates back when appropriate
- Grasshopper Reader reads the updated model

### 5.4 Cache Cleanup

The system automatically:

- keeps recent cache files
- removes old cache files
- provides an explicit cleanup tool when manual cleanup is required

---

## 6. Version Control System

### 6.1 Public Interface

The unified versioning entry point is `version_control(action=...)`.

### 6.2 Supported Actions

- `list`
- `save`
- `load`
- `undo`
- `redo`
- `compare`
- `info`
- `delete`
- `clear`
- `cleanup`

### 6.3 Snapshot Policy

Version snapshots keep the full serialized model dictionary, including:

- Honeybee Core data
- Energy extension data
- Radiance extension data

This is why version restore can recover both geometry and reusable resources rather than only host objects.

---

## 7. Skills System

The skills root is located at:

```text
agent/skills/
```

The role of the skills system has shifted from "remembering a long list of old tool filenames" to "understanding when to use the unified buses and the state, sync, and version layers."

For future skill authoring and maintenance, the recommendation is:

- center workflows around `query / apply / add / remove`
- mention legacy interfaces only when necessary
- describe work as a workflow instead of a flat list of tool names

---

## 8. Workflow Guide

### 8.1 Standard Workflow

```text
1. LOAD MODEL
   -> load_model() / load_model_from_shared_memory()

2. QUERY MODEL
   -> query(...)

3. SEARCH PROPERTIES (Optional)
   -> search_properties(...)

4. VISUALIZE (Optional)
   -> visualization(...)

5. EDIT MODEL
   -> add(...) / apply(...) / remove(...)

6. VERIFY CHANGES
   -> query(...)

7. SAVE OR SYNC
   -> save_model() / save_model_to_shared_memory()
```

### 8.2 Shared Memory Workflow

```text
Grasshopper Writer -> shared memory -> load_model()
AI operations      -> auto-save      -> Grasshopper Reader
```

### 8.3 Legacy Workflow

Legacy workflows can still run, but they are no longer the preferred way to describe the system. Future documentation, skills, and automation scripts should prioritize the unified-bus workflow.

---

## 9. Best Practices

### 9.1 Query First

Inspect the current state before editing.

```python
query(target_type="model", fields=["faces", "rooms"])
query(target_type="face", identifiers=faces, fields=["identifier", "type", "boundary_condition"])
```

### 9.2 Prefer Unified Buses

New features, new skills, and new scripts should prefer:

- `query`
- `apply`
- `add`
- `remove`

### 9.3 Extend via Registry Thinking

When you need a new capability, think in this order:

- Is it a new query field?
- Is it a new apply operation?
- Is it a new add operation?
- Is it a new remove operation?

Do not default to adding another flat wrapper tool file.

### 9.4 Shared Memory Safety

When a model comes from shared memory, successful edits may be written back automatically. If overwriting the shared state would be risky, save elsewhere first or use a distinct name.

---

## 10. Common Task Examples

### 10.1 Add Windows to Exterior Walls

```python
faces = query(target_type="model", fields=["faces"])["data"]["faces"]

face_info = query(
    target_type="face",
    identifiers=faces,
    fields=["identifier", "type", "boundary_condition"]
)["data"]

exterior_walls = [
    fid for fid, info in face_info.items()
    if info["type"] == "Wall" and info["boundary_condition"] == "Outdoors"
]

add(
    operation="apertures_by_ratio",
    target_type="face",
    identifiers=exterior_walls,
    params={"ratio": 0.4}
)
```

### 10.2 Add Louvers

```python
apertures = query(target_type="model", fields=["apertures"])["data"]["apertures"]

add(
    operation="louvers_by_count",
    target_type="aperture",
    identifiers=apertures,
    params={"louver_count": 5, "depth": 0.5}
)
```

### 10.3 Apply Room Properties

```python
apply(
    operation="room_attributes",
    target_type="room",
    values={"program_type_identifier": "Office_Open"}
)

apply(
    operation="hvac",
    target_type="room",
    values={"system_category": "Ideal"}
)
```

### 10.4 Remove Shade-Related Objects

```python
remove(operation="all_shades")
```

```python
remove(
    operation="all_shades",
    identifiers=["Tree_1", "Building_2"]
)
```

---

## 11. Error Handling

### 11.1 Common Errors

- `No model loaded`
- `Model not found`
- `Invalid identifier`
- `Invalid operation`
- `Invalid field path`
- `Shared memory error`

### 11.2 Return Shape

The recommended stable return shape is:

```python
{
    "success": bool,
    "message": str,
    "error": str,
    "hint": str
}
```

For `query`, `apply`, `add`, and `remove`, preserving a stable response style is preferred over allowing each operation branch to drift into its own custom shape.

---

## 12. Code Standards

### 12.1 New Work Should Follow the Refactored Architecture

New code should primarily be placed under:

- `tools/state`
- `tools/sync`
- `tools/operations`

Only modify legacy wrapper files when compatibility truly requires it.

### 12.2 Naming

- Tool functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

### 12.3 Preferred Extension Strategy

When adding a new feature:

1. First decide whether it belongs to `query`, `apply`, `add`, or `remove`.
2. Then decide whether the change is a new field, a new registered operation, or a service implementation change.
3. Only after that should you consider whether a compatibility wrapper is still needed.

### 12.4 Documentation Policy

Documentation should describe the refactored architecture as the primary story. The older flat tool layout should no longer be the main narrative.

---

## 13. HBJSON Resource Extension Pattern

### 13.1 Treat Energy and Radiance Resources as HBJSON-Native Data

When extending `honeybee-energy` or `honeybee-radiance`, agents should start from the HBJSON resource model instead of thinking only about runtime Python objects.

The key questions are:

1. Is the target object a reusable resource, a host-attached object, or both?
2. Will Honeybee preserve it automatically in `model.to_dict()`?
3. If not, how should MCP preserve it so that `save / load / version / shared memory` remain lossless?

The current project answer is:

- reusable resources belong to model-bound MCP resource stores in `tools/state`
- host-attached objects still belong on Honeybee model objects
- the final persistence target should remain `HBJSON.properties.energy` or `HBJSON.properties.radiance`

### 13.2 Resource Store Pattern

When the Honeybee runtime cannot reliably preserve unattached resources, agents should introduce a model-bound resource store and connect it to `ModelManager`.

Current examples:

- `tools/state/energy_resources.py`
- `tools/state/radiance_resources.py`

This pattern should include:

- empty store initialization
- loading or rebuilding from HBJSON dictionary data
- collecting resources already attached to the loaded model
- merging MCP-managed resources back into serialized HBJSON
- register, unregister, and resolve helpers
- an explicit distinction between `session_store` and `model_attached`

### 13.3 Resolver Precedence Must Be Explicit

Whenever a tool accepts an identifier for a reusable resource, the resolution order should be explicit and stable.

Recommended precedence:

1. MCP resource store
2. currently attached model resources
3. official Honeybee library

This rule should be documented in service helpers instead of being left implicit in scattered business code.

### 13.4 Extend Unified Buses, Not New Top-Level Tools

For both Energy and Radiance, the preferred public surface remains:

- `query`
- `add`
- `apply`
- `remove`

Agents should not create one-off public wrappers such as `create_schedule.py`, `add_modifier.py`, or `edit_sensor_grid.py`. New capability should be registered inside the existing buses and delegated to service modules.

### 13.5 Persistence Is a Full Chain

Any new resource family is incomplete unless it is wired through the full persistence chain:

1. `load_model` / `load_model_from_dict`
2. `manager.serialized_model_dict()`
3. `save_model`
4. shared-memory read and write
5. version control save, load, undo, and redo

If one of these layers is skipped, the feature should still be considered unfinished.

### 13.6 Safe Removal Is Required

Reusable resources must not be removed blindly.

Before deletion, agents should check references from:

- rooms
- faces
- apertures
- doors
- shades
- schedules or modifier sets
- HVAC, SHW, process loads, or other higher-level objects

If references exist, the delete operation should be blocked and should return a readable reference summary.

---

## 14. Planning Lessons from Energy and Radiance Work

### 14.1 The Shared Structure of the Two Plans

The two recent expansion plans succeeded because they shared the same planning backbone.

They first grounded themselves in the real Honeybee and HBJSON object model. They did not assume that a Python object being constructible automatically meant it was persistable, reloadable, or safely deletable.

They then separated reusable resources from host-attached objects. This was the central architectural move. For Energy, schedules and constructions were treated differently from room loads. For Radiance, modifiers and modifier sets were treated differently from sensor grids and views.

They also treated persistence as part of the feature definition. A capability was not considered supported merely because an object could be instantiated or assigned. It had to survive:

- query
- save
- reload
- shared-memory sync
- version restore

Finally, both plans used the same verification loop:

`create -> attach or reference -> query -> save -> reload -> query again`

This should be treated as the default acceptance path for future cross-cutting extensions.

### 14.2 What Was Worth Keeping

The most valuable shared qualities were:

- decisions based on actual class interfaces and `to_dict()/from_dict()` behavior
- preservation of the unified bus surface
- early definition of resolver precedence
- HBJSON as the persistence target
- early query visibility so new resources were inspectable
- reference-safe deletion design
- roundtrip tests instead of only isolated object-creation tests

### 14.3 Recommended Future Agent Workflow

When adding a new object family, agents should follow this order:

1. inspect Honeybee and HBJSON native schema plus runtime behavior
2. classify objects into reusable resources versus host-attached objects
3. decide whether a model-bound MCP resource store is needed
4. add query visibility first
5. add create, update, and delete support through the unified buses
6. wire serialization through load, save, versioning, and shared memory
7. add roundtrip tests covering create, attach, persist, reload, and safe delete

### 14.4 Future Expansion Checklist

Before considering an AGENTS-guided extension complete, confirm all of the following:

- the object family can be queried through `query`
- the object family can be created through `add`
- the object family can be updated or assigned through `apply`
- the object family can be removed through `remove`, with reference safety when needed
- the object family survives `save_model` and `load_model`
- the object family survives shared-memory auto-save if it participates in model serialization
- the object family survives version control save, load, undo, and redo
- tests include at least one HBJSON roundtrip case

---

*Document Version: 2.1*  
*Last Updated: 2026-03-10*  
*This document reflects the refactored Honeybee-MCP architecture.*
