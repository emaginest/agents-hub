"""
Causal reasoning mechanism for the cognitive architecture.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import re
from agents_hub.cognitive.reasoning.base import BaseReasoning

# Initialize logger
logger = logging.getLogger(__name__)


class CausalReasoning(BaseReasoning):
    """
    Causal reasoning mechanism.
    
    This class implements causal reasoning, which involves identifying
    cause-effect relationships and making inferences based on them.
    """
    
    def __init__(self):
        """Initialize the causal reasoning mechanism."""
        super().__init__(
            name="causal",
            description="Causal reasoning involves identifying cause-effect relationships and making inferences based on them.",
        )
    
    async def apply(
        self,
        memory_state: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Apply causal reasoning.
        
        Args:
            memory_state: Current state of working memory
            context: Context information
            
        Returns:
            Reasoning results
        """
        # Extract input and active items
        input_text = self._extract_input(memory_state)
        active_items = self._extract_active_items(memory_state)
        
        # Identify causes and effects
        causes, effects = self._identify_causes_effects(input_text, active_items)
        
        # Identify causal relationships
        causal_relationships = self._identify_causal_relationships(causes, effects, input_text)
        
        # Apply causal reasoning
        steps, conclusion = self._apply_causal_reasoning(causal_relationships)
        
        # Generate output
        output = self._generate_output(steps, conclusion)
        
        # Calculate confidence
        confidence = self._calculate_confidence(steps, causal_relationships)
        
        return {
            "steps": steps,
            "output": output,
            "confidence": confidence,
            "causes": causes,
            "effects": effects,
            "causal_relationships": causal_relationships,
        }
    
    def get_suitability(
        self,
        memory_state: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """
        Get the suitability of causal reasoning for the current state.
        
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
        
        # Check for causal keywords
        causal_keywords = ["cause", "effect", "result", "lead to", "leads to", "because", "since", "due to", "as a result", "consequently", "therefore", "thus", "hence", "impact", "influence", "affect", "affects", "affected", "caused by", "resulting in", "outcome", "consequence"]
        for keyword in causal_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', input_lower):
                suitability += 0.1
        
        # Cap at 1.0
        suitability = min(suitability, 1.0)
        
        # Check for task type
        for item in memory_state.get("items", []):
            if item["type"] == "task_type" and item["content"] in ["analysis", "explanation", "problem-solving"]:
                suitability += 0.2
        
        # Check for domain
        for item in memory_state.get("items", []):
            if item["type"] == "domain" and item["content"] in ["science", "health", "business", "technology"]:
                suitability += 0.2
        
        # Check for question type
        for item in memory_state.get("items", []):
            if item["type"] == "question_type" and item["content"] in ["explanatory", "why"]:
                suitability += 0.2
        
        # Cap at 1.0
        suitability = min(suitability, 1.0)
        
        return suitability
    
    def _identify_causes_effects(
        self,
        input_text: str,
        active_items: List[Dict[str, Any]],
    ) -> tuple[List[str], List[str]]:
        """
        Identify causes and effects from input text and active items.
        
        Args:
            input_text: Input text
            active_items: Active items in working memory
            
        Returns:
            Tuple of (causes, effects)
        """
        causes = []
        effects = []
        
        # Look for explicit cause-effect statements
        causal_patterns = [
            r'(.*) causes? (.*)',
            r'(.*) leads? to (.*)',
            r'(.*) results? in (.*)',
            r'(.*) produces? (.*)',
            r'(.*) triggers? (.*)',
            r'(.*) is caused by (.*)',
            r'(.*) is the result of (.*)',
            r'(.*) is due to (.*)',
            r'(.*) happens because (.*)',
            r'(.*) is triggered by (.*)',
            r'because (.*), (.*)',
            r'since (.*), (.*)',
            r'(.*), therefore (.*)',
            r'(.*), thus (.*)',
            r'(.*), hence (.*)',
            r'(.*), consequently (.*)',
            r'(.*), as a result (.*)',
        ]
        
        for pattern in causal_patterns:
            matches = re.finditer(pattern, input_text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) == 2:
                    # Check pattern type
                    if pattern.startswith(r'(.*) is caused by') or pattern.startswith(r'(.*) is the result of') or pattern.startswith(r'(.*) is due to') or pattern.startswith(r'(.*) is triggered by') or pattern.startswith(r'because') or pattern.startswith(r'since'):
                        cause = match.group(2).strip() if pattern.startswith(r'(.*) is') else match.group(1).strip()
                        effect = match.group(1).strip() if pattern.startswith(r'(.*) is') else match.group(2).strip()
                    else:
                        cause = match.group(1).strip()
                        effect = match.group(2).strip()
                    
                    if cause and cause not in causes:
                        causes.append(cause)
                    if effect and effect not in effects:
                        effects.append(effect)
        
        # Add causes and effects from active items
        for item in active_items:
            if item["type"] in ["entity", "keyword", "topic"]:
                # Check if item is mentioned in input
                if item["content"].lower() in input_text.lower():
                    # Check if it's more likely a cause or effect
                    if any(item["content"].lower() in cause.lower() for cause in causes):
                        if item["content"] not in causes:
                            causes.append(item["content"])
                    elif any(item["content"].lower() in effect.lower() for effect in effects):
                        if item["content"] not in effects:
                            effects.append(item["content"])
        
        return causes, effects
    
    def _identify_causal_relationships(
        self,
        causes: List[str],
        effects: List[str],
        input_text: str,
    ) -> List[Dict[str, str]]:
        """
        Identify causal relationships between causes and effects.
        
        Args:
            causes: List of causes
            effects: List of effects
            input_text: Input text
            
        Returns:
            List of causal relationships
        """
        relationships = []
        
        # Look for explicit relationships in input text
        for cause in causes:
            for effect in effects:
                # Check if cause and effect are mentioned together
                cause_effect_pattern = r'{}.*{}|{}.*{}'.format(
                    re.escape(cause),
                    re.escape(effect),
                    re.escape(effect),
                    re.escape(cause)
                )
                
                if re.search(cause_effect_pattern, input_text, re.IGNORECASE):
                    # Determine relationship type
                    relationship_type = "causes"
                    
                    # Check for modifiers
                    if re.search(r'may|might|could|possibly|perhaps', input_text, re.IGNORECASE):
                        relationship_type = "may cause"
                    elif re.search(r'always|definitely|certainly|inevitably', input_text, re.IGNORECASE):
                        relationship_type = "always causes"
                    elif re.search(r'sometimes|occasionally|in some cases', input_text, re.IGNORECASE):
                        relationship_type = "sometimes causes"
                    elif re.search(r'rarely|seldom', input_text, re.IGNORECASE):
                        relationship_type = "rarely causes"
                    
                    relationships.append({
                        "cause": cause,
                        "effect": effect,
                        "type": relationship_type,
                    })
        
        # If no relationships found, create inferred relationships
        if not relationships and causes and effects:
            for cause in causes:
                for effect in effects:
                    relationships.append({
                        "cause": cause,
                        "effect": effect,
                        "type": "may cause",
                    })
        
        return relationships
    
    def _apply_causal_reasoning(
        self,
        causal_relationships: List[Dict[str, str]],
    ) -> tuple[List[str], str]:
        """
        Apply causal reasoning to causal relationships.
        
        Args:
            causal_relationships: List of causal relationships
            
        Returns:
            Tuple of (reasoning steps, conclusion)
        """
        steps = []
        
        # Add causal relationships
        steps.append("Identifying causal relationships:")
        for i, relationship in enumerate(causal_relationships, 1):
            steps.append(f"Relationship {i}: {relationship['cause']} {relationship['type']} {relationship['effect']}")
        
        # If no relationships, add a note
        if not causal_relationships:
            steps.append("No clear causal relationships identified.")
            return steps, "Unable to determine clear cause-effect relationships."
        
        # Add reasoning about causal chains
        if len(causal_relationships) >= 2:
            steps.append("Analyzing potential causal chains...")
            
            # Look for chains where effect of one relationship is cause of another
            chains = []
            for rel1 in causal_relationships:
                for rel2 in causal_relationships:
                    if rel1 != rel2 and rel1["effect"] == rel2["cause"]:
                        chains.append((rel1, rel2))
            
            # Add chains to steps
            for i, (rel1, rel2) in enumerate(chains, 1):
                steps.append(f"Causal Chain {i}: {rel1['cause']} → {rel1['effect']} → {rel2['effect']}")
            
            if not chains:
                steps.append("No clear causal chains identified.")
        
        # Add reasoning about causal factors
        steps.append("Analyzing causal factors...")
        
        # Count occurrences of each cause
        cause_counts = {}
        for relationship in causal_relationships:
            cause = relationship["cause"]
            cause_counts[cause] = cause_counts.get(cause, 0) + 1
        
        # Identify primary causes (most frequent)
        primary_causes = [cause for cause, count in cause_counts.items() if count == max(cause_counts.values())]
        
        for cause in primary_causes:
            steps.append(f"Primary Causal Factor: {cause}")
        
        # Generate conclusion
        if primary_causes:
            conclusion = f"The primary cause appears to be {primary_causes[0]}. "
            
            # Add effects
            effects = [rel["effect"] for rel in causal_relationships if rel["cause"] == primary_causes[0]]
            if effects:
                conclusion += f"This {causal_relationships[0]['type']} {effects[0]}."
            
            # Add chain if available
            if len(causal_relationships) >= 2 and chains:
                conclusion += f" Furthermore, this can lead to {chains[0][1]['effect']}."
        else:
            conclusion = "The causal relationships are complex and interconnected."
        
        steps.append(f"Therefore, {conclusion}")
        
        return steps, conclusion
    
    def _generate_output(self, steps: List[str], conclusion: str) -> str:
        """
        Generate output from reasoning steps and conclusion.
        
        Args:
            steps: List of reasoning steps
            conclusion: Conclusion
            
        Returns:
            Generated output
        """
        return conclusion
    
    def _calculate_confidence(
        self,
        steps: List[str],
        causal_relationships: List[Dict[str, str]],
    ) -> float:
        """
        Calculate confidence in the reasoning.
        
        Args:
            steps: List of reasoning steps
            causal_relationships: List of causal relationships
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Base confidence
        confidence = 0.5
        
        # Adjust based on number of relationships
        relationship_count = len(causal_relationships)
        if relationship_count >= 3:
            confidence += 0.2
        elif relationship_count >= 2:
            confidence += 0.1
        elif relationship_count >= 1:
            confidence += 0.0
        else:
            confidence -= 0.2
        
        # Adjust based on relationship types
        certain_relationships = sum(1 for rel in causal_relationships if rel["type"] in ["causes", "always causes"])
        uncertain_relationships = sum(1 for rel in causal_relationships if rel["type"] in ["may cause", "sometimes causes", "rarely causes"])
        
        if certain_relationships >= 2:
            confidence += 0.2
        elif certain_relationships >= 1:
            confidence += 0.1
        
        if uncertain_relationships > certain_relationships:
            confidence -= 0.1
        
        # Adjust based on causal chains
        if any("Causal Chain" in step for step in steps):
            confidence += 0.1
        
        # Adjust based on primary causal factors
        if any("Primary Causal Factor" in step for step in steps):
            confidence += 0.1
        
        # Cap at 0.0 and 1.0
        confidence = max(0.0, min(confidence, 1.0))
        
        return confidence
