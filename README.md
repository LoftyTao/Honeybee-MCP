# Honeybee-MCP(beta)

<img src="src\resource\Honeybee-MCP.png" alt="Honeybee-MCP" width="150">

## What is Honeybee-MCP?

Honeybee-MCP is a sophisticated Model Context Protocol (MCP) server designed to bridge the gap between Large Language Models (LLMs) and the Honeybee ecosystem for building energy modeling (BEM). 

The primary objective of Honeybee-MCP is to provide a seamless integration layer for manipulating HBJSON and HBpkl files within AI-augmented design environments. It abstracts the underlying complexities of the honeybee-core libraries, offering a set of high-level tools that allow an AI to "understand" and "modify" 3D building models. 

## Technical Requirements and Installation

### Prerequisites

To ensure stability and performance, the server requires Python 3.8 or higher. It is built upon the fastmcp framework, which handles the asynchronous communication between the AI IDE and the Python runtime.

### Installation Procedure

**IMPORTANT NOTE**: Due to Pydantic version conflicts between fastMCP and Ladybug/Honeybee packages, please use the provided installation scripts instead of running `pip install -r requirements.txt` directly. The scripts handle the conflict by reinstalling fastMCP with the `--no-deps` flag.

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

We recommend using **uv**, a fast and modern Python package manager that significantly speeds up dependency resolution and installation.

#### Option 1: Using uv (Recommended)

1. Install uv (if not already installed):

```
pip install uv
```

2. Navigate to the project directory:

```
cd path/to/Honeybee-MCP
```

3. Create a virtual environment in the project folder:

```
uv venv
```

4. **Install dependencies using the provided script** (Windows):

```
install.bat
```

Or (Linux/Mac):

```
bash install.sh
```

5. Activate the environment:

Windows:
```
.venv\Scripts\activate
```

Unix/macOS:
```
source .venv/bin/activate
```

#### Option 2: Using traditional pip

1. Navigate to the project directory:

```
cd path/to/Honeybee-MCP
```

2. Create a virtual environment in the project folder:

```
python -m venv venv
```

3. Activate the environment:

Windows:
```
venv\Scripts\activate
```

Unix/macOS:
```
source venv/bin/activate
```

4. **Install dependencies using the provided script** (Windows):

```
install.bat
```

Or (Linux/Mac):

```
bash install.sh
```

**Note**: The installation script will:
- Install all dependencies from requirements.txt
- Reinstall fastMCP with `--no-deps` to resolve Pydantic conflicts

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
        "./venv/Scripts/python.exe",
        "./server.py"
      ],
      "enabled": true
    }
  }
}
```

Note: The paths use relative paths from the project directory. If you're using a different virtual environment location, adjust the Python executable path accordingly.

### Other AI IDEs

Honeybee-MCP is compatible with MCP-enabled IDEs including:

- **VS Code** - Via MCP extensions
- **Cursor** - Built-in MCP support
- **Trae** - Native MCP integration
- **Other AI IDE**

For these IDEs, navigate to the MCP settings panel and add a new server. Configure the command to point to your Python executable (from the virtual environment) and the arguments to include the path to `server.py`.

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
│   ├── hvac_config.json      # HVAC configuration presets
│   └── search_properties_lib.py # Library property search
├── src/                  # Default directory for source files and outputs
│   ├── resource/         # Project resources (images, etc.)
│   │   └── Honeybee-MCP.png
│   └── sample/           # Sample HBJSON files
│       └── Revit_Sample.hbjson
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

| Tool Name | Description |
| :--- | :--- |
| load_model | Load Honeybee model from HBJSON/HBpkl file |
| save_model | Save current model to HBJSON file |
| add_louvers | Add louver shades to apertures |
| add_louvers_by_count | Add louvers with specified count |
| add_louvers_by_distance_between | Add louvers with specified spacing |
| add_aperture_by_width_height | Add rectangular aperture by width/height |
| add_apertures_by_ratio | Add apertures by area ratio |
| add_apertures_by_ratio_rectangle | Add rectangular apertures by ratio |
| add_apertures_by_ratio_gridded | Add gridded apertures by ratio |
| add_apertures_by_width_height_rectangle | Add repeated rectangular apertures |
| remove_face_objects | Remove objects from faces |
| remove_room_shades | Remove shades from rooms |
| remove_all_apertures | Remove all apertures from model |
| remove_all_doors | Remove all doors from model |
| remove_all_shades | Remove all shades from model |
| query_model | Query model information and objects |
| query_rooms | Query room properties |
| query_faces | Query face properties |
| query_apertures | Query aperture properties |
| query_doors | Query door properties |
| query_shades | Query shade properties |
| apply_opaque_attributes | Apply Opaque Constructions (Energy) or Modifiers (Radiance) to faces, doors, or exterior walls |
| apply_window_attributes | Apply Window Constructions (Energy) or Modifiers (Radiance) to apertures, glass doors, or child apertures |
| apply_shade_attributes | Apply Shade Constructions (Energy) or Modifiers (Radiance) to shades or attached objects |
| apply_hvac | Apply HVAC systems (Ideal, AllAir, DOAS, HeatCool, SHW) to rooms with advanced Radiant configuration |
| apply_room_attributes | Apply Construction Set, Modifier Set, Program Type, or conditioning status to rooms |
| search_properties | Search for Constructions, Modifiers, Program Types, and Construction Sets in library |
