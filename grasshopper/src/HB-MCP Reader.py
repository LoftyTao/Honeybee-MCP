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
via the Honeybee-MCP server. It supports both manual and automatic update modes.

    Args:
        _name: Name of the shared memory segment (should match the model's display_name).
        _read: Set to "True" to read the model from shared memory (manual mode).
        _interval_: Check interval in milliseconds for auto mode (default: 500).
        run_: Set to "True" to enable automatic monitoring for MCP changes.
        clear_: Set to "True" to clear shared memory after reading.

    Returns:
        report: Reports, errors, warnings, etc.
        model: A Honeybee Model object that has been loaded from shared memory.
        updated: True when model was just updated (auto mode only).
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
from datetime import datetime

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    import clr
    clr.AddReference('System')
    from System.Threading import Timer, TimerCallback
    _timer_available = True
except:
    _timer_available = False


MAP_NAME_PREFIX = "hb_model_"
HEADER_SIZE = 8

_listener_state = {
    'timer': None,
    'last_modified': 0,
    'last_size': 0,
    'component': None,
    'name': None,
    'last_reported_modified': 0
}


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


def write_clear_signal(name, model_name):
    """Write a clear signal to shared memory for MCP to detect."""
    try:
        map_path = get_map_path(name)
        if map_path is None:
            return False
        
        clear_signal = {
            "cleared": True,
            "model_name": model_name,
            "timestamp": datetime.now().isoformat() if 'datetime' in dir() else ""
        }
        
        json_data = json.dumps(clear_signal, ensure_ascii=False)
        json_bytes = json_data.encode('utf-8')
        data_size = len(json_bytes)
        total_size = HEADER_SIZE + data_size
        
        with open(map_path, 'wb') as f:
            f.write(b'\x00' * total_size)
        
        with open(map_path, 'r+b') as f:
            mm = mmap.mmap(f.fileno(), total_size)
            
            header = struct.pack('<Q', data_size)
            mm[:HEADER_SIZE] = header
            mm[HEADER_SIZE:total_size] = json_bytes
            
            mm.flush()
            mm.close()
        
        return True
    except:
        return False


def check_for_updates(state):
    """Callback to check for shared memory updates."""
    try:
        if state['component'] is None or state['name'] is None:
            return
        
        map_path = get_map_path(state['name'])
        if map_path is None or not os.path.exists(map_path):
            return
        
        current_modified = os.path.getmtime(map_path)
        current_size = os.path.getsize(map_path)
        
        if current_modified != state['last_modified'] or current_size != state['last_size']:
            state['last_modified'] = current_modified
            state['last_size'] = current_size
            
            comp = state['component']
            if comp is not None:
                comp.ExpireSolution(True)
    except:
        pass


def start_listener(name, interval, component):
    """Start the monitoring timer."""
    if not _timer_available:
        return False, ".NET Timer not available"
    
    stop_listener()
    
    map_path = get_map_path(name)
    if map_path and os.path.exists(map_path):
        _listener_state['last_modified'] = os.path.getmtime(map_path)
        _listener_state['last_size'] = os.path.getsize(map_path)
    else:
        _listener_state['last_modified'] = 0
        _listener_state['last_size'] = 0
    
    _listener_state['name'] = name
    _listener_state['component'] = component
    
    try:
        callback = TimerCallback(lambda s: check_for_updates(_listener_state))
        _listener_state['timer'] = Timer(callback, None, interval, interval)
        return True, "Auto-monitoring started"
    except Exception as e:
        return False, "Failed to start timer: {}".format(str(e))


def stop_listener():
    """Stop the monitoring timer."""
    if _listener_state['timer'] is not None:
        try:
            _listener_state['timer'].Dispose()
        except:
            pass
        _listener_state['timer'] = None
    _listener_state['component'] = None
    _listener_state['name'] = None


# Initialize outputs
report = []
model = None
updated = False

if not all_required_inputs(ghenv.Component):
    pass
else:
    try:
        interval = int(_interval_) if _interval_ is not None else 500
    except:
        interval = 500
    
    if run_:
        if _listener_state['component'] is None:
            success, msg = start_listener(_name, interval, ghenv.Component)
            if success:
                report.append("Auto-monitoring: ON (interval: {} ms)".format(interval))
            else:
                report.append(msg)
                give_warning(ghenv.Component, msg)
        
        model_dict, msg = read_from_mmap(_name)
        
        if model_dict is not None:
            try:
                model = Model.from_dict(model_dict)
                model_name = model.display_name if model.display_name else model.identifier
                
                report.append("Model: {}".format(model_name))
                report.append("Rooms: {}".format(len(model.rooms)))
                
                map_path = get_map_path(_name)
                if map_path and os.path.exists(map_path):
                    current_modified = os.path.getmtime(map_path)
                    if current_modified != _listener_state.get('last_reported_modified', 0):
                        updated = True
                        _listener_state['last_reported_modified'] = current_modified
                        report.append("Model updated from MCP")
                
                if clear_:
                    if write_clear_signal(_name, model_name):
                        report.append("Clear signal sent to MCP")
                    else:
                        report.append("Warning: Could not send clear signal")
            except Exception as e:
                report.append("Failed to convert to Model: {}".format(str(e)))
                give_warning(ghenv.Component, "Failed to convert dictionary to Model")
        else:
            report.append(msg)
            give_warning(ghenv.Component, msg)
    else:
        stop_listener()
        
        if _read:
            model_dict, msg = read_from_mmap(_name)
            
            if model_dict is not None:
                try:
                    model = Model.from_dict(model_dict)
                    model_name = model.display_name if model.display_name else model.identifier
                    
                    report.append("Successfully loaded Honeybee Model from shared memory")
                    report.append("Model: {}".format(model_name))
                    report.append("Rooms: {}".format(len(model.rooms)))
                    
                    if clear_:
                        if write_clear_signal(_name, model_name):
                            report.append("Clear signal sent to MCP")
                        else:
                            report.append("Warning: Could not send clear signal")
                except Exception as e:
                    report.append("Failed to convert to Model: {}".format(str(e)))
                    give_warning(ghenv.Component, "Failed to convert dictionary to Model")
            else:
                report.append(msg)
                give_warning(ghenv.Component, msg)
        else:
            report.append("Set _read=True (manual) or run_=True (auto) to read model")
