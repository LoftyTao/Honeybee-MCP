"""
MCP Tools for Model Version Control

Automatic version control - tracks model changes in memory.
"""

from mcp.server.fastmcp import FastMCP
from .version_control import (
    save_version_auto,
    list_versions,
    load_version,
    undo_last,
    get_latest_version,
    clear_versions,
    get_all_model_names
)
from .shared_memory_tools import cleanup_old_cache_files


def register_version_tools(mcp: FastMCP):
    """Register version control tools with the MCP server."""
    
    @mcp.tool()
    def save_version(description: str = "") -> dict:
        """
        Manually save current model as a version snapshot.
        
        This tool creates a version snapshot of the currently loaded model.
        Versions are stored in memory and can be used to undo changes or
        restore previous states. Maximum 10 versions are kept per model.
        
        Args:
            description: Optional description for this version snapshot.
                Use this to document what changes were made or why this
                version is being saved. (Default: "")
        
        Returns:
            dict: Dictionary containing:
                - success (bool): Whether the version was saved
                - version_id (str): Version identifier (e.g., "001", "002")
                - model_name (str): Name of the model
                - timestamp (str): When the version was saved
                - total_versions (int): Total number of versions for this model
                - error (str): Error message if saving failed
        
        Example:
            save_version("Added windows to south facade")
            save_version()  # No description
        """
        from tools.load_model import manager
        
        if manager.model is None:
            return {
                "success": False,
                "error": "No model loaded. Load a model first."
            }
        
        model_name = manager.model.display_name or manager.model.identifier
        model_dict = manager.model.to_dict()
        
        return save_version_auto(model_dict, model_name, description)
    
    @mcp.tool()
    def list_model_versions(model_name: str = None) -> dict:
        """
        List all saved versions for a model.
        
        This tool retrieves the version history for a specific model or all models.
        Use this to see what versions are available for restoration.
        
        Args:
            model_name: Name of the model to list versions for. If not specified,
                lists all models with their version counts. (Default: None)
        
        Returns:
            dict: Dictionary containing:
                - success (bool): Whether the operation was successful
                - model_name (str): Name of the model (if specified)
                - versions (list): List of version info dictionaries with:
                    - version (str): Version ID (e.g., "001")
                    - timestamp (str): When the version was saved
                    - description (str): Version description
                    - rooms_count (int): Number of rooms at this version
                    - outdoor_shades_count (int): Number of outdoor shades
                - total_versions (int): Total number of versions
                - max_versions (int): Maximum versions allowed (10)
                - models (list): List of all models with version counts (if no model_name)
                - error (str): Error message if operation failed
        
        Example:
            list_model_versions("MyModel")  # List versions for specific model
            list_model_versions()  # List all models with versions
        """
        if model_name:
            return list_versions(model_name)
        else:
            all_models = get_all_model_names()
            if not all_models:
                return {
                    "success": True,
                    "models": [],
                    "total_models": 0,
                    "message": "No models with version history"
                }
            
            model_list = []
            for mname in all_models:
                versions_info = list_versions(mname)
                if versions_info.get("success"):
                    model_list.append({
                        "model_name": mname,
                        "total_versions": versions_info["total_versions"],
                        "max_versions": versions_info["max_versions"]
                    })
            
            return {
                "success": True,
                "models": model_list,
                "total_models": len(model_list)
            }
    
    @mcp.tool()
    def load_model_version(model_name: str, version_id: str) -> dict:
        """
        Load a specific version of a model.
        
        This tool restores a model to a previously saved version. The model
        is loaded into the current session, replacing any existing model.
        
        Args:
            model_name: Name of the model to load a version from.
            version_id: Version number to load (e.g., "001", "002", "010").
                Use list_model_versions to see available versions.
        
        Returns:
            dict: Dictionary containing:
                - success (bool): Whether the version was loaded
                - message (str): Status message
                - model_name (str): Name of the model
                - version_id (str): Version that was loaded
                - timestamp (str): When this version was saved
                - description (str): Version description
                - rooms_count (int): Number of rooms in the loaded model
                - error (str): Error message if loading failed
                - available_versions (list): List of available versions (if version not found)
        
        Example:
            load_model_version("MyModel", "001")
            load_model_version("MyModel", "5")  # Will be padded to "005"
        """
        from tools.load_model import manager
        
        result = load_version(model_name, version_id)
        
        if result.get("success"):
            manager.load_from_dict(result["model_dict"])
            return {
                "success": True,
                "message": "Loaded version {} of model '{}'".format(version_id, model_name),
                "model_name": model_name,
                "version_id": result["version_id"],
                "timestamp": result["timestamp"],
                "description": result.get("description", ""),
                "rooms_count": len(manager.model.rooms)
            }
        
        return result
    
    @mcp.tool()
    def undo_last_change(model_name: str = None) -> dict:
        """
        Undo to the previous version (restore before last change).
        
        This tool reverts the model to the second-to-last saved version,
        effectively undoing the most recent change. Useful for quickly
        reverting unwanted modifications.
        
        Args:
            model_name: Name of the model to undo. If not specified, uses
                the currently loaded model. (Default: None)
        
        Returns:
            dict: Dictionary containing:
                - success (bool): Whether the undo was successful
                - message (str): Status message
                - model_name (str): Name of the model
                - version_id (str): Version restored to
                - timestamp (str): When this version was saved
                - rooms_count (int): Number of rooms in the restored model
                - error (str): Error message if undo failed
                - current_version (str): Current version ID (if only one version exists)
        
        Example:
            undo_last_change()  # Undo current model
            undo_last_change("MyModel")  # Undo specific model
        """
        from tools.load_model import manager
        
        if model_name is None:
            if manager.model is None:
                return {
                    "success": False,
                    "error": "No model loaded and no model_name specified."
                }
            model_name = manager.model.display_name or manager.model.identifier
        
        result = undo_last(model_name)
        
        if result.get("success"):
            manager.load_from_dict(result["model_dict"])
            return {
                "success": True,
                "message": "Undo successful. Restored to version {}".format(result["version_id"]),
                "model_name": model_name,
                "version_id": result["version_id"],
                "timestamp": result["timestamp"],
                "rooms_count": len(manager.model.rooms)
            }
        
        return result
    
    @mcp.tool()
    def clear_version_history(model_name: str = None) -> dict:
        """
        Clear version history for a model or all models.
        
        This tool removes all saved versions from memory. Use with caution
        as this action cannot be undone.
        
        Args:
            model_name: Name of the model to clear versions for. If not specified,
                clears version history for ALL models. (Default: None)
        
        Returns:
            dict: Dictionary containing:
                - success (bool): Whether the clear was successful
                - message (str): Status message with count of cleared models
                - error (str): Error message if clearing failed
        
        Example:
            clear_version_history("MyModel")  # Clear specific model
            clear_version_history()  # Clear ALL models
        """
        return clear_versions(model_name)
    
    @mcp.tool()
    def cleanup_cache() -> dict:
        """
        Clean up old shared memory cache files.
        
        This tool removes old memory-mapped files from the temp directory to
        free up disk space. It keeps only the most recent files and removes
        files older than 24 hours.
        
        Cleanup Rules:
        - Keeps only the most recent 5 files
        - Removes files older than 24 hours
        
        Returns:
            dict: Dictionary containing:
                - success (bool): Whether cleanup was successful
                - kept_files (int): Number of files kept
                - removed_files (int): Number of files removed
                - removed_details (list): Details of removed files
                - error (str): Error message if cleanup failed
        
        Example:
            cleanup_cache()
        """
        return cleanup_old_cache_files()
