"""
Backend Developer Agent for the Agents Hub framework.

This module implements the Backend Developer agent, responsible for developing
backend services.
"""

from agents_hub import Agent
from agents_hub.llm.base import BaseLLM
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logger = logging.getLogger(__name__)

class BackendDeveloperAgent(Agent):
    """
    Agent responsible for developing backend services.
    
    This agent uses Claude 3.5 Sonnet for superior code generation capabilities.
    It designs and implements API endpoints, creates database models, implements
    business logic, and ensures security and performance.
    
    Example:
        ```python
        from agents_hub.coding.agents import BackendDeveloperAgent
        from agents_hub.llm.providers import ClaudeProvider
        
        # Initialize LLM provider
        llm = ClaudeProvider(api_key="your-anthropic-api-key")
        
        # Initialize Backend Developer agent
        backend_developer = BackendDeveloperAgent(
            llm=llm,
            project_name="My Project",
            project_description="A web application with user authentication.",
        )
        
        # Design API structure
        api_structure = await backend_developer.design_api_structure(
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
        Initialize the backend developer agent.
        
        Args:
            llm: LLM provider (Claude 3.5 Sonnet optimized for backend development)
            tools: Optional list of tools
            project_name: Name of the project
            project_description: Description of the project
        """
        system_prompt = f"""You are a backend developer specialized in FastAPI for the project: {project_name}.

Project Description:
{project_description}

Your tasks include:
1. Designing and implementing API endpoints
2. Creating database models and schemas
3. Implementing business logic
4. Ensuring security and performance
5. Writing unit tests for backend code
6. Documenting the API

You excel at writing clean, efficient, and well-documented code.
You follow best practices for FastAPI development and RESTful API design.

When developing backend code, consider:
- API design principles (RESTful, consistent, intuitive)
- Database design and optimization
- Authentication and authorization
- Input validation and error handling
- Performance and scalability
- Security best practices
- Testing and documentation

Always write code that is:
- Well-structured and organized
- Properly documented with docstrings and comments
- Secure and follows best practices
- Testable and maintainable
- Efficient and performant

You should use FastAPI with SQLAlchemy for database access, Pydantic for data validation,
and pytest for testing. The API will be deployed to AWS Lambda via API Gateway.
"""
        
        super().__init__(
            name="backend_developer",
            llm=llm,
            tools=tools or [],
            system_prompt=system_prompt,
        )
        
        self.project_name = project_name
        self.project_description = project_description
    
    async def design_api_structure(self, specifications: str) -> Dict[str, Any]:
        """
        Design the API structure based on specifications.
        
        Args:
            specifications: Project specifications
            
        Returns:
            API structure design
        """
        logger.info(f"Designing API structure for {self.project_name}")
        
        prompt = f"""
        Design the API structure for a FastAPI application based on the following specifications:
        
        {specifications}
        
        Your design should include:
        1. Project structure (folders and files)
        2. API routes and endpoints
        3. Database models
        4. Dependency injection setup
        5. Authentication and authorization approach
        6. Error handling strategy
        
        Format the response as a structured design document with code examples where appropriate.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "api_structure": response,
        }
    
    async def create_database_models(self, specifications: str) -> Dict[str, Any]:
        """
        Create database models based on specifications.
        
        Args:
            specifications: Project specifications
            
        Returns:
            Database models code
        """
        logger.info(f"Creating database models for {self.project_name}")
        
        prompt = f"""
        Create SQLAlchemy database models based on the following specifications:
        
        {specifications}
        
        For each model:
        1. Define the table name and schema
        2. Define columns with appropriate types and constraints
        3. Define relationships with other models
        4. Add indexes for performance
        5. Include docstrings and comments
        
        Use SQLAlchemy 2.0 syntax with type annotations.
        Format the response as Python code files that can be directly used in a FastAPI application.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "database_models": response,
        }
    
    async def implement_api_endpoint(self, endpoint_spec: str) -> Dict[str, Any]:
        """
        Implement an API endpoint based on specifications.
        
        Args:
            endpoint_spec: Endpoint specifications
            
        Returns:
            API endpoint implementation
        """
        logger.info(f"Implementing API endpoint for {self.project_name}")
        
        prompt = f"""
        Implement a FastAPI endpoint based on the following specification:
        
        {endpoint_spec}
        
        Your implementation should include:
        1. Route definition with appropriate HTTP method and path
        2. Request and response models using Pydantic
        3. Dependency injection for database access
        4. Input validation and error handling
        5. Business logic implementation
        6. Authentication and authorization checks
        7. Comprehensive docstrings and comments
        
        Format the response as Python code that can be directly used in a FastAPI application.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "api_endpoint": response,
        }
    
    async def write_unit_tests(self, implementation: str) -> Dict[str, Any]:
        """
        Write unit tests for an implementation.
        
        Args:
            implementation: Implementation code
            
        Returns:
            Unit tests code
        """
        logger.info(f"Writing unit tests for {self.project_name}")
        
        prompt = f"""
        Write comprehensive unit tests for the following FastAPI implementation:
        
        {implementation}
        
        Your tests should:
        1. Use pytest with pytest-asyncio for testing async code
        2. Include tests for successful operations
        3. Include tests for error cases and edge cases
        4. Use mocking for external dependencies
        5. Achieve high code coverage
        6. Be well-organized and maintainable
        
        Format the response as Python test code that can be directly used with pytest.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "unit_tests": response,
        }
    
    async def optimize_performance(self, implementation: str) -> Dict[str, Any]:
        """
        Optimize the performance of an implementation.
        
        Args:
            implementation: Implementation code
            
        Returns:
            Optimized implementation
        """
        logger.info(f"Optimizing performance for {self.project_name}")
        
        prompt = f"""
        Review the following FastAPI implementation and optimize it for performance:
        
        {implementation}
        
        Consider:
        1. Database query optimization
        2. Caching strategies
        3. Async operations
        4. Response payload optimization
        5. N+1 query problems
        6. Indexing and database access patterns
        
        Provide the optimized code with explanations of the changes made.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "optimized_implementation": response,
        }
