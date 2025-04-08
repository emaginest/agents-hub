"""
Code Generator Tool for the Agents Hub framework.

This module provides a tool for generating code based on specifications.
"""

from agents_hub.tools.base import BaseTool
from typing import Dict, Any, Optional
import os
import logging
import json

# Configure logging
logger = logging.getLogger(__name__)

class CodeGeneratorTool(BaseTool):
    """
    Tool for generating code based on specifications.
    
    This tool provides methods for generating code files and directories
    based on specifications provided by the agents.
    
    Example:
        ```python
        from agents_hub.tools.coding import CodeGeneratorTool
        
        # Initialize Code Generator tool
        code_generator = CodeGeneratorTool()
        
        # Use the tool
        result = await agent.run_tool("code_generator", {
            "operation": "create_file",
            "path": "/path/to/file.py",
            "content": "print('Hello, world!')",
        })
        ```
    """
    
    def __init__(self):
        """Initialize the code generator tool."""
        super().__init__(
            name="code_generator",
            description="Generate code based on specifications",
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["create_file", "create_directory", "list_files"],
                        "description": "Operation to perform",
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to the file or directory",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content of the file (for create_file operation)",
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Whether to overwrite existing files",
                        "default": False,
                    },
                },
                "required": ["operation", "path"],
            },
        )
    
    async def run(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Run the code generator tool.
        
        Args:
            parameters: Parameters for the tool
            context: Optional context information
            
        Returns:
            Result of the operation
        """
        operation = parameters.get("operation")
        path = parameters.get("path")
        
        logger.info(f"Running code generator {operation} operation on {path}")
        
        try:
            if operation == "create_file":
                content = parameters.get("content", "")
                overwrite = parameters.get("overwrite", False)
                return await self._create_file(path, content, overwrite)
            
            elif operation == "create_directory":
                return await self._create_directory(path)
            
            elif operation == "list_files":
                return await self._list_files(path)
            
            else:
                return {
                    "status": "error",
                    "message": f"Unknown operation: {operation}",
                    "operation": operation,
                    "path": path,
                }
        
        except Exception as e:
            logger.exception(f"Error executing {operation} operation: {str(e)}")
            return {
                "status": "error",
                "message": f"Error executing {operation} operation: {str(e)}",
                "operation": operation,
                "path": path,
            }
    
    async def _create_file(self, path: str, content: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Create a file with the specified content.
        
        Args:
            path: File path
            content: File content
            overwrite: Whether to overwrite existing files
            
        Returns:
            Result of the operation
        """
        # Check if file exists
        if os.path.exists(path) and not overwrite:
            return {
                "status": "error",
                "message": f"File already exists: {path}",
                "operation": "create_file",
                "path": path,
            }
        
        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        # Write file
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return {
            "status": "success",
            "message": f"File created: {path}",
            "operation": "create_file",
            "path": path,
            "size": len(content),
        }
    
    async def _create_directory(self, path: str) -> Dict[str, Any]:
        """
        Create a directory.
        
        Args:
            path: Directory path
            
        Returns:
            Result of the operation
        """
        # Create directory
        os.makedirs(path, exist_ok=True)
        
        return {
            "status": "success",
            "message": f"Directory created: {path}",
            "operation": "create_directory",
            "path": path,
        }
    
    async def _list_files(self, path: str) -> Dict[str, Any]:
        """
        List files in a directory.
        
        Args:
            path: Directory path
            
        Returns:
            Result of the operation
        """
        # Check if path exists
        if not os.path.exists(path):
            return {
                "status": "error",
                "message": f"Path does not exist: {path}",
                "operation": "list_files",
                "path": path,
            }
        
        # List files
        if os.path.isdir(path):
            files = os.listdir(path)
            
            # Get file types
            file_info = []
            for file in files:
                file_path = os.path.join(path, file)
                file_type = "directory" if os.path.isdir(file_path) else "file"
                file_info.append({
                    "name": file,
                    "type": file_type,
                    "size": os.path.getsize(file_path) if os.path.isfile(file_path) else None,
                })
            
            return {
                "status": "success",
                "message": f"Files listed: {path}",
                "operation": "list_files",
                "path": path,
                "files": file_info,
            }
        else:
            return {
                "status": "error",
                "message": f"Path is not a directory: {path}",
                "operation": "list_files",
                "path": path,
            }
