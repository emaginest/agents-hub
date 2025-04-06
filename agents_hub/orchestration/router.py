"""
Agent Workforce orchestration for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from agents_hub.agents.base import Agent


class AgentWorkforce:
    """
    Agent Workforce for orchestrating multiple agents.
    
    This class manages a team of agents and routes tasks to the appropriate agent.
    """
    
    def __init__(
        self,
        agents: List[Agent],
        orchestrator_agent: Optional[Agent] = None,
    ):
        """
        Initialize an agent workforce.
        
        Args:
            agents: List of agents in the workforce
            orchestrator_agent: Optional agent to use as the orchestrator
        """
        self.agents = {agent.config.name: agent for agent in agents}
        self.orchestrator = orchestrator_agent
    
    async def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        agent_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a task with the workforce.
        
        Args:
            task: Task description
            context: Optional context information
            agent_name: Optional name of the agent to use
            
        Returns:
            Result of the task execution
        """
        context = context or {}
        
        # If a specific agent is requested, use that agent
        if agent_name and agent_name in self.agents:
            agent = self.agents[agent_name]
            result = await agent.run(task, context)
            return {
                "result": result,
                "agent": agent_name,
                "subtasks": [],
            }
        
        # If an orchestrator is available, use it to route the task
        if self.orchestrator:
            return await self._orchestrated_execution(task, context)
        
        # Otherwise, use the first agent
        default_agent_name = next(iter(self.agents.keys()))
        agent = self.agents[default_agent_name]
        result = await agent.run(task, context)
        return {
            "result": result,
            "agent": default_agent_name,
            "subtasks": [],
        }
    
    async def _orchestrated_execution(
        self,
        task: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a task using the orchestrator to route subtasks.
        
        Args:
            task: Task description
            context: Context information
            
        Returns:
            Result of the task execution
        """
        # Prepare the orchestration prompt
        agent_descriptions = "\n".join(
            f"- {name}: {agent.config.description}" for name, agent in self.agents.items()
        )
        
        orchestration_prompt = f"""
        Task: {task}
        
        Available Agents:
        {agent_descriptions}
        
        Your job is to break down this task into subtasks and assign each subtask to the most appropriate agent.
        For each subtask, provide:
        1. The subtask description
        2. The name of the agent to assign it to
        3. The order in which the subtask should be executed
        
        Respond in the following JSON format:
        {{
            "subtasks": [
                {{
                    "description": "subtask description",
                    "agent": "agent_name",
                    "order": 1
                }},
                ...
            ]
        }}
        """
        
        # Get the orchestration plan
        orchestration_result = await self.orchestrator.run(orchestration_prompt, context)
        
        # Parse the orchestration plan
        try:
            import json
            plan = json.loads(orchestration_result)
            subtasks = plan.get("subtasks", [])
        except Exception as e:
            # If parsing fails, use the first agent
            default_agent_name = next(iter(self.agents.keys()))
            agent = self.agents[default_agent_name]
            result = await agent.run(task, context)
            return {
                "result": result,
                "agent": default_agent_name,
                "subtasks": [],
                "error": f"Failed to parse orchestration plan: {str(e)}",
            }
        
        # Sort subtasks by order
        subtasks.sort(key=lambda x: x.get("order", 0))
        
        # Execute each subtask
        results = []
        final_result = ""
        
        for subtask in subtasks:
            subtask_description = subtask.get("description", "")
            agent_name = subtask.get("agent", "")
            
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                subtask_result = await agent.run(subtask_description, context)
                
                results.append({
                    "description": subtask_description,
                    "agent": agent_name,
                    "result": subtask_result,
                })
                
                # Append to the final result
                final_result += f"\n\n{subtask_result}"
            else:
                # If agent doesn't exist, use the first agent
                default_agent_name = next(iter(self.agents.keys()))
                agent = self.agents[default_agent_name]
                subtask_result = await agent.run(subtask_description, context)
                
                results.append({
                    "description": subtask_description,
                    "agent": default_agent_name,
                    "result": subtask_result,
                    "error": f"Agent '{agent_name}' not found",
                })
                
                # Append to the final result
                final_result += f"\n\n{subtask_result}"
        
        # Generate a summary of the results
        summary_prompt = f"""
        Task: {task}
        
        Subtask Results:
        {final_result}
        
        Please provide a concise summary of the results.
        """
        
        summary = await self.orchestrator.run(summary_prompt, context)
        
        return {
            "result": summary,
            "agent": self.orchestrator.config.name,
            "subtasks": results,
        }
    
    def add_agent(self, agent: Agent) -> None:
        """
        Add an agent to the workforce.
        
        Args:
            agent: Agent to add
        """
        self.agents[agent.config.name] = agent
    
    def remove_agent(self, agent_name: str) -> None:
        """
        Remove an agent from the workforce.
        
        Args:
            agent_name: Name of the agent to remove
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
    
    def get_agent(self, agent_name: str) -> Optional[Agent]:
        """
        Get an agent by name.
        
        Args:
            agent_name: Name of the agent to get
            
        Returns:
            The agent, or None if not found
        """
        return self.agents.get(agent_name)
