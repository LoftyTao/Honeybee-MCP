---
name: "honeybee-grasshopper-sync"
description: "Synchronizes models between AI IDE and Grasshopper via shared memory. Invoke when user wants to exchange models with Grasshopper or check connection status."
---

# Honeybee Grasshopper Sync

This skill manages the synchronization between AI IDE and Grasshopper via shared memory.

## Tools

### load_model_from_shared_memory

Load a Honeybee model from shared memory.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | "hb_model_shared" | Shared memory name (must match the name used in Grasshopper). |
| `cleanup_irrational` | boolean | False | Boolean to clean irrational geometry from the model. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the model was loaded successfully |
| `message` | str | Status message |
| `display_name` | str | Model display name |
| `floor_area` | float | Total floor area in m² |
| `rooms_count` | int | Number of rooms in the model |
| `outdoor_shades_count` | int | Number of outdoor shades |
| `writer_signal` | bool | True if model was written by Grasshopper Writer |
| `cleared` | bool | True if clear signal was detected |
| `error` | str | Error message if loading failed |

**Example:**
```python
load_model_from_shared_memory("my_model")
load_model_from_shared_memory()  # Uses default name
```

---

### save_model_to_shared_memory

Save the current model to shared memory.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | "hb_model_shared" | Shared memory name (must match the name used in Grasshopper). |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the model was saved successfully |
| `message` | str | Status message with file size |
| `display_name` | str | Model display name |
| `rooms_count` | int | Number of rooms in the model |
| `hint` | str | Instructions for reading in Grasshopper |
| `error` | str | Error message if saving failed |

**Example:**
```python
save_model_to_shared_memory("my_model")
save_model_to_shared_memory()  # Uses default name
```

---

### check_shared_memory_status

Check if there is a model in shared memory.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | "hb_model_shared" | Shared memory name to check. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `exists` | bool | Whether shared memory exists |
| `signal_type` | str | "clear", "write", or None |
| `size_bytes` | int | Size of data in bytes (if model exists) |
| `size_kb` | float | Size in kilobytes |
| `size_mb` | float | Size in megabytes |
| `name` | str | Shared memory name |
| `path` | str | Full path to the memory-mapped file |
| `writer_timestamp` | str | Timestamp when model was written (for write signal) |
| `model_name` | str | Model name (for clear signal) |
| `message` | str | Status message |
| `error` | str | Error message if check failed |

**Example:**
```python
check_shared_memory_status("my_model")
check_shared_memory_status()  # Uses default name
```

---

### clear_shared_memory_model

Clear and remove the shared memory segment.

**Args:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | "hb_model_shared" | Shared memory name to clear. |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether the shared memory was cleared |
| `message` | str | Status message |
| `error` | str | Error message if clearing failed |

**Example:**
```python
clear_shared_memory_model("my_model")
clear_shared_memory_model()  # Uses default name
```

---

### cleanup_shared_memory_cache

Clean up old shared memory cache files.

**Args:**
None

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether cleanup was successful |
| `kept_files` | int | Number of files kept |
| `removed_files` | int | Number of files removed |
| `removed_details` | list | Details of removed files (name, age, size) |
| `message` | str | Status message |
| `error` | str | Error message if cleanup failed |

**Example:**
```python
cleanup_shared_memory_cache()
```

## Synchronization Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AI IDE ↔ Grasshopper Sync                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   GRASSHOPPER                      AI IDE                          │
│   ───────────                      ───────                         │
│                                                                     │
│   ┌─────────────┐                  ┌─────────────┐                 │
│   │ HB Writer   │ ───write──────▶  │ load_model  │                 │
│   │ Component   │                  │             │                 │
│   └─────────────┘                  └─────────────┘                 │
│                                          │                         │
│                                          ▼                         │
│                                   ┌─────────────┐                  │
│                                   │ Edit Model  │                  │
│                                   │ (add/remove)│                  │
│                                   └─────────────┘                  │
│                                          │                         │
│                                          ▼                         │
│   ┌─────────────┐                  ┌─────────────┐                 │
│   │ HB Reader   │ ◀───write──────  │ save_model  │                 │
│   │ Component   │                  │ _to_shared  │                 │
│   └─────────────┘                  └─────────────┘                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Typical Workflow

### From Grasshopper to AI IDE
```
1. In Grasshopper: Connect model to HB_Model_SharedMemory_Writer
2. In AI IDE: load_model()  # Auto-detects Grasshopper model
3. Edit model as needed
   Note: All edits are automatically saved back to shared memory!
4. (Optional) save_model_to_shared_memory() - for backup or different name
5. In Grasshopper: HB_Model_SharedMemory_Reader reads the result
```

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
When auto-save triggers, editing tools return an additional `auto_save` field:
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

## Shared Memory Names

- Default name: `"hb_model_shared"`
- Custom names supported for multiple models
- Use same name for Writer (GH) and Reader (AI IDE)

## Signal Detection

The sync detects special signals:
- **Write signal**: Grasshopper Writer has written new model
- **Clear signal**: Grasshopper Reader has cleared preview

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No model found" | Run HB Writer in Grasshopper first |
| "Model not updating" | Check shared memory name matches |
| "Memory full" | Run `cleanup_shared_memory_cache()` |
| "Old model loading" | Check for multiple .mmap files |

## Notes

- Shared memory uses memory-mapped files (.mmap)
- Files stored in temp directory
- Auto-cleanup keeps only 5 most recent files
- Files older than 24 hours are removed
- Works with both Rhino 7 (IronPython) and Rhino 8 (Python 3)
