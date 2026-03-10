---
name: "honeybee-search-lib"
description: "Use when a task requires finding valid Honeybee Energy or Radiance identifiers before applying properties or creating reusable resources."
---

# Honeybee Search Library

## Use This Skill When

- The exact identifier is unknown
- The user asks "what options do I have?"
- An `apply` or `add` call would otherwise require guessing

## Tool

### `search_properties`
**Args**
- `category: str`
- `keywords: list | None = None`
- `vintage: str | None = None`
- `climate_zone: str | None = None`
- `construction_type: str | None = None`
- `building_program: str | None = None`
- `exact_match: bool = False`

**Returns**
- `status: str`
- `category: str`
- `results: list | dict`
- `count` or `total_count` when relevant

## Available Categories

| Category | Description |
|----------|-------------|
| `Construction` | Opaque, window, and shade constructions from ASHRAE/NECB libraries |
| `ConstructionSet` | Climate-zone-specific construction sets (requires `climate_zone`) |
| `ProgramType` | Building program types (Office, Apartment, etc.) |
| `Schedule` | Energy schedules (library + model + session resources) |
| `ScheduleTypeLimit` | Schedule type limits (library + model + session resources) |
| `Modifier` | Radiance modifiers (library + model + session resources) |
| `ModifierSet` | Radiance modifier sets (library + model + session resources) |

## Category-Specific Return Structures

### `Construction`
Returns a dict with keys:
- `opaque` — List of opaque construction identifiers
- `window` — List of window construction identifiers
- `shade` — List of shade construction identifiers

### `ConstructionSet`
Returns a list of generated identifiers. Requires `climate_zone`.
Common parameters: `vintage` (e.g. `"2019"`), `construction_type` (e.g. `"SteelFramed"`, `"WoodFramed"`, `"Mass"`).

### `ProgramType`
Returns a flat list of program type identifiers. Use `building_program` to filter (e.g. `"Office"`, `"MidriseApartment"`, `"Hospital"`).

### `Schedule` / `ScheduleTypeLimit` / `Modifier` / `ModifierSet`
Results may include items from three sources:
- `library` — Built-in Honeybee standards
- `model_resource` — Attached to the current model
- `session_resource` — Created in the current session via `add`

## Examples

### Search constructions
```python
search_properties(category="Construction", keywords=["Concrete"])
search_properties(category="Construction", keywords=["Generic"])
```

### Search construction sets by climate zone
```python
search_properties(
    category="ConstructionSet",
    climate_zone="4A",
    vintage="2019",
    construction_type="SteelFramed"
)
```

### Search program types
```python
search_properties(category="ProgramType", building_program="Office")
search_properties(category="ProgramType", keywords=["Apartment"])
```

### Search schedules and type limits
```python
search_properties(category="Schedule", keywords=["Office"])
search_properties(category="ScheduleTypeLimit", keywords=["Fraction"])
```

### Search Radiance modifiers
```python
search_properties(category="Modifier", keywords=["glass"])
search_properties(category="ModifierSet", keywords=["Generic"])
```

## Search → Apply Workflow

A common pattern is to search first, then apply the found identifier:

```python
# Step 1: Search for a suitable program type
result = search_properties(category="ProgramType", building_program="Office")
program_id = result["results"][0]

# Step 2: Apply to rooms
apply(
    operation="room_attributes",
    target_type="room",
    identifiers=["Room_1", "Room_2"],
    values={"program_type_identifier": program_id}
)

# Step 3: Verify
query(
    target_type="room",
    identifiers=["Room_1"],
    fields=["identifier", "properties.energy.program_type.identifier"]
)
```

## Return Guidance

- Feed exact returned identifiers into `apply` or `add`.
- If the result source is `session_resource` or `model_resource`, prefer that identifier before guessing a library fallback.
- For `ConstructionSet`, use the generated identifier directly rather than expecting a large list.
- Use `keywords` for fuzzy matching; use `exact_match=True` only when the exact name is known.
