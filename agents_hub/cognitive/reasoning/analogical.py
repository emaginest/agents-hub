"""
Analogical reasoning mechanism for the cognitive architecture.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import re
from agents_hub.cognitive.reasoning.base import BaseReasoning

# Initialize logger
logger = logging.getLogger(__name__)


class AnalogicalReasoning(BaseReasoning):
    """
    Analogical reasoning mechanism.
    
    This class implements analogical reasoning, which involves drawing
    parallels between different situations or domains.
    """
    
    def __init__(self):
        """Initialize the analogical reasoning mechanism."""
        super().__init__(
            name="analogical",
            description="Analogical reasoning involves drawing parallels between different situations or domains.",
        )
    
    async def apply(
        self,
        memory_state: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Apply analogical reasoning.
        
        Args:
            memory_state: Current state of working memory
            context: Context information
            
        Returns:
            Reasoning results
        """
        # Extract input and active items
        input_text = self._extract_input(memory_state)
        active_items = self._extract_active_items(memory_state)
        
        # Identify source and target domains
        source_domain, target_domain = self._identify_domains(input_text, active_items)
        
        # Identify mappings between domains
        mappings = self._identify_mappings(source_domain, target_domain, input_text)
        
        # Apply analogical reasoning
        steps, conclusion = self._apply_analogical_reasoning(source_domain, target_domain, mappings)
        
        # Generate output
        output = self._generate_output(steps, conclusion)
        
        # Calculate confidence
        confidence = self._calculate_confidence(steps, mappings)
        
        return {
            "steps": steps,
            "output": output,
            "confidence": confidence,
            "source_domain": source_domain,
            "target_domain": target_domain,
            "mappings": mappings,
        }
    
    def get_suitability(
        self,
        memory_state: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """
        Get the suitability of analogical reasoning for the current state.
        
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
        
        # Check for analogy keywords
        analogy_keywords = ["like", "as", "similar", "analogy", "metaphor", "comparison", "compare", "parallel", "resembles", "resemblance", "corresponds", "corresponds to", "just as", "in the same way", "similarly", "comparable", "equivalent"]
        for keyword in analogy_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', input_lower):
                suitability += 0.1
        
        # Cap at 1.0
        suitability = min(suitability, 1.0)
        
        # Check for task type
        for item in memory_state.get("items", []):
            if item["type"] == "task_type" and item["content"] in ["comparison", "explanation", "creation"]:
                suitability += 0.2
        
        # Check for domain
        for item in memory_state.get("items", []):
            if item["type"] == "domain" and item["content"] in ["education", "arts", "philosophy"]:
                suitability += 0.2
        
        # Check for question type
        for item in memory_state.get("items", []):
            if item["type"] == "question_type" and item["content"] in ["explanatory", "comparative"]:
                suitability += 0.2
        
        # Cap at 1.0
        suitability = min(suitability, 1.0)
        
        return suitability
    
    def _identify_domains(
        self,
        input_text: str,
        active_items: List[Dict[str, Any]],
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Identify source and target domains from input text and active items.
        
        Args:
            input_text: Input text
            active_items: Active items in working memory
            
        Returns:
            Tuple of (source_domain, target_domain)
        """
        source_domain = {"name": "", "description": "", "elements": []}
        target_domain = {"name": "", "description": "", "elements": []}
        
        # Look for explicit domain comparisons
        comparison_patterns = [
            r'(.*) is like (.*)',
            r'(.*) is similar to (.*)',
            r'(.*) resembles (.*)',
            r'(.*) can be compared to (.*)',
            r'(.*) is analogous to (.*)',
            r'compare (.*) to (.*)',
            r'(.*) corresponds to (.*)',
        ]
        
        for pattern in comparison_patterns:
            match = re.search(pattern, input_text, re.IGNORECASE)
            if match:
                target_domain["name"] = match.group(1).strip()
                source_domain["name"] = match.group(2).strip()
                break
        
        # If no explicit comparison found, try to infer from content
        if not source_domain["name"] or not target_domain["name"]:
            # Extract domains from active items
            domains = []
            for item in active_items:
                if item["type"] == "domain":
                    domains.append(item["content"])
            
            # If two domains found, use them
            if len(domains) >= 2:
                target_domain["name"] = domains[0]
                source_domain["name"] = domains[1]
            # Otherwise, use a generic source domain
            elif len(domains) == 1:
                target_domain["name"] = domains[0]
                source_domain["name"] = "familiar concept"
            else:
                target_domain["name"] = "current situation"
                source_domain["name"] = "familiar concept"
        
        # Extract elements for each domain
        source_domain["elements"] = self._extract_domain_elements(source_domain["name"], input_text)
        target_domain["elements"] = self._extract_domain_elements(target_domain["name"], input_text)
        
        # Add descriptions
        source_domain["description"] = f"The domain of {source_domain['name']}"
        target_domain["description"] = f"The domain of {target_domain['name']}"
        
        return source_domain, target_domain
    
    def _extract_domain_elements(self, domain_name: str, input_text: str) -> List[str]:
        """
        Extract elements for a domain from input text.
        
        Args:
            domain_name: Name of the domain
            input_text: Input text
            
        Returns:
            List of domain elements
        """
        elements = []
        
        # Look for sentences mentioning the domain
        domain_sentences = []
        sentences = re.split(r'[.!?]+', input_text)
        for sentence in sentences:
            if domain_name.lower() in sentence.lower():
                domain_sentences.append(sentence)
        
        # Extract entities from domain sentences
        for sentence in domain_sentences:
            # Extract capitalized words
            entities = re.findall(r'\b[A-Z][a-z]+\b', sentence)
            elements.extend(entities)
        
        # Add generic elements if none found
        if not elements:
            elements = ["components", "structure", "behavior", "properties"]
        
        return elements
    
    def _identify_mappings(
        self,
        source_domain: Dict[str, Any],
        target_domain: Dict[str, Any],
        input_text: str,
    ) -> List[Dict[str, str]]:
        """
        Identify mappings between source and target domains.
        
        Args:
            source_domain: Source domain information
            target_domain: Target domain information
            input_text: Input text
            
        Returns:
            List of mappings between domains
        """
        mappings = []
        
        # Look for explicit mappings
        mapping_patterns = [
            r'(.*) in (.*) is like (.*) in (.*)',
            r'(.*) corresponds to (.*)',
            r'(.*) is the (.*) of (.*)',
        ]
        
        for pattern in mapping_patterns:
            matches = re.finditer(pattern, input_text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) == 4:
                    source_element = match.group(3).strip()
                    target_element = match.group(1).strip()
                    mappings.append({
                        "source": source_element,
                        "target": target_element,
                        "relation": "corresponds to",
                    })
                elif len(match.groups()) == 2:
                    target_element = match.group(1).strip()
                    source_element = match.group(2).strip()
                    mappings.append({
                        "source": source_element,
                        "target": target_element,
                        "relation": "corresponds to",
                    })
                elif len(match.groups()) == 3:
                    target_element = match.group(1).strip()
                    relation = match.group(2).strip()
                    source_domain_name = match.group(3).strip()
                    if source_domain_name.lower() == source_domain["name"].lower():
                        mappings.append({
                            "source": "corresponding element",
                            "target": target_element,
                            "relation": relation,
                        })
        
        # If no explicit mappings found, create inferred mappings
        if not mappings:
            # Map elements based on position
            source_elements = source_domain["elements"]
            target_elements = target_domain["elements"]
            
            for i in range(min(len(source_elements), len(target_elements))):
                mappings.append({
                    "source": source_elements[i],
                    "target": target_elements[i],
                    "relation": "may correspond to",
                })
        
        return mappings
    
    def _apply_analogical_reasoning(
        self,
        source_domain: Dict[str, Any],
        target_domain: Dict[str, Any],
        mappings: List[Dict[str, str]],
    ) -> tuple[List[str], str]:
        """
        Apply analogical reasoning to domains and mappings.
        
        Args:
            source_domain: Source domain information
            target_domain: Target domain information
            mappings: Mappings between domains
            
        Returns:
            Tuple of (reasoning steps, conclusion)
        """
        steps = []
        
        # Add domain information
        steps.append(f"Source Domain: {source_domain['name']}")
        steps.append(f"Target Domain: {target_domain['name']}")
        
        # Add mappings
        steps.append("Identifying mappings between domains:")
        for i, mapping in enumerate(mappings, 1):
            steps.append(f"Mapping {i}: {mapping['target']} in {target_domain['name']} {mapping['relation']} {mapping['source']} in {source_domain['name']}")
        
        # If no mappings, add a note
        if not mappings:
            steps.append("No clear mappings identified between domains.")
            return steps, "Unable to draw a clear analogy."
        
        # Add reasoning about structural alignment
        steps.append("Analyzing structural alignment between domains...")
        
        # Add reasoning about inferences
        steps.append("Drawing inferences based on the analogy...")
        
        # Generate conclusion
        conclusion = f"The {target_domain['name']} can be understood by analogy to {source_domain['name']}. "
        
        if mappings:
            conclusion += f"Just as {mappings[0]['source']} functions in {source_domain['name']}, "
            conclusion += f"{mappings[0]['target']} serves a similar role in {target_domain['name']}."
        
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
        mappings: List[Dict[str, str]],
    ) -> float:
        """
        Calculate confidence in the reasoning.
        
        Args:
            steps: List of reasoning steps
            mappings: Mappings between domains
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Base confidence
        confidence = 0.5
        
        # Adjust based on number of mappings
        mapping_count = len(mappings)
        if mapping_count >= 3:
            confidence += 0.2
        elif mapping_count >= 2:
            confidence += 0.1
        elif mapping_count >= 1:
            confidence += 0.0
        else:
            confidence -= 0.2
        
        # Adjust based on mapping quality
        explicit_mappings = sum(1 for mapping in mappings if mapping["relation"] == "corresponds to")
        if explicit_mappings >= 2:
            confidence += 0.2
        elif explicit_mappings >= 1:
            confidence += 0.1
        
        # Adjust based on structural alignment
        if any("structural alignment" in step for step in steps):
            confidence += 0.1
        
        # Adjust based on inference drawing
        if any("inferences" in step for step in steps):
            confidence += 0.1
        
        # Analogical reasoning is inherently less certain than deductive
        confidence -= 0.1
        
        # Cap at 0.0 and 1.0
        confidence = max(0.0, min(confidence, 1.0))
        
        return confidence
