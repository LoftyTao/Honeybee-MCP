# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
#
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Read a Honeybee Model from the refactored Honeybee-MCP sync channel.

This component reads a model from the memory-mapped cache used by the refactored
Honeybee-MCP sync bus. The typical workflow is:

1. HB-MCP Writer writes a Honeybee Model to a shared name.
2. MCP loads it with load_model() or load_model_from_shared_memory().
3. MCP edits the model through query / apply / add / remove.
4. If the model source is shared memory, MCP auto-saves edits back to the same
   shared name.
5. HB-MCP Reader reads the updated model.
-
The reader understands the current protocol metadata, including writer signals
and clear signals, and supports both manual and automatic update modes.

    Args:
        _name: Shared name used by the sync channel. If empty, the default name
               "hb_model_shared" is used. Connecting the 'name' output from
               HB-MCP Writer is the recommended workflow.
        _read: Set to "True" to read the model from shared memory (manual mode).
        _interval_: Check interval in milliseconds for auto mode (default: 500).
        run_: Set to "True" to enable automatic monitoring for MCP updates.
        clear_: Set to "True" to send a clear signal back to MCP after reading.

    Returns:
        report: Reports, errors, warnings, etc.
        model: A Honeybee Model object loaded from the sync channel.
        updated: True when the watched shared file changed during auto mode.
"""

ghenv.Component.Name = 'HB MCP Reader'
ghenv.Component.NickName = 'MCPReader'
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
DEFAULT_NAME = "hb_model_shared"
WRITER_SIGNAL_KEY = "_writer_signal"
CLEAR_FLAG_KEY = "cleared"

_listener_state = {
    'timer': None,
    'last_modified': 0,
    'last_size': 0,
    'component': None,
    'name': None,
    'interval': None,
    'last_reported_modified': 0
}


def normalize_name(name):
    """Normalize the shared name to match MCP's default behavior."""
    return name if name else DEFAULT_NAME


def get_map_path(name):
    """Get the file path for memory-mapped file."""
    name = normalize_name(name)
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, MAP_NAME_PREFIX + name + ".mmap")


def decode_protocol_payload(raw_dict, name):
    """Strip protocol metadata and classify the current payload."""
    if not isinstance(raw_dict, dict):
        return None, "Invalid shared payload in '{}'".format(name), None

    if raw_dict.get(CLEAR_FLAG_KEY) is True:
        model_identifier = raw_dict.get('model_name', 'unknown')
        return None, "Clear signal detected for model '{}'".format(model_identifier), "clear"

    model_dict = dict(raw_dict)
    writer_signal = model_dict.pop(WRITER_SIGNAL_KEY, None)
    if writer_signal and writer_signal.get("written") is True:
        return model_dict, "Model read from shared memory '{}' (writer signal detected)".format(name), "write"

    return model_dict, "Model read from shared memory '{}'".format(name), None


def read_from_mmap(name):
    """Read model dictionary from the MCP memory-mapped sync cache."""
    try:
        name = normalize_name(name)
        map_path = get_map_path(name)
        
        if map_path is None or not os.path.exists(map_path):
            return None, "Shared memory '{}' not found. Run HB-MCP Writer first.".format(name), None
        
        with open(map_path, 'rb') as f:
            header = f.read(HEADER_SIZE)
            data_size = struct.unpack('<Q', header)[0]
            
            if data_size == 0:
                return None, "No data in shared memory '{}'".format(name), None
            
            json_bytes = f.read(data_size)
            json_data = json_bytes.decode('utf-8')
            raw_dict = json.loads(json_data)
            
        return decode_protocol_payload(raw_dict, name)
        
    except Exception as e:
        return None, "Error: {}".format(str(e)), None


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
        name = normalize_name(name)
        map_path = get_map_path(name)
        if map_path is None:
            return False
        
        clear_signal = {
            CLEAR_FLAG_KEY: True,
            "model_name": model_name,
            "timestamp": datetime.now().isoformat()
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
    
    name = normalize_name(name)
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
    _listener_state['interval'] = interval
    
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
    _listener_state['interval'] = None


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

    shared_name = normalize_name(_name)
    
    if run_:
        listener_needs_restart = (
            _listener_state['component'] is None or
            _listener_state['name'] != shared_name or
            _listener_state.get('interval') != interval
        )

        if listener_needs_restart:
            success, msg = start_listener(shared_name, interval, ghenv.Component)
            if success:
                report.append("Auto-monitoring: ON (name: {}, interval: {} ms)".format(shared_name, interval))
            else:
                report.append(msg)
                give_warning(ghenv.Component, msg)
        
        model_dict, msg, signal_type = read_from_mmap(shared_name)
        
        if signal_type == "clear":
            report.append(msg)
            report.append("Waiting for MCP to write a new model to '{}'".format(shared_name))
        elif model_dict is not None:
            try:
                model = Model.from_dict(model_dict)
                model_identifier = model.identifier
                model_display_name = model.display_name if model.display_name else model_identifier
                
                report.append("Identifier: {}".format(model_identifier))
                if model_display_name != model_identifier:
                    report.append("Display name: {}".format(model_display_name))
                report.append("Rooms: {}".format(len(model.rooms)))
                if signal_type == "write":
                    report.append("Writer signal detected")
            
                map_path = get_map_path(shared_name)
                if map_path and os.path.exists(map_path):
                    current_modified = os.path.getmtime(map_path)
                    if current_modified != _listener_state.get('last_reported_modified', 0):
                        updated = True
                        _listener_state['last_reported_modified'] = current_modified
                        report.append("Model updated from MCP")
            
                if clear_:
                    if write_clear_signal(shared_name, model_identifier):
                        report.append("Clear signal sent to MCP for '{}'".format(shared_name))
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
            model_dict, msg, signal_type = read_from_mmap(shared_name)
            
            if signal_type == "clear":
                report.append(msg)
                report.append("No model payload is available until MCP writes back to '{}'".format(shared_name))
            elif model_dict is not None:
                try:
                    model = Model.from_dict(model_dict)
                    model_identifier = model.identifier
                    model_display_name = model.display_name if model.display_name else model_identifier
                    
                    report.append("Successfully loaded Honeybee Model from shared memory")
                    report.append("Identifier: {}".format(model_identifier))
                    if model_display_name != model_identifier:
                        report.append("Display name: {}".format(model_display_name))
                    report.append("Rooms: {}".format(len(model.rooms)))
                    if signal_type == "write":
                        report.append("Writer signal detected")
                    
                    if clear_:
                        if write_clear_signal(shared_name, model_identifier):
                            report.append("Clear signal sent to MCP for '{}'".format(shared_name))
                        else:
                            report.append("Warning: Could not send clear signal")
                except Exception as e:
                    report.append("Failed to convert to Model: {}".format(str(e)))
                    give_warning(ghenv.Component, "Failed to convert dictionary to Model")
            else:
                report.append(msg)
                give_warning(ghenv.Component, msg)
        else:
            report.append("Set _read=True (manual) or run_=True (auto) to read model from '{}'".format(shared_name))
