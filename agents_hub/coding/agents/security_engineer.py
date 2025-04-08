"""
Security Engineer Agent for the Agents Hub framework.

This module implements the Security Engineer agent, responsible for implementing
security measures with AWS API Gateway and other security best practices.
"""

from agents_hub import Agent
from agents_hub.llm.base import BaseLLM
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logger = logging.getLogger(__name__)

class SecurityEngineerAgent(Agent):
    """
    Agent responsible for implementing security measures.
    
    This agent uses Claude 3 Opus for strong reasoning about security concerns.
    It implements authentication and authorization, secures API endpoints,
    configures AWS security services, and ensures compliance with security standards.
    
    Example:
        ```python
        from agents_hub.coding.agents import SecurityEngineerAgent
        from agents_hub.llm.providers import ClaudeProvider
        
        # Initialize LLM provider
        llm = ClaudeProvider(api_key="your-anthropic-api-key")
        
        # Initialize Security Engineer agent
        security_engineer = SecurityEngineerAgent(
            llm=llm,
            project_name="My Project",
            project_description="A web application with user authentication.",
        )
        
        # Design security architecture
        security_architecture = await security_engineer.design_security_architecture(
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
        Initialize the security engineer agent.
        
        Args:
            llm: LLM provider (Claude 3 Opus optimized for security considerations)
            tools: Optional list of tools
            project_name: Name of the project
            project_description: Description of the project
        """
        system_prompt = f"""You are a security engineer responsible for implementing security measures for the project: {project_name}.

Project Description:
{project_description}

Your tasks include:
1. Implementing authentication and authorization
2. Securing API endpoints with AWS API Gateway
3. Configuring AWS security services (IAM, Cognito, etc.)
4. Identifying and mitigating security vulnerabilities
5. Ensuring compliance with security standards
6. Implementing secure coding practices

You excel at identifying security risks and implementing robust security measures.
You have a deep understanding of security best practices and AWS security services.

When implementing security measures, consider:
- Authentication and authorization mechanisms
- API security and input validation
- Data protection and encryption
- Infrastructure security
- Compliance requirements
- Secure coding practices
- Security monitoring and incident response

Always prioritize security while balancing usability and performance.
Your goal is to implement security measures that protect the application
without unnecessarily hindering user experience or development velocity.
"""
        
        super().__init__(
            name="security_engineer",
            llm=llm,
            tools=tools or [],
            system_prompt=system_prompt,
        )
        
        self.project_name = project_name
        self.project_description = project_description
    
    async def design_security_architecture(self, specifications: str) -> Dict[str, Any]:
        """
        Design the security architecture based on specifications.
        
        Args:
            specifications: Project specifications
            
        Returns:
            Security architecture design
        """
        logger.info(f"Designing security architecture for {self.project_name}")
        
        prompt = f"""
        Design a comprehensive security architecture based on the following specifications:
        
        {specifications}
        
        Your design should include:
        1. Authentication and authorization approach
        2. API security measures
        3. Data protection and encryption
        4. Infrastructure security
        5. Security monitoring and logging
        6. Compliance considerations
        
        The architecture should focus on AWS services such as Cognito, API Gateway, IAM, and WAF.
        Format the response as a structured design document with code examples where appropriate.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "security_architecture": response,
        }
    
    async def implement_api_gateway_security(self, api_spec: str) -> Dict[str, Any]:
        """
        Implement API Gateway security based on specifications.
        
        Args:
            api_spec: API specifications
            
        Returns:
            API Gateway security implementation
        """
        logger.info(f"Implementing API Gateway security for {self.project_name}")
        
        prompt = f"""
        Implement AWS API Gateway security measures based on the following API specification:
        
        {api_spec}
        
        Your implementation should include:
        1. API key configuration
        2. Usage plans and throttling
        3. Request validation
        4. Authorization (Cognito, Lambda authorizer, or IAM)
        5. CORS configuration
        6. WAF integration
        
        Format the response as AWS CDK code (TypeScript) that can be directly used for deployment.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "api_gateway_security": response,
        }
    
    async def implement_authentication(self, requirements: str) -> Dict[str, Any]:
        """
        Implement authentication based on requirements.
        
        Args:
            requirements: Authentication requirements
            
        Returns:
            Authentication implementation
        """
        logger.info(f"Implementing authentication for {self.project_name}")
        
        prompt = f"""
        Implement authentication based on the following requirements:
        
        {requirements}
        
        Your implementation should include:
        1. User registration and login
        2. Token-based authentication
        3. Password policies and security
        4. Multi-factor authentication (if required)
        5. Session management
        6. Integration with frontend and backend
        
        Use AWS Cognito for authentication and provide code for both backend (FastAPI) and frontend (React).
        Format the response as code that can be directly used in the application.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "authentication_implementation": response,
        }
    
    async def implement_authorization(self, requirements: str) -> Dict[str, Any]:
        """
        Implement authorization based on requirements.
        
        Args:
            requirements: Authorization requirements
            
        Returns:
            Authorization implementation
        """
        logger.info(f"Implementing authorization for {self.project_name}")
        
        prompt = f"""
        Implement authorization based on the following requirements:
        
        {requirements}
        
        Your implementation should include:
        1. Role-based access control
        2. Permission management
        3. API endpoint protection
        4. Resource-level access control
        5. Integration with authentication system
        6. Authorization checks in frontend and backend
        
        Provide code for both backend (FastAPI) and frontend (React).
        Format the response as code that can be directly used in the application.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "authorization_implementation": response,
        }
    
    async def perform_security_review(self, code: str) -> Dict[str, Any]:
        """
        Perform a security review of code.
        
        Args:
            code: Code to review
            
        Returns:
            Security review results
        """
        logger.info(f"Performing security review for {self.project_name}")
        
        prompt = f"""
        Perform a comprehensive security review of the following code:
        
        {code}
        
        Your review should identify:
        1. Potential security vulnerabilities
        2. Input validation issues
        3. Authentication and authorization flaws
        4. Data protection concerns
        5. Secure coding practice violations
        6. Recommendations for improvement
        
        For each issue, provide a clear description, potential impact, and suggested fix.
        Format the response as a structured security report.
        """
        
        response = await self.run(prompt)
        
        return {
            "project_name": self.project_name,
            "security_review": response,
        }
