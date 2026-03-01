# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
#
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Write a Honeybee Model to shared memory for MCP interaction.
-
This component enables real-time model exchange between Grasshopper and AI IDE
via memory-mapped files. The shared memory name is automatically derived from
the model's display_name.

    Args:
        _model: A Honeybee Model object to be written to shared memory.
        _write: Set to "True" to write the model to shared memory.

    Returns:
        report: Reports, errors, warnings, etc.
        name: The shared memory name used (derived from model display_name).
        success: True if the model was written successfully.
"""

ghenv.Component.Name = 'HB-MCP Writer'
ghenv.Component.NickName = 'MCPWriter'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'HB-MCP'
ghenv.Component.SubCategory = '0 :: Mcp'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import json
import struct
import mmap
import os
import tempfile

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


MAP_NAME_PREFIX = "hb_model_"
HEADER_SIZE = 8
MAX_SIZE = 100 * 1024 * 1024


def get_map_path(name):
    """Get the file path for memory-mapped file."""
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, MAP_NAME_PREFIX + name + ".mmap")


def get_model_dict(model):
    """Extract dictionary from Honeybee Model object."""
    if model is None:
        return None, "No model provided"
    
    if hasattr(model, 'to_dict'):
        try:
            model_dict = model.to_dict()
            return model_dict, "Model converted via to_dict()"
        except Exception as e:
            return None, "Failed to convert model: {}".format(str(e))
    
    return None, "Unknown model type: {}".format(type(model))


def get_model_name(model):
    """Get the identifier from Honeybee Model object (stable, unique)."""
    if model is None:
        return None
    
    if hasattr(model, 'identifier'):
        return model.identifier
    
    return "unnamed_model"


def write_to_mmap(model_dict, name):
    """Write model dictionary to memory-mapped file."""
    try:
        from datetime import datetime
        
        model_dict["_writer_signal"] = {
            "written": True,
            "timestamp": datetime.now().isoformat()
        }
        
        json_data = json.dumps(model_dict, ensure_ascii=False)
        json_bytes = json_data.encode('utf-8')
        data_size = len(json_bytes)
        total_size = HEADER_SIZE + data_size
        
        if total_size > MAX_SIZE:
            return False, "Model too large: {} bytes (max: {})".format(total_size, MAX_SIZE)
        
        map_path = get_map_path(name)
        
        with open(map_path, 'wb') as f:
            f.write(b'\x00' * total_size)
        
        with open(map_path, 'r+b') as f:
            mm = mmap.mmap(f.fileno(), total_size)
            
            header = struct.pack('<Q', data_size)
            mm[:HEADER_SIZE] = header
            mm[HEADER_SIZE:total_size] = json_bytes
            
            mm.flush()
            mm.close()
        
        return True, "Model written to shared memory '{}'".format(name)
        
    except Exception as e:
        return False, "Error: {}".format(str(e))


# Initialize outputs
report = []
name = None
success = False

if all_required_inputs(ghenv.Component) and _write:
    model_name = get_model_name(_model)
    name = model_name
    
    model_dict, msg = get_model_dict(_model)
    
    if model_dict is not None:
        success, msg = write_to_mmap(model_dict, model_name)
        report.append(msg)
        
        if not success:
            give_warning(ghenv.Component, msg)
    else:
        report.append(msg)
        give_warning(ghenv.Component, msg)
else:
    if not _write:
        report.append("Set _write=True to write model to shared memory")
    if _model is None:
        report.append("Connect a Honeybee Model to _model input")
