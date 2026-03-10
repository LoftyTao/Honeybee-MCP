<p align="center">
  <img src="src/resource/Honeybee-MCP.png" alt="Honeybee-MCP" width="280"/>
</p>

<h1 align="center">Honeybee-MCP</h1>

<p align="center">
  <b>Bridge LLMs with the Ladybug Tools / Honeybee building-energy-modeling ecosystem via MCP.</b>
</p>

<p align="center">
  <a href="README_ZH.md">中文文档</a> ·
  <a href="https://github.com/LoftyTao/Honeybee-MCP">GitHub</a> ·
  <a href="LICENSE">GPL-3.0</a>
</p>

---

## What is Honeybee-MCP?

Honeybee-MCP is a **Model Context Protocol (MCP) server** built on [FastMCP](https://github.com/jlowin/fastmcp). It exposes the capabilities of the [Ladybug Tools / Honeybee](https://www.ladybug.tools/) ecosystem as structured tool calls, allowing AI agents in any MCP-compatible IDE (Cursor, VS Code + Copilot, OpenCode, etc.) to **understand, query, and manipulate Honeybee building energy models** through natural language.

In short: you describe what you want in plain English, and the AI agent drives Honeybee for you.

<p align="center">
  <img src="src/resource/gh-sample.gif" alt="Grasshopper Integration Demo" width="720"/>
</p>

---

## Tool Suite

Honeybee-MCP currently provides **27 MCP tools** organized into the following modules. Each module is designed as a "bus" -- a single unified entry point that dispatches to specialized service functions behind the scenes.

### Model I/O

`load_model` and `save_model` handle the lifecycle of a Honeybee Model.

- **Loading** supports three sources: local HBJSON / HBpkl files, Grasshopper shared-memory models, and in-memory dictionaries. When no file is specified, the server automatically scans for Grasshopper models first.
- **Saving** exports the current in-memory model to an HBJSON file, with optional pretty-print indentation and property filtering (e.g. energy-only or radiance-only export).

### Query

`query` is the unified read interface. It accepts a `target_type` (e.g. `room`, `face`, `aperture`, `schedule`, `modifier`, `sensor_grid`) and returns the requested `fields` for all matching objects.

Typical use cases:
- List all rooms and their floor areas
- Inspect boundary conditions and aperture ratios on specific faces
- Check which energy schedules or radiance modifiers are currently defined
- Count objects without fetching full data (`output_mode="count"`)

### Add

`add` creates new child objects or resources in the model. Every `add` call specifies an `operation` string that selects the concrete creation logic:

| Operation | What it does |
|-----------|--------------|
| `apertures_by_ratio` | Add windows to faces by wall-to-window ratio |
| `aperture_by_width_height` | Add a single window with exact dimensions |
| `louvers` / `louvers_by_count` | Add louver shading devices to apertures |
| `schedule_type_limit` / `schedule_day` / `schedule_ruleset` | Build energy schedules step by step |
| `modifier` / `modifier_set` | Create radiance modifiers and modifier sets |
| `sensor_grid` / `view` | Add radiance analysis objects |

### Apply

`apply` assigns attributes and resources to existing objects. This is where room programs, HVAC systems, constructions, and load definitions get attached:

| Operation | What it does |
|-----------|--------------|
| `room_attributes` | Set room-level properties: program type, construction set, modifier set |
| `hvac` | Assign HVAC systems (Ideal, PTAC, VAV, etc.) to rooms |
| `opaque_attributes` / `window_attributes` | Set or create constructions on faces and apertures |
| `people` / `lighting` / `electric_equipment` | Define internal loads with custom schedules |
| `setpoint` / `ventilation` | Configure thermal setpoints and outdoor air requirements |
| `modifier` / `modifier_set` | Assign radiance modifiers to faces, apertures, or rooms |

### Remove

`remove` deletes objects with referential-integrity checks. For example, removing a radiance modifier that is still referenced by a face will return a `blocked` response instead of silently breaking the model.

Supported operations: `all_apertures`, `all_doors`, `all_shades`, `face_objects`, `room_shades`, `schedule`, `modifier`, `sensor_grid`, `view`, and more.

### Library Search

`search_properties` searches the Honeybee standards library (ASHRAE, NECB, etc.) for pre-defined constructions, construction sets, program types, and modifier sets. Results can be filtered by vintage, climate zone, construction type, and building program.

### Visualization

`visualization` exports the model or selected objects as a VisualizationSet and optional files (VTK, SVG). Supports custom display options, SVG rendering, and file export to a specified folder.

### Grasshopper Sync

A set of shared-memory tools for real-time bidirectional communication with Rhino/Grasshopper:

- `load_model_from_shared_memory` -- Read a model that Grasshopper has written via HB MCP Writer.
- `save_model_to_shared_memory` -- Push the AI-edited model back for Grasshopper to read via HB MCP Reader.
- `check_shared_memory_status` / `clear_shared_memory_model` -- Inspect or reset the shared-memory channel.
- `cleanup_shared_memory_cache` -- Remove stale cache files.

### Version Control

`version_control` provides an in-memory undo/redo stack, plus named snapshot management:

- `save` / `load` -- Manually create or restore a named snapshot.
- `undo` / `redo` -- Step backward or forward through edit history.
- `compare` -- Diff two snapshots and see what changed (rooms added/removed, properties modified).
- `info` / `delete` / `clear` -- Inspect, remove, or wipe version history.

---

## Grasshopper Components

Two custom GHPython User Objects are included in `grasshopper/`:

- **HB MCP Writer** -- Serializes a Honeybee Model from Grasshopper to shared memory for the MCP server to read.
- **HB MCP Reader** -- Reads a model back from shared memory after the AI agent has finished editing.

Install the `.ghuser` files from `grasshopper/user_objects/` into your Grasshopper User Objects folder (typically `%APPDATA%/Grasshopper/UserObjects/`). The shared-memory transport uses memory-mapped files, so both Grasshopper and the MCP server must run on the same machine.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/LoftyTao/Honeybee-MCP.git
cd Honeybee-MCP
```

### 2. Set up with AI assistance (recommended)

Open the project folder in your MCP-compatible IDE (Cursor, VS Code, OpenCode, etc.), then simply tell the AI:

```
Help me set up this project:
create a .venv, activate it, pip install -r requirements.txt,
then create the MCP config file for this IDE.
```

The AI agent will handle virtual environment creation, dependency installation, and MCP configuration automatically. This is the fastest way to get started.

### 3. Manual setup (alternative)

If you prefer to do it yourself:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

Then add the MCP server config to your IDE. The file location depends on the IDE:

- **Cursor** -- `.cursor/mcp.json`
- **VS Code** -- `.vscode/mcp.json`
- **OpenCode** -- `.opencode/opencode.json`

Example configuration:

```json
{
  "mcpServers": {
    "honeybee-mcp": {
      "command": "D:/Projects/Honeybee-MCP/.venv/Scripts/python",
      "args": ["server.py"],
      "cwd": "D:/Projects/Honeybee-MCP"
    }
  }
}
```

### 4. Verify

```bash
python server.py
```

If no errors appear, the MCP server is ready.

---

## Usage Examples

Each example below consists of three parts: **your input** (natural language prompt), **Honeybee-MCP tool results** (JSON returned behind the scenes), and **AI response** (what the agent tells you).

### Example 1 -- Load a model file

**You:**

> load src\sample\Revit_Sample.hbjson file.

**Honeybee-MCP returns:**

```json
{
  "success": true,
  "source": "file",
  "identifier": "Revit_Sample",
  "display_name": "Revit_Sample",
  "rooms": 15,
  "floor_area": 295.74,
  "outdoor_shades": 105,
  "orphaned_objects": 0
}
```

**AI response:**

> Successfully loaded the model from src\sample\Revit_Sample.hbjson.
> - Display Name: Revit_Sample
> - Floor Area: 295.74 m²
> - Number of Rooms: 15
> - Outdoor Shades: 105
> - Orphaned Objects: 0 (faces, shades, apertures, doors)

---

### Example 2 -- Query rooms and check constructions

**You:**

> query all room list and show me their floor areas. Also check what constructions are available for climate zone 5.

**Honeybee-MCP returns** (two tool calls):

```json
// query -- rooms
{
  "success": true,
  "count": 15,
  "data": [
    {"identifier": "Bedroom_1_a3f2c", "display_name": "Bedroom 1", "floor_area": 18.2},
    {"identifier": "Bedroom_2_b7e1d", "display_name": "Bedroom 2", "floor_area": 15.6},
    {"identifier": "LivingRoom_1_c9a4e", "display_name": "Living Room", "floor_area": 32.1},
    ...
  ]
}

// search_properties -- opaque constructions
{
  "success": true,
  "category": "opaque_constructions",
  "results": [
    {"identifier": "Generic Exterior Wall R-19", "vintage": "2019", "climate_zone": "5"},
    {"identifier": "ASHRAE 189.1-2009 ExtWall Mass ClimateZone 5", "vintage": "2009"},
    ...
  ],
  "total": 12
}
```

**AI response:**

> The model has 15 rooms. Two of them appear to be bedrooms based on their display names: "Bedroom 1" (18.2 m²) and "Bedroom 2" (15.6 m²). The rest include living spaces, bathrooms, and utility rooms.
>
> For climate zone 5, there are 12 pre-defined exterior wall constructions in the standards library. The most commonly used one is "Generic Exterior Wall R-19". Let me know which one to apply or what to do next.

---

### Example 3 -- Add windows with directional ratios

**You:**

> Clean all the Apertures and Doors.
> Add windows to vertical exterior walls of all the bedrooms in proportion. The proportions of four directions (east, west, south, and north) are 0.35, 0.5, 0.75, and 0.25 respectively.
> **Critical**: Only add windows to wall faces. Do not touch floors, roofs, or any other face type.

**Honeybee-MCP returns** (multiple tool calls):

```json
// remove -- clear all apertures and doors
{"success": true, "removed_apertures": 24, "removed_doors": 6}

// add -- south-facing walls, ratio 0.75
{"success": true, "added": 3, "ratio": 0.75}

// add -- west-facing walls, ratio 0.5
{"success": true, "added": 2, "ratio": 0.5}

// add -- east-facing walls, ratio 0.35
{"success": true, "added": 2, "ratio": 0.35}

// add -- north-facing walls, ratio 0.25
{"success": true, "added": 2, "ratio": 0.25}
```

**AI response:**

> Cleared all existing apertures (24) and doors (6). Then added windows to the bedroom exterior walls by direction:
> - South: 75% window-to-wall ratio (3 faces)
> - West: 50% (2 faces)
> - East: 35% (2 faces)
> - North: 25% (2 faces)
>
> Only wall-type faces were processed; floor, roof, and other face types were excluded.

---

### Example 4 -- Checkpoint and rollback

**You:**

> save a version first. I want to try something and might need to undo.

**Honeybee-MCP returns:**

```json
{"success": true, "version_id": "v3", "description": "Manual save"}
```

**AI response:**

> Checkpoint saved as version v3. Go ahead with your changes -- you can undo back to this point at any time.

---

### Example 5 -- Complex multi-step workflow

This example demonstrates a complete end-to-end BEM workflow in a single prompt. The AI agent breaks it down into sequential tool calls automatically.

**You:**

> load src\sample\Revit_Sample.hbjson file.
> query all room list and identify bedrooms.
> Clean all the Apertures and Doors.
> Search for available Program types and apply an appropriate apartment program to all bedrooms.
> Add windows to vertical exterior walls of all the bedrooms in proportion. The proportions of four directions (east, west, south, and north) are 0.35, 0.5, 0.75, and 0.25 respectively.
> **Critical**: Only add windows to wall faces. Do not touch floors, roofs, or any other face type.
> Add louvers to the south-facing windows, and the properties can be customized by you.
> Apply a PTAC system to all bedrooms for heating and cooling.
> Check all the modifications of this model and generate a process report.md.
> Save the model to the "output" folder in the project folder and name it "demo".

**Honeybee-MCP processes** (10+ sequential tool calls):

```
1. load_model        --> Loaded Revit_Sample, 15 rooms, 295.74 m²
2. query (rooms)     --> Identified 2 bedrooms by display name
3. remove            --> Cleared all apertures and doors
4. search_properties --> Found matching apartment program types
5. apply (program)   --> Applied apartment program to 2 bedrooms
6. add (apertures)   --> Added directional windows (S:0.75, W:0.5, E:0.35, N:0.25)
7. add (louvers)     --> Added louver shading to south-facing windows
8. apply (hvac)      --> Applied PTAC system to 2 bedrooms
9. query (summary)   --> Collected all modification details
10. save_model       --> Saved as output/demo.hbjson
```

**AI response:**

> All steps completed. Here is the process summary:
>
> 1. **Model loaded** -- Revit_Sample: 15 rooms, 295.74 m² floor area.
> 2. **Bedrooms identified** -- Bedroom 1 (18.2 m²) and Bedroom 2 (15.6 m²).
> 3. **Apertures and doors cleared** -- Removed 24 apertures and 6 doors.
> 4. **Program applied** -- "2019::MidriseApartment::Apartment" assigned to both bedrooms.
> 5. **Windows added** -- South 75%, West 50%, East 35%, North 25%. Only wall-type faces were processed.
> 6. **Louvers added** -- South-facing windows received louver shading (depth 0.15 m, 6 louvers per window).
> 7. **HVAC applied** -- PTAC (AllAir category) assigned to both bedrooms.
> 8. **Model saved** -- output/demo.hbjson
>
> A detailed process report has been saved to report.md.

<p align="center">
  <img src="src/resource/Demo_Model-1.png" alt="Demo result 1" width="380"/>
  <img src="src/resource/Demo_Model-2.png" alt="Demo result 2" width="380"/>
</p>

---

## Project Structure

```
Honeybee-MCP/
├── server.py                    # Entry point
├── tools/
│   ├── mcp_context.py           # FastMCP instance
│   ├── load_model.py            # Model loading (file + shared memory)
│   ├── save_model.py            # Model saving (HBJSON export)
│   ├── operations/              # add / apply / query / remove buses
│   ├── library/                 # Standards library search
│   ├── visualization/           # VTK / SVG export
│   ├── sync/                    # Grasshopper shared-memory bridge
│   ├── versioning/              # Undo / redo / version snapshots
│   └── state/                   # In-memory model state manager
├── grasshopper/
│   ├── src/                     # GHPython source (Reader / Writer)
│   └── user_objects/            # Compiled .ghuser components
├── src/
│   ├── docs/                    # Tutorial slides, workflow docs
│   ├── resource/                # Images and demo assets
│   └── sample/                  # Sample HBJSON model
├── requirements.txt
└── LICENSE                      # GPL-3.0
```

---

## Requirements

- Python 3.10+
- Core: `honeybee-core`, `honeybee-energy`, `honeybee-radiance`, `ladybug-core`, `ladybug-geometry`, `ladybug-vtk`
- MCP runtime: `fastmcp >= 3.1.0`
- Visualization: `vtk >= 9.6.0`

See [requirements.txt](requirements.txt) for the full pinned dependency list.

---

## Documentation

| Document | Description |
|----------|-------------|
| [Tutorial (PDF)](src/docs/Tutorial.pdf) | Slide deck: setup, basic & advanced usage |
| [Resource Workflows](src/docs/Resource_Workflows.md) | End-to-end examples: Energy schedules, constructions, Radiance modifiers, sensor grids |

---

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

---

## Contact

- **Author**: Lofty Tao
- **Email**: loftytao@foxmail.com
- **GitHub**: [https://github.com/LoftyTao](https://github.com/LoftyTao)
