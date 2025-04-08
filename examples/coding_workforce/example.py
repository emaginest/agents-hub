"""
Coding Workforce Example

This example demonstrates how to use the CodingWorkforce class from the agents-hub
framework to develop a complete software project with specialized agents.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

from agents_hub.coding import CodingWorkforce
from agents_hub.llm.providers import OpenAIProvider, ClaudeProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("coding_workforce.log"),
    ],
)
logger = logging.getLogger(__name__)


async def main():
    """Run the coding workforce example."""
    # Load environment variables
    load_dotenv()

    # Check for required API keys
    if not os.environ.get("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is required")
        return

    if not os.environ.get("ANTHROPIC_API_KEY"):
        logger.error("ANTHROPIC_API_KEY environment variable is required")
        return

    # Initialize LLM providers
    openai_llm = OpenAIProvider(api_key=os.environ["OPENAI_API_KEY"])
    claude_llm = ClaudeProvider(api_key=os.environ["ANTHROPIC_API_KEY"])

    # Create LLM mapping for different agent roles
    llm_mapping = {
        "project_manager": openai_llm,  # GPT-4o for project management
        "analyst": claude_llm,  # Claude 3 Opus for requirements analysis
        "backend_developer": claude_llm,  # Claude 3.5 Sonnet for backend development
        "frontend_developer": claude_llm,  # Claude 3.5 Sonnet for frontend development
        "devops_engineer": openai_llm,  # GPT-4o for DevOps
        "security_engineer": claude_llm,  # Claude 3 Opus for security
        "qa_tester": openai_llm,  # GPT-4o for QA testing
    }

    # Initialize coding workforce with LLM mapping
    workforce = CodingWorkforce(
        llm_mapping=llm_mapping,
        project_name="TaskManager",
        project_description="""
        A task management application with a FastAPI backend and a React frontend.
        The API should provide CRUD operations for tasks with the following fields:
        - id: unique identifier
        - title: task title
        - description: task description
        - status: pending, in-progress, completed
        - due_date: deadline for the task
        - priority: low, medium, high

        The frontend should provide a user-friendly interface for:
        - Viewing all tasks with filtering and sorting options
        - Creating new tasks
        - Updating existing tasks
        - Deleting tasks

        The application should be deployed to AWS using CDK with:
        - API Gateway for API management
        - Lambda for serverless backend
        - DynamoDB for data storage
        - S3 and CloudFront for frontend hosting
        """,
        output_dir="examples/coding_workforce/generated_code",
    )

    # Run the development process
    try:
        project_dir = await workforce.develop_project()

        logger.info(
            f"\nDevelopment completed! Generated code is available at: {project_dir}"
        )
        logger.info(
            "You can review the code and approve Git operations and AWS deployments when prompted."
        )

    except Exception as e:
        logger.exception(f"Error during development: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
