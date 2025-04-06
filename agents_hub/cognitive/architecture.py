"""
Cognitive architecture for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
import logging
from agents_hub.cognitive.perception import Perception
from agents_hub.cognitive.memory import WorkingMemory
from agents_hub.cognitive.reasoning import ReasoningManager
from agents_hub.cognitive.metacognition import Metacognition
from agents_hub.cognitive.learning import Learning

# Initialize logger
logger = logging.getLogger(__name__)


class CognitiveArchitecture:
    """
    Multi-layer cognitive architecture inspired by human cognition.
    
    This architecture provides agents with human-like cognitive capabilities,
    including perception, working memory, reasoning, metacognition, and learning.
    """
    
    def __init__(
        self,
        perception_config: Optional[Dict[str, Any]] = None,
        memory_config: Optional[Dict[str, Any]] = None,
        reasoning_config: Optional[Dict[str, Any]] = None,
        metacognition_config: Optional[Dict[str, Any]] = None,
        learning_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the cognitive architecture.
        
        Args:
            perception_config: Configuration for the perception layer
            memory_config: Configuration for the working memory system
            reasoning_config: Configuration for the reasoning layer
            metacognition_config: Configuration for the metacognitive layer
            learning_config: Configuration for the learning layer
        """
        self.perception = Perception(**(perception_config or {}))
        self.memory = WorkingMemory(**(memory_config or {}))
        self.reasoning = ReasoningManager(**(reasoning_config or {}))
        self.metacognition = Metacognition(**(metacognition_config or {}))
        self.learning = Learning(**(learning_config or {}))
    
    async def process(
        self,
        input_text: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Process input through the cognitive architecture.
        
        Args:
            input_text: Input text to process
            context: Context information
            
        Returns:
            Processing results including reasoning steps and metacognitive reflections
        """
        try:
            # Perception: Process input and extract features
            perception_result = await self.perception.process(input_text, context)
            
            # Working Memory: Store active information
            memory_state = await self.memory.update(perception_result, context)
            
            # Reasoning: Apply appropriate reasoning mechanisms
            reasoning_result = await self.reasoning.reason(memory_state, context)
            
            # Metacognition: Reflect on the reasoning process
            metacognition_result = await self.metacognition.reflect(reasoning_result, context)
            
            # Learning: Update knowledge and strategies based on experience
            learning_result = await self.learning.update(metacognition_result, context)
            
            return {
                "perception": perception_result,
                "memory": memory_state,
                "reasoning": reasoning_result,
                "metacognition": metacognition_result,
                "learning": learning_result,
                "result": metacognition_result.get("final_output", reasoning_result.get("output", "")),
                "reasoning_trace": self._generate_reasoning_trace(
                    perception_result,
                    reasoning_result,
                    metacognition_result,
                ),
            }
        
        except Exception as e:
            logger.exception(f"Error in cognitive processing: {e}")
            # Return a fallback result
            return {
                "error": str(e),
                "result": "I encountered an error in my thinking process. Let me try a simpler approach.",
                "reasoning_trace": f"Error in cognitive processing: {str(e)}",
            }
    
    def _generate_reasoning_trace(
        self,
        perception_result: Dict[str, Any],
        reasoning_result: Dict[str, Any],
        metacognition_result: Dict[str, Any],
    ) -> str:
        """
        Generate a human-readable trace of the reasoning process.
        
        Args:
            perception_result: Result of perception processing
            reasoning_result: Result of reasoning processing
            metacognition_result: Result of metacognitive reflection
            
        Returns:
            Human-readable reasoning trace
        """
        trace = []
        
        # Add perception insights
        if "insights" in perception_result:
            trace.append("Initial Observations:")
            for insight in perception_result.get("insights", []):
                trace.append(f"- {insight}")
        
        # Add reasoning steps
        if "steps" in reasoning_result:
            trace.append("\nReasoning Process:")
            for i, step in enumerate(reasoning_result.get("steps", []), 1):
                trace.append(f"{i}. {step}")
        
        # Add metacognitive reflections
        if "reflections" in metacognition_result:
            trace.append("\nReflections:")
            for reflection in metacognition_result.get("reflections", []):
                trace.append(f"- {reflection}")
        
        # Add confidence assessment
        if "confidence" in metacognition_result:
            confidence = metacognition_result.get("confidence", 0.0)
            trace.append(f"\nConfidence: {confidence:.2f}")
        
        return "\n".join(trace)
