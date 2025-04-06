"""
Response formatter for the cognitive architecture.

This module provides functions to format responses from the cognitive architecture
to ensure they directly answer the questions asked.
"""

import re
from typing import Dict, Any, List, Optional


def format_response(
    cognitive_result: Dict[str, Any],
    input_text: str,
    context: Dict[str, Any]
) -> str:
    """
    Format the response from the cognitive architecture to ensure it directly answers the question.

    Args:
        cognitive_result: Result from the cognitive architecture
        input_text: Original input text
        context: Context information

    Returns:
        Formatted response that directly answers the question
    """
    # Extract the raw result
    raw_result = cognitive_result.get("result", "")
    
    # If the raw result is empty or just repeats the question, generate a better response
    if not raw_result or _is_question_repetition(raw_result, input_text):
        # Generate a response based on the reasoning and metacognition
        reasoning_result = cognitive_result.get("reasoning", {})
        metacognition_result = cognitive_result.get("metacognition", {})
        
        # Get the reasoning mechanism used
        mechanism = reasoning_result.get("mechanism", "unknown")
        
        # Get the reasoning steps
        steps = reasoning_result.get("steps", [])
        
        # Get the confidence level
        confidence = metacognition_result.get("confidence", 0.5)
        
        # Generate a response based on the reasoning mechanism
        if mechanism == "deductive":
            return _format_deductive_response(steps, input_text, confidence)
        elif mechanism == "inductive":
            return _format_inductive_response(steps, input_text, confidence)
        elif mechanism == "abductive":
            return _format_abductive_response(steps, input_text, confidence)
        elif mechanism == "analogical":
            return _format_analogical_response(steps, input_text, confidence)
        elif mechanism == "causal":
            return _format_causal_response(steps, input_text, confidence)
        else:
            # Default formatting
            return _format_default_response(steps, input_text, confidence)
    
    # If the raw result is good, return it
    return raw_result


def _is_question_repetition(response: str, question: str) -> bool:
    """
    Check if the response is just repeating the question.

    Args:
        response: Response to check
        question: Original question

    Returns:
        True if the response is just repeating the question
    """
    # Clean up the strings for comparison
    clean_response = re.sub(r'[^\w\s]', '', response.lower())
    clean_question = re.sub(r'[^\w\s]', '', question.lower())
    
    # Check if the response contains most of the question
    question_words = set(clean_question.split())
    response_words = set(clean_response.split())
    
    # If more than 70% of question words are in the response, it might be a repetition
    if len(question_words) > 0:
        overlap_ratio = len(question_words.intersection(response_words)) / len(question_words)
        if overlap_ratio > 0.7:
            return True
    
    return False


def _format_deductive_response(steps: List[str], question: str, confidence: float) -> str:
    """
    Format a response for deductive reasoning.

    Args:
        steps: Reasoning steps
        question: Original question
        confidence: Confidence level

    Returns:
        Formatted response
    """
    # Extract premises and conclusion
    premises = []
    conclusion = None
    
    for step in steps:
        if step.startswith("Premise"):
            premises.append(step)
        elif step.startswith("Therefore") or step.startswith("Conclusion"):
            conclusion = step
    
    # If we have a conclusion, use it as the main response
    if conclusion:
        # Extract the actual conclusion text
        if conclusion.startswith("Therefore, "):
            conclusion = conclusion[len("Therefore, "):]
        elif conclusion.startswith("Conclusion: "):
            conclusion = conclusion[len("Conclusion: "):]
        
        # Format the response
        response = conclusion
        
        # Add reasoning if confidence is not high
        if confidence < 0.8 and premises:
            response += f"\n\nThis conclusion is based on the following premises:\n"
            for premise in premises:
                response += f"- {premise}\n"
        
        return response
    
    # If no conclusion, try to extract an answer from the last step
    if steps:
        return steps[-1]
    
    # Fallback response
    return "Based on deductive reasoning, I cannot reach a definitive conclusion with the given information."


def _format_inductive_response(steps: List[str], question: str, confidence: float) -> str:
    """
    Format a response for inductive reasoning.

    Args:
        steps: Reasoning steps
        question: Original question
        confidence: Confidence level

    Returns:
        Formatted response
    """
    # Look for pattern or generalization
    pattern = None
    observations = []
    
    for step in steps:
        if step.startswith("Observation"):
            observations.append(step)
        elif "pattern emerges" in step or "generalization" in step:
            pattern = step
    
    # If we have a pattern, use it as the main response
    if pattern:
        # Extract the actual pattern text
        if "pattern emerges: " in pattern:
            pattern = pattern.split("pattern emerges: ")[1]
        elif "generalization: " in pattern:
            pattern = pattern.split("generalization: ")[1]
        
        # Format the response
        response = pattern
        
        # Add observations if confidence is not high
        if confidence < 0.8 and observations:
            response += f"\n\nThis generalization is based on the following observations:\n"
            for observation in observations:
                response += f"- {observation}\n"
        
        return response
    
    # If no pattern, try to extract an answer from the last step
    if steps:
        return steps[-1]
    
    # Fallback response
    return "Based on inductive reasoning, I cannot identify a clear pattern from the given information."


def _format_abductive_response(steps: List[str], question: str, confidence: float) -> str:
    """
    Format a response for abductive reasoning.

    Args:
        steps: Reasoning steps
        question: Original question
        confidence: Confidence level

    Returns:
        Formatted response
    """
    # Look for best explanation or hypothesis
    best_explanation = None
    observations = []
    hypotheses = []
    
    for step in steps:
        if step.startswith("Observation"):
            observations.append(step)
        elif step.startswith("Hypothesis"):
            hypotheses.append(step)
        elif "most likely explanation" in step or "best hypothesis" in step:
            best_explanation = step
    
    # If we have a best explanation, use it as the main response
    if best_explanation:
        # Extract the actual explanation text
        if "most likely explanation is: " in best_explanation:
            best_explanation = best_explanation.split("most likely explanation is: ")[1]
        elif "best hypothesis is: " in best_explanation:
            best_explanation = best_explanation.split("best hypothesis is: ")[1]
        
        # Format the response
        response = best_explanation
        
        # Add supporting information if confidence is not high
        if confidence < 0.8:
            if observations:
                response += f"\n\nThis explanation is based on the following observations:\n"
                for observation in observations[:3]:  # Limit to top 3
                    response += f"- {observation}\n"
            
            if hypotheses and len(hypotheses) > 1:
                response += f"\n\nI considered multiple explanations, including:\n"
                for hypothesis in hypotheses[:3]:  # Limit to top 3
                    response += f"- {hypothesis}\n"
        
        return response
    
    # If no best explanation, try to extract an answer from the last step
    if steps:
        return steps[-1]
    
    # Fallback response
    return "Based on abductive reasoning, I cannot determine the most likely explanation with the given information."


def _format_analogical_response(steps: List[str], question: str, confidence: float) -> str:
    """
    Format a response for analogical reasoning.

    Args:
        steps: Reasoning steps
        question: Original question
        confidence: Confidence level

    Returns:
        Formatted response
    """
    # Look for analogies and mappings
    source_domain = None
    target_domain = None
    mappings = []
    conclusion = None
    
    for step in steps:
        if "source domain" in step:
            source_domain = step
        elif "target domain" in step:
            target_domain = step
        elif "mapping" in step or "similarity" in step:
            mappings.append(step)
        elif "conclusion" in step.lower() or "therefore" in step.lower():
            conclusion = step
    
    # If we have a conclusion, use it as the main response
    if conclusion:
        # Extract the actual conclusion text
        if "conclusion: " in conclusion.lower():
            conclusion = conclusion.split("conclusion: ", 1)[1]
        elif "therefore, " in conclusion.lower():
            conclusion = conclusion.split("therefore, ", 1)[1]
        
        # Format the response
        response = conclusion
        
        # Add supporting information if confidence is not high
        if confidence < 0.8:
            if source_domain and target_domain:
                response += f"\n\nThis analogy compares {source_domain.replace('Source domain: ', '')} to {target_domain.replace('Target domain: ', '')}."
            
            if mappings:
                response += f"\n\nKey similarities include:\n"
                for mapping in mappings[:3]:  # Limit to top 3
                    response += f"- {mapping}\n"
        
        return response
    
    # If no conclusion, try to extract an answer from the last step
    if steps:
        return steps[-1]
    
    # Fallback response
    return "Based on analogical reasoning, I cannot establish a meaningful analogy with the given information."


def _format_causal_response(steps: List[str], question: str, confidence: float) -> str:
    """
    Format a response for causal reasoning.

    Args:
        steps: Reasoning steps
        question: Original question
        confidence: Confidence level

    Returns:
        Formatted response
    """
    # Look for causes, effects, and causal relationships
    causes = []
    effects = []
    causal_relationship = None
    conclusion = None
    
    for step in steps:
        if "cause:" in step.lower():
            causes.append(step)
        elif "effect:" in step.lower():
            effects.append(step)
        elif "causal relationship" in step.lower():
            causal_relationship = step
        elif "conclusion" in step.lower() or "therefore" in step.lower():
            conclusion = step
    
    # If we have a conclusion, use it as the main response
    if conclusion:
        # Extract the actual conclusion text
        if "conclusion: " in conclusion.lower():
            conclusion = conclusion.split("conclusion: ", 1)[1]
        elif "therefore, " in conclusion.lower():
            conclusion = conclusion.split("therefore, ", 1)[1]
        
        # Format the response
        response = conclusion
        
        # Add supporting information if confidence is not high
        if confidence < 0.8:
            if causal_relationship:
                response += f"\n\n{causal_relationship}"
            
            if causes:
                response += f"\n\nCauses:\n"
                for cause in causes[:3]:  # Limit to top 3
                    response += f"- {cause}\n"
            
            if effects:
                response += f"\n\nEffects:\n"
                for effect in effects[:3]:  # Limit to top 3
                    response += f"- {effect}\n"
        
        return response
    
    # If no conclusion, try to extract an answer from the last step
    if steps:
        return steps[-1]
    
    # Fallback response
    return "Based on causal reasoning, I cannot establish a clear cause-effect relationship with the given information."


def _format_default_response(steps: List[str], question: str, confidence: float) -> str:
    """
    Format a default response when no specific reasoning mechanism is identified.

    Args:
        steps: Reasoning steps
        question: Original question
        confidence: Confidence level

    Returns:
        Formatted response
    """
    # Try to extract a conclusion or final step
    conclusion = None
    
    for step in steps:
        if "conclusion" in step.lower() or "therefore" in step.lower():
            conclusion = step
    
    # If we have a conclusion, use it as the main response
    if conclusion:
        # Extract the actual conclusion text
        if "conclusion: " in conclusion.lower():
            conclusion = conclusion.split("conclusion: ", 1)[1]
        elif "therefore, " in conclusion.lower():
            conclusion = conclusion.split("therefore, ", 1)[1]
        
        return conclusion
    
    # If no conclusion, try to extract an answer from the last step
    if steps:
        return steps[-1]
    
    # Fallback response
    return "I've analyzed the information but cannot provide a definitive answer with the given information."
