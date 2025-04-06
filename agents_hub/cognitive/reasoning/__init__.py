"""
Reasoning mechanisms for the cognitive architecture.
"""

from agents_hub.cognitive.reasoning.base import BaseReasoning
from agents_hub.cognitive.reasoning.deductive import DeductiveReasoning
from agents_hub.cognitive.reasoning.inductive import InductiveReasoning
from agents_hub.cognitive.reasoning.abductive import AbductiveReasoning
from agents_hub.cognitive.reasoning.analogical import AnalogicalReasoning
from agents_hub.cognitive.reasoning.causal import CausalReasoning
from agents_hub.cognitive.reasoning.manager import ReasoningManager

__all__ = [
    "BaseReasoning",
    "DeductiveReasoning",
    "InductiveReasoning",
    "AbductiveReasoning",
    "AnalogicalReasoning",
    "CausalReasoning",
    "ReasoningManager",
]
