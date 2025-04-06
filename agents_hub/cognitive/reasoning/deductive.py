"""
Deductive reasoning mechanism for the cognitive architecture.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import re
from agents_hub.cognitive.reasoning.base import BaseReasoning

# Initialize logger
logger = logging.getLogger(__name__)


class DeductiveReasoning(BaseReasoning):
    """
    Deductive reasoning mechanism.
    
    This class implements deductive reasoning, which involves drawing
    logical conclusions from premises.
    """
    
    def __init__(self):
        """Initialize the deductive reasoning mechanism."""
        super().__init__(
            name="deductive",
            description="Deductive reasoning involves drawing logical conclusions from premises.",
        )
    
    async def apply(
        self,
        memory_state: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Apply deductive reasoning.
        
        Args:
            memory_state: Current state of working memory
            context: Context information
            
        Returns:
            Reasoning results
        """
        # Extract input and active items
        input_text = self._extract_input(memory_state)
        active_items = self._extract_active_items(memory_state)
        
        # Identify premises and conclusion
        premises, conclusion = self._identify_premises_conclusion(input_text, active_items)
        
        # Apply logical rules
        steps = self._apply_logical_rules(premises, conclusion)
        
        # Generate output
        output = self._generate_output(steps)
        
        # Calculate confidence
        confidence = self._calculate_confidence(steps)
        
        return {
            "steps": steps,
            "output": output,
            "confidence": confidence,
            "premises": premises,
            "conclusion": conclusion,
        }
    
    def get_suitability(
        self,
        memory_state: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """
        Get the suitability of deductive reasoning for the current state.
        
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
        
        # Check for logical keywords
        logical_keywords = ["if", "then", "therefore", "thus", "hence", "so", "must", "always", "never", "all", "every", "any", "none", "no", "not", "and", "or", "but", "because", "since", "given that", "assuming that", "it follows that"]
        for keyword in logical_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', input_lower):
                suitability += 0.1
        
        # Cap at 1.0
        suitability = min(suitability, 1.0)
        
        # Check for task type
        for item in memory_state.get("items", []):
            if item["type"] == "task_type" and item["content"] in ["problem-solving", "analysis"]:
                suitability += 0.2
        
        # Check for domain
        for item in memory_state.get("items", []):
            if item["type"] == "domain" and item["content"] in ["mathematics", "philosophy", "science"]:
                suitability += 0.2
        
        # Check for question type
        for item in memory_state.get("items", []):
            if item["type"] == "question_type" and item["content"] in ["factual", "yes/no"]:
                suitability += 0.1
        
        # Cap at 1.0
        suitability = min(suitability, 1.0)
        
        return suitability
    
    def _identify_premises_conclusion(
        self,
        input_text: str,
        active_items: List[Dict[str, Any]],
    ) -> tuple[List[str], Optional[str]]:
        """
        Identify premises and conclusion from input text and active items.
        
        Args:
            input_text: Input text
            active_items: Active items in working memory
            
        Returns:
            Tuple of (premises, conclusion)
        """
        premises = []
        conclusion = None
        
        # Split input into sentences
        sentences = re.split(r'[.!?]+', input_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Identify conclusion (sentence with "therefore", "thus", etc.)
        conclusion_keywords = ["therefore", "thus", "hence", "so", "it follows that", "consequently", "as a result"]
        for sentence in sentences:
            for keyword in conclusion_keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', sentence.lower()):
                    conclusion = sentence
                    break
            if conclusion:
                break
        
        # If no conclusion found, use the last sentence
        if not conclusion and sentences:
            conclusion = sentences[-1]
        
        # Identify premises (sentences that are not the conclusion)
        for sentence in sentences:
            if sentence != conclusion:
                premises.append(sentence)
        
        # Add premises from active items
        for item in active_items:
            if item["type"] in ["entity", "keyword", "topic", "domain"]:
                premise = f"{item['content']} is relevant to the question."
                if premise not in premises:
                    premises.append(premise)
        
        return premises, conclusion
    
    def _apply_logical_rules(
        self,
        premises: List[str],
        conclusion: Optional[str],
    ) -> List[str]:
        """
        Apply logical rules to premises and conclusion.
        
        Args:
            premises: List of premises
            conclusion: Conclusion
            
        Returns:
            List of reasoning steps
        """
        steps = []
        
        # Add premises as initial steps
        for i, premise in enumerate(premises, 1):
            steps.append(f"Premise {i}: {premise}")
        
        # If no premises, add a note
        if not premises:
            steps.append("No clear premises identified.")
        
        # If no conclusion, add a note
        if not conclusion:
            steps.append("No clear conclusion identified.")
            return steps
        
        # Add intermediate steps
        if premises:
            steps.append("Considering the above premises...")
            
            # Check for conditional statements
            conditionals = [p for p in premises if "if" in p.lower() and "then" in p.lower()]
            if conditionals:
                steps.append("Applying conditional logic to the premises.")
                
                # Extract conditions and consequences
                for conditional in conditionals:
                    match = re.search(r'if\s+(.*?)\s+then\s+(.*)', conditional, re.IGNORECASE)
                    if match:
                        condition = match.group(1)
                        consequence = match.group(2)
                        steps.append(f"If {condition}, then {consequence}.")
                        
                        # Check if condition is met in other premises
                        for premise in premises:
                            if condition.lower() in premise.lower() and premise != conditional:
                                steps.append(f"Since {condition} is established, {consequence} follows.")
            
            # Check for universal statements
            universals = [p for p in premises if any(word in p.lower() for word in ["all", "every", "any", "always"])]
            if universals:
                steps.append("Applying universal logic to the premises.")
                
                # Extract universal claims
                for universal in universals:
                    steps.append(f"Considering the universal claim: {universal}")
            
            # Check for negations
            negations = [p for p in premises if any(word in p.lower() for word in ["not", "no", "none", "never"])]
            if negations:
                steps.append("Applying negation logic to the premises.")
                
                # Extract negations
                for negation in negations:
                    steps.append(f"Considering the negation: {negation}")
        
        # Add conclusion
        steps.append(f"Therefore, {conclusion}")
        
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
        if steps:
            conclusion = steps[-1]
            if conclusion.startswith("Therefore, "):
                return conclusion[len("Therefore, "):]
        
        # Fallback: combine steps
        return " ".join(steps)
    
    def _calculate_confidence(self, steps: List[str]) -> float:
        """
        Calculate confidence in the reasoning.
        
        Args:
            steps: List of reasoning steps
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Base confidence
        confidence = 0.5
        
        # Adjust based on number of premises
        premise_count = sum(1 for step in steps if step.startswith("Premise "))
        if premise_count >= 3:
            confidence += 0.2
        elif premise_count >= 1:
            confidence += 0.1
        else:
            confidence -= 0.2
        
        # Adjust based on conditional logic
        if any("if" in step.lower() and "then" in step.lower() for step in steps):
            confidence += 0.1
        
        # Adjust based on universal logic
        if any(word in " ".join(steps).lower() for word in ["all", "every", "any", "always"]):
            confidence += 0.1
        
        # Adjust based on conclusion
        if any(step.startswith("Therefore, ") for step in steps):
            confidence += 0.1
        
        # Cap at 0.0 and 1.0
        confidence = max(0.0, min(confidence, 1.0))
        
        return confidence
