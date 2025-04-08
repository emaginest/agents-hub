"""
Simple example of using the coding agents and tools from the agents-hub framework.

This example demonstrates how to use individual coding agents and tools
from the agents-hub framework to perform specific tasks.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

from agents_hub.llm.providers import OpenAIProvider, ClaudeProvider
from agents_hub.coding.agents import (
    BackendDeveloperAgent,
    SecurityEngineerAgent,
)
from agents_hub.tools.coding import (
    CodeGeneratorTool,
    CodeAnalyzerTool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Run the simple coding agents example."""
    # Load environment variables
    load_dotenv()
    
    # Check for required API keys
    if not os.environ.get("OPENAI_API_KEY") or not os.environ.get("ANTHROPIC_API_KEY"):
        logger.error("Both OPENAI_API_KEY and ANTHROPIC_API_KEY environment variables are required")
        return
    
    # Initialize LLM providers
    openai_llm = OpenAIProvider(api_key=os.environ["OPENAI_API_KEY"])
    claude_llm = ClaudeProvider(api_key=os.environ["ANTHROPIC_API_KEY"])
    
    # Initialize tools
    code_generator = CodeGeneratorTool()
    code_analyzer = CodeAnalyzerTool()
    
    # Initialize agents
    backend_developer = BackendDeveloperAgent(
        llm=claude_llm,
        tools=[code_generator, code_analyzer],
        project_name="SimpleAPI",
        project_description="A simple FastAPI application with user authentication",
    )
    
    security_engineer = SecurityEngineerAgent(
        llm=claude_llm,
        tools=[code_analyzer],
        project_name="SimpleAPI",
        project_description="A simple FastAPI application with user authentication",
    )
    
    # Create output directory
    output_dir = "examples/coding_workforce/simple_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Generate API structure
    logger.info("Generating API structure...")
    api_structure = await backend_developer.design_api_structure(
        """
        Create a simple API with the following endpoints:
        - POST /auth/register: Register a new user
        - POST /auth/login: Login a user
        - GET /users/me: Get current user profile
        - PUT /users/me: Update current user profile
        """
    )
    
    # Step 2: Generate main.py file
    logger.info("Generating main.py file...")
    main_py_content = await backend_developer.run(
        f"Create a main.py file for a FastAPI application based on the following API structure:\n\n{api_structure['api_structure']}"
    )
    
    # Save main.py file
    await code_generator.run({
        "operation": "create_file",
        "path": os.path.join(output_dir, "main.py"),
        "content": main_py_content,
    })
    
    # Step 3: Security review
    logger.info("Performing security review...")
    security_review = await security_engineer.perform_security_review(main_py_content)
    
    # Save security review
    await code_generator.run({
        "operation": "create_file",
        "path": os.path.join(output_dir, "security_review.md"),
        "content": security_review["security_review"],
    })
    
    # Step 4: Implement security improvements
    logger.info("Implementing security improvements...")
    auth_py_content = await security_engineer.run(
        f"Create an auth.py file with secure authentication implementation based on the security review:\n\n{security_review['security_review']}"
    )
    
    # Save auth.py file
    await code_generator.run({
        "operation": "create_file",
        "path": os.path.join(output_dir, "auth.py"),
        "content": auth_py_content,
    })
    
    logger.info(f"Example completed! Output is available in {output_dir}")

if __name__ == "__main__":
    asyncio.run(main())
