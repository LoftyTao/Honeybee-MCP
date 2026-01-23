# Honeybee-MCP(beta)

Honeybee-MCP is a sophisticated Model Context Protocol (MCP) server designed to bridge the gap between Large Language Models (LLMs) and the Honeybee ecosystem for building energy modeling (BEM). 

## Project Overview

The primary objective of Honeybee-MCP is to provide a seamless integration layer for manipulating HBJSON and HBpkl files within AI-augmented design environments. It abstracts the underlying complexities of the honeybee-core libraries, offering a set of high-level tools that allow an AI to "understand" and "modify" 3D building models. 

## Technical Requirements and Installation

### Prerequisites

To ensure stability and performance, the server requires Python 3.8 or higher. It is built upon the fastmcp framework, which handles the asynchronous communication between the AI IDE and the Python runtime.

### Installation Procedure

The installation process follows standard Pythonic practices to ensure environment isolation:

Environment Setup: Initialize a virtual environment to manage dependencies:

```
python -m venv venv
```

Activation: Activate the environment based on your operating system:

Windows:
```
venv\Scripts\activate
```

Unix/macOS: 
```
source venv/bin/activate
```

Dependency Installation: Install the core libraries and geometry engines:

```
pip install -r requirements.txt
```

Verification: Execute the server locally to confirm the transport layer is functioning:

```
python server.py
```
## IDE Configuration

### Claude Desktop Integration

Integrating Honeybee-MCP into an AI-powered IDE requires defining the server's entry point in the respective configuration file.

```json
{
  "mcpServers": {
    "honeybee": {
      "command": "python",
      "args": ["C:\\path\\to\\Honeybee-MCP\\server.py"],
      "cwd": "C:\\path\\to\\Honeybee-MCP"
    }
  }
}
```

### Cursor IDE or VS Code

For IDEs like Cursor or VS Code (via MCP extensions), navigate to the MCP settings panel and add a new server. Ensure the Command points to your Python executable and the Arguments include the absolute path to server.py. Absolute paths are mandatory to prevent execution errors related to the working directory.

## Project Architecture

The repository is structured to separate the MCP protocol logic from the Honeybee geometry engines:

``server.py``: The main entry point initializing the FastMCP server.

``tools/``: A modular directory containing individual Python scripts for each tool category (e.g., aperture_editor.py, query_model.py).

``src/``: The default directory for storing source HBJSON files and generated outputs.

## Available Tools

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
