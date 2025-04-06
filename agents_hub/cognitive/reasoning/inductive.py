"""
Inductive reasoning mechanism for the cognitive architecture.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import re
from agents_hub.cognitive.reasoning.base import BaseReasoning

# Initialize logger
logger = logging.getLogger(__name__)


class InductiveReasoning(BaseReasoning):
    """
    Inductive reasoning mechanism.
    
    This class implements inductive reasoning, which involves drawing
    general conclusions from specific observations.
    """
    
    def __init__(self):
        """Initialize the inductive reasoning mechanism."""
        super().__init__(
            name="inductive",
            description="Inductive reasoning involves drawing general conclusions from specific observations.",
        )
    
    async def apply(
        self,
        memory_state: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Apply inductive reasoning.
        
        Args:
            memory_state: Current state of working memory
            context: Context information
            
        Returns:
            Reasoning results
        """
        # Extract input and active items
        input_text = self._extract_input(memory_state)
        active_items = self._extract_active_items(memory_state)
        
        # Identify observations and pattern
        observations, pattern = self._identify_observations_pattern(input_text, active_items)
        
        # Apply inductive reasoning
        steps = self._apply_inductive_reasoning(observations, pattern)
        
        # Generate output
        output = self._generate_output(steps)
        
        # Calculate confidence
        confidence = self._calculate_confidence(steps, observations)
        
        return {
            "steps": steps,
            "output": output,
            "confidence": confidence,
            "observations": observations,
            "pattern": pattern,
        }
    
    def get_suitability(
        self,
        memory_state: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """
        Get the suitability of inductive reasoning for the current state.
        
        Args:
            memory_state: Current state of working memory
            context: Context information
            
        Returns:
            Suitability score (0.0 to 1.0)
        """
        suitability = 0.0
        
        # Extract input
        input_text = self._extract_input(memory_state)
        input_lower = input_text.lower()
        
        # Check for pattern keywords
        pattern_keywords = ["pattern", "trend", "example", "instance", "case", "observation", "sample", "data", "evidence", "suggest", "indicate", "imply", "likely", "probably", "most", "many", "some", "few", "generally", "typically", "usually", "often", "sometimes", "rarely"]
        for keyword in pattern_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', input_lower):
                suitability += 0.1
        
        # Cap at 1.0
        suitability = min(suitability, 1.0)
        
        # Check for task type
        for item in memory_state.get("items", []):
            if item["type"] == "task_type" and item["content"] in ["analysis", "summarization"]:
                suitability += 0.2
        
        # Check for domain
        for item in memory_state.get("items", []):
            if item["type"] == "domain" and item["content"] in ["science", "business", "health"]:
                suitability += 0.2
        
        # Check for question type
        for item in memory_state.get("items", []):
            if item["type"] == "question_type" and item["content"] in ["explanatory", "evaluative"]:
                suitability += 0.1
        
        # Cap at 1.0
        suitability = min(suitability, 1.0)
        
        return suitability
    
    def _identify_observations_pattern(
        self,
        input_text: str,
        active_items: List[Dict[str, Any]],
    ) -> tuple[List[str], Optional[str]]:
        """
        Identify observations and pattern from input text and active items.
        
        Args:
            input_text: Input text
            active_items: Active items in working memory
            
        Returns:
            Tuple of (observations, pattern)
        """
        observations = []
        pattern = None
        
        # Split input into sentences
        sentences = re.split(r'[.!?]+', input_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Identify pattern (sentence with "pattern", "trend", etc.)
        pattern_keywords = ["pattern", "trend", "generally", "typically", "usually", "often", "suggests", "indicates", "implies"]
        for sentence in sentences:
            for keyword in pattern_keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', sentence.lower()):
                    pattern = sentence
                    break
            if pattern:
                break
        
        # If no pattern found, use the last sentence
        if not pattern and sentences:
            pattern = sentences[-1]
        
        # Identify observations (sentences that are not the pattern)
        for sentence in sentences:
            if sentence != pattern:
                observations.append(sentence)
        
        # Add observations from active items
        for item in active_items:
            if item["type"] in ["entity", "keyword", "topic"]:
                observation = f"{item['content']} is observed in the context."
                if observation not in observations:
                    observations.append(observation)
        
        return observations, pattern
    
    def _apply_inductive_reasoning(
        self,
        observations: List[str],
        pattern: Optional[str],
    ) -> List[str]:
        """
        Apply inductive reasoning to observations and pattern.
        
        Args:
            observations: List of observations
            pattern: Identified pattern
            
        Returns:
            List of reasoning steps
        """
        steps = []
        
        # Add observations as initial steps
        for i, observation in enumerate(observations, 1):
            steps.append(f"Observation {i}: {observation}")
        
        # If no observations, add a note
        if not observations:
            steps.append("No clear observations identified.")
        
        # If no pattern, add a note
        if not pattern:
            steps.append("No clear pattern identified.")
            return steps
        
        # Add intermediate steps
        if observations:
            steps.append("Analyzing the observations for patterns...")
            
            # Look for similarities
            steps.append("Looking for similarities across observations.")
            
            # Look for frequencies
            steps.append("Examining the frequency of occurrences.")
            
            # Look for correlations
            steps.append("Identifying potential correlations.")
        
        # Add generalization
        steps.append(f"Based on these observations, a pattern emerges: {pattern}")
        
        # Add inductive conclusion
        steps.append(f"Therefore, it is reasonable to infer that this pattern will continue or apply more broadly.")
        
        return steps
    
    def _generate_output(self, steps: List[str]) -> str:
        """
        Generate output from reasoning steps.
        
        Args:
            steps: List of reasoning steps
            
        Returns:
            Generated output
        """
        # Extract conclusion (last step)
        if len(steps) >= 2:
            pattern_step = steps[-2]
            if pattern_step.startswith("Based on these observations, a pattern emerges: "):
                return pattern_step[len("Based on these observations, a pattern emerges: "):]
        
        # Fallback: combine steps
        return " ".join(steps)
    
    def _calculate_confidence(self, steps: List[str], observations: List[str]) -> float:
        """
        Calculate confidence in the reasoning.
        
        Args:
            steps: List of reasoning steps
            observations: List of observations
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Base confidence
        confidence = 0.5
        
        # Adjust based on number of observations
        observation_count = len(observations)
        if observation_count >= 5:
            confidence += 0.2
        elif observation_count >= 3:
            confidence += 0.1
        elif observation_count >= 1:
            confidence += 0.0
        else:
            confidence -= 0.2
        
        # Adjust based on pattern identification
        if any("pattern emerges" in step for step in steps):
            confidence += 0.1
        
        # Adjust based on similarity analysis
        if any("similarities" in step for step in steps):
            confidence += 0.1
        
        # Adjust based on frequency analysis
        if any("frequency" in step for step in steps):
            confidence += 0.1
        
        # Adjust based on correlation analysis
        if any("correlations" in step for step in steps):
            confidence += 0.1
        
        # Inductive reasoning is inherently less certain than deductive
        confidence -= 0.1
        
        # Cap at 0.0 and 1.0
        confidence = max(0.0, min(confidence, 1.0))
        
        return confidence
