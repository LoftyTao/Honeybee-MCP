# Honeybee-MCP(beta)

<img src="src\resource\Honeybee-MCP.png" alt="Honeybee-MCP" width="150">

Honeybee-MCP is a sophisticated Model Context Protocol (MCP) server designed to bridge the gap between Large Language Models (LLMs) and the Honeybee ecosystem for building energy modeling (BEM). 

The primary objective of Honeybee-MCP is to provide a seamless integration layer for manipulating HBJSON and HBpkl files within AI-augmented design environments. It abstracts the underlying complexities of the honeybee-core libraries, offering a set of high-level tools that allow an AI to "understand" and "modify" 3D building models. 

> **Note:** This MCP server only supports **local deployment**. 

## Documentation

For a comprehensive tutorial on how to use Honeybee-MCP, please refer to the [Tutorial.pdf](src/docs/Tutorial.pdf). 

### Quick Start Guide

1. **Clone the repository** from [GitHub](https://github.com/LoftyTao/Honeybee-MCP).
2. **Install an AI IDE** .(OpenCode, Cursor, VS Code, etc.)
3. **Configure MCP** Automatically build the project through AI Agent.
4. **Use prompts** to interact with your Honeybee models.

## Technical Requirements and Installation

### Prerequisites

To ensure stability and performance, the server requires:

- **Python 3.8 or higher**
- **Ladybug Tools 1.10** (including Ladybug Tools SDK 1.10)

The server is built upon the fastmcp framework, which handles the asynchronous communication between the AI IDE and the Python runtime.

### Installation Procedure

First, clone the repository to your local machine:

**Option 1: Using Git**

```
git clone https://github.com/yourusername/Honeybee-MCP.git
cd Honeybee-MCP
```

**Option 2: Using GitHub Desktop**

Whether you're new to Git or a seasoned user, GitHub Desktop simplifies your development workflow.

1. Download and install [GitHub Desktop](https://github.com/apps/desktop)
2. Open GitHub Desktop and go to `File` > `Clone Repository`
3. Enter the repository URL: `https://github.com/yourusername/Honeybee-MCP.git`
4. Choose a local path and click `Clone`

We recommend using **native Python** for creating virtual environments, which is the standard and most compatible approach.

#### Option 1: Using native Python (Recommended)

1. Navigate to the project directory:

```
cd path/to/Honeybee-MCP
```

2. Create a virtual environment in the project folder:

Windows:
```
python -m venv venv
```

Unix/macOS:
```
python3 -m venv venv
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Activate the environment:

Windows:
```
venv\Scripts\activate
```

Unix/macOS:
```
source venv/bin/activate
```

#### Verification

Execute the server locally to confirm the transport layer is functioning:

```
python server.py
```

## IDE Configuration

### OpenCode Integration

Create or edit the `.opencode/opencode.json` file in your project directory:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "honeybee-mcp": {
      "type": "local",
      "command": [
        //Note: The paths use relative paths from the project directory. If you're using a different virtual environment location, adjust the Python executable path accordingly.
        "./Honeybee-MCP/venv/Scripts/python.exe",
        "./Honeybee-MCP/venv/Scripts/python.exe/server.py"
      ],
      "enabled": true
    }
  }
}
```

### Other AI IDEs

Honeybee-MCP is compatible with MCP-enabled IDEs including:

- **VS Code** - Via MCP extensions
- **Cursor** - Built-in MCP support
- **Trae** - Native MCP integration
- **Other AI IDE**

For these IDEs, navigate to the MCP settings panel and add a new server. Configure the command to point to your Python executable (from the virtual environment) and the arguments to include the path to `server.py`.

## Grasshopper Integration

Honeybee-MCP provides Grasshopper components for real-time model exchange between Grasshopper and AI IDE via shared memory (memory-mapped files).

### Components

Two Grasshopper components are provided:

| Component | File | Description |
|-----------|------|-------------|
| **HB-MCP Writer** | `HB-MCP Writer.ghuser` | Write Honeybee Model to shared memory |
| **HB-MCP Reader** | `HB-MCP Reader.ghuser` | Read Honeybee Model from shared memory (manual & auto modes) |

### Installation

1. **Using .ghuser files (Recommended):**
   - The `.ghuser` files are located in `grasshopper/user_object/`
   - In Grasshopper, go to `File → Special Folders → User Object Folder`
   - Copy `HB-MCP Reader.ghuser` and `HB-MCP Writer.ghuser` to this folder
   - Restart Grasshopper - components will appear under `HB-MCP → 0 :: Mcp` category

2. **Using Python Script component:**
   - Source code is available in `grasshopper/src/`
   - Create a Python Script component in Grasshopper
   - Copy the contents of `HB-MCP Reader.py` or `HB-MCP Writer.py` into the component

### Usage Workflow

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

**Step-by-step:**

1. **Writer Component:**
   - Input: Connect a Honeybee Model to `_model`
   - Input: Set `_write=True` to write to shared memory
   - Output: `name` (auto-derived from model's display_name)

2. **AI IDE:**
   - Use `load_model_from_shared_memory` to load the model
   - Modify the model using MCP tools
   - **Auto-save**: All edits are automatically saved back to shared memory when model is loaded from shared memory
   - (Optional) Use `save_model_to_shared_memory` for manual backup or different names

3. **Reader Component:**
   - Input: Connect `name` from Writer to `_name`
   - Input: Set `_read=True` to read from shared memory
   - Output: Modified Honeybee Model

### Auto-Save Feature

**Important**: When a model is loaded from Grasshopper shared memory, all editing operations automatically save the model back to shared memory. This provides a seamless workflow without requiring manual save calls.

**Auto-save behavior:**
- Automatically triggers after each edit operation
- Saves to the same shared memory name used for loading
- Creates version snapshots for undo capability
- Only applies to models loaded from shared memory

**When to use manual save:**
- Save model from file to shared memory
- Save to a different shared memory name
- Create backups with different names
- Manually control save timing

**Auto-save response:**
When auto-save triggers, editing tools return an additional `auto_save` field in their response:
```python
{
  "success": True,
  "message": "Apertures added successfully",
  "auto_save": {
    "auto_saved": True,
    "message": "Model saved to shared memory successfully",
    "source_name": "hb_model_shared"
  }
}
```

### Component Details

#### HB-MCP Writer

| Input | Type | Description |
|-------|------|-------------|
| `_model` | Model | Honeybee Model object |
| `_write` | Boolean | Set to True to write |

| Output | Type | Description |
|--------|------|-------------|
| `report` | List | Status messages |
| `name` | String | Shared memory name (model display_name) |
| `success` | Boolean | Write success status |

#### HB-MCP Reader

| Input | Type | Description |
|-------|------|-------------|
| `_name` | String | Shared memory name |
| `_read` | Boolean | Set to True for manual read |
| `_interval_` | Integer | Check interval in ms (default: 500) |
| `run_` | Boolean | Set to True for auto-monitoring |
| `clear_` | Boolean | Set to True to clear after reading |

| Output | Type | Description |
|--------|------|-------------|
| `report` | List | Status messages |
| `model` | Model | Honeybee Model object |
| `updated` | Boolean | True when model was just updated (auto mode) |

## Project Architecture

The repository is structured to separate the MCP protocol logic from the Honeybee geometry engines:

```
Honeybee-MCP/
├── server.py              # Main entry point initializing the FastMCP server
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── tools/                # Modular directory containing individual Python scripts
│   ├── __init__.py
│   ├── mcp_context.py    # MCP context management
│   ├── load_model.py     # Model loading utilities
│   ├── save_model.py     # Model saving utilities
│   ├── query_model.py    # Model querying tools
│   ├── query_room.py     # Room property queries
│   ├── query_face.py     # Face property queries
│   ├── query_aperture.py # Aperture property queries
│   ├── query_door.py     # Door property queries
│   ├── query_shade.py    # Shade property queries
│   ├── aperture_editor.py    # Aperture manipulation tools
│   ├── face_editor.py        # Face manipulation tools
│   ├── room_editor.py        # Room manipulation tools
│   ├── model_editor.py       # Model-level editing tools
│   ├── apply_all_face.py     # Apply attributes to faces
│   ├── apply_hvac.py         # HVAC system configuration
│   ├── apply_room.py         # Room-level attribute application
│   ├── shared_memory.py      # Shared memory management
│   ├── shared_memory_tools.py # Shared memory MCP tools
│   ├── version_control.py    # Version control system
│   ├── version_tools.py      # Version control MCP tools
│   ├── hvac_config.json      # HVAC configuration presets
│   └── search_properties_lib.py # Library property search
├── grasshopper/          # Grasshopper integration
│   ├── src/              # Source code for components
│   │   ├── HB-MCP Reader.py
│   │   └── HB-MCP Writer.py
│   └── user_object/      # Compiled .ghuser components
│       ├── HB-MCP Reader.ghuser
│       └── HB-MCP Writer.ghuser
└── src/                  # Default directory for source files and outputs
    ├── docs/             # Documentation
    │   ├── Tutorial.pdf
    │   └── Tutorial.typ
    ├── resource/         # Project resources (images, etc.)
    │   └── Honeybee-MCP.png
    └── sample/           # Sample HBJSON files
        └── Revit_Sample.hbjson
```

## Future Plan

At present, the Honeybee-MCP has relatively complete functions for querying, editing and applying the model. I expect to add more functions in the near future.

- **Agent Skill and Prompts Templates.**
- **More tools for creating and editing Honeybee Properties.**
- **The model exporter and the local preview method**
- **From AI Agent to Simulation Capabilities**
- **More MCP tools from the Ladybug Tools ecosystem**
- ......

## Available Tools

The currently available and tested MCP tools：

### Model I/O

| Tool Name | Description |
| :--- | :--- |
| load_model | Load Honeybee model from HBJSON/HBpkl file (auto-detects Grasshopper shared memory) |
| load_model_from_dict | Load model from dictionary representation |
| load_model_from_shared_memory | Load model from shared memory (Grasshopper) |
| save_model | Save current model to HBJSON file |
| save_model_to_shared_memory | Save model to shared memory (Grasshopper) - optional when using auto-save |
| check_shared_memory_status | Check if model exists in shared memory |
| clear_shared_memory_model | Clear shared memory segment |

**Note**: When a model is loaded from Grasshopper shared memory, all editing operations automatically save changes back to shared memory. Manual save is optional and useful for creating backups or saving to different names.

### Aperture Tools

| Tool Name | Description |
| :--- | :--- |
| add_louvers | Add louver shades to apertures |
| add_louvers_by_count | Add louvers with specified count |
| add_louvers_by_distance_between | Add louvers with specified spacing |
| add_aperture_by_width_height | Add rectangular aperture by width/height |
| add_apertures_by_ratio | Add apertures by area ratio |
| add_apertures_by_ratio_rectangle | Add rectangular apertures by ratio |
| add_apertures_by_ratio_gridded | Add gridded apertures by ratio |
| add_apertures_by_width_height_rectangle | Add repeated rectangular apertures |

### Removal Tools

| Tool Name | Description |
| :--- | :--- |
| remove_face_objects | Remove objects from faces |
| remove_room_shades | Remove shades from rooms |
| remove_all_apertures | Remove all apertures from model |
| remove_all_doors | Remove all doors from model |
| remove_all_shades | Remove all shades from model |

### Query Tools

| Tool Name | Description |
| :--- | :--- |
| query_model | Query model information and objects |
| query_room | Query room properties with detailed Energy/Radiance attributes |
| query_faces | Query face properties |
| query_apertures | Query aperture properties |
| query_doors | Query door properties |
| query_shades | Query shade properties |

### Apply Tools

| Tool Name | Description |
| :--- | :--- |
| apply_opaque_attributes | Apply Opaque Constructions (Energy) or Modifiers (Radiance) to faces, doors, or exterior walls |
| apply_window_attributes | Apply Window Constructions (Energy) or Modifiers (Radiance) to apertures, glass doors, or child apertures |
| apply_shade_attributes | Apply Shade Constructions (Energy) or Modifiers (Radiance) to shades or attached objects |
| apply_hvac | Apply HVAC systems (Ideal, AllAir, DOAS, HeatCool, SHW) to rooms with advanced Radiant configuration |
| apply_room_attributes | Apply Construction Set, Modifier Set, Program Type, or conditioning status to rooms |

### Search Tools

| Tool Name | Description |
| :--- | :--- |
| search_properties | Search for Constructions, Modifiers, Program Types, and Construction Sets in library |

### Version Control Tools

| Tool Name | Description |
| :--- | :--- |
| version_control | Unified version control tool with actions: list, save, load, undo, redo, compare, info, delete, clear, cleanup |

**Note:** Version control is automatic. Every time a model is loaded or saved, a version is automatically recorded. Maximum 10 versions are kept in memory.

**Shared Memory Cache Management:**
- Automatic cleanup when loading models (keeps most recent 5 files)
- Removes cache files older than 24 hours
- Manual cleanup available via `cleanup_cache` tool
