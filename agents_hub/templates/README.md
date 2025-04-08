# Templates Module for Agents Hub

This module provides code templates for various frameworks and technologies, primarily used by the coding agents to generate boilerplate code.

## Components

### FastAPI Templates

The fastapi directory contains templates for FastAPI applications:
- **Main App**: Basic FastAPI application structure
- **Routers**: API route definitions
- **Models**: Pydantic data models
- **Database**: Database connection and models
- **Authentication**: JWT authentication implementation
- **Testing**: Test fixtures and examples

### Frontend Templates

The frontend directory contains templates for frontend applications:
- **React**: React application templates
- **Vue**: Vue.js application templates
- **Angular**: Angular application templates
- **HTML/CSS**: Basic HTML and CSS templates
- **TypeScript**: TypeScript configuration and utilities

### AWS CDK Templates

The aws_cdk directory contains templates for AWS CDK infrastructure:
- **App**: Main CDK application
- **Stacks**: CDK stack definitions
- **Constructs**: Custom CDK constructs
- **API Gateway**: API Gateway configurations
- **Lambda**: Lambda function templates
- **DynamoDB**: DynamoDB table definitions
- **S3/CloudFront**: Static website hosting

## Usage

### Using Templates with Coding Agents

The templates are primarily used by the coding agents in the framework:

```python
from agents_hub.coding.agents import BackendDeveloperAgent
from agents_hub.llm.providers import ClaudeProvider

# Initialize LLM provider
llm = ClaudeProvider(api_key="your-anthropic-api-key")

# Create backend developer agent
backend_developer = BackendDeveloperAgent(
    llm=llm,
    project_name="TaskManager",
    project_description="A task management application with a FastAPI backend."
)

# The agent will use the FastAPI templates to generate code
api_structure = await backend_developer.design_api_structure(
    "Create an API for task management with CRUD operations."
)
```

### Accessing Templates Directly

You can also access the templates directly:

```python
from agents_hub.templates import TemplateManager

# Create template manager
template_manager = TemplateManager()

# Get FastAPI main app template
fastapi_main = template_manager.get_template(
    category="fastapi",
    name="main_app"
)

# Render the template with variables
rendered_code = template_manager.render_template(
    template=fastapi_main,
    variables={
        "app_name": "TaskManager",
        "description": "A task management API",
        "version": "1.0.0",
        "include_auth": True,
        "database_type": "postgresql"
    }
)

print(rendered_code)
```

### Creating Custom Templates

You can create custom templates for your specific needs:

```python
from agents_hub.templates import TemplateManager

# Create template manager
template_manager = TemplateManager()

# Add a custom template
custom_template = """
# {{app_name}}

## Description
{{description}}

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
uvicorn main:app --reload
```

{% if include_docs %}
## API Documentation
API documentation is available at http://localhost:8000/docs
{% endif %}
"""

template_manager.add_template(
    category="custom",
    name="readme",
    template=custom_template
)

# Render the custom template
rendered_readme = template_manager.render_template(
    category="custom",
    name="readme",
    variables={
        "app_name": "TaskManager",
        "description": "A task management API",
        "include_docs": True
    }
)

print(rendered_readme)
```

## Template Categories

### FastAPI Templates

```python
# Available FastAPI templates
fastapi_templates = template_manager.list_templates(category="fastapi")
print(fastapi_templates)
# ['main_app', 'router', 'model', 'database', 'auth', 'test']

# Get FastAPI router template
router_template = template_manager.get_template(
    category="fastapi",
    name="router"
)

# Render router template
rendered_router = template_manager.render_template(
    template=router_template,
    variables={
        "router_name": "tasks",
        "model_name": "Task",
        "endpoints": [
            {"method": "GET", "path": "/", "operation": "get_all"},
            {"method": "GET", "path": "/{id}", "operation": "get_by_id"},
            {"method": "POST", "path": "/", "operation": "create"},
            {"method": "PUT", "path": "/{id}", "operation": "update"},
            {"method": "DELETE", "path": "/{id}", "operation": "delete"}
        ],
        "include_auth": True
    }
)

print(rendered_router)
```

### Frontend Templates

```python
# Available React templates
react_templates = template_manager.list_templates(category="frontend/react")
print(react_templates)
# ['app', 'component', 'context', 'hook', 'router', 'api']

# Get React component template
component_template = template_manager.get_template(
    category="frontend/react",
    name="component"
)

# Render component template
rendered_component = template_manager.render_template(
    template=component_template,
    variables={
        "component_name": "TaskList",
        "props": [
            {"name": "tasks", "type": "Task[]"},
            {"name": "onDelete", "type": "(id: string) => void"},
            {"name": "onEdit", "type": "(task: Task) => void"}
        ],
        "imports": [
            {"name": "useState", "source": "react"},
            {"name": "Task", "source": "../types"}
        ],
        "use_typescript": True
    }
)

print(rendered_component)
```

### AWS CDK Templates

```python
# Available AWS CDK templates
cdk_templates = template_manager.list_templates(category="aws_cdk")
print(cdk_templates)
# ['app', 'stack', 'api_gateway', 'lambda', 'dynamodb', 'static_site']

# Get CDK stack template
stack_template = template_manager.get_template(
    category="aws_cdk",
    name="stack"
)

# Render stack template
rendered_stack = template_manager.render_template(
    template=stack_template,
    variables={
        "stack_name": "TaskManagerStack",
        "resources": [
            {"type": "api_gateway", "name": "api"},
            {"type": "lambda", "name": "taskFunction"},
            {"type": "dynamodb", "name": "taskTable"}
        ],
        "environment": "dev",
        "region": "us-east-1"
    }
)

print(rendered_stack)
```

## Integration with Other Modules

The templates module integrates with:
- **Coding Module**: For generating code in various frameworks
- **Tools Module**: For code generation tools
- **Utils Module**: For template rendering utilities
