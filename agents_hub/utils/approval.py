"""
Human Approval Interface for the Agents Hub framework.

This module provides an interface for requesting and handling human approvals
for critical operations like Git pushes and AWS deployments.
"""

import asyncio
from typing import Dict, Any, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

class ApprovalInterface:
    """
    Interface for handling human approval requests.
    
    This class provides methods for requesting and handling human approvals
    for critical operations like Git pushes and AWS deployments.
    
    Example:
        ```python
        from agents_hub.utils.approval import ApprovalInterface
        
        approval_interface = ApprovalInterface()
        
        # Request approval for a critical operation
        approved = await approval_interface.request_approval(
            "git_push",
            {"repository": "my-repo", "branch": "main"},
            "Approve Git push to main branch?"
        )
        
        if approved:
            # Proceed with the operation
            print("Operation approved!")
        else:
            # Cancel the operation
            print("Operation cancelled.")
        ```
    """
    
    @staticmethod
    async def request_approval(
        operation: str,
        details: Dict[str, Any],
        message: Optional[str] = None
    ) -> bool:
        """
        Request human approval for an operation.
        
        Args:
            operation: Type of operation (git_push, aws_deploy, etc.)
            details: Details of the operation
            message: Optional message to display
            
        Returns:
            True if approved, False otherwise
        """
        message = message or f"Approval required for {operation}"
        
        print("\n" + "="*80)
        print(f"APPROVAL REQUIRED: {message}")
        print("-"*80)
        
        for key, value in details.items():
            print(f"{key}: {value}")
        
        print("-"*80)
        response = input("Do you approve this operation? (yes/no): ").strip().lower()
        
        approved = response in ["yes", "y"]
        
        if approved:
            logger.info(f"Operation '{operation}' approved by user")
        else:
            logger.info(f"Operation '{operation}' rejected by user")
        
        return approved
    
    @staticmethod
    async def notify(message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Notify the user about an important event.
        
        Args:
            message: Message to display
            details: Optional details to display
        """
        print("\n" + "="*80)
        print(f"NOTIFICATION: {message}")
        print("-"*80)
        
        if details:
            for key, value in details.items():
                print(f"{key}: {value}")
            
            print("-"*80)
    
    @staticmethod
    async def request_input(prompt: str) -> str:
        """
        Request input from the user.
        
        Args:
            prompt: Prompt to display
            
        Returns:
            User input
        """
        print("\n" + "="*80)
        print(f"INPUT REQUIRED: {prompt}")
        print("-"*80)
        
        response = input("> ").strip()
        
        return response
