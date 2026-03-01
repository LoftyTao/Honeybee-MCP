# Honeybee-MCP Agent Working Guide

> This document provides comprehensive project understanding and working guidance for AI IDE Agents, designed to help future AI assistants quickly understand the project architecture, tool usage, and best practices.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Core Architecture](#2-core-architecture)
3. [Model Manager](#3-model-manager)
4. [Tool Categories and Usage](#4-tool-categories-and-usage)
5. [Shared Memory System](#5-shared-memory-system)
6. [Version Control System](#6-version-control-system)
7. [Skills System](#7-skills-system)
8. [Workflow Guide](#8-workflow-guide)
9. [Best Practices](#9-best-practices)
10. [Common Task Examples](#10-common-task-examples)
11. [Error Handling](#11-error-handling)
12. [Code Standards](#12-code-standards)

---

## 1. Project Overview

### 1.1 Project Positioning

**Honeybee-MCP** is a Model Context Protocol (MCP) server designed to bridge Large Language Models (LLMs) with the Honeybee building energy modeling ecosystem.

**Core Objectives:**
- Provide a seamless integration layer for AI-augmented design environments to manipulate HBJSON and HBpkl files
- Abstract the underlying complexities of honeybee-core libraries, offering high-level tools that allow AI to "understand" and "modify" 3D building models
- Enable real-time bidirectional data exchange with Grasshopper

**Technology Stack:**
- **Framework**: fastmcp (MCP protocol implementation)
- **Core Libraries**: honeybee-core, honeybee-energy, honeybee-radiance
- **Python Version**: 3.8+
- **Dependencies**: Ladybug Tools 1.10

### 1.2 Deployment Mode

> **Important**: This MCP server only supports **local deployment**; remote server deployment is not supported.

### 1.3 Project Structure

```
Honeybee-MCP/
├── server.py              # Main entry point, initializes FastMCP server
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
│
├── tools/                 # Core tools module
│   ├── mcp_context.py     # MCP context management (FastMCP instance)
│   ├── load_model.py      # Model loading tools + Model_Manager singleton
│   ├── save_model.py      # Model saving tools
│   ├── query_*.py         # Various query tools
│   ├── *_editor.py        # Various editing tools
│   ├── apply_*.py         # Property application tools
│   ├── shared_memory.py   # Shared memory manager
│   ├── version_control.py # Version control system
│   └── hvac_config.json   # HVAC system configuration presets
│
├── grasshopper/           # Grasshopper integration components
│   ├── src/               # Python source code
│   └── user_object/       # Compiled .ghuser components
│
└── agent/skills/          # AI Agent skill definitions (13 skill modules)
```

---

## 2. Core Architecture

### 2.1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI IDE (Client)                          │
│                    (Cursor / Trae / VS Code)                    │
└─────────────────────────────┬───────────────────────────────────┘
                              │ MCP Protocol
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Honeybee-MCP Server                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Model Manager│  │   Version    │  │   Shared     │          │
│  │  (Singleton) │  │   Control    │  │   Memory     │          │
│  └──────┬───────┘  └──────────────┘  └──────┬───────┘          │
│         │                                     │                  │
│  ┌──────▼─────────────────────────────────────▼───────┐         │
│  │                    Tools Layer                     │         │
│  │  Query │ Edit │ Apply │ I/O │ Search │ Version    │         │
│  └────────────────────────────────────────────────────┘         │
└─────────────────────────────┬───────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  HBJSON/HBpkl │    │   Grasshopper │    │   honeybee-   │
│    Files      │    │ Shared Memory │    │     core      │
└───────────────┘    └───────────────┘    └───────────────┘
```

### 2.2 Data Flow

```
Load Model:
  Grasshopper/File → Shared Memory/File → Model_Manager.model

Modify Model:
  Tool Call → Model_Manager.model.modify() → Version Control Record

Save Model:
  Model_Manager.model → Shared Memory/File → Grasshopper Read
```

---

## 3. Model Manager

### 3.1 Model_Manager Singleton

The model manager is the core of the entire system, using the singleton pattern to manage the currently loaded Honeybee model.

**Location**: `tools/load_model.py`

```python
class Model_Manager:
    def __init__(self):
        self.model = None  # Currently loaded honeybee Model object
    
    def load(self, hb_file: str, cleanup_irrational: bool = False):
        """Load model from file"""
        
    def load_from_dict(self, data: dict, cleanup_irrational: bool = False):
        """Load model from dictionary"""

# Global singleton
manager = Model_Manager()
```

### 3.2 Model Loading Priority

When calling `load_model()`, the system loads models in the following priority:

1. **Grasshopper Shared Memory** (highest priority)
   - Automatically detects models in shared memory
   - If present, loads from shared memory first

2. **Specified File Path**
   - If `hb_file` parameter is provided
   - Loads from HBJSON or HBpkl file

3. **Error Handling**
   - Returns error message and hints when no model is available

### 3.3 Model State Check

All tools should check the model state before execution:

```python
if manager.model is None:
    return {
        "success": False,
        "message": "No model loaded. Please use load_model to load a model first."
    }
```

---

## 4. Tool Categories and Usage

### 4.1 Model I/O Tools

| Tool Name | Description | Use Case |
|---------|---------|---------|
| `load_model` | Load model from file or shared memory | Before any operation |
| `load_model_from_dict` | Load model from dictionary | Version recovery, API responses |
| `save_model` | Save model to HBJSON file | Export model |
| `load_model_from_shared_memory` | Load from shared memory | Grasshopper workflow |
| `save_model_to_shared_memory` | Save to shared memory | Grasshopper workflow |

### 4.2 Query Tools

| Tool Name | Query Object | Common Parameters |
|---------|---------|---------|
| `query_model` | Overall model information | `rooms`, `floor_area`, `volume` |
| `query_room` | Room properties | `general_properties`, `hvac_properties` |
| `query_faces` | Face properties | `area`, `normal`, `aperture_ratio` |
| `query_apertures` | Aperture properties | `area`, `is_operable`, `parent` |
| `query_doors` | Door properties | `area`, `is_glass` |
| `query_shades` | Shade properties | `area`, `is_indoor`, `parent` |

**Query Modes:**

```python
# Get identifier list
query_model(rooms=True)  # Returns ["Room_1", "Room_2", ...]

# Get count
query_model(rooms=True, return_count=True)  # Returns {"rooms": 5}

# Get multiple properties
query_model(floor_area=True, volume=True, rooms=True)
```

### 4.3 Editing Tools

| Tool Name | Description |
|---------|---------|
| `remove_all_apertures` | Remove all apertures |
| `remove_all_doors` | Remove all doors |
| `remove_all_shades` | Remove all shades (including ShadeMesh) |
| `remove_face_objects` | Remove objects from specified faces |
| `remove_room_shades` | Remove shades from rooms |

### 4.4 Aperture/Shade Addition Tools

| Tool Name | Description | Parameter Example |
|---------|---------|---------|
| `add_aperture_by_width_height` | Add aperture by dimensions | `width=2, height=1.5` |
| `add_apertures_by_ratio` | Add apertures by area ratio | `ratio=0.4` (40% WWR) |
| `add_apertures_by_ratio_rectangle` | Add rectangular apertures by ratio | `ratio=0.3, aperture_height=1.5` |
| `add_apertures_by_ratio_gridded` | Add gridded apertures by ratio | `ratio=0.4, x_dim=1.5` |
| `add_louvers` | Add louver shades | `depth=0.5, louver_count=5` |
| `add_louvers_by_count` | Add louvers by count | `louver_count=4, depth=0.6` |
| `add_louvers_by_distance_between` | Add louvers by spacing | `distance=0.3, depth=0.5` |

### 4.5 Property Application Tools

| Tool Name | Application Target | Property Type |
|---------|---------|---------|
| `apply_room_attributes` | Room | Construction set, program type, conditioning status |
| `apply_hvac` | Room | HVAC system |
| `apply_opaque_attributes` | Face/Door | Opaque construction, Radiance modifier |
| `apply_window_attributes` | Aperture/Glass Door | Window construction, Radiance modifier |
| `apply_shade_attributes` | Shade | Shade construction, Radiance modifier |

### 4.6 Search Tools

```python
# Search construction sets
search_properties(category="construction_sets", keywords=["office"])

# Search program types
search_properties(category="program_types", building_program="Office")

# Search constructions
search_properties(category="constructions", construction_type="wall")

# Search modifiers
search_properties(category="modifiers", keywords=["glass"])
```

---

## 5. Shared Memory System

### 5.1 Architecture Design

The shared memory system is based on memory-mapped files for inter-process communication.

**Protocol Format:**
```
┌───────────────┬─────────────────────────────────┐
│  Header (8B)  │        JSON Data                │
│  Data Size    │   (UTF-8 Encoded Model Dict)    │
└───────────────┴─────────────────────────────────┘
```

**Key Parameters:**
- Header size: 8 bytes (unsigned long long, little-endian)
- Maximum model size: 100 MB
- File location: System temp directory
- File naming: `hb_model_{name}.mmap`

### 5.2 SharedMemoryManager Class

**Location**: `tools/shared_memory.py`

```python
class SharedMemoryManager:
    def write_model(self, model_dict: dict, create: bool = True) -> bool:
        """Write model to shared memory"""
        
    def read_model(self) -> Optional[dict]:
        """Read model from shared memory"""
        
    def clear(self):
        """Clear shared memory"""
        
    def close(self):
        """Close and cleanup shared memory"""
```

### 5.3 Grasshopper Workflow

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Honeybee Model │      │  HB-MCP Writer  │      │  Shared Memory  │
│   (Grasshopper) │ ───► │                 │ ───► │   (.mmap file)  │
└─────────────────┘      └─────────────────┘      └────────┬────────┘
                                                           │
                                                           ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Honeybee Model │      │  HB-MCP Reader  │      │    AI IDE +     │
│   (Modified)    │ ◄─── │                 │ ◄─── │  Honeybee-MCP   │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

**Operation Steps:**

1. **Grasshopper → AI IDE**
   ```python
   # Grasshopper side: Use HB-MCP Writer component to write model
   # AI IDE side:
   load_model_from_shared_memory()  # Or load_model() for auto-detection
   ```

2. **AI IDE → Grasshopper**
   ```python
   # AI IDE side:
   save_model_to_shared_memory()
   # Grasshopper side: Use HB-MCP Reader component to read model
   ```

### 5.4 Cache Management

The system automatically manages shared memory cache:

- Automatically cleans old cache when loading models (keeps most recent 5 files)
- Removes cache files older than 24 hours
- Manual cleanup: `cleanup_cache` tool

---

## 6. Version Control System

### 6.1 Automatic Version Tracking

The version control system automatically records versions at:

- Model loading
- Model saving
- Manual `save_version` call

**Version Limit:** Maximum 10 versions per model (implemented using deque)

### 6.2 Version Control Tools

| Tool Name | Description |
|---------|---------|
| `save_version` | Manually save version snapshot |
| `list_model_versions` | List all versions of a model |
| `load_model_version` | Load a specific version |
| `undo_last_change` | Undo to previous version |

### 6.3 Version Data Structure

```python
version_data = {
    "version_id": "001",           # Version number (3-digit padded)
    "timestamp": "2024-01-15 14:30:00",
    "description": "Added windows", # Optional description
    "model_dict": {...},           # Complete model dictionary
    "rooms_count": 5,
    "outdoor_shades_count": 2
}
```

### 6.4 Usage Examples

```python
# View version history
list_model_versions("MyModel")
# Returns: {"versions": [{"version": "003", ...}, {"version": "002", ...}, ...]}

# Undo last change
undo_last_change("MyModel")
# Returns: {"success": True, "version_id": "002", "model_dict": {...}}

# Load specific version
load_model_version("MyModel", "001")
```

---

## 7. Skills System

### 7.1 Skills Overview

The skills system provides structured workflow guidance for AI Agents. Each skill corresponds to a type of operation scenario.

**Skills Directory**: `agent/skills/`

### 7.2 Available Skills

| Skill Name | Trigger Scenario | Main Tools |
|---------|---------|---------|
| `honeybee-model-loader` | Load model | `load_model` |
| `honeybee-model-saver` | Save model | `save_model` |
| `honeybee-query` | Query model info | `query_model`, `query_room`, etc. |
| `honeybee-model-editor` | Edit model | `remove_all_*` |
| `honeybee-aperture-adder` | Add apertures | `add_apertures_by_*` |
| `honeybee-aperture-remover` | Remove apertures | `remove_all_apertures` |
| `honeybee-louver-adder` | Add louvers | `add_louvers*` |
| `honeybee-shade-remover` | Remove shades | `remove_all_shades` |
| `honeybee-door-editor` | Edit doors | Door-related tools |
| `honeybee-apply-properties` | Apply properties | `apply_*` |
| `honeybee-search-lib` | Search library | `search_properties` |
| `honeybee-grasshopper-sync` | Grasshopper sync | Shared memory tools |
| `honeybee-version-control` | Version control | `save_version`, `undo_last_change` |

### 7.3 Skill File Format

Each skill contains a `SKILL.md` file with the following format:

```markdown
---
name: "skill-name"
description: "Skill description for AI to understand when to invoke"
---

# Skill Title

## Tools
### tool_name
**Args:** ...
**Returns:** ...

## Workflow
1. Step 1
2. Step 2

## Notes
- Important notes
```

---

## 8. Workflow Guide

### 8.1 Standard Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                     Standard Workflow                        │
├─────────────────────────────────────────────────────────────┤
│  1. LOAD MODEL                                              │
│     └─► load_model() / load_model_from_shared_memory()      │
│                                                              │
│  2. QUERY MODEL (Optional)                                  │
│     └─► query_model() / query_room() / query_faces()        │
│                                                              │
│  3. SEARCH PROPERTIES (Optional)                            │
│     └─► search_properties()                                 │
│                                                              │
│  4. EDIT MODEL                                              │
│     └─► add_* / remove_* / apply_*                          │
│                                                              │
│  5. VERIFY CHANGES                                          │
│     └─► query_model() to confirm                            │
│                                                              │
│  6. SAVE MODEL                                              │
│     └─► save_model() / save_model_to_shared_memory()        │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Grasshopper Collaboration Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                  Grasshopper Workflow                        │
├─────────────────────────────────────────────────────────────┤
│  Grasshopper Side:                                          │
│  1. Create Honeybee Model                                   │
│  2. Connect to HB-MCP Writer                                │
│  3. Set _write=True to export to shared memory              │
│                                                              │
│  AI IDE Side:                                               │
│  4. load_model() - auto-detects from shared memory          │
│  5. Modify model using MCP tools                            │
│  6. save_model_to_shared_memory()                           │
│                                                              │
│  Grasshopper Side:                                          │
│  7. HB-MCP Reader reads modified model                      │
│  8. Continue design workflow                                │
└─────────────────────────────────────────────────────────────┘
```

### 8.3 Error Recovery Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                  Error Recovery Workflow                     │
├─────────────────────────────────────────────────────────────┤
│  1. undo_last_change() - Restore previous version           │
│                                                              │
│  2. If undo unavailable:                                    │
│     └─► list_model_versions()                               │
│     └─► load_model_version(version_id)                      │
│                                                              │
│  3. Re-apply changes carefully                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Best Practices

### 9.1 Model Loading Best Practices

```python
# Recommended: Let the system auto-detect
load_model()

# If specific file is needed
load_model(hb_file="/path/to/model.hbjson")

# If geometry cleanup is needed
load_model(cleanup_irrational=True)

# Load latest Grasshopper model
load_model("latest")
```

### 9.2 Query Best Practices

```python
# Get overview first
query_model(rooms=True, floor_area=True, identifier=True, display_name=True)

# Then query detailed information
query_faces(face_identifiers, area=True, aperture_ratio=True)

# Use return_count to reduce data volume
query_model(apertures=True, return_count=True)
```

### 9.3 Editing Best Practices

```python
# Query and confirm before editing
faces = query_model(faces=True)["faces"]
query_faces(faces, area=True, type=True)

# Execute edit
add_apertures_by_ratio(face_identifiers=faces, ratio=0.4)

# Verify after editing
query_faces(faces, aperture_ratio=True)
```

### 9.4 Property Application Best Practices

```python
# 1. Search available properties first
search_properties(category="construction_sets", keywords=["office"])

# 2. Apply to model
apply_room_attributes(construction_set_identifier="Office_Construction_Set")

# 3. Verify application result
query_room(general_properties=True)
```

### 9.5 HVAC Application Best Practices

```python
# 1. View available options
apply_hvac(system_category="AllAir", list_options=True)

# 2. Apply system
apply_hvac(
    system_category="AllAir",
    system_type="VAV",
    vintage="ASHRAE_2019",
    sensible_heat_recovery=0.7
)

# 3. Verify
query_room(hvac_properties=True)
```

### 9.6 Orientation-Based Property Application

When multiple constructions/modifiers are provided, the system assigns by orientation:

```python
# 1 item: Apply to all
apply_window_attributes(construction_identifiers=["DoubleGlazed"])

# 2 items: North, South
apply_window_attributes(construction_identifiers=["NorthGlazing", "SouthGlazing"])

# 4 items: North, East, South, West
apply_window_attributes(construction_identifiers=["N", "E", "S", "W"])

# 8 items: N, NE, E, SE, S, SW, W, NW
apply_window_attributes(construction_identifiers=["N", "NE", "E", "SE", "S", "SW", "W", "NW"])
```

---

## 10. Common Task Examples

### 10.1 Add Windows to Exterior Walls

```python
# Step 1: Load model
load_model()

# Step 2: Query exterior walls
model_info = query_model(rooms=True)
faces_info = query_faces(
    query_model(faces=True)["faces"],
    type=True,
    boundary_condition=True
)
exterior_walls = [f for f, info in faces_info.items() 
                  if info["type"] == "Wall" and info["boundary_condition"] == "Outdoors"]

# Step 3: Add windows (40% WWR)
add_apertures_by_ratio(face_identifiers=exterior_walls, ratio=0.4)

# Step 4: Verify
query_faces(exterior_walls, aperture_ratio=True)

# Step 5: Save
save_model_to_shared_memory()
```

### 10.2 Add Louver Shades

```python
# Step 1: Query apertures
apertures = query_model(apertures=True)["apertures"]

# Step 2: Add louvers (5 pieces, 0.5m depth)
add_louvers_by_count(
    aperture_identifiers=apertures,
    louver_count=5,
    depth=0.5
)

# Step 3: Verify
query_shades(
    query_model(outdoor_shades=True)["outdoor_shades"],
    area=True
)
```

### 10.3 Apply Building Properties

```python
# Step 1: Search program types
programs = search_properties(category="program_types", building_program="Office")
# Returns: ["Office_Open", "Office_Enclosed", "Office_Meeting", ...]

# Step 2: Apply program type
apply_room_attributes(program_type_identifier="Office_Open")

# Step 3: Apply HVAC
apply_hvac(system_category="Ideal")

# Step 4: Verify
query_room(general_properties=True, hvac_properties=True)
```

### 10.4 Remove Specific Shade Types

```python
# Step 1: Query all shades
shades_info = query_model(shades=True, shade_meshes=True)

# Step 2: If both types exist, ask user
if shades_info["shades"] and shades_info["shade_meshes"]:
    # Ask user which type to remove
    pass

# Step 3: Remove
remove_all_shades()  # Remove all
# Or
remove_all_shades(shade_mesh_ids=["Tree_1", "Building_2"])  # Remove specific ShadeMesh only
```

---

## 11. Error Handling

### 11.1 Common Error Types

| Error Type | Cause | Solution |
|---------|------|---------|
| `No model loaded` | Model not loaded | Call `load_model()` first |
| `Model not found` | Incorrect file path | Check if path is correct |
| `Invalid identifier` | Identifier doesn't exist | Query first to get correct identifiers |
| `Geometry error` | Invalid geometry data | Use `cleanup_irrational=True` |
| `Shared memory error` | Shared memory issue | Try `clear_shared_memory_model()` |

### 11.2 Error Return Format

```python
{
    "success": False,
    "error": "Error message here",
    "hint": "Suggested action to resolve the error"
}
```

### 11.3 Error Recovery Strategy

```python
# 1. Check return value
result = some_tool()
if not result.get("success"):
    print(f"Error: {result.get('error')}")
    if result.get("hint"):
        print(f"Hint: {result.get('hint')}")

# 2. Use version control to recover
if critical_error:
    undo_last_change(model_name)

# 3. Reload model
load_model_from_dict(version_data["model_dict"])
```

---

## 12. Code Standards

### 12.1 Tool Definition Standard

```python
@mcp.tool()
def tool_name(param1: type, param2: type = default) -> dict:
    """
    Brief description of the tool.
    
    Detailed description with any important notes.
    
    Args:
        param1: Description of parameter 1.
        param2: Description of parameter 2.
    
    Returns:
        Dictionary with results including success status.
    """
    # 1. Check model state
    if manager.model is None:
        return {
            "success": False,
            "message": "No model loaded."
        }
    
    # 2. Execute operation
    try:
        # ... operation code ...
        return {
            "success": True,
            "message": "Operation completed.",
            # other return data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### 12.2 Return Value Standard

All tools should return a dictionary containing:

```python
{
    "success": bool,      # Required: whether operation succeeded
    "message": str,       # Optional: status message
    "error": str,         # On failure: error message
    "hint": str,          # On failure: resolution suggestion
    # ... other data fields
}
```

### 12.3 Naming Conventions

- **Tool Functions**: `snake_case` (e.g., `add_apertures_by_ratio`)
- **Parameters**: `snake_case` (e.g., `face_identifiers`)
- **Class Names**: `PascalCase` (e.g., `Model_Manager`, `SharedMemoryManager`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_VERSIONS`, `HEADER_SIZE`)

### 12.4 Docstring Standard

```python
"""
Brief one-line description.

Extended description with more details about the tool's behavior,
important notes, and usage guidelines.

Args:
    param1 (type): Description. Default: value.
    param2 (type): Description. Default: value.

Returns:
    dict: Description of return value structure.
"""
```

---

## Appendix A: HVAC System Types Reference

### A.1 System Categories

| Category | Description | Typical Systems |
|------|------|---------|
| Ideal | Ideal Air System | IdealAirSystem |
| AllAir | All-Air Systems | VAV, PVAV, PSZ-AC, PTAC |
| DOAS | Dedicated Outdoor Air Systems | FCUwithDOAS, RadiantwithDOAS |
| HeatCool | Heating and Cooling Systems | Baseboard, Radiant, VRF, WSHP |
| SHW | Service Hot Water Systems | GasWaterHeater, ElectricWaterHeater |

### A.2 Standard Vintages

- ASHRAE_2004, ASHRAE_2007, ASHRAE_2010, ASHRAE_2013, ASHRAE_2016, ASHRAE_2019
- DOE_Ref_1980-2004, DOE_Ref_2004, DOE_Ref_2007, DOE_Ref_2010, DOE_Ref_2013

---

## Appendix B: Honeybee Model Element Hierarchy

```
Model
├── rooms[]                    # Room list
│   ├── faces[]               # Face list
│   │   ├── apertures[]       # Aperture list
│   │   │   ├── indoor_shades[]   # Indoor shades
│   │   │   └── outdoor_shades[]  # Outdoor shades
│   │   ├── doors[]           # Door list
│   │   │   ├── indoor_shades[]
│   │   │   └── outdoor_shades[]
│   │   ├── indoor_shades[]   # Face indoor shades
│   │   └── outdoor_shades[]  # Face outdoor shades
│   └── indoor_shades[]       # Room indoor shades
│
├── orphaned_faces[]          # Orphaned faces
├── orphaned_apertures[]      # Orphaned apertures
├── orphaned_doors[]          # Orphaned doors
├── outdoor_shades[]          # Outdoor shades (attached)
├── indoor_shades[]           # Indoor shades (attached)
└── shade_meshes[]            # Shade meshes (independent geometry)
```

---

## Appendix C: Quick Reference Card

### Load Model
```python
load_model()                          # Auto-detect
load_model("latest")                  # Latest GH model
load_model("/path/to/file.hbjson")    # From file
```

### Query Model
```python
query_model(rooms=True, floor_area=True)
query_faces(["Face_1"], area=True, aperture_ratio=True)
query_room(["Room_1"], hvac_properties=True)
```

### Add Windows
```python
add_apertures_by_ratio(faces, ratio=0.4)
add_apertures_by_width_height(faces, width=2, height=1.5)
```

### Add Shades
```python
add_louvers_by_count(apertures, louver_count=5, depth=0.5)
add_louvers_by_distance_between(apertures, distance=0.3, depth=0.5)
```

### Apply Properties
```python
apply_room_attributes(program_type_identifier="Office_Open")
apply_hvac(system_category="Ideal")
apply_window_attributes(construction_identifiers=["DoubleGlazed"])
```

### Version Control
```python
save_version(description="Before major changes")
list_model_versions("MyModel")
undo_last_change("MyModel")
```

---

*Document Version: 1.0*
*Last Updated: 2026*
*Applicable to Honeybee-MCP beta version*
