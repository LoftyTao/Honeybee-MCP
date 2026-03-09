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

## Category Patterns

### Construction
Returns grouped `opaque`, `window`, and `shade` constructions.

### ConstructionSet
Returns generated identifiers and requires `climate_zone`.

### ProgramType
Returns program identifiers, optionally filtered by `building_program`.

### Schedule / ScheduleTypeLimit
Returns Energy schedule-related identifiers.

Results can include:

- `library`
- `model_resource`
- `session_resource`

### Modifier / ModifierSet
Returns Radiance modifier-related identifiers.

Results can include:

- `library`
- `model_resource`
- `session_resource`

## Examples

```python
search_properties(category="Construction", keywords=["Concrete"])
search_properties(category="ProgramType", building_program="Office")
search_properties(category="Schedule", keywords=["Office"])
search_properties(category="ScheduleTypeLimit", keywords=["Fraction"])
search_properties(category="Modifier", keywords=["glass"])
```

```python
search_properties(
    category="ConstructionSet",
    climate_zone="4A",
    vintage="2019",
    construction_type="SteelFramed"
)
```

## Return Guidance

- Feed exact returned identifiers into `apply` or `add`.
- If the result source is `session_resource` or `model_resource`, prefer that identifier before guessing a library fallback.
- For `ConstructionSet`, use the generated identifier directly rather than expecting a large list.
