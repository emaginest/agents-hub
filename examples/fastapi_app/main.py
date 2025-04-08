"""
Example FastAPI application using the Agents Hub framework.
"""

import os
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
import uvicorn

from agents_hub import Agent, AgentWorkforce, CognitiveAgent
from agents_hub.llm.providers.openai import OpenAIProvider
from agents_hub.llm.providers.anthropic import ClaudeProvider
from agents_hub.llm.providers.google import GeminiProvider
from agents_hub.llm.providers.ollama import OllamaProvider
from agents_hub.memory.backends.postgres import PostgreSQLMemory
from agents_hub.tools.standard.calculator import CalculatorTool
from agents_hub.tools.standard.scraper import ScraperTool
from agents_hub.tools.standard.pgvector_tool import PGVectorTool
from agents_hub.tools.standard.mcp import MCPTool
from agents_hub.tools.standard.tavily import TavilyTool
from agents_hub.moderation import RuleBasedModerator, OpenAIModerator, ModerationRegistry
from agents_hub.monitoring import LangfuseMonitor
from agents_hub.cognitive import CognitiveArchitecture


# Models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    conversation_id: str = Field(..., description="Unique conversation identifier")
    agent_name: Optional[str] = Field(None, description="Optional agent name to use")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Agent response")
    agent: str = Field(..., description="Agent that generated the response")
    conversation_id: str = Field(..., description="Conversation identifier")


class AgentRequest(BaseModel):
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    system_prompt: str = Field(..., description="System prompt for the agent")
    llm_provider: str = Field(..., description="LLM provider (openai, claude, gemini, ollama)")
    llm_model: str = Field(..., description="LLM model name")
    enable_moderation: bool = Field(False, description="Whether to enable content moderation")
    moderation_action: str = Field("block", description="Action to take on moderation violation (block, warn, log)")


class AgentResponse(BaseModel):
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    llm_provider: str = Field(..., description="LLM provider")
    llm_model: str = Field(..., description="LLM model name")
    moderation_enabled: bool = Field(False, description="Whether content moderation is enabled")


# Initialize FastAPI app
app = FastAPI(
    title="Agents Hub API",
    description="API for interacting with the Agents Hub framework",
    version="0.1.0",
)

# Global variables
llm_providers = {}
agents = {}
workforce = None
memory = None
moderators = {}
tools = {}
monitor = None
cognitive_architecture = None


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global llm_providers, agents, workforce, memory, moderators, tools, monitor, cognitive_architecture

    # Initialize LLM providers
    if os.environ.get("OPENAI_API_KEY"):
        llm_providers["openai"] = OpenAIProvider(
            api_key=os.environ["OPENAI_API_KEY"],
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        )

    if os.environ.get("ANTHROPIC_API_KEY"):
        llm_providers["claude"] = ClaudeProvider(
            api_key=os.environ["ANTHROPIC_API_KEY"],
            model=os.environ.get("CLAUDE_MODEL", "claude-3-haiku-20240307"),
        )

    if os.environ.get("GOOGLE_API_KEY"):
        llm_providers["gemini"] = GeminiProvider(
            api_key=os.environ["GOOGLE_API_KEY"],
            model=os.environ.get("GEMINI_MODEL", "gemini-pro"),
        )

    # Ollama doesn't require an API key
    llm_providers["ollama"] = OllamaProvider(
        model=os.environ.get("OLLAMA_MODEL", "llama3"),
        base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
    )

    # Initialize memory if PostgreSQL is configured
    if all([
        os.environ.get("POSTGRES_HOST"),
        os.environ.get("POSTGRES_DB"),
        os.environ.get("POSTGRES_USER"),
        os.environ.get("POSTGRES_PASSWORD"),
    ]):
        memory = PostgreSQLMemory(
            host=os.environ["POSTGRES_HOST"],
            port=int(os.environ.get("POSTGRES_PORT", "5432")),
            database=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            table_prefix="agents_hub_",
        )

        # Initialize default LLM provider
        default_llm = next(iter(llm_providers.values()))

    # Initialize moderators
    # Rule-based moderator (no API key required)
    moderators["rule_based"] = RuleBasedModerator()

    # OpenAI moderator (if API key is available)
    if os.environ.get("OPENAI_API_KEY"):
        moderators["openai"] = OpenAIModerator(
            api_key=os.environ["OPENAI_API_KEY"],
        )

    # Create a combined moderator if both are available
    if "rule_based" in moderators and "openai" in moderators:
        moderators["combined"] = ModerationRegistry(
            moderators=[moderators["rule_based"], moderators["openai"]],
            mode="any",
        )

    # Initialize Langfuse monitoring if credentials are available
    if all([
        os.environ.get("LANGFUSE_PUBLIC_KEY"),
        os.environ.get("LANGFUSE_SECRET_KEY"),
    ]):
        monitor = LangfuseMonitor(
            public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
            secret_key=os.environ["LANGFUSE_SECRET_KEY"],
            host=os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com"),
            release=os.environ.get("APP_VERSION", "1.0.0"),
        )

    # Initialize cognitive architecture
    cognitive_architecture = CognitiveArchitecture()

    # Initialize tools
    tools["calculator"] = CalculatorTool()
    tools["scraper"] = ScraperTool()

    # Initialize Tavily search tool if API key is available
    if os.environ.get("TAVILY_API_KEY"):
        tools["tavily"] = TavilyTool(
            api_key=os.environ["TAVILY_API_KEY"],
            search_depth="basic",
            max_results=5,
        )

    # Initialize PGVector tool if PostgreSQL credentials are available
    if os.environ.get("POSTGRES_HOST"):
        tools["pgvector"] = PGVectorTool(
            llm=default_llm,
            host=os.environ["POSTGRES_HOST"],
            port=int(os.environ.get("POSTGRES_PORT", "5432")),
            database=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
        )

    # Initialize MCP tool for filesystem access
    try:
        tools["filesystem"] = MCPTool(
            server_name="filesystem",
            server_command="npx",
            server_args=["-y", "@modelcontextprotocol/server-filesystem", "./"],
            transport="stdio",
        )
    except Exception as e:
        print(f"Failed to initialize filesystem MCP tool: {e}")

    # Create default agents
    if "openai" in llm_providers:
        # Get the combined moderator if available, otherwise use rule-based
        default_moderator = moderators.get("combined", moderators.get("rule_based"))

        # Get the monitor if available
        default_monitor = monitor

        # Create a researcher agent
        researcher_tools = [tools["calculator"], tools["scraper"]]
        if "tavily" in tools:
            researcher_tools.append(tools["tavily"])

        agents["researcher"] = Agent(
            name="researcher",
            llm=llm_providers["openai"],
            memory=memory,
            tools=researcher_tools,
            system_prompt="You are a helpful research assistant. Your job is to provide accurate, well-researched information on any topic. Use the web_scraper tool to gather information when needed. If available, use the tavily tool for more comprehensive web searches. Always cite your sources when possible.",
            description="Research assistant that provides accurate information on any topic",
            moderation=default_moderator,
            on_moderation_violation="block",
            monitor=default_monitor,
        )

        # Create a writer agent
        agents["writer"] = Agent(
            name="writer",
            llm=llm_providers["openai"],
            memory=memory,
            tools=[tools["calculator"]],
            system_prompt="You are a skilled writer and editor. Your job is to help create, refine, and improve written content. You can help with drafting, editing, proofreading, and providing feedback on writing style and structure.",
            description="Writer and editor that helps create and improve written content",
            moderation=default_moderator,
            on_moderation_violation="block",
            monitor=default_monitor,
        )

        # Create a knowledge agent if PGVector tool is available
        if "pgvector" in tools:
            agents["knowledge"] = Agent(
                name="knowledge",
                llm=llm_providers["openai"],
                memory=memory,
                tools=[tools["pgvector"]],
                system_prompt="You are a knowledge management assistant. Your job is to help store, retrieve, and analyze information. Use the pgvector tool to add documents and search for information.",
                description="Knowledge assistant that helps manage information",
                moderation=default_moderator,
                on_moderation_violation="block",
                monitor=default_monitor,
            )

        # Create a filesystem agent if MCP filesystem tool is available
        if "filesystem" in tools:
            agents["filesystem"] = Agent(
                name="filesystem",
                llm=llm_providers["openai"],
                memory=memory,
                tools=[tools["filesystem"]],
                system_prompt="You are a filesystem assistant. Your job is to help users access and manage files. Use the MCP filesystem tool to list and read files.",
                description="Filesystem assistant that helps access and manage files",
                moderation=default_moderator,
                on_moderation_violation="block",
                monitor=default_monitor,
            )

        # Create an orchestrator agent
        orchestrator = Agent(
            name="orchestrator",
            llm=llm_providers["openai"],
            memory=memory,
            system_prompt="You are a task orchestrator. Your job is to break down complex tasks into smaller subtasks and assign them to the most appropriate specialized agents. You then synthesize their outputs into a cohesive final result.",
            description="Task orchestrator that coordinates other agents",
            moderation=default_moderator,
            on_moderation_violation="block",
            monitor=default_monitor,
        )

        # Create a cognitive agent
        agents["cognitive"] = CognitiveAgent(
            name="cognitive",
            llm=llm_providers["openai"],
            memory=memory,
            cognitive_architecture=cognitive_architecture,
            system_prompt="You are a thoughtful assistant with advanced reasoning capabilities. You carefully analyze problems and provide well-reasoned responses.",
            description="Cognitive assistant with advanced reasoning capabilities",
            moderation=default_moderator,
            on_moderation_violation="block",
            monitor=default_monitor,
            cognitive_config={
                "reasoning_trace_enabled": True,
                "metacognition_enabled": True,
                "learning_enabled": True,
                "reasoning_depth": 2,
                "default_reasoning_mechanism": "deductive",
            },
        )

        # Create the workforce
        workforce = AgentWorkforce(
            agents=list(agents.values()),
            orchestrator_agent=orchestrator,
        )


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the Agents Hub API"}


@app.get("/agents")
async def list_agents():
    """List all available agents."""
    return {
        "agents": [
            {
                "name": agent.config.name,
                "description": agent.config.description,
                "llm_provider": agent.llm.provider_name,
                "llm_model": agent.llm.model_name,
            }
            for agent in agents.values()
        ]
    }


@app.post("/agents", response_model=AgentResponse)
async def create_agent(agent_request: AgentRequest):
    """Create a new agent."""
    # Check if agent already exists
    if agent_request.name in agents:
        raise HTTPException(status_code=400, detail=f"Agent '{agent_request.name}' already exists")

    # Check if LLM provider exists
    if agent_request.llm_provider not in llm_providers:
        raise HTTPException(status_code=400, detail=f"LLM provider '{agent_request.llm_provider}' not available")

    # Get moderator if moderation is enabled
    moderator = None
    if agent_request.enable_moderation:
        # Use combined moderator if available, otherwise use rule-based
        moderator = moderators.get("combined", moderators.get("rule_based"))
        if not moderator:
            raise HTTPException(status_code=400, detail="Moderation requested but no moderator is available")

    # Create the agent
    agents[agent_request.name] = Agent(
        name=agent_request.name,
        llm=llm_providers[agent_request.llm_provider],
        memory=memory,
        system_prompt=agent_request.system_prompt,
        description=agent_request.description,
        moderation=moderator,
        on_moderation_violation=agent_request.moderation_action,
    )

    # Update the workforce
    global workforce
    workforce = AgentWorkforce(
        agents=list(agents.values()),
        orchestrator_agent=agents.get("orchestrator"),
    )

    return {
        "name": agent_request.name,
        "description": agent_request.description,
        "llm_provider": agent_request.llm_provider,
        "llm_model": agent_request.llm_model,
        "moderation_enabled": agent_request.enable_moderation,
    }


@app.delete("/agents/{agent_name}")
async def delete_agent(agent_name: str):
    """Delete an agent."""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    # Don't allow deleting the orchestrator
    if agent_name == "orchestrator":
        raise HTTPException(status_code=400, detail="Cannot delete the orchestrator agent")

    # Delete the agent
    del agents[agent_name]

    # Update the workforce
    global workforce
    workforce = AgentWorkforce(
        agents=list(agents.values()),
        orchestrator_agent=agents.get("orchestrator"),
    )

    return {"message": f"Agent '{agent_name}' deleted"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with an agent or the workforce."""
    if not workforce:
        raise HTTPException(status_code=500, detail="Workforce not initialized")

    # Execute the task
    result = await workforce.execute(
        task=request.message,
        context={"conversation_id": request.conversation_id},
        agent_name=request.agent_name,
    )

    return {
        "response": result["result"],
        "agent": result["agent"],
        "conversation_id": request.conversation_id,
    }


@app.get("/conversations/{conversation_id}")
async def get_conversation_history(conversation_id: str, limit: int = 10):
    """Get conversation history."""
    if not memory:
        raise HTTPException(status_code=500, detail="Memory not initialized")

    history = await memory.get_history(conversation_id, limit=limit)

    return {"conversation_id": conversation_id, "history": history}


@app.delete("/conversations/{conversation_id}")
async def clear_conversation_history(conversation_id: str):
    """Clear conversation history."""
    if not memory:
        raise HTTPException(status_code=500, detail="Memory not initialized")

    await memory.clear_history(conversation_id)

    return {"message": f"Conversation '{conversation_id}' history cleared"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
