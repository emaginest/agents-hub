"""
Requirements Analyst Agent for the Agents Hub framework.

This module implements the Requirements Analyst agent, responsible for analyzing
requirements and creating detailed specifications.
"""

from agents_hub import Agent
from agents_hub.llm.base import BaseLLM
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logger = logging.getLogger(__name__)

class AnalystAgent(Agent):
    """
    Agent responsible for analyzing requirements and creating specifications.
    
    This agent uses Claude 3 Opus for excellent understanding of complex requirements.
    It analyzes project requirements, creates detailed specifications, identifies
    edge cases, and ensures requirements are clear and complete.
    
    Example:
        ```python
        from agents_hub.coding.agents import AnalystAgent
        from agents_hub.llm.providers import ClaudeProvider
        
        # Initialize LLM provider
        llm = ClaudeProvider(api_key="your-anthropic-api-key")
        
        # Initialize Requirements Analyst agent
        analyst = AnalystAgent(
            llm=llm,
            project_name="My Project",
            project_description="A web application with user authentication.",
        )
        
        # Analyze requirements
        specifications = await analyst.analyze_requirements(
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
        Initialize the requirements analyst agent.
        
        Args:
            llm: LLM provider (Claude 3 Opus optimized for requirements analysis)
            tools: Optional list of tools
            project_name: Name of the project
            project_description: Description of the project
        """
        system_prompt = f"""You are a requirements analyst responsible for analyzing requirements and creating detailed specifications for the project: {project_name}.

Project Description:
{project_description}

Your tasks include:
1. Analyzing high-level requirements and breaking them down into detailed specifications
2. Identifying edge cases and potential issues
3. Creating user stories and acceptance criteria
4. Defining data models and API contracts
5. Ensuring requirements are clear, complete, and testable
6. Collaborating with other team members to clarify requirements

You excel at understanding complex requirements and translating them into clear, actionable specifications.
You have a strong attention to detail and can identify potential issues before they become problems.

When analyzing requirements, consider:
- User needs and expectations
- Technical constraints and possibilities
- Security and compliance requirements
- Performance and scalability requirements
- Maintainability and extensibility

Always be thorough, precise, and comprehensive in your specifications.
"""
        
        super().__init__(
            name="analyst",
            llm=llm,
            tools=tools or [],
            system_prompt=system_prompt,
        )
        
        self.project_name = project_name
        self.project_description = project_description
    
    async def analyze_requirements(self, requirements: str) -> Dict[str, Any]:
        """
        Analyze requirements and create detailed specifications.
        
        Args:
            requirements: Project requirements
            
        Returns:
            Detailed specifications
        """
        logger.info(f"Analyzing requirements for {self.project_name}")
        
        prompt = f"""
        Analyze the following requirements and create detailed specifications:
        
        {requirements}
        
        Your analysis should include:
        1. A breakdown of functional requirements
        2. Non-functional requirements (performance, security, etc.)
        3. Data models with fields and relationships
        4. API endpoints with request/response formats
        5. User stories and acceptance criteria
        6. Edge cases and potential issues
        
        Format the response as a structured specification that can be used by developers.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "specifications": response,
        }
    
    async def create_data_models(self, requirements: str) -> Dict[str, Any]:
        """
        Create data models based on requirements.
        
        Args:
            requirements: Project requirements
            
        Returns:
            Data models
        """
        logger.info(f"Creating data models for {self.project_name}")
        
        prompt = f"""
        Based on the following requirements, create detailed data models:
        
        {requirements}
        
        For each data model, include:
        1. Model name
        2. Fields with types and constraints
        3. Relationships with other models
        4. Validation rules
        5. Example JSON representation
        
        Format the response as a structured specification that can be used by developers.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "data_models": response,
        }
    
    async def define_api_contract(self, requirements: str) -> Dict[str, Any]:
        """
        Define API contract based on requirements.
        
        Args:
            requirements: Project requirements
            
        Returns:
            API contract
        """
        logger.info(f"Defining API contract for {self.project_name}")
        
        prompt = f"""
        Based on the following requirements, define a detailed API contract:
        
        {requirements}
        
        For each API endpoint, include:
        1. HTTP method and path
        2. Request parameters and body schema
        3. Response schema with status codes
        4. Authentication and authorization requirements
        5. Rate limiting and caching considerations
        6. Example request and response
        
        Format the response as a structured API contract that follows RESTful principles and can be implemented with FastAPI.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "api_contract": response,
        }
    
    async def identify_edge_cases(self, specifications: str) -> Dict[str, Any]:
        """
        Identify edge cases and potential issues in specifications.
        
        Args:
            specifications: Project specifications
            
        Returns:
            Edge cases and potential issues
        """
        logger.info(f"Identifying edge cases for {self.project_name}")
        
        prompt = f"""
        Review the following specifications and identify edge cases and potential issues:
        
        {specifications}
        
        Consider:
        1. Input validation edge cases
        2. Error handling scenarios
        3. Concurrency and race conditions
        4. Security vulnerabilities
        5. Performance bottlenecks
        6. Scalability challenges
        
        For each issue, provide a clear description and suggested mitigation.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "edge_cases": response,
        }
