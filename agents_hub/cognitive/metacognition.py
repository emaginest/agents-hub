"""
Metacognition system for the cognitive architecture.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import re

# Initialize logger
logger = logging.getLogger(__name__)


class Metacognition:
    """
    Metacognitive capabilities for self-reflection and improvement.
    
    This class provides agents with the ability to monitor and control their
    cognitive processes, evaluate their performance, and adapt their strategies.
    """
    
    def __init__(
        self,
        reflection_depth: int = 1,
        confidence_threshold: float = 0.7,
        strategy_adaptation: bool = True,
    ):
        """
        Initialize the metacognition system.
        
        Args:
            reflection_depth: Depth of self-reflection (1-3)
            confidence_threshold: Threshold for confidence estimation
            strategy_adaptation: Whether to adapt strategies based on performance
        """
        self.reflection_depth = max(1, min(reflection_depth, 3))
        self.confidence_threshold = confidence_threshold
        self.strategy_adaptation = strategy_adaptation
    
    async def reflect(
        self,
        reasoning_result: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Reflect on the reasoning process.
        
        Args:
            reasoning_result: Result of the reasoning process
            context: Context information
            
        Returns:
            Reflection results including confidence estimation and strategy recommendations
        """
        try:
            # Evaluate the reasoning process
            evaluation = await self._evaluate_reasoning(reasoning_result)
            
            # Estimate confidence in the result
            confidence = await self._estimate_confidence(reasoning_result, evaluation)
            
            # Detect and correct errors
            corrected_result = await self._detect_and_correct_errors(reasoning_result, evaluation)
            
            # Select strategy for future reasoning
            strategy_recommendation = await self._select_strategy(evaluation, context)
            
            # Generate self-explanation
            explanation = await self._generate_explanation(corrected_result, confidence)
            
            # Generate reflections
            reflections = await self._generate_reflections(
                reasoning_result,
                evaluation,
                confidence,
                corrected_result,
                strategy_recommendation,
            )
            
            # Determine final output
            if confidence >= self.confidence_threshold:
                final_output = corrected_result["output"]
            else:
                final_output = self._generate_low_confidence_output(corrected_result, confidence)
            
            return {
                "evaluation": evaluation,
                "confidence": confidence,
                "corrected_result": corrected_result,
                "strategy_recommendation": strategy_recommendation,
                "explanation": explanation,
                "reflections": reflections,
                "final_output": final_output,
            }
        
        except Exception as e:
            logger.exception(f"Error in metacognitive reflection: {e}")
            
            # Return a fallback result
            return {
                "evaluation": {"quality": "unknown", "issues": [str(e)]},
                "confidence": 0.5,
                "corrected_result": reasoning_result,
                "strategy_recommendation": {},
                "explanation": "I encountered an error during my reflection process.",
                "reflections": ["Error in metacognitive reflection."],
                "final_output": reasoning_result.get("output", ""),
            }
    
    async def _evaluate_reasoning(self, reasoning_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the reasoning process.
        
        Args:
            reasoning_result: Result of the reasoning process
            
        Returns:
            Evaluation results
        """
        evaluation = {
            "quality": "unknown",
            "strengths": [],
            "weaknesses": [],
            "issues": [],
        }
        
        # Get reasoning mechanism
        mechanism = reasoning_result.get("mechanism", "unknown")
        
        # Get reasoning steps
        steps = reasoning_result.get("steps", [])
        
        # Get confidence
        confidence = reasoning_result.get("confidence", 0.0)
        
        # Evaluate quality based on confidence
        if confidence >= 0.8:
            evaluation["quality"] = "high"
        elif confidence >= 0.6:
            evaluation["quality"] = "medium"
        else:
            evaluation["quality"] = "low"
        
        # Evaluate strengths
        if len(steps) >= 5:
            evaluation["strengths"].append("Thorough reasoning process with multiple steps.")
        
        if confidence >= 0.7:
            evaluation["strengths"].append("High confidence in the reasoning.")
        
        # Evaluate weaknesses
        if len(steps) < 3:
            evaluation["weaknesses"].append("Limited reasoning steps.")
        
        if confidence < 0.5:
            evaluation["weaknesses"].append("Low confidence in the reasoning.")
        
        # Check for specific issues based on mechanism
        if mechanism == "deductive":
            if not any("Premise" in step for step in steps):
                evaluation["issues"].append("No clear premises identified in deductive reasoning.")
            
            if not any("Therefore" in step for step in steps):
                evaluation["issues"].append("No clear conclusion in deductive reasoning.")
        
        elif mechanism == "inductive":
            if not any("Observation" in step for step in steps):
                evaluation["issues"].append("No clear observations identified in inductive reasoning.")
            
            if not any("pattern" in step.lower() for step in steps):
                evaluation["issues"].append("No clear pattern identified in inductive reasoning.")
        
        elif mechanism == "abductive":
            if not any("Hypothesis" in step for step in steps):
                evaluation["issues"].append("No clear hypotheses identified in abductive reasoning.")
            
            if not any("most likely explanation" in step.lower() for step in steps):
                evaluation["issues"].append("No clear best explanation in abductive reasoning.")
        
        elif mechanism == "analogical":
            if not any("Source Domain" in step for step in steps):
                evaluation["issues"].append("No clear source domain identified in analogical reasoning.")
            
            if not any("Target Domain" in step for step in steps):
                evaluation["issues"].append("No clear target domain identified in analogical reasoning.")
            
            if not any("Mapping" in step for step in steps):
                evaluation["issues"].append("No clear mappings identified in analogical reasoning.")
        
        elif mechanism == "causal":
            if not any("Relationship" in step for step in steps):
                evaluation["issues"].append("No clear causal relationships identified in causal reasoning.")
        
        return evaluation
    
    async def _estimate_confidence(
        self,
        reasoning_result: Dict[str, Any],
        evaluation: Dict[str, Any],
    ) -> float:
        """
        Estimate confidence in the reasoning result.
        
        Args:
            reasoning_result: Result of the reasoning process
            evaluation: Evaluation of the reasoning process
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Start with the reasoning confidence
        confidence = reasoning_result.get("confidence", 0.5)
        
        # Adjust based on evaluation
        if evaluation["quality"] == "high":
            confidence += 0.1
        elif evaluation["quality"] == "low":
            confidence -= 0.1
        
        # Adjust based on strengths
        confidence += 0.05 * len(evaluation["strengths"])
        
        # Adjust based on weaknesses
        confidence -= 0.05 * len(evaluation["weaknesses"])
        
        # Adjust based on issues
        confidence -= 0.1 * len(evaluation["issues"])
        
        # Cap at 0.0 and 1.0
        confidence = max(0.0, min(confidence, 1.0))
        
        return confidence
    
    async def _detect_and_correct_errors(
        self,
        reasoning_result: Dict[str, Any],
        evaluation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Detect and correct errors in the reasoning result.
        
        Args:
            reasoning_result: Result of the reasoning process
            evaluation: Evaluation of the reasoning process
            
        Returns:
            Corrected reasoning result
        """
        # Start with the original result
        corrected_result = reasoning_result.copy()
        
        # Check for issues
        issues = evaluation.get("issues", [])
        
        if issues:
            # Add a note about the issues
            output = corrected_result.get("output", "")
            
            # Check if output already acknowledges limitations
            if not any(phrase in output.lower() for phrase in ["however", "although", "note that", "it's important to", "keep in mind", "consider that"]):
                # Add a note about limitations
                limitation_note = " However, it's important to note that "
                
                if len(issues) == 1:
                    limitation_note += issues[0].lower()
                else:
                    limitation_note += "there are some limitations in this reasoning: "
                    limitation_note += "; ".join(issue.lower() for issue in issues)
                
                limitation_note += "."
                
                corrected_result["output"] = output + limitation_note
        
        return corrected_result
    
    async def _select_strategy(
        self,
        evaluation: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Select strategy for future reasoning.
        
        Args:
            evaluation: Evaluation of the reasoning process
            context: Context information
            
        Returns:
            Strategy recommendation
        """
        if not self.strategy_adaptation:
            return {}
        
        strategy = {
            "recommended_mechanism": None,
            "reasoning_depth": None,
            "use_multiple_mechanisms": False,
            "explanation": "",
        }
        
        # Get current mechanism
        current_mechanism = context.get("reasoning_mechanism", "unknown")
        
        # Check for issues
        issues = evaluation.get("issues", [])
        
        if issues:
            # Recommend a different mechanism based on issues
            if "No clear premises" in str(issues) or "No clear conclusion" in str(issues):
                strategy["recommended_mechanism"] = "abductive"
                strategy["explanation"] = "Switching to abductive reasoning to generate hypotheses when premises or conclusions are unclear."
            
            elif "No clear observations" in str(issues) or "No clear pattern" in str(issues):
                strategy["recommended_mechanism"] = "deductive"
                strategy["explanation"] = "Switching to deductive reasoning when observations or patterns are unclear."
            
            elif "No clear hypotheses" in str(issues) or "No clear best explanation" in str(issues):
                strategy["recommended_mechanism"] = "causal"
                strategy["explanation"] = "Switching to causal reasoning to identify cause-effect relationships when hypotheses are unclear."
            
            elif "No clear source domain" in str(issues) or "No clear target domain" in str(issues) or "No clear mappings" in str(issues):
                strategy["recommended_mechanism"] = "deductive"
                strategy["explanation"] = "Switching to deductive reasoning when analogical domains or mappings are unclear."
            
            elif "No clear causal relationships" in str(issues):
                strategy["recommended_mechanism"] = "abductive"
                strategy["explanation"] = "Switching to abductive reasoning to generate hypotheses when causal relationships are unclear."
        
        # If quality is low, recommend using multiple mechanisms
        if evaluation["quality"] == "low":
            strategy["use_multiple_mechanisms"] = True
            strategy["explanation"] += " Using multiple reasoning mechanisms to improve confidence."
        
        # If no specific recommendation, use the current mechanism
        if not strategy["recommended_mechanism"]:
            strategy["recommended_mechanism"] = current_mechanism
        
        # Recommend reasoning depth based on quality
        if evaluation["quality"] == "high":
            strategy["reasoning_depth"] = 1
        elif evaluation["quality"] == "medium":
            strategy["reasoning_depth"] = 2
        else:
            strategy["reasoning_depth"] = 3
        
        return strategy
    
    async def _generate_explanation(
        self,
        corrected_result: Dict[str, Any],
        confidence: float,
    ) -> str:
        """
        Generate self-explanation for the reasoning process.
        
        Args:
            corrected_result: Corrected reasoning result
            confidence: Confidence in the result
            
        Returns:
            Self-explanation
        """
        # Get reasoning mechanism
        mechanism = corrected_result.get("mechanism", "unknown")
        
        # Get reasoning steps
        steps = corrected_result.get("steps", [])
        
        # Generate explanation based on mechanism
        explanation = f"I used {mechanism} reasoning to approach this problem. "
        
        if mechanism == "deductive":
            explanation += "This involves drawing logical conclusions from premises. "
        elif mechanism == "inductive":
            explanation += "This involves drawing general conclusions from specific observations. "
        elif mechanism == "abductive":
            explanation += "This involves forming the most likely explanation for observations. "
        elif mechanism == "analogical":
            explanation += "This involves drawing parallels between different situations or domains. "
        elif mechanism == "causal":
            explanation += "This involves identifying cause-effect relationships. "
        
        # Add confidence information
        if confidence >= 0.8:
            explanation += "I have high confidence in this reasoning. "
        elif confidence >= 0.6:
            explanation += "I have moderate confidence in this reasoning. "
        else:
            explanation += "I have low confidence in this reasoning. "
        
        # Add reasoning steps summary
        if len(steps) > 0:
            explanation += f"My reasoning involved {len(steps)} steps, "
            
            if mechanism == "deductive":
                premise_count = sum(1 for step in steps if "Premise" in step)
                explanation += f"including {premise_count} premises. "
            elif mechanism == "inductive":
                observation_count = sum(1 for step in steps if "Observation" in step)
                explanation += f"including {observation_count} observations. "
            elif mechanism == "abductive":
                hypothesis_count = sum(1 for step in steps if "Hypothesis" in step)
                explanation += f"including {hypothesis_count} hypotheses. "
            elif mechanism == "analogical":
                mapping_count = sum(1 for step in steps if "Mapping" in step)
                explanation += f"including {mapping_count} mappings between domains. "
            elif mechanism == "causal":
                relationship_count = sum(1 for step in steps if "Relationship" in step)
                explanation += f"including {relationship_count} causal relationships. "
        
        return explanation
    
    async def _generate_reflections(
        self,
        reasoning_result: Dict[str, Any],
        evaluation: Dict[str, Any],
        confidence: float,
        corrected_result: Dict[str, Any],
        strategy_recommendation: Dict[str, Any],
    ) -> List[str]:
        """
        Generate reflections on the reasoning process.
        
        Args:
            reasoning_result: Original reasoning result
            evaluation: Evaluation of the reasoning process
            confidence: Confidence in the result
            corrected_result: Corrected reasoning result
            strategy_recommendation: Strategy recommendation
            
        Returns:
            List of reflections
        """
        reflections = []
        
        # Add reflection on reasoning quality
        reflections.append(f"The quality of my reasoning is {evaluation['quality']}.")
        
        # Add reflection on strengths
        if evaluation["strengths"]:
            reflections.append("Strengths in my reasoning:")
            for strength in evaluation["strengths"]:
                reflections.append(f"- {strength}")
        
        # Add reflection on weaknesses
        if evaluation["weaknesses"]:
            reflections.append("Weaknesses in my reasoning:")
            for weakness in evaluation["weaknesses"]:
                reflections.append(f"- {weakness}")
        
        # Add reflection on issues
        if evaluation["issues"]:
            reflections.append("Issues in my reasoning:")
            for issue in evaluation["issues"]:
                reflections.append(f"- {issue}")
        
        # Add reflection on confidence
        reflections.append(f"My confidence in this reasoning is {confidence:.2f}.")
        
        # Add reflection on corrections
        if corrected_result["output"] != reasoning_result.get("output", ""):
            reflections.append("I've made corrections to my original reasoning.")
        
        # Add reflection on strategy
        if strategy_recommendation.get("explanation"):
            reflections.append(f"Strategy adjustment: {strategy_recommendation['explanation']}")
        
        # Add deeper reflections based on reflection depth
        if self.reflection_depth >= 2:
            reflections.append("Deeper reflection on my reasoning process:")
            
            # Add reflection on reasoning mechanism
            mechanism = reasoning_result.get("mechanism", "unknown")
            reflections.append(f"- I used {mechanism} reasoning, which has specific strengths and limitations.")
            
            # Add reflection on alternative approaches
            reflections.append("- Alternative reasoning approaches might have yielded different insights.")
        
        if self.reflection_depth >= 3:
            reflections.append("Meta-reflection on my thinking:")
            
            # Add reflection on cognitive biases
            reflections.append("- I should be aware of potential cognitive biases in my reasoning.")
            
            # Add reflection on knowledge limitations
            reflections.append("- My reasoning is limited by the information available to me.")
            
            # Add reflection on uncertainty
            reflections.append("- There is inherent uncertainty in this type of reasoning.")
        
        return reflections
    
    def _generate_low_confidence_output(
        self,
        corrected_result: Dict[str, Any],
        confidence: float,
    ) -> str:
        """
        Generate output for low confidence results.
        
        Args:
            corrected_result: Corrected reasoning result
            confidence: Confidence in the result
            
        Returns:
            Modified output acknowledging low confidence
        """
        output = corrected_result.get("output", "")
        
        # Add a disclaimer about low confidence
        disclaimer = "I'm not entirely confident in this answer, but based on my reasoning: "
        
        # Check if output already has a disclaimer
        if not output.startswith("I'm not") and not output.startswith("I am not"):
            output = disclaimer + output
        
        # Add a note about the confidence level
        if not "confidence" in output.lower():
            confidence_note = f" (Confidence: {confidence:.2f})"
            output += confidence_note
        
        return output
