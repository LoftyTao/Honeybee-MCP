# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
#
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Write a Honeybee Model to the refactored Honeybee-MCP sync channel.
-
This component writes a Honeybee Model to the memory-mapped cache used by the
refactored Honeybee-MCP sync bus. The written shared name should then be used
by MCP through load_model() or load_model_from_shared_memory().

The shared name is derived from the model identifier, which is the stable and
recommended key on the MCP side.

    Args:
        _model: A Honeybee Model object to be written to shared memory.
        _write: Set to "True" to write the model to shared memory.

    Returns:
        report: Reports, errors, warnings, etc.
        name: The shared name written by this component.
        success: True if the model was written successfully.
"""

ghenv.Component.Name = 'HB MCP Writer'
ghenv.Component.NickName = 'MCPWriter'
ghenv.Component.Message = '1.10.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '4 :: Mcp'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

# Keep this script compatible with Grasshopper GHPython / IronPython syntax.
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
WRITER_SIGNAL_KEY = "_writer_signal"


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


def get_model_name(model, model_dict=None):
    """Get the stable shared name, preferring the serialized identifier."""
    if model_dict and model_dict.get('identifier'):
        return model_dict['identifier']

    if model is None:
        return None
    
    if hasattr(model, 'identifier') and model.identifier:
        return model.identifier

    if hasattr(model, 'display_name') and model.display_name:
        return model.display_name
    
    return "unnamed_model"


def write_to_mmap(model_dict, name):
    """Write model dictionary to memory-mapped file."""
    try:
        from datetime import datetime
        
        payload = dict(model_dict)
        payload[WRITER_SIGNAL_KEY] = {
            "written": True,
            "timestamp": datetime.now().isoformat()
        }
        
        json_data = json.dumps(payload, ensure_ascii=False)
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
    model_dict, msg = get_model_dict(_model)
    model_name = get_model_name(_model, model_dict)
    name = model_name
    
    if model_dict is not None:
        success, msg = write_to_mmap(model_dict, model_name)
        report.append(msg)
        if success:
            report.append("Shared name: {}".format(model_name))
            if model_dict.get('display_name') and model_dict.get('display_name') != model_name:
                report.append("Display name: {}".format(model_dict.get('display_name')))
            report.append("MCP can load it with load_model() or load_model_from_shared_memory(name='{}')".format(model_name))
            report.append("If MCP edits this shared-memory model, the refactored post-edit pipeline will auto-save back to the same name.")
        
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
