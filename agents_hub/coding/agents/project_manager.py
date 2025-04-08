"""
Project Manager Agent for the Agents Hub framework.

This module implements the Project Manager agent, responsible for coordinating
the development process and managing tasks.
"""

from agents_hub import Agent
from agents_hub.llm.base import BaseLLM
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logger = logging.getLogger(__name__)

class ProjectManagerAgent(Agent):
    """
    Agent responsible for coordinating the development process.
    
    This agent uses GPT-4o for strong reasoning and planning capabilities.
    It breaks down requirements, assigns tasks, tracks progress, and
    facilitates communication between team members.
    
    Example:
        ```python
        from agents_hub.coding.agents import ProjectManagerAgent
        from agents_hub.llm.providers import OpenAIProvider
        
        # Initialize LLM provider
        llm = OpenAIProvider(api_key="your-openai-api-key")
        
        # Initialize Project Manager agent
        project_manager = ProjectManagerAgent(
            llm=llm,
            project_name="My Project",
            project_description="A web application with user authentication.",
        )
        
        # Create a project plan
        project_plan = await project_manager.create_project_plan(
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
        Initialize the project manager agent.
        
        Args:
            llm: LLM provider (GPT-4o optimized for project management)
            tools: Optional list of tools
            project_name: Name of the project
            project_description: Description of the project
        """
        system_prompt = f"""You are a project manager responsible for coordinating the software development process for the project: {project_name}.

Project Description:
{project_description}

Your tasks include:
1. Breaking down requirements into specific, actionable tasks
2. Assigning tasks to appropriate team members based on their expertise
3. Tracking progress and ensuring deadlines are met
4. Facilitating communication between team members
5. Identifying and resolving blockers
6. Making high-level architectural decisions

You work with a team of specialized agents:
- Requirements Analyst: Analyzes requirements and creates detailed specifications
- Backend Developer: Develops backend services
- Frontend Developer: Develops frontend applications
- DevOps Engineer: Handles deployment, Git operations, and infrastructure
- Security Engineer: Implements security measures
- QA Tester: Tests the application and identifies issues

You excel at planning, coordination, and ensuring the team works efficiently.
You should always maintain a high-level view of the project while being able to
dive into details when necessary.

When making decisions, consider:
- Technical feasibility
- Project timeline and priorities
- Resource constraints
- Best practices and standards
- Security and compliance requirements

Always be clear, concise, and specific in your communications.
"""
        
        super().__init__(
            name="project_manager",
            llm=llm,
            tools=tools or [],
            system_prompt=system_prompt,
        )
        
        self.project_name = project_name
        self.project_description = project_description
        self.tasks = []
        self.task_assignments = {}
        self.task_status = {}
    
    async def create_project_plan(self, requirements: str) -> Dict[str, Any]:
        """
        Create a project plan based on requirements.
        
        Args:
            requirements: Project requirements
            
        Returns:
            Project plan
        """
        logger.info(f"Creating project plan for {self.project_name}")
        
        prompt = f"""
        Create a detailed project plan for the following requirements:
        
        {requirements}
        
        The plan should include:
        1. A breakdown of the project into major components (backend, frontend, infrastructure, etc.)
        2. A list of specific tasks for each component
        3. Dependencies between tasks
        4. Estimated effort for each task (low, medium, high)
        5. Suggested assignment of tasks to team members based on their expertise
        
        Format the response as a structured plan that can be easily parsed.
        """
        
        response = await self.run(prompt)
        
        # Process the response to extract tasks
        # In a real implementation, this would parse the response into a structured plan
        
        return {
            "project_name": self.project_name,
            "plan": response,
        }
    
    async def assign_tasks(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assign tasks to team members.
        
        Args:
            tasks: List of tasks
            
        Returns:
            Task assignments
        """
        logger.info(f"Assigning tasks for {self.project_name}")
        
        self.tasks = tasks
        
        # In a real implementation, this would assign tasks based on agent expertise
        
        return {
            "project_name": self.project_name,
            "assignments": self.task_assignments,
        }
    
    async def track_progress(self) -> Dict[str, Any]:
        """
        Track progress of tasks.
        
        Returns:
            Task status
        """
        logger.info(f"Tracking progress for {self.project_name}")
        
        # In a real implementation, this would check the status of each task
        
        return {
            "project_name": self.project_name,
            "status": self.task_status,
        }
    
    async def resolve_blocker(self, blocker: str) -> str:
        """
        Resolve a blocker.
        
        Args:
            blocker: Description of the blocker
            
        Returns:
            Resolution
        """
        logger.info(f"Resolving blocker: {blocker}")
        
        prompt = f"""
        Help resolve the following blocker in the project:
        
        {blocker}
        
        Provide a clear solution or workaround, considering the impact on the project timeline and other components.
        """
        
        response = await self.run(prompt)
        
        return response
