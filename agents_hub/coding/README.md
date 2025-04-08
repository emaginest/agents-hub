# Coding Module for Agents Hub

This module provides specialized agents and tools for software development tasks. It includes a team of agents optimized for different roles in the software development process, along with tools for Git operations, AWS CDK deployment, code generation, code analysis, and testing.

## Components

### Agents

- **Project Manager Agent**: Coordinates the development process and manages tasks
- **Requirements Analyst Agent**: Analyzes requirements and creates detailed specifications
- **Backend Developer Agent**: Develops backend services
- **Frontend Developer Agent**: Develops frontend applications
- **DevOps Engineer Agent**: Handles infrastructure, Git operations, and deployment
- **Security Engineer Agent**: Implements security measures
- **QA Tester Agent**: Tests applications and identifies issues

### Tools

- **Git Tool**: Handles Git operations with human approval for critical actions
- **AWS CDK Tool**: Manages AWS CDK operations with human approval for deployments
- **Code Generator Tool**: Generates code based on specifications
- **Code Analyzer Tool**: Analyzes code quality and structure
- **Testing Tool**: Runs tests and analyzes test results

### Workforce

- **CodingWorkforce**: Coordinates a team of specialized agents for software development

## Usage

### Using the CodingWorkforce

```python
from agents_hub.coding import CodingWorkforce
from agents_hub.llm.providers import OpenAIProvider, ClaudeProvider

# Initialize LLM providers
openai_llm = OpenAIProvider(api_key="your-openai-api-key")
claude_llm = ClaudeProvider(api_key="your-anthropic-api-key")

# Create LLM mapping for different agent roles
llm_mapping = {
    "project_manager": openai_llm,  # GPT-4o for project management
    "analyst": claude_llm,          # Claude 3 Opus for requirements analysis
    "backend_developer": claude_llm, # Claude 3.5 Sonnet for backend development
    "frontend_developer": claude_llm, # Claude 3.5 Sonnet for frontend development
    "devops_engineer": openai_llm,   # GPT-4o for DevOps
    "security_engineer": claude_llm, # Claude 3 Opus for security
    "qa_tester": openai_llm,         # GPT-4o for QA testing
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

### Using Individual Agents and Tools

```python
from agents_hub.llm.providers import ClaudeProvider
from agents_hub.coding.agents import BackendDeveloperAgent
from agents_hub.tools.coding import CodeGeneratorTool

# Initialize LLM provider
llm = ClaudeProvider(api_key="your-anthropic-api-key")

# Initialize tools
code_generator = CodeGeneratorTool()

# Initialize agent
backend_developer = BackendDeveloperAgent(
    llm=llm,
    tools=[code_generator],
    project_name="SimpleAPI",
    project_description="A simple FastAPI application",
)

# Use the agent
api_structure = await backend_developer.design_api_structure(
    "Create a simple API with user authentication"
)

# Generate code
main_py_content = await backend_developer.run(
    f"Create a main.py file based on the API structure:\n\n{api_structure['api_structure']}"
)

# Save the code
await code_generator.run({
    "operation": "create_file",
    "path": "output/main.py",
    "content": main_py_content,
})
```

## Human Approval

Critical operations like Git pushes and AWS deployments require human approval before proceeding. This ensures that you have control over when code is committed to repositories or deployed to AWS.

## Templates

The module includes templates for code generation:

- FastAPI backend templates
- React frontend templates
- AWS CDK infrastructure templates

These templates are used by the code generator tool to create boilerplate code.
