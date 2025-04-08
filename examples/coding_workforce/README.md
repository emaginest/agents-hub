# Coding Workforce Example with Specialized LLMs

This example demonstrates how to use the agents-hub framework's built-in coding agents and tools to create a team of specialized agents for software development, each using an LLM optimized for their specific role. The workforce generates a complete project structure with backend, frontend, and infrastructure code.

## Overview

The coding workforce consists of the following agents, each using an optimized LLM:

1. **Project Manager Agent (GPT-4o)**: Coordinates the development process
2. **Requirements Analyst Agent (Claude 3 Opus)**: Analyzes requirements and creates specifications
3. **Backend Developer Agent (Claude 3.5 Sonnet)**: Develops FastAPI backend services
4. **Frontend Developer Agent (Claude 3.5 Sonnet)**: Develops frontend applications
5. **DevOps Engineer Agent (GPT-4o)**: Handles AWS CDK deployment, Git operations, and infrastructure
6. **Security Engineer Agent (Claude 3 Opus)**: Implements security measures with AWS API Gateway
7. **QA Tester Agent (GPT-4o)**: Tests the application and identifies issues

## LLM Selection Rationale

Each agent uses an LLM that is optimized for their specific tasks:

- **GPT-4o**: Used for project management, DevOps, and QA testing due to its strong reasoning and planning capabilities
- **Claude 3 Opus**: Used for requirements analysis and security engineering due to its excellent understanding of complex requirements and security concerns
- **Claude 3.5 Sonnet**: Used for backend and frontend development due to its superior code generation capabilities

## Generated Code Structure

The workforce generates code in the `generated_code` directory with the following structure:

```
generated_code/
└── [project_name]_[timestamp]/
    ├── backend/                    # FastAPI backend application
    ├── frontend/                   # React frontend application
    ├── infrastructure/             # AWS CDK infrastructure code
    ├── docs/                       # Project documentation
    └── README.md                   # Project overview
```

## Human Approval for Critical Operations

The DevOps Engineer agent requires human approval for critical operations:

- Git push operations
- AWS CDK deployments

This ensures that you have control over when code is committed to repositories or deployed to AWS.

## Setup

### Prerequisites

- Python 3.9+
- Node.js 14+
- AWS CLI configured
- Git

### API Keys

To use this example, you'll need API keys for the following providers:

- OpenAI (for GPT-4o)
- Anthropic (for Claude 3 Opus and Claude 3.5 Sonnet)

Create a `.env` file with the following variables:

```
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### Installation

```bash
pip install -e .
```

This will install the agents-hub package in development mode, making the coding agents and tools available for use.

### Running the Example

```bash
python examples/coding_workforce/example.py
```

This will:

1. Initialize the coding workforce
2. Generate a complete project based on the requirements
3. Save the generated code to the `generated_code` directory
4. Request human approval for Git and AWS operations

## Simple Example

For a simpler example that demonstrates using individual coding agents and tools, see `simple_example.py`:

```bash
python examples/coding_workforce/simple_example.py
```

This example:

1. Uses the BackendDeveloperAgent to design an API structure
2. Generates a main.py file for a FastAPI application
3. Uses the SecurityEngineerAgent to perform a security review
4. Implements security improvements based on the review

## Customization

You can customize the project by modifying the `project_description` in `example.py` and by adjusting the LLM mapping to use different models for different agents. The project description should include:

- Backend requirements (API endpoints, data models, etc.)
- Frontend requirements (UI components, features, etc.)
- Infrastructure requirements (AWS services, security considerations, etc.)

## Example Project

The default example creates a task management application with:

- FastAPI backend with CRUD operations for tasks
- React frontend with a user-friendly interface
- AWS CDK infrastructure for serverless deployment
- API Gateway for API management and security
