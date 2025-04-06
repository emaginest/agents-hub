"""
Reasoning manager for the cognitive architecture.
"""

from typing import Dict, List, Any, Optional, Union
import logging
from agents_hub.cognitive.reasoning.base import BaseReasoning
from agents_hub.cognitive.reasoning.deductive import DeductiveReasoning
from agents_hub.cognitive.reasoning.inductive import InductiveReasoning
from agents_hub.cognitive.reasoning.abductive import AbductiveReasoning
from agents_hub.cognitive.reasoning.analogical import AnalogicalReasoning
from agents_hub.cognitive.reasoning.causal import CausalReasoning

# Initialize logger
logger = logging.getLogger(__name__)


class ReasoningManager:
    """
    Manager for different reasoning mechanisms.
    
    This class provides a unified interface for accessing and applying
    different reasoning mechanisms based on the task requirements.
    """
    
    def __init__(
        self,
        enabled_mechanisms: Optional[List[str]] = None,
        default_mechanism: str = "deductive",
    ):
        """
        Initialize the reasoning manager.
        
        Args:
            enabled_mechanisms: List of enabled reasoning mechanisms
            default_mechanism: Default reasoning mechanism to use
        """
        self.enabled_mechanisms = enabled_mechanisms or ["deductive", "inductive", "abductive", "analogical", "causal"]
        self.default_mechanism = default_mechanism
        
        # Initialize reasoning mechanisms
        self.mechanisms = {}
        if "deductive" in self.enabled_mechanisms:
            self.mechanisms["deductive"] = DeductiveReasoning()
        if "inductive" in self.enabled_mechanisms:
            self.mechanisms["inductive"] = InductiveReasoning()
        if "abductive" in self.enabled_mechanisms:
            self.mechanisms["abductive"] = AbductiveReasoning()
        if "analogical" in self.enabled_mechanisms:
            self.mechanisms["analogical"] = AnalogicalReasoning()
        if "causal" in self.enabled_mechanisms:
            self.mechanisms["causal"] = CausalReasoning()
    
    async def reason(
        self,
        memory_state: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Apply appropriate reasoning mechanisms.
        
        Args:
            memory_state: Current state of working memory
            context: Context information
            
        Returns:
            Reasoning results
        """
        # Select appropriate reasoning mechanism
        mechanism_name = await self._select_mechanism(memory_state, context)
        mechanism = self.mechanisms.get(mechanism_name, self.mechanisms[self.default_mechanism])
        
        # Apply the selected mechanism
        reasoning_result = await mechanism.apply(memory_state, context)
        
        # Combine results if multiple mechanisms are used
        if context.get("use_multiple_mechanisms", False):
            combined_result = await self._combine_results(memory_state, context)
            reasoning_result["combined_result"] = combined_result
        
        return {
            "mechanism": mechanism_name,
            "steps": reasoning_result["steps"],
            "output": reasoning_result["output"],
            "confidence": reasoning_result.get("confidence", 0.0),
            "details": reasoning_result,
        }
    
    async def _select_mechanism(
        self,
        memory_state: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        """
        Select the most appropriate reasoning mechanism.
        
        Args:
            memory_state: Current state of working memory
            context: Context information
            
        Returns:
            Name of the selected mechanism
        """
        # Check if mechanism is specified in context
        if "reasoning_mechanism" in context:
            mechanism_name = context["reasoning_mechanism"]
            if mechanism_name in self.mechanisms:
                return mechanism_name
        
        # Calculate suitability scores for each mechanism
        suitability_scores = {}
        for name, mechanism in self.mechanisms.items():
            suitability_scores[name] = mechanism.get_suitability(memory_state, context)
        
        # Select mechanism with highest suitability score
        if suitability_scores:
            best_mechanism = max(suitability_scores.items(), key=lambda x: x[1])
            if best_mechanism[1] > 0.3:  # Minimum threshold
                return best_mechanism[0]
        
        # Fallback to default mechanism
        return self.default_mechanism
    
    async def _combine_results(
        self,
        memory_state: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Combine results from multiple reasoning mechanisms.
        
        Args:
            memory_state: Current state of working memory
            context: Context information
            
        Returns:
            Combined reasoning results
        """
        combined_results = {}
        
        # Apply each mechanism
        mechanism_results = {}
        for name, mechanism in self.mechanisms.items():
            try:
                result = await mechanism.apply(memory_state, context)
                mechanism_results[name] = result
            except Exception as e:
                logger.exception(f"Error applying {name} reasoning: {e}")
        
        # Combine steps from all mechanisms
        combined_steps = []
        for name, result in mechanism_results.items():
            combined_steps.append(f"=== {name.capitalize()} Reasoning ===")
            combined_steps.extend(result["steps"])
        
        # Select best output based on confidence
        best_mechanism = max(mechanism_results.items(), key=lambda x: x[1].get("confidence", 0.0))
        best_output = best_mechanism[1]["output"]
        best_confidence = best_mechanism[1].get("confidence", 0.0)
        
        combined_results["steps"] = combined_steps
        combined_results["output"] = best_output
        combined_results["confidence"] = best_confidence
        combined_results["mechanism_results"] = mechanism_results
        
        return combined_results
