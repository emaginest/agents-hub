"""
Agent Workforce orchestration for the Agents Hub framework.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from agents_hub.agents.base import Agent
from agents_hub.utils.json_parser import extract_json, JSONParsingError
from agents_hub.orchestration.agent_selector import AgentSelector

logger = logging.getLogger(__name__)


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
        self.agent_selector = AgentSelector(self.agents)

        logger.info(
            f"Initialized AgentWorkforce with {len(self.agents)} agents: {list(self.agents.keys())}"
        )
        if self.orchestrator:
            logger.info(f"Using orchestrator agent: {self.orchestrator.config.name}")

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

        # Otherwise, use intelligent agent selection
        try:
            selected_agent_name = self.agent_selector.select_best_agent(task, context)
            agent = self.agents[selected_agent_name]
            result = await agent.run(task, context)

            logger.info(
                f"Task executed by intelligently selected agent: {selected_agent_name}"
            )

            return {
                "result": result,
                "agent": selected_agent_name,
                "subtasks": [],
                "selection_method": "intelligent_fallback",
            }
        except Exception as e:
            # Final fallback to first agent
            logger.warning(
                f"Intelligent agent selection failed: {e}. Using first agent as final fallback."
            )
            default_agent_name = next(iter(self.agents.keys()))
            agent = self.agents[default_agent_name]
            result = await agent.run(task, context)
            return {
                "result": result,
                "agent": default_agent_name,
                "subtasks": [],
                "selection_method": "first_agent_fallback",
                "fallback_reason": str(e),
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
            f"- {name}: {agent.config.description}"
            for name, agent in self.agents.items()
        )

        orchestration_prompt = f"""
        Task: {task}

        Available Agents:
        {agent_descriptions}

        Your job is to break down this task into subtasks and assign each subtask to the most appropriate agent.
        For each subtask, provide:
        1. The subtask description
        2. The name of the agent to assign it to (must be one of the available agents)
        3. The order in which the subtask should be executed

        IMPORTANT: You must respond with valid JSON only. Do not include any explanatory text before or after the JSON.

        Respond in exactly this JSON format:
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

        Available agent names: {list(self.agents.keys())}
        """

        # Get the orchestration plan
        orchestration_result = await self.orchestrator.run(
            orchestration_prompt, context
        )

        logger.debug(f"Orchestrator response: {orchestration_result}")

        # Parse the orchestration plan using robust JSON parsing
        try:
            # Define expected schema for validation
            expected_schema = {
                "subtasks": list,
            }

            plan = extract_json(orchestration_result, expected_schema)
            subtasks = plan.get("subtasks", [])

            # Validate subtasks structure
            for i, subtask in enumerate(subtasks):
                if not isinstance(subtask, dict):
                    raise ValueError(f"Subtask {i} is not a dictionary")
                if "description" not in subtask or "agent" not in subtask:
                    raise ValueError(f"Subtask {i} missing required fields")
                if subtask["agent"] not in self.agents:
                    logger.warning(
                        f"Subtask {i} references unknown agent '{subtask['agent']}', will use intelligent selection"
                    )

            logger.info(
                f"Successfully parsed orchestration plan with {len(subtasks)} subtasks"
            )

        except JSONParsingError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.debug(f"Original content: {e.original_content}")
            logger.debug(f"Attempted strategies: {e.attempted_strategies}")

            # Use intelligent agent selection as fallback
            return await self._intelligent_fallback_execution(
                task, context, f"JSON parsing failed: {str(e)}"
            )

        except Exception as e:
            logger.error(f"Orchestration plan validation failed: {e}")

            # Use intelligent agent selection as fallback
            return await self._intelligent_fallback_execution(
                task, context, f"Plan validation failed: {str(e)}"
            )

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

                results.append(
                    {
                        "description": subtask_description,
                        "agent": agent_name,
                        "result": subtask_result,
                    }
                )

                # Append to the final result
                final_result += f"\n\n{subtask_result}"
            else:
                # If agent doesn't exist, use intelligent agent selection
                try:
                    selected_agent_name = self.agent_selector.select_best_agent(
                        subtask_description, context
                    )
                    agent = self.agents[selected_agent_name]
                    subtask_result = await agent.run(subtask_description, context)

                    logger.info(
                        f"Used intelligent selection for subtask: {selected_agent_name} (original: {agent_name})"
                    )

                    results.append(
                        {
                            "description": subtask_description,
                            "agent": selected_agent_name,
                            "result": subtask_result,
                            "original_agent": agent_name,
                            "selection_method": "intelligent_fallback",
                            "warning": f"Agent '{agent_name}' not found, used intelligent selection",
                        }
                    )

                    # Append to the final result
                    final_result += f"\n\n{subtask_result}"
                except Exception as selection_error:
                    # Final fallback to first agent
                    logger.warning(
                        f"Intelligent selection failed for subtask: {selection_error}"
                    )
                    default_agent_name = next(iter(self.agents.keys()))
                    agent = self.agents[default_agent_name]
                    subtask_result = await agent.run(subtask_description, context)

                    results.append(
                        {
                            "description": subtask_description,
                            "agent": default_agent_name,
                            "result": subtask_result,
                            "original_agent": agent_name,
                            "selection_method": "first_agent_fallback",
                            "error": f"Agent '{agent_name}' not found, intelligent selection failed: {selection_error}",
                        }
                    )

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

    async def _intelligent_fallback_execution(
        self, task: str, context: Dict[str, Any], error_reason: str
    ) -> Dict[str, Any]:
        """
        Execute task using intelligent agent selection as fallback.

        Args:
            task: Task description
            context: Context information
            error_reason: Reason for fallback

        Returns:
            Result of the task execution
        """
        try:
            selected_agent_name = self.agent_selector.select_best_agent(task, context)
            agent = self.agents[selected_agent_name]
            result = await agent.run(task, context)

            logger.info(
                f"Fallback execution successful with agent: {selected_agent_name}"
            )

            return {
                "result": result,
                "agent": selected_agent_name,
                "subtasks": [],
                "selection_method": "intelligent_fallback",
                "fallback_reason": error_reason,
            }
        except Exception as e:
            # Final fallback to first agent
            logger.warning(
                f"Intelligent fallback failed: {e}. Using first agent as final fallback."
            )
            default_agent_name = next(iter(self.agents.keys()))
            agent = self.agents[default_agent_name]
            result = await agent.run(task, context)

            return {
                "result": result,
                "agent": default_agent_name,
                "subtasks": [],
                "selection_method": "first_agent_fallback",
                "fallback_reason": f"{error_reason}; intelligent fallback failed: {str(e)}",
            }

    def add_agent(self, agent: Agent) -> None:
        """
        Add an agent to the workforce.

        Args:
            agent: Agent to add
        """
        self.agents[agent.config.name] = agent
        # Refresh agent selector with updated agents
        self.agent_selector = AgentSelector(self.agents)
        logger.info(f"Added agent '{agent.config.name}' to workforce")

    def remove_agent(self, agent_name: str) -> None:
        """
        Remove an agent from the workforce.

        Args:
            agent_name: Name of the agent to remove
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
            # Refresh agent selector with updated agents
            self.agent_selector = AgentSelector(self.agents)
            logger.info(f"Removed agent '{agent_name}' from workforce")

    def get_agent(self, agent_name: str) -> Optional[Agent]:
        """
        Get an agent by name.

        Args:
            agent_name: Name of the agent to get

        Returns:
            The agent, or None if not found
        """
        return self.agents.get(agent_name)
