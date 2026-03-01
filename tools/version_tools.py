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
        
        Args:
            description: Optional description for this version.
        
        Returns:
            Dictionary with version info and status.
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
        
        Args:
            model_name: Name of the model (lists all models if not specified).
        
        Returns:
            Dictionary with version history.
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
        
        Args:
            model_name: Name of the model.
            version_id: Version number to load (e.g., "001", "002").
        
        Returns:
            Dictionary with load status and model info.
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
        
        Args:
            model_name: Name of the model (uses current model if not specified).
        
        Returns:
            Dictionary with restore status.
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
        
        Args:
            model_name: Name of the model (clears all if not specified).
        
        Returns:
            Dictionary with status.
        """
        return clear_versions(model_name)
    
    @mcp.tool()
    def cleanup_cache() -> dict:
        """
        Clean up old shared memory cache files.
        
        Keeps only the most recent cache files.
        Removes files older than 24 hours.
        
        Returns:
            Dictionary with cleanup status and details.
        """
        return cleanup_old_cache_files()
