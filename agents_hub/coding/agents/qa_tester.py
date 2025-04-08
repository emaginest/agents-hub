"""
QA Tester Agent for the Agents Hub framework.

This module implements the QA Tester agent, responsible for testing the application
and identifying issues.
"""

from agents_hub import Agent
from agents_hub.llm.base import BaseLLM
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logger = logging.getLogger(__name__)

class QATesterAgent(Agent):
    """
    Agent responsible for testing the application and identifying issues.
    
    This agent uses GPT-4o for generating test cases and identifying potential issues.
    It designs and implements test plans, writes automated tests, performs manual testing,
    and identifies and reports bugs.
    
    Example:
        ```python
        from agents_hub.coding.agents import QATesterAgent
        from agents_hub.llm.providers import OpenAIProvider
        from agents_hub.tools.coding import TestingTool
        
        # Initialize LLM provider
        llm = OpenAIProvider(api_key="your-openai-api-key")
        
        # Initialize QA Tester agent
        qa_tester = QATesterAgent(
            llm=llm,
            tools=[TestingTool()],
            project_name="My Project",
            project_description="A web application with user authentication.",
        )
        
        # Create test plan
        test_plan = await qa_tester.create_test_plan(
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
        Initialize the QA tester agent.
        
        Args:
            llm: LLM provider (GPT-4o optimized for QA testing)
            tools: Optional list of tools
            project_name: Name of the project
            project_description: Description of the project
        """
        system_prompt = f"""You are a QA tester responsible for testing the application and identifying issues for the project: {project_name}.

Project Description:
{project_description}

Your tasks include:
1. Designing and implementing test plans
2. Writing automated tests (unit, integration, end-to-end)
3. Performing manual testing
4. Identifying and reporting bugs
5. Verifying bug fixes
6. Ensuring quality standards are met

You excel at finding edge cases, identifying potential issues, and ensuring software quality.
You have a strong attention to detail and a systematic approach to testing.

When testing, consider:
- Functional requirements
- Edge cases and error handling
- Performance and scalability
- Security and data validation
- User experience and accessibility
- Cross-browser and cross-device compatibility

Always be thorough, systematic, and detail-oriented in your testing approach.
Your goal is to identify issues before they reach production and ensure
the application meets quality standards.
"""
        
        super().__init__(
            name="qa_tester",
            llm=llm,
            tools=tools or [],
            system_prompt=system_prompt,
        )
        
        self.project_name = project_name
        self.project_description = project_description
    
    async def create_test_plan(self, specifications: str) -> Dict[str, Any]:
        """
        Create a test plan based on specifications.
        
        Args:
            specifications: Project specifications
            
        Returns:
            Test plan
        """
        logger.info(f"Creating test plan for {self.project_name}")
        
        prompt = f"""
        Create a comprehensive test plan based on the following specifications:
        
        {specifications}
        
        Your test plan should include:
        1. Test objectives and scope
        2. Test approach and methodology
        3. Test environments and tools
        4. Test cases organized by feature/component
        5. Test data requirements
        6. Test schedule and resources
        
        Format the response as a structured test plan document.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "test_plan": response,
        }
    
    async def write_api_tests(self, api_spec: str) -> Dict[str, Any]:
        """
        Write API tests based on specifications.
        
        Args:
            api_spec: API specifications
            
        Returns:
            API tests code
        """
        logger.info(f"Writing API tests for {self.project_name}")
        
        prompt = f"""
        Write comprehensive API tests based on the following API specification:
        
        {api_spec}
        
        Your tests should:
        1. Cover all API endpoints
        2. Test successful operations
        3. Test error cases and edge cases
        4. Validate response schemas
        5. Test authentication and authorization
        6. Include performance and load tests
        
        Use pytest for backend API testing.
        Format the response as Python code that can be directly used for testing.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "api_tests": response,
        }
    
    async def write_frontend_tests(self, component_spec: str) -> Dict[str, Any]:
        """
        Write frontend tests based on specifications.
        
        Args:
            component_spec: Component specifications
            
        Returns:
            Frontend tests code
        """
        logger.info(f"Writing frontend tests for {self.project_name}")
        
        prompt = f"""
        Write comprehensive frontend tests based on the following component specification:
        
        {component_spec}
        
        Your tests should:
        1. Test component rendering
        2. Test user interactions
        3. Test state changes
        4. Test error states and edge cases
        5. Test accessibility
        6. Test integration with other components
        
        Use Jest and React Testing Library for frontend testing.
        Format the response as TypeScript code that can be directly used for testing.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "frontend_tests": response,
        }
    
    async def write_e2e_tests(self, user_flows: str) -> Dict[str, Any]:
        """
        Write end-to-end tests based on user flows.
        
        Args:
            user_flows: User flow descriptions
            
        Returns:
            End-to-end tests code
        """
        logger.info(f"Writing end-to-end tests for {self.project_name}")
        
        prompt = f"""
        Write comprehensive end-to-end tests based on the following user flows:
        
        {user_flows}
        
        Your tests should:
        1. Test complete user journeys
        2. Validate UI elements and interactions
        3. Test data persistence and state management
        4. Test error handling and recovery
        5. Test performance and responsiveness
        6. Test cross-browser compatibility
        
        Use Cypress for end-to-end testing.
        Format the response as TypeScript code that can be directly used for testing.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "e2e_tests": response,
        }
    
    async def identify_bugs(self, implementation: str) -> Dict[str, Any]:
        """
        Identify bugs in an implementation.
        
        Args:
            implementation: Implementation code
            
        Returns:
            Bug report
        """
        logger.info(f"Identifying bugs for {self.project_name}")
        
        prompt = f"""
        Review the following implementation and identify potential bugs and issues:
        
        {implementation}
        
        Your review should identify:
        1. Functional bugs
        2. Logic errors
        3. Edge cases not handled
        4. Performance issues
        5. Security vulnerabilities
        6. Usability issues
        
        For each issue, provide a clear description, steps to reproduce, expected vs. actual behavior, and suggested fix.
        Format the response as a structured bug report.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "bug_report": response,
        }
