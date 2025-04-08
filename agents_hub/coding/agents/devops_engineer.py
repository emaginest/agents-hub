"""
DevOps Engineer Agent for the Agents Hub framework.

This module implements the DevOps Engineer agent, responsible for handling
infrastructure, Git operations, and deployment.
"""

from agents_hub import Agent
from agents_hub.llm.base import BaseLLM
from agents_hub.utils.approval import ApprovalInterface
from typing import Dict, Any, Optional, List
import logging
import os

# Configure logging
logger = logging.getLogger(__name__)

class DevOpsEngineerAgent(Agent):
    """
    Agent responsible for handling infrastructure, Git operations, and deployment.
    
    This agent uses GPT-4o for strong understanding of infrastructure and deployment concepts.
    It sets up AWS CDK infrastructure, manages Git repositories, implements CI/CD pipelines,
    and configures AWS services.
    
    Example:
        ```python
        from agents_hub.coding.agents import DevOpsEngineerAgent
        from agents_hub.llm.providers import OpenAIProvider
        from agents_hub.tools.coding import GitTool, AWSCDKTool
        
        # Initialize LLM provider
        llm = OpenAIProvider(api_key="your-openai-api-key")
        
        # Initialize DevOps Engineer agent
        devops_engineer = DevOpsEngineerAgent(
            llm=llm,
            tools=[GitTool(), AWSCDKTool()],
            project_name="My Project",
            project_description="A web application with user authentication.",
        )
        
        # Design infrastructure
        infrastructure_design = await devops_engineer.design_infrastructure(
            "The application should have user registration, login, and profile management."
        )
        ```
    """
    
    def __init__(
        self,
        llm: BaseLLM,
        tools: Optional[List[Any]] = None,
        project_name: str = "Project",
        project_description: str = "",
    ):
        """
        Initialize the DevOps engineer agent.
        
        Args:
            llm: LLM provider (GPT-4o optimized for DevOps)
            tools: Optional list of tools
            project_name: Name of the project
            project_description: Description of the project
        """
        system_prompt = f"""You are a DevOps engineer responsible for infrastructure, Git operations, and deployment for the project: {project_name}.

Project Description:
{project_description}

Your tasks include:
1. Setting up AWS CDK infrastructure as code
2. Managing Git repositories and version control
3. Implementing CI/CD pipelines
4. Configuring AWS services (API Gateway, Lambda, etc.)
5. Ensuring security best practices in infrastructure
6. Monitoring and logging setup

IMPORTANT: For critical operations like Git pushes and AWS deployments,
you must always request human approval before proceeding. Never execute
these operations without explicit confirmation from the user.

You excel at creating scalable, secure, and maintainable infrastructure.
You follow best practices for infrastructure as code and DevOps principles.

When developing infrastructure code, consider:
- Security and compliance requirements
- Scalability and performance
- Cost optimization
- Monitoring and observability
- Disaster recovery and backup strategies
- Infrastructure as code best practices

Always write code that is:
- Well-structured and organized
- Properly documented with comments
- Secure and follows best practices
- Testable and maintainable
- Efficient and cost-effective

You should use AWS CDK with TypeScript for infrastructure as code, along with
AWS services such as API Gateway, Lambda, DynamoDB, S3, and CloudFront.
"""
        
        super().__init__(
            name="devops_engineer",
            llm=llm,
            tools=tools or [],
            system_prompt=system_prompt,
        )
        
        self.project_name = project_name
        self.project_description = project_description
        self.approval_interface = ApprovalInterface()
    
    async def design_infrastructure(self, specifications: str) -> Dict[str, Any]:
        """
        Design the infrastructure based on specifications.
        
        Args:
            specifications: Project specifications
            
        Returns:
            Infrastructure design
        """
        logger.info(f"Designing infrastructure for {self.project_name}")
        
        prompt = f"""
        Design the AWS infrastructure for a project based on the following specifications:
        
        {specifications}
        
        Your design should include:
        1. AWS services to be used
        2. Architecture diagram (described in text)
        3. Security considerations
        4. Scalability approach
        5. Cost optimization strategies
        6. Monitoring and logging approach
        
        The infrastructure should support a FastAPI backend deployed to Lambda with API Gateway,
        and a React frontend deployed to S3 with CloudFront.
        
        Format the response as a structured design document with code examples where appropriate.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "infrastructure_design": response,
        }
    
    async def create_cdk_infrastructure(self, specifications: str, output_dir: str) -> Dict[str, Any]:
        """
        Create AWS CDK infrastructure code based on specifications.
        
        Args:
            specifications: Project specifications
            output_dir: Output directory for the code
            
        Returns:
            CDK infrastructure code
        """
        logger.info(f"Creating CDK infrastructure for {self.project_name}")
        
        prompt = f"""
        Create AWS CDK infrastructure code based on the following specifications:
        
        {specifications}
        
        Your implementation should include:
        1. CDK app setup
        2. Stack definitions
        3. Resource configurations
        4. Security settings
        5. Environment variables and parameters
        6. Deployment instructions
        
        The infrastructure should support a FastAPI backend deployed to Lambda with API Gateway,
        and a React frontend deployed to S3 with CloudFront.
        
        Format the response as TypeScript code that can be directly used with AWS CDK.
        """
        
        response = await self.run(prompt)
        
        # In a real implementation, this would parse the response and create files
        
        return {
            "project_name": self.project_name,
            "cdk_infrastructure": response,
            "output_dir": output_dir,
        }
    
    async def initialize_git_repository(self, project_path: str) -> Dict[str, Any]:
        """
        Initialize a Git repository for the project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Result message
        """
        logger.info(f"Initializing Git repository for {self.project_name} at {project_path}")
        
        # Request human approval
        approval_details = {
            "Operation": "Initialize Git repository",
            "Path": project_path,
            "Project": self.project_name,
        }
        
        approved = await self.approval_interface.request_approval(
            "git_init",
            approval_details,
            f"Approve Git repository initialization for {self.project_name}?"
        )
        
        if not approved:
            return {
                "status": "cancelled",
                "message": "Git repository initialization was cancelled by user",
                "project_name": self.project_name,
                "project_path": project_path,
            }
        
        # Initialize Git repository
        result = await self.run_tool("git_tool", {
            "operation": "init",
            "path": project_path,
        })
        
        return {
            "status": "success" if result.get("status") == "success" else "error",
            "message": result.get("message", "Unknown error"),
            "project_name": self.project_name,
            "project_path": project_path,
        }
    
    async def commit_changes(self, project_path: str, message: str) -> Dict[str, Any]:
        """
        Commit changes to the Git repository.
        
        Args:
            project_path: Path to the project directory
            message: Commit message
            
        Returns:
            Result message
        """
        logger.info(f"Committing changes for {self.project_name} at {project_path}")
        
        # Add all files
        add_result = await self.run_tool("git_tool", {
            "operation": "add",
            "path": project_path,
            "files": ["."],
        })
        
        if add_result.get("status") != "success":
            return {
                "status": "error",
                "message": f"Failed to add files: {add_result.get('message', 'Unknown error')}",
                "project_name": self.project_name,
                "project_path": project_path,
            }
        
        # Commit changes
        commit_result = await self.run_tool("git_tool", {
            "operation": "commit",
            "path": project_path,
            "message": message,
        })
        
        return {
            "status": "success" if commit_result.get("status") == "success" else "error",
            "message": commit_result.get("message", "Unknown error"),
            "project_name": self.project_name,
            "project_path": project_path,
        }
    
    async def push_to_remote(self, project_path: str, remote: str, branch: str) -> Dict[str, Any]:
        """
        Push changes to a remote repository with human approval.
        
        Args:
            project_path: Path to the project directory
            remote: Remote name
            branch: Branch name
            
        Returns:
            Result message
        """
        logger.info(f"Pushing changes for {self.project_name} to {remote}/{branch}")
        
        # Request human approval
        approval_details = {
            "Operation": "Push to remote",
            "Path": project_path,
            "Remote": remote,
            "Branch": branch,
            "Project": self.project_name,
        }
        
        approved = await self.approval_interface.request_approval(
            "git_push",
            approval_details,
            f"Approve Git push to {remote}/{branch} for {self.project_name}?"
        )
        
        if not approved:
            return {
                "status": "cancelled",
                "message": "Git push was cancelled by user",
                "project_name": self.project_name,
                "project_path": project_path,
                "remote": remote,
                "branch": branch,
            }
        
        # Push changes
        result = await self.run_tool("git_tool", {
            "operation": "push",
            "path": project_path,
            "remote": remote,
            "branch": branch,
        })
        
        return {
            "status": "success" if result.get("status") == "success" else "error",
            "message": result.get("message", "Unknown error"),
            "project_name": self.project_name,
            "project_path": project_path,
            "remote": remote,
            "branch": branch,
        }
    
    async def deploy_cdk_stack(self, project_path: str, stack_name: str) -> Dict[str, Any]:
        """
        Deploy an AWS CDK stack with human approval.
        
        Args:
            project_path: Path to the project directory
            stack_name: Name of the CDK stack
            
        Returns:
            Result message
        """
        logger.info(f"Deploying CDK stack {stack_name} for {self.project_name}")
        
        # Request human approval
        approval_details = {
            "Operation": "Deploy CDK stack",
            "Path": project_path,
            "Stack": stack_name,
            "Project": self.project_name,
        }
        
        approved = await self.approval_interface.request_approval(
            "cdk_deploy",
            approval_details,
            f"Approve AWS CDK deployment of stack '{stack_name}' for {self.project_name}?"
        )
        
        if not approved:
            return {
                "status": "cancelled",
                "message": "CDK deployment was cancelled by user",
                "project_name": self.project_name,
                "project_path": project_path,
                "stack_name": stack_name,
            }
        
        # Deploy stack
        result = await self.run_tool("aws_cdk_tool", {
            "operation": "deploy",
            "path": project_path,
            "stack": stack_name,
        })
        
        return {
            "status": "success" if result.get("status") == "success" else "error",
            "message": result.get("message", "Unknown error"),
            "project_name": self.project_name,
            "project_path": project_path,
            "stack_name": stack_name,
        }
