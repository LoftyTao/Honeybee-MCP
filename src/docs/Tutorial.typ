#import "@preview/touying:0.6.1": *
#import themes.simple: *

#show: simple-theme.with(aspect-ratio: "16-9")

#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.1": *
#show: codly-init.with()

#focus-slide[
  #grid(
    columns: 2,
      figure(
      image(
        height: 250pt,
        width: 225pt,
        "../resource/Honeybee-MCP.png"
        )
    ),
    align(left)[
      #text(size: 36pt)[*Honeybee-MCP*]

      #text(size: 26pt)[*Using AI Agents to assist in modeling.*]

      #text(size: 24pt)[Lofty Tao  2026.1]
    ]
  )
]

== What Honeybee-MCP ?

- Bridging LLMs and *LBT : Honeybee* ecosystem.

- Provides tools for AI to *Understand Honeybee Models*.

- Enables *Honeybee Model* manipulation in AI Agent.

- *Blurification* instruction modeling driven by LLMs.

== What functions are currently available?

The number of available tools at present is *27* . eg.

- *Model Management Tools*.

- *Query Tools*.

- *Object Editor Tools*.

- *Apply Attributes Tools*.

- *Search Library Tools*.

- ......

== How to use Honeybee-MCP ?

=== Overview

#v(0.5em)

- Clone Honyebe-MCP repository.

- Install AI IDE (e.g. Cursor,Visual Studio Code or Open Code etc.) 

- Configure the MCP service to the IDE.

- Using MCP Server with Prompts-driven AI Agent.

---

=== 1. Clone Honyebe-MCP Repository

#v(0.5em)

Choose the way you like best.eg.

- Git Clone.

- Github Desktop Clone.

- Download ZIP (Suitable for non-developers)
#v(2em)

*Repository link* : #text(fill: blue)[https://github.com/LoftyTao/Honeybee-MCP]

---

=== 2. Install AI IDE

#v(0.5em)

Choose the way you like best.eg.

- Cursor.

- Visual Studio Code.

- OpenCode.

- ......

*OpenCODE link* : #text(fill: blue)[https://opencode.ai/download]

---

=== 3. Configure the MCP service to the IDE

#v(0.5em)

- Open this project in OpenCode

- Tell OpenCode to carry out the following plan.

#text(size: 18pt)[
```Prompts
Build this project following README.md instructions:
Create a virtual environment using UV.
Activate the environment.
Install dependencies using the installation script:
  - Windows: install.bat
  - Linux/Mac: bash install.sh
Create .opencode/opencode.json with MCP configuration
Verify by running python server.py
```
]

== How to Use Honeybee-MCP in an AI IDE

Tell OpenCode :

#text(size: 16pt)[
```Prompts
load src\sample\Revit_Sample.hbjson file.
```
]

It should return something similar:

#text(size: 16pt)[
```Prompts
Successfully loaded the model from src\sample\Revit_Sample.hbjson
Model Summary:
- Display Name: Revit_Sample
- Floor Area: 295.74 m²
- Number of Rooms: 15
- Outdoor Shades: 105
- Orphaned Objects: 0 (faces, shades, apertures, doors)
```
]


== Is it possible to use the complex scene?

It's time to test the AI Agent, Try it！

#text(size: 14pt)[
```Prompts
load src\sample\Revit_Sample.hbjson file.
query all room list and identify bedrooms.
Clean all the Apertures and Doors.
Search for available Program types and apply an appropriate apartment program to all bedrooms.
Add windows to vertical exterior walls of all the bedrooms in proportion.
The proportions of four directions (east, west, south, and north) are 0.35, 0.5, 0.75, and 0.25 respectively.
Critical: Only add windows to faces with type="Wall". Exclude all types of "face" except "wall".
Add louvers to the south-facing windows, and the properties can be customized by you.
Apply PTAC HVAC system to all bedrooms. Important: PTAC belongs to the "AllAir" system category, use system_category="AllAir" and system_type="PTAC".
Check all the modifications of this model and generate a process report.md.
Save the model to the "output" folder in the project folder and name it "demo".
```
]

---

Very prompt and accurate response! *Only use the free model*.

#align(center)[
  #grid(
  columns: (45%,45%),
  grid(
    columns: 1,
    rows: 2,
    image("../resource/Demo_Model-1.png"),
    image("../resource/Demo_Model-2.png"),
  ),
  image("../resource/Complex-prompt.png"),
)
]

#focus-slide[
  #grid(
    columns: 2,
      figure(
    image(
      height: 250pt,
      width: 225pt,
      "../resource/Honeybee-MCP.png"
      )
    ),
    align(left)[
      #text(size: 26pt)[*This for all Ladybug Tools user!*]

      #text(size: 18pt)[*How to contact me?*]

      #text(size: 16pt)[#text(fill: blue)[*Email*: loftytao\@foxmail.com]]

      #text(size: 16pt)[#text(fill: blue)[*Github*: https://github.com/LoftyTao]]
    ]
  )
]