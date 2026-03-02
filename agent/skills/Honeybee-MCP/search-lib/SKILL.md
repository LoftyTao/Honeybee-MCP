---
name: "honeybee-search-lib"
description: "Searches Honeybee libraries for constructions, modifiers, program types, and construction sets. Invoke when user wants to find available properties to apply or browse the library."
---

# Honeybee Search Library

This skill searches Honeybee libraries for available properties.

## Tools

### search_properties

Search for Honeybee properties including Constructions, Modifiers, Program Types, and Construction Sets.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `category` | string | required | Search target category: "Construction", "ConstructionSet", "ProgramType", "Modifier", "ModifierSet". |
| `keywords` | list | None | List of words to filter results. Case-insensitive partial match. |
| `vintage` | string | None | Standard year for code compliance: "ASHRAE_2019", "ASHRAE_2016", "ASHRAE_2013", "ASHRAE_2010", or short form "2019", "2016", etc. |
| `climate_zone` | string | None | ASHRAE climate zone number (1-8). Can include letter suffix like "4A" or just "4". Required for ConstructionSet search. |
| `construction_type` | string | None | Building construction type: "SteelFramed", "WoodFramed", "Mass", "Metal Building". |
| `building_program` | string | None | Building type for ProgramType search: "Office", "School", "Hospital", "Retail", "Residential". |
| `exact_match` | bool | False | If True, keywords are joined and matched as a phrase. If False, keywords are matched individually (OR logic). |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `status` | str | "success" or "error" |
| `category` | str | The search category |
| `results` | list/dict | Matching items or categorized results |
| `count` | int | Number of results (for list results) |
| `message` | str | Error message (if status is "error") |

**Example:**
```python
search_properties(category="Construction", keywords=["Concrete"])
search_properties(category="ConstructionSet", climate_zone="4", vintage="2019")
search_properties(category="ProgramType", building_program="Office")
search_properties(category="Modifier", keywords=["glass"])
```

## Search Categories

### Construction

Search for opaque, window, and shade constructions.

**Returns:**
```python
{
  "status": "success",
  "category": "Construction",
  "results": {
    "opaque": [...],
    "window": [...],
    "shade": [...]
  },
  "total_count": 123
}
```

### ConstructionSet

Generate construction set identifier based on inputs.

**Required Args:**
- `climate_zone`: Climate zone number (1-8)
- `vintage`: Standard year (optional, default: "2019")
- `construction_type`: Building type (optional, default: "SteelFramed")

**Returns:**
```python
{
  "status": "success",
  "category": "ConstructionSet",
  "results": ["2019::ClimateZone4::SteelFramed"],
  "note": "Construction Sets are generated based on inputs..."
}
```

### ProgramType

Search for program types with loads and schedules.

**Args:**
- `building_program`: Filter by building type
- `vintage`: Filter by standard year
- `keywords`: Additional filter keywords

**Returns:**
```python
{
  "status": "success",
  "category": "ProgramType",
  "count": 10,
  "results": ["2019::Office::OpenOffice", ...]
}
```

### Modifier

Search for Radiance material modifiers.

**Returns:**
```python
{
  "status": "success",
  "category": "Modifier",
  "count": 50,
  "results": ["glass_90", "metal_aluminum", ...]
}
```

### ModifierSet

Search for Radiance modifier sets.

**Returns:**
```python
{
  "status": "success",
  "category": "ModifierSet",
  "count": 5,
  "results": [...]
}
```

## Program Type Hierarchy

Program types follow the pattern:
```
{Vintage}::{BuildingProgram}::{RoomProgram}
```

Examples:
- `2019::Office::OpenOffice`
- `2019::Residential::Bedroom`
- `2019::School::Classroom`

## Workflow

```
1. Search for properties: search_properties()
2. Select appropriate identifier
3. Apply to model: apply_*_attributes()
```

## Notes

- Keywords use partial matching (case-insensitive)
- Use `exact_match=True` for phrase matching
- Building programs: Office, Residential, School, Hospital, Retail, etc.
- Always search before applying to verify valid identifiers
