"""
Intelligent agent selection for the Agents Hub framework.

This module provides utilities for selecting the most appropriate agent
when orchestration fails or when intelligent fallback is needed.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
from agents_hub.agents.base import Agent

logger = logging.getLogger(__name__)


class AgentSelector:
    """
    Intelligent agent selector that can choose the best agent based on task content.
    """

    def __init__(self, agents: Dict[str, Agent]):
        """
        Initialize the agent selector.

        Args:
            agents: Dictionary of agent name to agent instance
        """
        self.agents = agents
        self._build_agent_profiles()

    def _build_agent_profiles(self) -> None:
        """Build profiles for each agent based on their configuration."""
        self.agent_profiles = {}

        for name, agent in self.agents.items():
            profile = {
                "name": name,
                "description": getattr(agent.config, "description", ""),
                "system_prompt": getattr(agent.config, "system_prompt", ""),
                "keywords": self._extract_keywords(agent),
                "capabilities": self._extract_capabilities(agent),
            }
            self.agent_profiles[name] = profile

    def _extract_keywords(self, agent: Agent) -> List[str]:
        """
        Extract keywords from agent configuration.

        Args:
            agent: Agent instance

        Returns:
            List of keywords
        """
        keywords = []

        # Extract from description
        description = getattr(agent.config, "description", "")
        if description:
            keywords.extend(self._tokenize_text(description))

        # Extract from system prompt
        system_prompt = getattr(agent.config, "system_prompt", "")
        if system_prompt:
            keywords.extend(self._tokenize_text(system_prompt))

        # Extract from agent name
        keywords.append(agent.config.name.lower())

        # Add domain-specific keywords based on agent type
        agent_name = agent.config.name.lower()
        if "cod" in agent_name or "program" in agent_name or "develop" in agent_name:
            keywords.extend(
                [
                    "python",
                    "javascript",
                    "java",
                    "function",
                    "script",
                    "algorithm",
                    "software",
                    "api",
                ]
            )
        elif "writ" in agent_name or "content" in agent_name or "editor" in agent_name:
            keywords.extend(["article", "blog", "content", "copy", "document", "text"])
        elif "research" in agent_name or "analys" in agent_name:
            keywords.extend(
                ["data", "analysis", "study", "report", "findings", "information"]
            )

        # Remove duplicates and common words
        keywords = list(set(keywords))
        keywords = [
            kw for kw in keywords if len(kw) > 2 and kw not in self._get_stop_words()
        ]

        return keywords

    def _extract_capabilities(self, agent: Agent) -> List[str]:
        """
        Extract capabilities from agent configuration.

        Args:
            agent: Agent instance

        Returns:
            List of capabilities
        """
        capabilities = []

        # Extract from tools
        if hasattr(agent, "tools") and agent.tools:
            for tool in agent.tools:
                tool_name = getattr(tool, "name", tool.__class__.__name__)
                capabilities.append(tool_name.lower())

        # Extract capability keywords from description and system prompt
        text = f"{getattr(agent.config, 'description', '')} {getattr(agent.config, 'system_prompt', '')}"
        capability_patterns = [
            r"\b(research|analyze|write|code|program|develop|test|debug|deploy|manage)\w*\b",
            r"\b(create|generate|build|design|implement|execute|process|handle)\w*\b",
            r"\b(expert|specialist|assistant|developer|engineer|analyst|writer|researcher|coder|programmer)\b",
            r"\b(python|javascript|java|function|script|algorithm|software)\w*\b",
        ]

        for pattern in capability_patterns:
            matches = re.findall(pattern, text.lower())
            capabilities.extend(matches)

        return list(set(capabilities))

    def _tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize text into meaningful words.

        Args:
            text: Text to tokenize

        Returns:
            List of tokens
        """
        # Remove punctuation and split
        text = re.sub(r"[^\w\s]", " ", text.lower())
        tokens = text.split()

        # Filter out short words and numbers
        tokens = [token for token in tokens if len(token) > 2 and not token.isdigit()]

        return tokens

    def _get_stop_words(self) -> List[str]:
        """Get common stop words to filter out."""
        return [
            "the",
            "and",
            "are",
            "you",
            "your",
            "that",
            "this",
            "with",
            "for",
            "can",
            "will",
            "help",
            "any",
            "all",
            "who",
            "what",
            "when",
            "where",
            "how",
            "why",
            "job",
            "task",
            "work",
            "able",
            "use",
            "make",
            "get",
            "have",
            "has",
            "been",
            "being",
            "from",
            "into",
            "such",
            "them",
            "they",
            "their",
            "also",
            "more",
            "most",
            "some",
            "very",
            "well",
        ]

    def select_best_agent(self, task: str, context: Optional[Dict] = None) -> str:
        """
        Select the best agent for a given task.

        Args:
            task: Task description
            context: Optional context information

        Returns:
            Name of the best agent
        """
        if not self.agents:
            raise ValueError("No agents available for selection")

        # Score each agent
        agent_scores = {}
        task_tokens = self._tokenize_text(task)

        for agent_name, profile in self.agent_profiles.items():
            score = self._calculate_agent_score(task, task_tokens, profile, context)
            agent_scores[agent_name] = score

            logger.debug(
                f"Agent '{agent_name}' scored {score:.3f} for task: {task[:50]}..."
            )

        # Select the agent with the highest score
        best_agent = max(agent_scores.items(), key=lambda x: x[1])

        logger.info(f"Selected agent '{best_agent[0]}' with score {best_agent[1]:.3f}")

        return best_agent[0]

    def _calculate_agent_score(
        self,
        task: str,
        task_tokens: List[str],
        profile: Dict,
        context: Optional[Dict] = None,
    ) -> float:
        """
        Calculate a score for how well an agent matches a task.

        Args:
            task: Task description
            task_tokens: Tokenized task
            profile: Agent profile
            context: Optional context

        Returns:
            Score between 0 and 1
        """
        score = 0.0

        # Keyword matching score (40% weight)
        keyword_score = self._calculate_keyword_score(task_tokens, profile["keywords"])
        score += keyword_score * 0.4

        # Capability matching score (30% weight)
        capability_score = self._calculate_capability_score(
            task, profile["capabilities"]
        )
        score += capability_score * 0.3

        # Description similarity score (20% weight)
        description_score = self._calculate_description_score(
            task, profile["description"]
        )
        score += description_score * 0.2

        # Name relevance score (10% weight)
        name_score = self._calculate_name_score(task, profile["name"])
        score += name_score * 0.1

        return min(score, 1.0)  # Cap at 1.0

    def _calculate_keyword_score(
        self, task_tokens: List[str], agent_keywords: List[str]
    ) -> float:
        """Calculate score based on keyword overlap."""
        if not agent_keywords:
            return 0.0

        matches = sum(1 for token in task_tokens if token in agent_keywords)
        return matches / len(task_tokens) if task_tokens else 0.0

    def _calculate_capability_score(self, task: str, capabilities: List[str]) -> float:
        """Calculate score based on capability matching."""
        if not capabilities:
            return 0.0

        task_lower = task.lower()

        # Define technical terms that should get higher weight
        technical_terms = {
            "code",
            "program",
            "debug",
            "function",
            "script",
            "algorithm",
            "python",
            "javascript",
            "java",
            "software",
            "developer",
            "programmer",
        }

        weighted_matches = 0
        total_weight = 0

        for cap in capabilities:
            if cap in task_lower:
                # Give higher weight to technical terms
                weight = 2.0 if cap in technical_terms else 1.0
                weighted_matches += weight
                total_weight += weight
            else:
                total_weight += 1.0

        return weighted_matches / total_weight if total_weight > 0 else 0.0

    def _calculate_description_score(self, task: str, description: str) -> float:
        """Calculate score based on description similarity."""
        if not description:
            return 0.0

        # Use sequence matcher for similarity
        similarity = SequenceMatcher(None, task.lower(), description.lower()).ratio()
        return similarity

    def _calculate_name_score(self, task: str, agent_name: str) -> float:
        """Calculate score based on agent name relevance."""
        task_lower = task.lower()
        name_lower = agent_name.lower()

        # Check if agent name or parts of it appear in task
        if name_lower in task_lower:
            return 1.0

        # Check for partial matches and root words
        name_parts = name_lower.split("_")
        matches = 0

        for part in name_parts:
            if part in task_lower:
                # Context-aware scoring for ambiguous terms
                if part == "write":
                    # "write" gets less credit if task has technical terms
                    technical_indicators = [
                        "python",
                        "function",
                        "code",
                        "script",
                        "algorithm",
                        "program",
                    ]
                    has_technical = any(
                        indicator in task_lower for indicator in technical_indicators
                    )
                    if has_technical and "cod" not in name_lower:
                        matches += 0.3  # Reduced credit for non-coding agents
                    else:
                        matches += 1.0
                else:
                    matches += 1.0
            else:
                # Check for root word matches (e.g., "research" in "researcher")
                if len(part) > 4:
                    root = part[:-2]  # Remove common suffixes like "er", "or"
                    if root in task_lower:
                        # Apply context-aware scoring for root matches too
                        if root == "writ":  # Root of "writer"
                            technical_indicators = [
                                "python",
                                "function",
                                "code",
                                "script",
                                "algorithm",
                                "program",
                            ]
                            has_technical = any(
                                indicator in task_lower
                                for indicator in technical_indicators
                            )
                            if has_technical and "cod" not in name_lower:
                                matches += (
                                    0.2  # Very reduced credit for non-coding agents
                                )
                            else:
                                matches += 0.8
                        else:
                            matches += 0.8  # Partial credit for root match

        return matches / len(name_parts) if name_parts else 0.0

    def get_ranked_agents(
        self, task: str, context: Optional[Dict] = None
    ) -> List[Tuple[str, float]]:
        """
        Get all agents ranked by their suitability for a task.

        Args:
            task: Task description
            context: Optional context information

        Returns:
            List of (agent_name, score) tuples sorted by score descending
        """
        if not self.agents:
            return []

        task_tokens = self._tokenize_text(task)
        agent_scores = []

        for agent_name, profile in self.agent_profiles.items():
            score = self._calculate_agent_score(task, task_tokens, profile, context)
            agent_scores.append((agent_name, score))

        # Sort by score descending
        agent_scores.sort(key=lambda x: x[1], reverse=True)

        return agent_scores
