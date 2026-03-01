---
name: "honeybee-query"
description: "Queries model properties including rooms, faces, apertures, doors, shades, and energy/radiance attributes. Invoke when user wants to inspect, analyze, or get information about model elements."
---

# Honeybee Query

This skill queries properties and attributes from loaded Honeybee models.

## Tools

### query_model

Query various properties and objects from the loaded model.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `identifier` | bool | False | Return the model identifier string. |
| `display_name` | bool | False | Return the model display name. |
| `rooms` | bool | False | Return room identifiers or count. |
| `faces` | bool | False | Return face identifiers or count. |
| `apertures` | bool | False | Return aperture identifiers or count. |
| `doors` | bool | False | Return door identifiers or count. |
| `shades` | bool | False | Return all shade identifiers or count. |
| `shade_meshes` | bool | False | Return shade mesh identifiers or count. |
| `indoor_shades` | bool | False | Return indoor shade identifiers or count. |
| `outdoor_shades` | bool | False | Return outdoor shade identifiers or count. |
| `orphaned_faces` | bool | False | Return orphaned face identifiers or count. |
| `orphaned_shades` | bool | False | Return orphaned shade identifiers or count. |
| `orphaned_apertures` | bool | False | Return orphaned aperture identifiers or count. |
| `orphaned_doors` | bool | False | Return orphaned door identifiers or count. |
| `stories` | bool | False | Return the list of story names. |
| `volume` | bool | False | Return the total model volume in m³. |
| `floor_area` | bool | False | Return the total floor area in m². |
| `exposed_area` | bool | False | Return the total exposed area in m². |
| `exterior_wall_area` | bool | False | Return the exterior wall area in m². |
| `exterior_roof_area` | bool | False | Return the exterior roof area in m². |
| `exterior_aperture_area` | bool | False | Return the total exterior aperture area in m². |
| `exterior_wall_aperture_area` | bool | False | Return the exterior wall aperture area in m². |
| `exterior_skylight_aperture_area` | bool | False | Return the exterior skylight aperture area in m². |
| `return_count` | bool | False | If True, return counts instead of identifier lists for objects. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| dict | dict | Dictionary containing requested properties. Each property is only included if its corresponding flag is True. |

**Example:**
```python
query_model(identifier=True, display_name=True, rooms=True)
query_model(floor_area=True, volume=True)
query_model(rooms=True, return_count=True)  # Returns count only
```

---

### query_faces

Query various properties for multiple faces.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `face_identifiers` | list | required | List of face identifiers to query. |
| `identifier` | bool | False | Return the face identifier string. |
| `display_name` | bool | False | Return the face display name. |
| `type` | bool | False | Return the face type (Wall, Floor, RoofCeiling, AirBoundary). |
| `boundary_condition` | bool | False | Return the boundary condition. |
| `apertures` | bool | False | Return aperture identifiers or count on this face. |
| `doors` | bool | False | Return door identifiers or count on this face. |
| `area` | bool | False | Return the face area in m². |
| `normal` | bool | False | Return the normal vector [x, y, z]. |
| `center` | bool | False | Return the center point [x, y, z]. |
| `tilt` | bool | False | Return the tilt angle in degrees. |
| `azimuth` | bool | False | Return the azimuth angle in degrees. |
| `aperture_area` | bool | False | Return the total aperture area in m². |
| `aperture_ratio` | bool | False | Return the aperture-to-wall ratio. |
| `energy_properties` | bool | False | Return detailed EnergyPlus properties. |
| `radiance_properties` | bool | False | Return detailed Radiance properties. |
| `return_count` | bool | False | If True, return counts instead of identifier lists. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| dict | dict | Dictionary mapping face identifiers to their queried properties. |

**Example:**
```python
query_faces(["Face_1"], area=True, normal=True)
query_faces(["Face_1", "Face_2"], energy_properties=True)
```

---

### query_room

Query detailed Energy and Radiance attributes for specific rooms.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `room_identifiers` | list | None | List of room IDs to query. If None, queries all rooms. |
| `general_properties` | bool | False | Return general properties (Program, Construction Set, Is Conditioned). |
| `load_properties` | bool | False | Return load density properties (People, Lighting, Equipment, Ventilation, Infiltration). |
| `schedule_properties` | bool | False | Return operation schedules. |
| `setpoint_properties` | bool | False | Return temperature setpoints. |
| `hvac_properties` | bool | False | Return HVAC system details. |
| `radiance_properties` | bool | False | Return Radiance properties. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| dict | dict | Dictionary mapping room identifiers to their queried properties. |

**Example:**
```python
query_room(general_properties=True)  # All rooms, general info
query_room(["Room_1"], load_properties=True, schedule_properties=True)
```

---

### query_apertures

Query various properties for multiple apertures.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `aperture_identifiers` | list | required | List of aperture identifiers to query. |
| `identifier` | bool | False | Return the aperture identifier string. |
| `display_name` | bool | False | Return the aperture display name. |
| `area` | bool | False | Return the aperture area in m². |
| `normal` | bool | False | Return the normal vector [x, y, z]. |
| `is_operable` | bool | False | Return True if aperture can be opened. |
| `is_exterior` | bool | False | Return True if aperture is on an exterior face. |
| `parent` | bool | False | Return the parent face identifier. |
| `tilt` | bool | False | Return the tilt angle in degrees. |
| `azimuth` | bool | False | Return the azimuth angle in degrees. |
| `indoor_shades` | bool | False | Return indoor shade identifiers or count. |
| `outdoor_shades` | bool | False | Return outdoor shade identifiers or count. |
| `return_count` | bool | False | If True, return counts instead of identifier lists. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| dict | dict | Dictionary mapping aperture identifiers to their queried properties. |

**Example:**
```python
query_apertures(["Window_1"], area=True, normal=True)
query_apertures(["Window_1", "Window_2"], is_operable=True)
```

---

### query_doors

Query various properties for multiple doors.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `door_identifiers` | list | required | List of door identifiers to query. |
| `identifier` | bool | False | Return the door identifier string. |
| `display_name` | bool | False | Return the door display name. |
| `is_glass` | bool | False | Return True if door is a glass door. |
| `area` | bool | False | Return the door area in m². |
| `boundary_condition` | bool | False | Return the boundary condition. |
| `return_count` | bool | False | If True, return counts instead of identifier lists. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| dict | dict | Dictionary mapping door identifiers to their queried properties. |

**Example:**
```python
query_doors(["Door_1"], area=True, is_glass=True)
```

---

### query_shades

Query various properties for multiple shades.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `shade_identifiers` | list | required | List of shade identifiers to query. |
| `identifier` | bool | False | Return the shade identifier string. |
| `display_name` | bool | False | Return the shade display name. |
| `is_detached` | bool | False | Return True if shade is orphaned. |
| `is_indoor` | bool | False | Return True if shade is an indoor shade. |
| `parent` | bool | False | Return the direct parent identifier. |
| `area` | bool | False | Return the shade area in m². |
| `normal` | bool | False | Return the normal vector [x, y, z]. |
| `tilt` | bool | False | Return the tilt angle in degrees. |
| `azimuth` | bool | False | Return the azimuth angle in degrees. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| dict | dict | Dictionary mapping shade identifiers to their queried properties. |

**Example:**
```python
query_shades(["Louver_1"], area=True, normal=True)
```

## Notes

- Model must be loaded before querying
- Use `return_count=True` for counts instead of ID lists
- Energy properties require honeybee-energy
- Radiance properties require honeybee-radiance
