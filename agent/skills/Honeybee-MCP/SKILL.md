---
name: honeybee-mcp
description: Comprehensive building energy modeling toolkit for Honeybee models. Use for model I/O (HBJSON/HBpkl), geometry editing (windows, doors, shades), property application (constructions, HVAC, program types), Grasshopper synchronization via shared memory, and version control. Best for AI-augmented building design workflows and automated energy model manipulation.
license: MIT
metadata:
    skill-author: Honeybee-MCP Team
---

# Honeybee-MCP: AI-Powered Building Energy Modeling

## Overview

Honeybee-MCP is a Model Context Protocol (MCP) server that bridges Large Language Models (LLMs) with the Honeybee building energy modeling ecosystem. It provides a comprehensive set of tools for loading, editing, querying, and saving Honeybee models, with seamless integration to Grasshopper via shared memory.

**Key Features:**
- Load/save Honeybee models (HBJSON, HBpkl, shared memory)
- Add/remove windows, doors, and shading elements
- Apply energy properties (constructions, program types, HVAC systems)
- Query model geometry and simulation attributes
- Real-time Grasshopper synchronization
- Version control with undo/redo capability

## When to Use This Skill

Use this skill when:

- Loading Honeybee models from files or Grasshopper shared memory
- Adding windows by ratio (WWR), dimensions, or grid pattern
- Removing windows, doors, or shading elements
- Adding louvers, overhangs, or blinds to windows
- Applying construction sets, program types, or HVAC systems
- Querying model properties (areas, volumes, element counts)
- Synchronizing models between AI IDE and Grasshopper
- Searching for available constructions, modifiers, or program types
- Undoing or redoing model changes
- Comparing model versions

## Core Capabilities

Honeybee-MCP is organized into modular skill areas, each addressing specific modeling tasks:

1. **Model I/O** - Load and save models from files or Grasshopper shared memory
2. **Query & Inspection** - Retrieve model geometry, properties, and statistics
3. **Aperture Operations** - Add or remove windows and skylights
4. **Shade Operations** - Add or remove louvers, overhangs, and context geometry
5. **Door Operations** - Edit and remove doors
6. **Property Application** - Apply constructions, program types, and HVAC systems
7. **Library Search** - Find available building properties
8. **Grasshopper Sync** - Real-time model exchange with Grasshopper
9. **Version Control** - Track changes with undo/redo capability

## Installation and Setup

Honeybee-MCP runs as an MCP server. Ensure the following prerequisites:

- Python 3.8+
- Ladybug Tools 1.10
- honeybee-core, honeybee-energy, honeybee-radiance

For Grasshopper integration:
- Install HB_Model_SharedMemory_Writer and HB_Model_SharedMemory_Reader components
- Use default shared memory name: `"hb_model_shared"`

## Using This Skill

This skill provides comprehensive documentation organized by functionality area. When working on a task, consult the relevant reference documentation:

### 1. Model Loading (honeybee-model-loader)

**Reference:** `model-loader/SKILL.md`

Use for:
- Loading models from HBJSON or HBpkl files
- Auto-detecting models from Grasshopper shared memory
- Loading models from dictionary representations
- Cleaning up irrational geometry

**Quick example:**
```python
# Auto-detect from Grasshopper
load_model()

# Load from file
load_model("/path/to/model.hbjson")

# Load with geometry cleanup
load_model(cleanup_irrational=True)
```

### 2. Model Saving (honeybee-model-saver)

**Reference:** `model-saver/SKILL.md`

Use for:
- Saving models to HBJSON files
- Exporting with specific property filters
- Triangulating sub-faces for compatibility

**Quick example:**
```python
# Save to file
save_model(folder="/output", name="my_model")

# Save with specific properties only
save_model(folder="/output", included_prop=["energy"])
```

### 3. Model Querying (honeybee-query)

**Reference:** `query/SKILL.md`

Use for:
- Getting model overview (rooms, areas, volumes)
- Listing element identifiers
- Querying face, aperture, door, or shade properties
- Checking HVAC and energy properties
- Getting window-to-wall ratios

**Quick example:**
```python
# Get model overview
query_model(rooms=True, floor_area=True, volume=True)

# Query face properties
query_faces(["Face_1", "Face_2"], area=True, aperture_ratio=True)

# Check room HVAC
query_room(["Room_1"], hvac_properties=True)
```

### 4. Adding Windows (honeybee-aperture-adder)

**Reference:** `aperture-adder/SKILL.md`

Use for:
- Adding windows by window-to-wall ratio (WWR)
- Adding windows by specific dimensions
- Adding windows in grid patterns
- Adding repeated rectangular windows

**Quick example:**
```python
# 40% WWR
add_apertures_by_ratio(["South_Face"], 0.4)

# Specific dimensions
add_aperture_by_width_height(["Face_1"], width=2.0, height=1.5)

# Grid pattern
add_apertures_by_ratio_gridded(["Face_2"], 0.3, x_dim=1.0, y_dim=1.5)
```

### 5. Removing Windows (honeybee-aperture-remover)

**Reference:** `aperture-remover/SKILL.md`

Use for:
- Removing all windows from model
- Removing windows from specific faces

**Quick example:**
```python
# Remove all windows
remove_all_apertures()

# Remove from specific faces
remove_face_objects(["Face_1", "Face_2"], apertures=True)
```

### 6. Adding Shading (honeybee-louver-adder)

**Reference:** `louver-adder/SKILL.md`

Use for:
- Adding horizontal louvers by count or spacing
- Adding overhangs and fins
- Configuring louver depth and angle

**Quick example:**
```python
# Add 5 louvers, 0.5m deep
add_louvers_by_count(["Window_1"], louver_count=5, depth=0.5)

# Add louvers with 0.3m spacing
add_louvers_by_distance_between(["Window_2"], distance=0.3, depth=0.4)
```

### 7. Removing Shades (honeybee-shade-remover)

**Reference:** `shade-remover/SKILL.md`

Use for:
- Removing all attached shades (louvers, overhangs)
- Removing context geometry (shade meshes)
- Removing specific shade types

**Quick example:**
```python
# Remove all shades and context
remove_all_shades()

# Remove only context buildings
remove_all_shades(shade_mesh_ids=["Building_1", "Tree_1"])
```

### 8. Editing Doors (honeybee-door-editor)

**Reference:** `door-editor/SKILL.md`

Use for:
- Removing doors from model
- Removing doors from specific faces
- Querying door properties

**Quick example:**
```python
# Remove all doors
remove_all_doors()

# Remove from specific faces
remove_face_objects(["Face_1"], doors=True)
```

### 9. Applying Properties (honeybee-apply-properties)

**Reference:** `apply-properties/SKILL.md`

Use for:
- Applying construction sets to rooms
- Applying program types (office, residential, etc.)
- Applying HVAC systems (Ideal Air, VAV, Radiant, etc.)
- Applying window constructions by orientation
- Applying shade materials

**Quick example:**
```python
# Apply program type
apply_room_attributes(program_type_identifier="Office_Open")

# Apply HVAC
apply_hvac(system_category="Ideal")

# Apply window construction by orientation
apply_window_attributes(construction_identifiers=["North", "South", "East", "West"])
```

### 10. Searching Library (honeybee-search-lib)

**Reference:** `search-lib/SKILL.md`

Use for:
- Finding available construction sets
- Finding program types by building type
- Finding HVAC system options
- Finding window constructions

**Quick example:**
```python
# Search construction sets
search_properties(category="construction_sets", keywords=["office"])

# Search program types
search_properties(category="program_types", building_program="Office")

# List HVAC options
apply_hvac(system_category="AllAir", list_options=True)
```

### 11. Grasshopper Synchronization (honeybee-grasshopper-sync)

**Reference:** `grasshopper-sync/SKILL.md`

Use for:
- Loading models from Grasshopper shared memory
- Saving models to Grasshopper shared memory
- Checking shared memory status
- Clearing shared memory

**Quick example:**
```python
# Check if Grasshopper model exists
check_shared_memory_status()

# Load from shared memory
load_model_from_shared_memory()

# Save to shared memory
save_model_to_shared_memory()
```

### 12. Version Control (honeybee-version-control)

**Reference:** `version-control/SKILL.md`

Use for:
- Saving version snapshots
- Undoing to previous versions
- Redoing undone changes
- Comparing versions
- Viewing version history

**Quick example:**
```python
# Save checkpoint
version_control("save", description="Before adding windows")

# Undo last change
version_control("undo")

# View history
version_control("list")
```

### 13. General Model Editing (honeybee-model-editor)

**Reference:** `model-editor/SKILL.md`

Use for:
- Removing multiple element types at once
- Removing objects from specific faces
- Removing shades from specific rooms

**Quick example:**
```python
# Remove windows and doors from faces
remove_face_objects(["Face_1"], apertures=True, doors=True)

# Remove shades from rooms
remove_room_shades(["Room_1"], outdoor_shades=True)
```

## Skill Selection Guide

When a user request is received, follow this decision process:

| User Intent | Skill to Invoke |
|-------------|-----------------|
| Load/import model | `honeybee-model-loader` |
| Save/export model | `honeybee-model-saver` |
| View model info | `honeybee-query` |
| Add windows | `honeybee-aperture-adder` |
| Remove windows | `honeybee-aperture-remover` |
| Add louvers/shades | `honeybee-louver-adder` |
| Remove shades | `honeybee-shade-remover` |
| Edit doors | `honeybee-door-editor` |
| Apply properties | `honeybee-apply-properties` |
| Search library | `honeybee-search-lib` |
| Sync with Grasshopper | `honeybee-grasshopper-sync` |
| Undo/redo changes | `honeybee-version-control` |

## Important Notes

### Auto-Save Behavior

When a model is loaded from Grasshopper shared memory:
- **All edit operations automatically save back to shared memory**
- No manual save required for normal workflow
- Manual save only needed for backups or different names

### Standard Workflow

```
1. Load model (honeybee-model-loader)
2. Query current state (honeybee-query)
3. Make edits (appropriate edit skill)
4. Verify changes (honeybee-query)
5. (Auto-saved if from Grasshopper)
```

### Error Recovery

```
1. Use honeybee-version-control to undo
2. Or load a specific version
3. Continue editing
```
