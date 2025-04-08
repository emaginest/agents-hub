"""
Coding Workforce for the Agents Hub framework.

This module implements the CodingWorkforce class, which coordinates a team of
specialized agents for software development.
"""

import os
import datetime
import logging
from typing import Dict, List, Any, Optional

from agents_hub import AgentWorkforce
from agents_hub.llm.base import BaseLLM
from agents_hub.utils.approval import ApprovalInterface

from agents_hub.coding.agents import (
    ProjectManagerAgent,
    AnalystAgent,
    BackendDeveloperAgent,
    FrontendDeveloperAgent,
    DevOpsEngineerAgent,
    SecurityEngineerAgent,
    QATesterAgent,
)
from agents_hub.tools.coding import (
    GitTool,
    AWSCDKTool,
    CodeGeneratorTool,
    CodeAnalyzerTool,
    TestingTool,
)

# Configure logging
logger = logging.getLogger(__name__)

class CodingWorkforce(AgentWorkforce):
    """
    A specialized workforce for software development with optimized LLMs.
    
    This workforce coordinates a team of agents for developing software,
    including backend APIs with FastAPI, frontend applications, and
    AWS deployment with CDK.
    
    Example:
        ```python
        from agents_hub.coding import CodingWorkforce
        from agents_hub.llm.providers import OpenAIProvider, ClaudeProvider
        
        # Initialize LLM providers
        openai_llm = OpenAIProvider(api_key="your-openai-api-key")
        claude_llm = ClaudeProvider(api_key="your-anthropic-api-key")
        
        # Create LLM mapping
        llm_mapping = {
            "project_manager": openai_llm,
            "analyst": claude_llm,
            "backend_developer": claude_llm,
            "frontend_developer": claude_llm,
            "devops_engineer": openai_llm,
            "security_engineer": claude_llm,
            "qa_tester": openai_llm,
        }
        
        # Initialize coding workforce
        workforce = CodingWorkforce(
            llm_mapping=llm_mapping,
            project_name="TaskManager",
            project_description="A task management application with a FastAPI backend and a React frontend.",
            output_dir="generated_code",
        )
        
        # Run the development process
        project_dir = await workforce.develop_project()
        ```
    """
    
    def __init__(
        self,
        llm_mapping: Dict[str, BaseLLM],
        project_name: str,
        project_description: str,
        output_dir: str = "generated_code",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the coding workforce.
        
        Args:
            llm_mapping: Mapping of agent names to LLM providers
            project_name: Name of the project
            project_description: Description of the project
            output_dir: Directory for generated code
            config: Optional configuration
        """
        self.llm_mapping = llm_mapping
        self.project_name = project_name
        self.project_description = project_description
        self.output_dir = output_dir
        self.config = config or {}
        
        # Create project output directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.project_dir = os.path.join(output_dir, f"{project_name.replace(' ', '_').lower()}_{timestamp}")
        os.makedirs(self.project_dir, exist_ok=True)
        
        # Create subdirectories
        self.backend_dir = os.path.join(self.project_dir, "backend")
        self.frontend_dir = os.path.join(self.project_dir, "frontend")
        self.infrastructure_dir = os.path.join(self.project_dir, "infrastructure")
        self.docs_dir = os.path.join(self.project_dir, "docs")
        
        os.makedirs(self.backend_dir, exist_ok=True)
        os.makedirs(self.frontend_dir, exist_ok=True)
        os.makedirs(self.infrastructure_dir, exist_ok=True)
        os.makedirs(self.docs_dir, exist_ok=True)
        
        # Initialize tools
        self.git_tool = GitTool()
        self.aws_cdk_tool = AWSCDKTool()
        self.code_generator_tool = CodeGeneratorTool()
        self.code_analyzer_tool = CodeAnalyzerTool()
        self.testing_tool = TestingTool()
        
        # Create agents with optimized LLMs
        self.project_manager = ProjectManagerAgent(
            llm=llm_mapping.get("project_manager"),
            tools=[self.code_generator_tool, self.code_analyzer_tool],
            project_name=project_name,
            project_description=project_description,
        )
        
        self.analyst = AnalystAgent(
            llm=llm_mapping.get("analyst"),
            tools=[self.code_generator_tool, self.code_analyzer_tool],
            project_name=project_name,
            project_description=project_description,
        )
        
        self.backend_developer = BackendDeveloperAgent(
            llm=llm_mapping.get("backend_developer"),
            tools=[self.code_generator_tool, self.code_analyzer_tool, self.testing_tool],
            project_name=project_name,
            project_description=project_description,
        )
        
        self.frontend_developer = FrontendDeveloperAgent(
            llm=llm_mapping.get("frontend_developer"),
            tools=[self.code_generator_tool, self.code_analyzer_tool, self.testing_tool],
            project_name=project_name,
            project_description=project_description,
        )
        
        self.devops_engineer = DevOpsEngineerAgent(
            llm=llm_mapping.get("devops_engineer"),
            tools=[self.git_tool, self.aws_cdk_tool, self.code_generator_tool],
            project_name=project_name,
            project_description=project_description,
        )
        
        self.security_engineer = SecurityEngineerAgent(
            llm=llm_mapping.get("security_engineer"),
            tools=[self.code_analyzer_tool],
            project_name=project_name,
            project_description=project_description,
        )
        
        self.qa_tester = QATesterAgent(
            llm=llm_mapping.get("qa_tester"),
            tools=[self.testing_tool, self.code_analyzer_tool],
            project_name=project_name,
            project_description=project_description,
        )
        
        # Initialize the approval interface
        self.approval_interface = ApprovalInterface()
        
        # Initialize the workforce with all agents
        super().__init__(
            agents=[
                self.project_manager,
                self.analyst,
                self.backend_developer,
                self.frontend_developer,
                self.devops_engineer,
                self.security_engineer,
                self.qa_tester,
            ],
            router_config={
                "default_agent": self.project_manager.name,
                "routing_strategy": "round_robin",
            },
        )
    
    async def develop_project(self) -> str:
        """
        Run the complete development process.
        
        Returns:
            Path to the generated project directory
        """
        logger.info(f"Starting development of project: {self.project_name}")
        logger.info(f"Generated code will be saved to: {self.project_dir}")
        
        try:
            # Step 1: Requirements Analysis
            await self._notify_step("Requirements Analysis")
            specifications = await self.analyst.analyze_requirements(self.project_description)
            
            # Step 2: Project Planning
            await self._notify_step("Project Planning")
            project_plan = await self.project_manager.create_project_plan(specifications["specifications"])
            
            # Step 3: Backend Development
            await self._notify_step("Backend Development")
            api_structure = await self.backend_developer.design_api_structure(specifications["specifications"])
            
            # Generate backend code
            await self._generate_backend_code(api_structure["api_structure"])
            
            # Step 4: Frontend Development
            await self._notify_step("Frontend Development")
            component_structure = await self.frontend_developer.design_component_structure(specifications["specifications"])
            
            # Generate frontend code
            await self._generate_frontend_code(component_structure["component_structure"])
            
            # Step 5: Infrastructure Development
            await self._notify_step("Infrastructure Development")
            infrastructure_design = await self.devops_engineer.design_infrastructure(specifications["specifications"])
            
            # Generate infrastructure code
            await self._generate_infrastructure_code(infrastructure_design["infrastructure_design"])
            
            # Step 6: Security Implementation
            await self._notify_step("Security Implementation")
            security_architecture = await self.security_engineer.design_security_architecture(specifications["specifications"])
            
            # Implement security measures
            await self._implement_security_measures(security_architecture["security_architecture"])
            
            # Step 7: Testing
            await self._notify_step("Testing")
            test_plan = await self.qa_tester.create_test_plan(specifications["specifications"])
            
            # Generate tests
            await self._generate_tests(test_plan["test_plan"])
            
            # Step 8: Documentation
            await self._notify_step("Documentation")
            await self._generate_documentation(specifications["specifications"])
            
            # Step 9: Git Repository Initialization
            await self._notify_step("Git Repository Initialization")
            await self.devops_engineer.initialize_git_repository(self.project_dir)
            
            # Step 10: Commit Changes
            await self._notify_step("Committing Changes")
            await self.devops_engineer.commit_changes(self.project_dir, "Initial commit")
            
            # Step 11: Deployment (with human approval)
            await self._notify_step("Deployment")
            await self._deploy_project()
            
            logger.info(f"Project development completed. Code is available at: {self.project_dir}")
            return self.project_dir
        
        except Exception as e:
            logger.exception(f"Error during project development: {str(e)}")
            raise
    
    async def _notify_step(self, step: str) -> None:
        """
        Notify the user about the current development step.
        
        Args:
            step: Current development step
        """
        await self.approval_interface.notify(
            f"Starting development step: {step}",
            {
                "Project": self.project_name,
                "Step": step,
                "Directory": self.project_dir,
            }
        )
    
    async def _generate_backend_code(self, api_structure: str) -> None:
        """
        Generate backend code based on API structure.
        
        Args:
            api_structure: API structure design
        """
        logger.info(f"Generating backend code for {self.project_name}")
        
        # Create main FastAPI app
        main_app_content = await self.backend_developer.run(
            f"Create a main.py file for a FastAPI application based on the following API structure:\n\n{api_structure}"
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(self.backend_dir, "main.py"),
            "content": main_app_content,
        })
        
        # Create database models
        models_content = await self.backend_developer.run(
            f"Create database models using SQLAlchemy based on the following API structure:\n\n{api_structure}"
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(self.backend_dir, "models.py"),
            "content": models_content,
        })
        
        # Create API routes
        routes_dir = os.path.join(self.backend_dir, "routes")
        await self.code_generator_tool.run({
            "operation": "create_directory",
            "path": routes_dir,
        })
        
        # Create __init__.py for routes
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(routes_dir, "__init__.py"),
            "content": "# Routes package\n",
        })
        
        # Create requirements.txt
        requirements_content = await self.backend_developer.run(
            "Create a requirements.txt file for a FastAPI application with SQLAlchemy, Pydantic, and other necessary dependencies."
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(self.backend_dir, "requirements.txt"),
            "content": requirements_content,
        })
    
    async def _generate_frontend_code(self, component_structure: str) -> None:
        """
        Generate frontend code based on component structure.
        
        Args:
            component_structure: Component structure design
        """
        logger.info(f"Generating frontend code for {self.project_name}")
        
        # Create package.json
        package_json_content = await self.frontend_developer.run(
            f"Create a package.json file for a React application with TypeScript based on the following component structure:\n\n{component_structure}"
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(self.frontend_dir, "package.json"),
            "content": package_json_content,
        })
        
        # Create tsconfig.json
        tsconfig_content = await self.frontend_developer.run(
            "Create a tsconfig.json file for a React application with TypeScript."
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(self.frontend_dir, "tsconfig.json"),
            "content": tsconfig_content,
        })
        
        # Create src directory
        src_dir = os.path.join(self.frontend_dir, "src")
        await self.code_generator_tool.run({
            "operation": "create_directory",
            "path": src_dir,
        })
        
        # Create index.tsx
        index_content = await self.frontend_developer.run(
            "Create an index.tsx file for a React application with TypeScript."
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(src_dir, "index.tsx"),
            "content": index_content,
        })
        
        # Create App.tsx
        app_content = await self.frontend_developer.run(
            f"Create an App.tsx file for a React application based on the following component structure:\n\n{component_structure}"
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(src_dir, "App.tsx"),
            "content": app_content,
        })
        
        # Create components directory
        components_dir = os.path.join(src_dir, "components")
        await self.code_generator_tool.run({
            "operation": "create_directory",
            "path": components_dir,
        })
    
    async def _generate_infrastructure_code(self, infrastructure_design: str) -> None:
        """
        Generate infrastructure code based on infrastructure design.
        
        Args:
            infrastructure_design: Infrastructure design
        """
        logger.info(f"Generating infrastructure code for {self.project_name}")
        
        # Create CDK app
        cdk_app_content = await self.devops_engineer.run(
            f"Create a CDK app.ts file based on the following infrastructure design:\n\n{infrastructure_design}"
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(self.infrastructure_dir, "app.ts"),
            "content": cdk_app_content,
        })
        
        # Create package.json for CDK
        package_json_content = await self.devops_engineer.run(
            "Create a package.json file for an AWS CDK application with TypeScript."
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(self.infrastructure_dir, "package.json"),
            "content": package_json_content,
        })
        
        # Create tsconfig.json for CDK
        tsconfig_content = await self.devops_engineer.run(
            "Create a tsconfig.json file for an AWS CDK application with TypeScript."
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(self.infrastructure_dir, "tsconfig.json"),
            "content": tsconfig_content,
        })
        
        # Create lib directory
        lib_dir = os.path.join(self.infrastructure_dir, "lib")
        await self.code_generator_tool.run({
            "operation": "create_directory",
            "path": lib_dir,
        })
        
        # Create stack file
        stack_content = await self.devops_engineer.run(
            f"Create a stack.ts file for an AWS CDK application based on the following infrastructure design:\n\n{infrastructure_design}"
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(lib_dir, f"{self.project_name.lower().replace(' ', '-')}-stack.ts"),
            "content": stack_content,
        })
    
    async def _implement_security_measures(self, security_architecture: str) -> None:
        """
        Implement security measures based on security architecture.
        
        Args:
            security_architecture: Security architecture design
        """
        logger.info(f"Implementing security measures for {self.project_name}")
        
        # Create security configuration for API Gateway
        api_gateway_security = await self.security_engineer.implement_api_gateway_security(security_architecture)
        
        # Update infrastructure code with security measures
        security_stack_content = await self.security_engineer.run(
            f"Create a security-stack.ts file for an AWS CDK application based on the following security architecture:\n\n{security_architecture}"
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(self.infrastructure_dir, "lib", "security-stack.ts"),
            "content": security_stack_content,
        })
        
        # Create authentication implementation for backend
        auth_content = await self.security_engineer.run(
            f"Create an auth.py file for a FastAPI application based on the following security architecture:\n\n{security_architecture}"
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(self.backend_dir, "auth.py"),
            "content": auth_content,
        })
    
    async def _generate_tests(self, test_plan: str) -> None:
        """
        Generate tests based on test plan.
        
        Args:
            test_plan: Test plan
        """
        logger.info(f"Generating tests for {self.project_name}")
        
        # Create backend tests
        backend_tests_dir = os.path.join(self.backend_dir, "tests")
        await self.code_generator_tool.run({
            "operation": "create_directory",
            "path": backend_tests_dir,
        })
        
        # Create __init__.py for tests
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(backend_tests_dir, "__init__.py"),
            "content": "# Tests package\n",
        })
        
        # Create test_main.py
        test_main_content = await self.qa_tester.run(
            f"Create a test_main.py file for testing a FastAPI application based on the following test plan:\n\n{test_plan}"
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(backend_tests_dir, "test_main.py"),
            "content": test_main_content,
        })
        
        # Create frontend tests
        frontend_tests_dir = os.path.join(self.frontend_dir, "src", "__tests__")
        await self.code_generator_tool.run({
            "operation": "create_directory",
            "path": frontend_tests_dir,
        })
        
        # Create App.test.tsx
        test_app_content = await self.qa_tester.run(
            f"Create an App.test.tsx file for testing a React application based on the following test plan:\n\n{test_plan}"
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(frontend_tests_dir, "App.test.tsx"),
            "content": test_app_content,
        })
    
    async def _generate_documentation(self, specifications: str) -> None:
        """
        Generate documentation based on specifications.
        
        Args:
            specifications: Project specifications
        """
        logger.info(f"Generating documentation for {self.project_name}")
        
        # Create README.md
        readme_content = await self.project_manager.run(
            f"Create a README.md file for the project {self.project_name} based on the following specifications:\n\n{specifications}"
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(self.project_dir, "README.md"),
            "content": readme_content,
        })
        
        # Create API documentation
        api_docs_content = await self.backend_developer.run(
            f"Create API documentation for the project {self.project_name} based on the following specifications:\n\n{specifications}"
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(self.docs_dir, "api.md"),
            "content": api_docs_content,
        })
        
        # Create deployment documentation
        deployment_docs_content = await self.devops_engineer.run(
            f"Create deployment documentation for the project {self.project_name} based on the following specifications:\n\n{specifications}"
        )
        
        await self.code_generator_tool.run({
            "operation": "create_file",
            "path": os.path.join(self.docs_dir, "deployment.md"),
            "content": deployment_docs_content,
        })
    
    async def _deploy_project(self) -> None:
        """
        Deploy the project with human approval.
        """
        logger.info(f"Preparing deployment for {self.project_name}")
        
        # Ask if the user wants to deploy
        deploy_approved = await self.approval_interface.request_approval(
            "deploy_project",
            {
                "Project": self.project_name,
                "Directory": self.project_dir,
            },
            f"Do you want to deploy the project {self.project_name}?"
        )
        
        if not deploy_approved:
            logger.info(f"Deployment cancelled for {self.project_name}")
            return
        
        # Deploy infrastructure
        stack_name = f"{self.project_name.lower().replace(' ', '-')}-stack"
        await self.devops_engineer.deploy_cdk_stack(self.infrastructure_dir, stack_name)
        
        logger.info(f"Deployment completed for {self.project_name}")
