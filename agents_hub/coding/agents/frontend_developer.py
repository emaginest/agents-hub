"""
Frontend Developer Agent for the Agents Hub framework.

This module implements the Frontend Developer agent, responsible for developing
frontend applications.
"""

from agents_hub import Agent
from agents_hub.llm.base import BaseLLM
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logger = logging.getLogger(__name__)

class FrontendDeveloperAgent(Agent):
    """
    Agent responsible for developing frontend applications.
    
    This agent uses Claude 3.5 Sonnet for strong frontend code generation capabilities.
    It designs and implements user interfaces, creates components, implements
    client-side logic, and ensures responsive and accessible design.
    
    Example:
        ```python
        from agents_hub.coding.agents import FrontendDeveloperAgent
        from agents_hub.llm.providers import ClaudeProvider
        
        # Initialize LLM provider
        llm = ClaudeProvider(api_key="your-anthropic-api-key")
        
        # Initialize Frontend Developer agent
        frontend_developer = FrontendDeveloperAgent(
            llm=llm,
            project_name="My Project",
            project_description="A web application with user authentication.",
        )
        
        # Design component structure
        component_structure = await frontend_developer.design_component_structure(
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
        Initialize the frontend developer agent.
        
        Args:
            llm: LLM provider (Claude 3.5 Sonnet optimized for frontend development)
            tools: Optional list of tools
            project_name: Name of the project
            project_description: Description of the project
        """
        system_prompt = f"""You are a frontend developer specialized in React for the project: {project_name}.

Project Description:
{project_description}

Your tasks include:
1. Designing and implementing user interfaces
2. Creating reusable React components
3. Implementing client-side logic and API integration
4. Ensuring responsive and accessible design
5. Writing unit tests for frontend code
6. Optimizing performance and user experience

You excel at writing clean, efficient, and well-structured frontend code.
You follow best practices for React development and modern frontend architecture.

When developing frontend code, consider:
- Component design and reusability
- State management
- API integration and data fetching
- Responsive design for different devices
- Accessibility (WCAG compliance)
- Performance optimization
- Testing and maintainability

Always write code that is:
- Well-structured and organized
- Properly documented with comments
- Accessible and follows best practices
- Testable and maintainable
- Efficient and performant

You should use React with TypeScript, along with modern tools and libraries such as:
- React Router for routing
- React Query for data fetching
- Styled Components or Tailwind CSS for styling
- Jest and React Testing Library for testing
"""
        
        super().__init__(
            name="frontend_developer",
            llm=llm,
            tools=tools or [],
            system_prompt=system_prompt,
        )
        
        self.project_name = project_name
        self.project_description = project_description
    
    async def design_component_structure(self, specifications: str) -> Dict[str, Any]:
        """
        Design the component structure based on specifications.
        
        Args:
            specifications: Project specifications
            
        Returns:
            Component structure design
        """
        logger.info(f"Designing component structure for {self.project_name}")
        
        prompt = f"""
        Design the React component structure for a frontend application based on the following specifications:
        
        {specifications}
        
        Your design should include:
        1. Project structure (folders and files)
        2. Component hierarchy and relationships
        3. State management approach
        4. Routing structure
        5. API integration strategy
        6. Styling approach
        
        Format the response as a structured design document with code examples where appropriate.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "component_structure": response,
        }
    
    async def create_react_component(self, component_spec: str) -> Dict[str, Any]:
        """
        Create a React component based on specifications.
        
        Args:
            component_spec: Component specifications
            
        Returns:
            React component code
        """
        logger.info(f"Creating React component for {self.project_name}")
        
        prompt = f"""
        Create a React component based on the following specification:
        
        {component_spec}
        
        Your implementation should include:
        1. Component definition with TypeScript interfaces
        2. Props and state management
        3. Hooks for side effects and lifecycle
        4. Event handlers and user interactions
        5. Styling (using Styled Components or Tailwind CSS)
        6. Accessibility considerations
        7. Comprehensive comments
        
        Format the response as TypeScript/React code that can be directly used in a React application.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "react_component": response,
        }
    
    async def implement_api_integration(self, api_spec: str) -> Dict[str, Any]:
        """
        Implement API integration based on specifications.
        
        Args:
            api_spec: API specifications
            
        Returns:
            API integration code
        """
        logger.info(f"Implementing API integration for {self.project_name}")
        
        prompt = f"""
        Implement API integration for a React application based on the following API specification:
        
        {api_spec}
        
        Your implementation should include:
        1. API client setup (using axios or fetch)
        2. Custom hooks for data fetching
        3. Request and response type definitions
        4. Error handling and loading states
        5. Caching and optimization strategies
        6. Authentication handling
        
        Use React Query for efficient data fetching and state management.
        Format the response as TypeScript code that can be directly used in a React application.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "api_integration": response,
        }
    
    async def write_component_tests(self, component: str) -> Dict[str, Any]:
        """
        Write tests for a React component.
        
        Args:
            component: Component code
            
        Returns:
            Component tests code
        """
        logger.info(f"Writing component tests for {self.project_name}")
        
        prompt = f"""
        Write comprehensive tests for the following React component:
        
        {component}
        
        Your tests should:
        1. Use Jest and React Testing Library
        2. Test component rendering
        3. Test user interactions and events
        4. Test props and state changes
        5. Test error states and edge cases
        6. Mock external dependencies and API calls
        
        Format the response as TypeScript test code that can be directly used with Jest.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "component_tests": response,
        }
    
    async def optimize_user_experience(self, implementation: str) -> Dict[str, Any]:
        """
        Optimize the user experience of an implementation.
        
        Args:
            implementation: Implementation code
            
        Returns:
            Optimized implementation
        """
        logger.info(f"Optimizing user experience for {self.project_name}")
        
        prompt = f"""
        Review the following React implementation and optimize it for user experience:
        
        {implementation}
        
        Consider:
        1. Loading states and skeleton screens
        2. Error handling and user feedback
        3. Form validation and error messages
        4. Accessibility improvements
        5. Performance optimization
        6. Responsive design enhancements
        
        Provide the optimized code with explanations of the changes made.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "optimized_implementation": response,
        }
