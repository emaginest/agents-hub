"""
AWS CDK Tool for the Agents Hub framework.

This module provides a tool for AWS CDK operations with human approval checkpoints.
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

class AWSCDKTool(BaseTool):
    """
    Tool for AWS CDK operations with human approval checkpoints.
    
    This tool provides methods for AWS CDK operations like init, synth, deploy, etc.
    Critical operations like deploy and destroy require human approval before proceeding.
    
    Example:
        ```python
        from agents_hub.tools.coding import AWSCDKTool
        
        # Initialize AWS CDK tool
        aws_cdk_tool = AWSCDKTool()
        
        # Use the tool
        result = await agent.run_tool("aws_cdk_tool", {
            "operation": "synth",
            "path": "/path/to/cdk/project",
            "stack": "MyStack",
        })
        ```
    """
    
    def __init__(self):
        """Initialize the AWS CDK tool."""
        super().__init__(
            name="aws_cdk_tool",
            description="Perform AWS CDK operations with human approval for deployments",
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["init", "synth", "diff", "deploy", "destroy", "list"],
                        "description": "CDK operation to perform",
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to the CDK project",
                    },
                    "stack": {
                        "type": "string",
                        "description": "Stack name (for stack-specific operations)",
                    },
                    "language": {
                        "type": "string",
                        "enum": ["typescript", "javascript", "python", "java", "csharp"],
                        "description": "Programming language (for init operation)",
                        "default": "typescript",
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
        Run the AWS CDK tool.
        
        Args:
            parameters: Parameters for the tool
            context: Optional context information
            
        Returns:
            Result of the operation
        """
        operation = parameters.get("operation")
        path = parameters.get("path")
        stack = parameters.get("stack")
        require_approval = parameters.get("require_approval", True)
        
        logger.info(f"Running CDK {operation} operation on {path}")
        
        # Critical operations that require human approval
        critical_operations = ["deploy", "destroy"]
        
        if operation in critical_operations and require_approval:
            # Request human approval
            approval_details = {
                "Operation": operation,
                "Path": path,
            }
            
            if stack:
                approval_details["Stack"] = stack
            
            # For deploy and destroy, show the diff
            if operation in ["deploy", "destroy"] and stack:
                try:
                    diff_result = await self._run_cdk_command(["diff", stack], path)
                    approval_details["Changes"] = diff_result.strip() or "No changes detected"
                except Exception as e:
                    approval_details["Changes"] = f"Error getting diff: {str(e)}"
            
            approved = await self.approval_interface.request_approval(
                f"cdk_{operation}",
                approval_details,
                f"Approve AWS CDK {operation} operation?"
            )
            
            if not approved:
                return {
                    "status": "cancelled",
                    "message": f"CDK {operation} operation was cancelled by user",
                    "operation": operation,
                    "path": path,
                }
        
        # Execute the CDK operation
        try:
            if operation == "init":
                language = parameters.get("language", "typescript")
                return await self._cdk_init(path, language)
            elif operation == "synth":
                return await self._cdk_synth(path, stack)
            elif operation == "diff":
                return await self._cdk_diff(path, stack)
            elif operation == "deploy":
                return await self._cdk_deploy(path, stack)
            elif operation == "destroy":
                return await self._cdk_destroy(path, stack)
            elif operation == "list":
                return await self._cdk_list(path)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown CDK operation: {operation}",
                    "operation": operation,
                    "path": path,
                }
        
        except Exception as e:
            logger.exception(f"Error executing CDK {operation} operation: {str(e)}")
            return {
                "status": "error",
                "message": f"Error executing CDK {operation} operation: {str(e)}",
                "operation": operation,
                "path": path,
            }
    
    async def _run_cdk_command(self, args: list, cwd: str) -> str:
        """
        Run a CDK command.
        
        Args:
            args: Command arguments
            cwd: Working directory
            
        Returns:
            Command output
        """
        cmd = ["cdk"] + args
        logger.debug(f"Running CDK command: {' '.join(cmd)}")
        
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
                logger.error(f"CDK command failed: {error_message}")
                raise Exception(f"CDK command failed: {error_message}")
            
            return stdout.decode().strip()
        
        except Exception as e:
            logger.exception(f"Error running CDK command: {str(e)}")
            raise
    
    async def _cdk_init(self, path: str, language: str) -> Dict[str, Any]:
        """
        Initialize a CDK project.
        
        Args:
            path: Path to initialize
            language: Programming language
            
        Returns:
            Result of the operation
        """
        # Create directory if it doesn't exist
        os.makedirs(path, exist_ok=True)
        
        # Initialize CDK project
        await self._run_cdk_command(["init", f"app", f"--language={language}"], path)
        
        return {
            "status": "success",
            "message": f"CDK project initialized at {path} with language {language}",
            "operation": "init",
            "path": path,
            "language": language,
        }
    
    async def _cdk_synth(self, path: str, stack: Optional[str] = None) -> Dict[str, Any]:
        """
        Synthesize a CDK stack.
        
        Args:
            path: Project path
            stack: Stack name (optional)
            
        Returns:
            Result of the operation
        """
        args = ["synth"]
        if stack:
            args.append(stack)
        
        output = await self._run_cdk_command(args, path)
        
        return {
            "status": "success",
            "message": f"CDK stack synthesized",
            "operation": "synth",
            "path": path,
            "stack": stack,
            "output": output,
        }
    
    async def _cdk_diff(self, path: str, stack: Optional[str] = None) -> Dict[str, Any]:
        """
        Show the difference between the current stack and deployed stack.
        
        Args:
            path: Project path
            stack: Stack name (optional)
            
        Returns:
            Result of the operation
        """
        args = ["diff"]
        if stack:
            args.append(stack)
        
        output = await self._run_cdk_command(args, path)
        
        return {
            "status": "success",
            "message": f"CDK diff completed",
            "operation": "diff",
            "path": path,
            "stack": stack,
            "output": output,
        }
    
    async def _cdk_deploy(self, path: str, stack: Optional[str] = None) -> Dict[str, Any]:
        """
        Deploy a CDK stack.
        
        Args:
            path: Project path
            stack: Stack name (optional)
            
        Returns:
            Result of the operation
        """
        args = ["deploy", "--require-approval=never"]  # We've already gotten approval
        if stack:
            args.append(stack)
        
        output = await self._run_cdk_command(args, path)
        
        return {
            "status": "success",
            "message": f"CDK stack deployed",
            "operation": "deploy",
            "path": path,
            "stack": stack,
            "output": output,
        }
    
    async def _cdk_destroy(self, path: str, stack: Optional[str] = None) -> Dict[str, Any]:
        """
        Destroy a CDK stack.
        
        Args:
            path: Project path
            stack: Stack name (optional)
            
        Returns:
            Result of the operation
        """
        args = ["destroy", "--force"]  # We've already gotten approval
        if stack:
            args.append(stack)
        
        output = await self._run_cdk_command(args, path)
        
        return {
            "status": "success",
            "message": f"CDK stack destroyed",
            "operation": "destroy",
            "path": path,
            "stack": stack,
            "output": output,
        }
    
    async def _cdk_list(self, path: str) -> Dict[str, Any]:
        """
        List all stacks in the CDK app.
        
        Args:
            path: Project path
            
        Returns:
            Result of the operation
        """
        output = await self._run_cdk_command(["list"], path)
        
        # Parse the output to get a list of stacks
        stacks = [line.strip() for line in output.split("\n") if line.strip()]
        
        return {
            "status": "success",
            "message": f"CDK stacks listed",
            "operation": "list",
            "path": path,
            "stacks": stacks,
        }
