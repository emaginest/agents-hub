"""
Git Tool for the Agents Hub framework.

This module provides a tool for Git operations with human approval checkpoints.
"""

from agents_hub.tools.base import BaseTool
from agents_hub.utils.approval import ApprovalInterface
from typing import Dict, Any, Optional
import subprocess
import os
import logging
import asyncio

# Configure logging
logger = logging.getLogger(__name__)

class GitTool(BaseTool):
    """
    Tool for Git operations with human approval checkpoints.
    
    This tool provides methods for Git operations like init, add, commit, push, etc.
    Critical operations like push require human approval before proceeding.
    
    Example:
        ```python
        from agents_hub.tools.coding import GitTool
        
        # Initialize Git tool
        git_tool = GitTool()
        
        # Use the tool
        result = await agent.run_tool("git_tool", {
            "operation": "init",
            "path": "/path/to/repository",
        })
        ```
    """
    
    def __init__(self):
        """Initialize the Git tool."""
        super().__init__(
            name="git_tool",
            description="Perform Git operations with human approval for critical actions",
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["init", "add", "commit", "push", "pull", "status", "clone"],
                        "description": "Git operation to perform",
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to the Git repository",
                    },
                    "message": {
                        "type": "string",
                        "description": "Commit message (for commit operation)",
                    },
                    "remote": {
                        "type": "string",
                        "description": "Remote name (for push/pull operations)",
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch name (for push/pull operations)",
                    },
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Files to add (for add operation)",
                    },
                    "url": {
                        "type": "string",
                        "description": "Repository URL (for clone operation)",
                    },
                    "require_approval": {
                        "type": "boolean",
                        "description": "Whether to require human approval for this operation",
                        "default": True,
                    },
                },
                "required": ["operation", "path"],
            },
        )
        
        self.approval_interface = ApprovalInterface()
    
    async def run(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Run the Git tool.
        
        Args:
            parameters: Parameters for the tool
            context: Optional context information
            
        Returns:
            Result of the operation
        """
        operation = parameters.get("operation")
        path = parameters.get("path")
        require_approval = parameters.get("require_approval", True)
        
        logger.info(f"Running Git {operation} operation on {path}")
        
        # Critical operations that require human approval
        critical_operations = ["push", "clone"]
        
        if operation in critical_operations and require_approval:
            # Request human approval
            approval_details = {
                "Operation": operation,
                "Path": path,
            }
            
            if operation == "push":
                remote = parameters.get("remote", "origin")
                branch = parameters.get("branch", "main")
                approval_details["Remote"] = remote
                approval_details["Branch"] = branch
                
                # Get the list of commits to be pushed
                try:
                    result = await self._run_git_command(
                        ["log", f"origin/{branch}..HEAD", "--oneline"],
                        path
                    )
                    approval_details["Commits to push"] = result.strip() or "No new commits"
                except Exception as e:
                    approval_details["Commits to push"] = f"Error getting commits: {str(e)}"
            
            elif operation == "clone":
                url = parameters.get("url", "")
                approval_details["URL"] = url
            
            approved = await self.approval_interface.request_approval(
                f"git_{operation}",
                approval_details,
                f"Approve Git {operation} operation?"
            )
            
            if not approved:
                return {
                    "status": "cancelled",
                    "message": f"Git {operation} operation was cancelled by user",
                    "operation": operation,
                    "path": path,
                }
        
        # Execute the Git operation
        try:
            if operation == "init":
                return await self._git_init(path)
            elif operation == "add":
                files = parameters.get("files", ["."])
                return await self._git_add(path, files)
            elif operation == "commit":
                message = parameters.get("message", "Commit by GitTool")
                return await self._git_commit(path, message)
            elif operation == "push":
                remote = parameters.get("remote", "origin")
                branch = parameters.get("branch", "main")
                return await self._git_push(path, remote, branch)
            elif operation == "pull":
                remote = parameters.get("remote", "origin")
                branch = parameters.get("branch", "main")
                return await self._git_pull(path, remote, branch)
            elif operation == "status":
                return await self._git_status(path)
            elif operation == "clone":
                url = parameters.get("url", "")
                return await self._git_clone(url, path)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown Git operation: {operation}",
                    "operation": operation,
                    "path": path,
                }
        
        except Exception as e:
            logger.exception(f"Error executing Git {operation} operation: {str(e)}")
            return {
                "status": "error",
                "message": f"Error executing Git {operation} operation: {str(e)}",
                "operation": operation,
                "path": path,
            }
    
    async def _run_git_command(self, args: list, cwd: str) -> str:
        """
        Run a Git command.
        
        Args:
            args: Command arguments
            cwd: Working directory
            
        Returns:
            Command output
        """
        cmd = ["git"] + args
        logger.debug(f"Running Git command: {' '.join(cmd)}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_message = stderr.decode().strip()
                logger.error(f"Git command failed: {error_message}")
                raise Exception(f"Git command failed: {error_message}")
            
            return stdout.decode().strip()
        
        except Exception as e:
            logger.exception(f"Error running Git command: {str(e)}")
            raise
    
    async def _git_init(self, path: str) -> Dict[str, Any]:
        """
        Initialize a Git repository.
        
        Args:
            path: Path to initialize
            
        Returns:
            Result of the operation
        """
        await self._run_git_command(["init"], path)
        
        return {
            "status": "success",
            "message": f"Git repository initialized at {path}",
            "operation": "init",
            "path": path,
        }
    
    async def _git_add(self, path: str, files: list) -> Dict[str, Any]:
        """
        Add files to the Git staging area.
        
        Args:
            path: Repository path
            files: Files to add
            
        Returns:
            Result of the operation
        """
        for file in files:
            await self._run_git_command(["add", file], path)
        
        return {
            "status": "success",
            "message": f"Added {len(files)} file(s) to staging area",
            "operation": "add",
            "path": path,
            "files": files,
        }
    
    async def _git_commit(self, path: str, message: str) -> Dict[str, Any]:
        """
        Commit changes to the Git repository.
        
        Args:
            path: Repository path
            message: Commit message
            
        Returns:
            Result of the operation
        """
        await self._run_git_command(["commit", "-m", message], path)
        
        return {
            "status": "success",
            "message": f"Changes committed with message: {message}",
            "operation": "commit",
            "path": path,
            "commit_message": message,
        }
    
    async def _git_push(self, path: str, remote: str, branch: str) -> Dict[str, Any]:
        """
        Push changes to a remote repository.
        
        Args:
            path: Repository path
            remote: Remote name
            branch: Branch name
            
        Returns:
            Result of the operation
        """
        await self._run_git_command(["push", remote, branch], path)
        
        return {
            "status": "success",
            "message": f"Changes pushed to {remote}/{branch}",
            "operation": "push",
            "path": path,
            "remote": remote,
            "branch": branch,
        }
    
    async def _git_pull(self, path: str, remote: str, branch: str) -> Dict[str, Any]:
        """
        Pull changes from a remote repository.
        
        Args:
            path: Repository path
            remote: Remote name
            branch: Branch name
            
        Returns:
            Result of the operation
        """
        await self._run_git_command(["pull", remote, branch], path)
        
        return {
            "status": "success",
            "message": f"Changes pulled from {remote}/{branch}",
            "operation": "pull",
            "path": path,
            "remote": remote,
            "branch": branch,
        }
    
    async def _git_status(self, path: str) -> Dict[str, Any]:
        """
        Get the status of the Git repository.
        
        Args:
            path: Repository path
            
        Returns:
            Result of the operation
        """
        status = await self._run_git_command(["status"], path)
        
        return {
            "status": "success",
            "message": "Git status retrieved",
            "operation": "status",
            "path": path,
            "git_status": status,
        }
    
    async def _git_clone(self, url: str, path: str) -> Dict[str, Any]:
        """
        Clone a Git repository.
        
        Args:
            url: Repository URL
            path: Destination path
            
        Returns:
            Result of the operation
        """
        # For clone, we need to run the command in the parent directory
        parent_dir = os.path.dirname(path)
        
        # Create parent directory if it doesn't exist
        os.makedirs(parent_dir, exist_ok=True)
        
        # Get the repository name from the URL
        repo_name = url.split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        
        await self._run_git_command(["clone", url, path], parent_dir)
        
        return {
            "status": "success",
            "message": f"Repository cloned from {url} to {path}",
            "operation": "clone",
            "path": path,
            "url": url,
        }
