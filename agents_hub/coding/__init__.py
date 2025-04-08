"""
Coding module for the Agents Hub framework.

This module provides specialized agents and tools for software development tasks.
"""

from agents_hub.coding.workforce import CodingWorkforce
from agents_hub.coding.agents import (
    ProjectManagerAgent,
    AnalystAgent,
    BackendDeveloperAgent,
    FrontendDeveloperAgent,
    DevOpsEngineerAgent,
    SecurityEngineerAgent,
    QATesterAgent,
)

__all__ = [
    "CodingWorkforce",
    "ProjectManagerAgent",
    "AnalystAgent",
    "BackendDeveloperAgent",
    "FrontendDeveloperAgent",
    "DevOpsEngineerAgent",
    "SecurityEngineerAgent",
    "QATesterAgent",
]
