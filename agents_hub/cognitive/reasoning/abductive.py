"""
Abductive reasoning mechanism for the cognitive architecture.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import re
from agents_hub.cognitive.reasoning.base import BaseReasoning

# Initialize logger
logger = logging.getLogger(__name__)


class AbductiveReasoning(BaseReasoning):
    """
    Abductive reasoning mechanism.
    
    This class implements abductive reasoning, which involves forming
    the most likely explanation for observations.
    """
    
    def __init__(self):
        """Initialize the abductive reasoning mechanism."""
        super().__init__(
            name="abductive",
            description="Abductive reasoning involves forming the most likely explanation for observations.",
        )
    
    async def apply(
        self,
        memory_state: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Apply abductive reasoning.
        
        Args:
            memory_state: Current state of working memory
            context: Context information
            
        Returns:
            Reasoning results
        """
        # Extract input and active items
        input_text = self._extract_input(memory_state)
        active_items = self._extract_active_items(memory_state)
        
        # Identify observations and hypotheses
        observations, hypotheses = self._identify_observations_hypotheses(input_text, active_items)
        
        # Apply abductive reasoning
        steps, best_hypothesis = self._apply_abductive_reasoning(observations, hypotheses)
        
        # Generate output
        output = self._generate_output(steps, best_hypothesis)
        
        # Calculate confidence
        confidence = self._calculate_confidence(steps, observations, hypotheses)
        
        return {
            "steps": steps,
            "output": output,
            "confidence": confidence,
            "observations": observations,
            "hypotheses": hypotheses,
            "best_hypothesis": best_hypothesis,
        }
    
    def get_suitability(
        self,
        memory_state: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """
        Get the suitability of abductive reasoning for the current state.
        
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
        
        # Check for explanation keywords
        explanation_keywords = ["explain", "explanation", "reason", "cause", "why", "how come", "hypothesis", "theory", "possibility", "maybe", "perhaps", "possibly", "probably", "likely", "best explanation", "most likely", "could be", "might be", "diagnosis", "solve"]
        for keyword in explanation_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', input_lower):
                suitability += 0.1
        
        # Cap at 1.0
        suitability = min(suitability, 1.0)
        
        # Check for task type
        for item in memory_state.get("items", []):
            if item["type"] == "task_type" and item["content"] in ["problem-solving", "analysis", "explanation"]:
                suitability += 0.2
        
        # Check for domain
        for item in memory_state.get("items", []):
            if item["type"] == "domain" and item["content"] in ["science", "health", "technology"]:
                suitability += 0.2
        
        # Check for question type
        for item in memory_state.get("items", []):
            if item["type"] == "question_type" and item["content"] in ["explanatory", "why"]:
                suitability += 0.2
        
        # Cap at 1.0
        suitability = min(suitability, 1.0)
        
        return suitability
    
    def _identify_observations_hypotheses(
        self,
        input_text: str,
        active_items: List[Dict[str, Any]],
    ) -> tuple[List[str], List[str]]:
        """
        Identify observations and hypotheses from input text and active items.
        
        Args:
            input_text: Input text
            active_items: Active items in working memory
            
        Returns:
            Tuple of (observations, hypotheses)
        """
        observations = []
        hypotheses = []
        
        # Split input into sentences
        sentences = re.split(r'[.!?]+', input_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Identify observations and hypotheses
        for sentence in sentences:
            # Check if sentence contains hypothesis markers
            hypothesis_markers = ["maybe", "perhaps", "possibly", "probably", "likely", "could be", "might be", "hypothesis", "theory", "explanation", "reason", "cause"]
            is_hypothesis = any(marker in sentence.lower() for marker in hypothesis_markers)
            
            if is_hypothesis:
                hypotheses.append(sentence)
            else:
                observations.append(sentence)
        
        # Add observations from active items
        for item in active_items:
            if item["type"] in ["entity", "keyword", "topic"]:
                observation = f"{item['content']} is observed in the context."
                if observation not in observations:
                    observations.append(observation)
        
        # Generate hypotheses if none found
        if not hypotheses:
            hypotheses = self._generate_hypotheses(observations)
        
        return observations, hypotheses
    
    def _generate_hypotheses(self, observations: List[str]) -> List[str]:
        """
        Generate hypotheses from observations.
        
        Args:
            observations: List of observations
            
        Returns:
            List of hypotheses
        """
        hypotheses = []
        
        # Generate a general hypothesis
        if observations:
            hypotheses.append("A possible explanation is that these observations are related to a common cause.")
            hypotheses.append("These observations might be explained by a specific underlying pattern.")
            hypotheses.append("The most likely explanation involves a combination of factors.")
        
        return hypotheses
    
    def _apply_abductive_reasoning(
        self,
        observations: List[str],
        hypotheses: List[str],
    ) -> tuple[List[str], Optional[str]]:
        """
        Apply abductive reasoning to observations and hypotheses.
        
        Args:
            observations: List of observations
            hypotheses: List of hypotheses
            
        Returns:
            Tuple of (reasoning steps, best hypothesis)
        """
        steps = []
        
        # Add observations as initial steps
        for i, observation in enumerate(observations, 1):
            steps.append(f"Observation {i}: {observation}")
        
        # If no observations, add a note
        if not observations:
            steps.append("No clear observations identified.")
        
        # Add intermediate steps
        if observations:
            steps.append("Considering possible explanations for these observations...")
            
            # Add hypotheses
            for i, hypothesis in enumerate(hypotheses, 1):
                steps.append(f"Hypothesis {i}: {hypothesis}")
            
            # If no hypotheses, add a note
            if not hypotheses:
                steps.append("No clear hypotheses identified.")
                return steps, None
            
            # Evaluate hypotheses
            steps.append("Evaluating hypotheses based on simplicity, explanatory power, and plausibility...")
            
            # Evaluate each hypothesis
            hypothesis_scores = []
            for i, hypothesis in enumerate(hypotheses, 1):
                # Simple scoring based on length (shorter is simpler)
                simplicity_score = 1.0 - min(len(hypothesis) / 200, 0.9)
                
                # Explanatory power based on coverage of observations
                explanatory_score = 0.5  # Default
                
                # Plausibility based on common sense
                plausibility_score = 0.5  # Default
                
                # Calculate total score
                total_score = (simplicity_score + explanatory_score + plausibility_score) / 3
                
                hypothesis_scores.append((hypothesis, total_score))
                
                steps.append(f"Evaluation of Hypothesis {i}:")
                steps.append(f"- Simplicity: {simplicity_score:.2f}")
                steps.append(f"- Explanatory Power: {explanatory_score:.2f}")
                steps.append(f"- Plausibility: {plausibility_score:.2f}")
                steps.append(f"- Overall Score: {total_score:.2f}")
            
            # Sort hypotheses by score (descending)
            hypothesis_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select best hypothesis
            best_hypothesis = hypothesis_scores[0][0] if hypothesis_scores else None
            
            # Add conclusion
            if best_hypothesis:
                steps.append(f"The most likely explanation is: {best_hypothesis}")
            else:
                steps.append("Unable to determine the most likely explanation.")
                best_hypothesis = None
        else:
            best_hypothesis = None
        
        return steps, best_hypothesis
    
    def _generate_output(self, steps: List[str], best_hypothesis: Optional[str]) -> str:
        """
        Generate output from reasoning steps and best hypothesis.
        
        Args:
            steps: List of reasoning steps
            best_hypothesis: Best hypothesis
            
        Returns:
            Generated output
        """
        # Use best hypothesis if available
        if best_hypothesis:
            return best_hypothesis
        
        # Extract conclusion (last step)
        if steps:
            last_step = steps[-1]
            if last_step.startswith("The most likely explanation is: "):
                return last_step[len("The most likely explanation is: "):]
        
        # Fallback: combine steps
        return " ".join(steps)
    
    def _calculate_confidence(
        self,
        steps: List[str],
        observations: List[str],
        hypotheses: List[str],
    ) -> float:
        """
        Calculate confidence in the reasoning.
        
        Args:
            steps: List of reasoning steps
            observations: List of observations
            hypotheses: List of hypotheses
            
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
        
        # Adjust based on number of hypotheses
        hypothesis_count = len(hypotheses)
        if hypothesis_count >= 3:
            confidence += 0.1
        elif hypothesis_count >= 1:
            confidence += 0.0
        else:
            confidence -= 0.1
        
        # Adjust based on evaluation
        if any("Evaluation of Hypothesis" in step for step in steps):
            confidence += 0.1
        
        # Adjust based on best hypothesis selection
        if any("most likely explanation" in step for step in steps):
            confidence += 0.1
        
        # Abductive reasoning is inherently less certain than deductive
        confidence -= 0.1
        
        # Cap at 0.0 and 1.0
        confidence = max(0.0, min(confidence, 1.0))
        
        return confidence
