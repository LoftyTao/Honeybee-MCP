# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
#
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Read a Honeybee Model from shared memory after MCP modifications.
-
This component reads a model that was written to shared memory by an AI IDE
via the Honeybee-MCP server.

    Args:
        _name: Name of the shared memory segment (should match the model's display_name).
        _read: Set to "True" to read the model from shared memory.
        clear_: Set to "True" to clear shared memory after reading.

    Returns:
        report: Reports, errors, warnings, etc.
        model: A Honeybee Model object that has been loaded from shared memory.
"""

ghenv.Component.Name = 'HB-MCP Reader'
ghenv.Component.NickName = 'MCPReader'
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

try:
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))


MAP_NAME_PREFIX = "hb_model_"
HEADER_SIZE = 8


def get_map_path(name):
    """Get the file path for memory-mapped file."""
    if name is None:
        return None
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, MAP_NAME_PREFIX + name + ".mmap")


def read_from_mmap(name):
    """Read model dictionary from memory-mapped file."""
    try:
        map_path = get_map_path(name)
        
        if map_path is None or not os.path.exists(map_path):
            return None, "Shared memory '{}' not found. Run Writer first.".format(name)
        
        with open(map_path, 'rb') as f:
            header = f.read(HEADER_SIZE)
            data_size = struct.unpack('<Q', header)[0]
            
            if data_size == 0:
                return None, "No data in shared memory"
            
            json_bytes = f.read(data_size)
            json_data = json_bytes.decode('utf-8')
            model_dict = json.loads(json_data)
            
        return model_dict, "Model read from shared memory '{}'".format(name)
        
    except Exception as e:
        return None, "Error: {}".format(str(e))


def clear_mmap(name):
    """Delete the memory-mapped file."""
    try:
        map_path = get_map_path(name)
        if map_path and os.path.exists(map_path):
            os.remove(map_path)
        return True
    except:
        return False


# Initialize outputs
report = []
model = None

if not all_required_inputs(ghenv.Component):
    pass
elif _read:
    model_dict, msg = read_from_mmap(_name)
    
    if model_dict is not None:
        try:
            model = Model.from_dict(model_dict)
            model_name = model.display_name if model.display_name else model.identifier
            
            report.append("Successfully loaded Honeybee Model from shared memory")
            report.append("Model: {}".format(model_name))
            report.append("Rooms: {}".format(len(model.rooms)))
            
            if clear_:
                if clear_mmap(_name):
                    report.append("Shared memory cleared")
                else:
                    report.append("Warning: Could not clear shared memory")
        except Exception as e:
            report.append("Failed to convert to Model: {}".format(str(e)))
            give_warning(ghenv.Component, "Failed to convert dictionary to Model")
    else:
        report.append(msg)
        give_warning(ghenv.Component, msg)
else:
    report.append("Set _read=True to read model from shared memory")
