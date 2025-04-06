"""
Learning system for the cognitive architecture.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import time

# Initialize logger
logger = logging.getLogger(__name__)


class Learning:
    """
    Learning system for adaptation and improvement.
    
    This class provides mechanisms for learning from experience,
    adapting strategies, and improving performance over time.
    """
    
    def __init__(
        self,
        experience_based_learning: bool = True,
        strategy_adaptation: bool = True,
        performance_tracking: bool = True,
        max_experiences: int = 100,
    ):
        """
        Initialize the learning system.
        
        Args:
            experience_based_learning: Whether to enable experience-based learning
            strategy_adaptation: Whether to enable strategy adaptation
            performance_tracking: Whether to enable performance tracking
            max_experiences: Maximum number of experiences to store
        """
        self.experience_based_learning = experience_based_learning
        self.strategy_adaptation = strategy_adaptation
        self.performance_tracking = performance_tracking
        self.max_experiences = max_experiences
        
        # Initialize learning state
        self.experiences = []
        self.strategy_history = []
        self.performance_metrics = {
            "confidence_history": [],
            "reasoning_quality_history": [],
            "strategy_effectiveness": {},
        }
    
    async def update(
        self,
        metacognition_result: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update learning based on metacognition result.
        
        Args:
            metacognition_result: Result of metacognitive reflection
            context: Context information
            
        Returns:
            Learning update results
        """
        try:
            # Extract relevant information
            confidence = metacognition_result.get("confidence", 0.0)
            evaluation = metacognition_result.get("evaluation", {})
            strategy_recommendation = metacognition_result.get("strategy_recommendation", {})
            
            # Update experiences if enabled
            if self.experience_based_learning:
                await self._update_experiences(metacognition_result, context)
            
            # Update strategies if enabled
            if self.strategy_adaptation:
                await self._update_strategies(strategy_recommendation, context)
            
            # Update performance metrics if enabled
            if self.performance_tracking:
                await self._update_performance_metrics(confidence, evaluation, context)
            
            # Generate learning insights
            insights = await self._generate_insights(metacognition_result, context)
            
            # Generate learning recommendations
            recommendations = await self._generate_recommendations(metacognition_result, context)
            
            return {
                "insights": insights,
                "recommendations": recommendations,
                "updated_context": self._update_context(context, strategy_recommendation),
            }
        
        except Exception as e:
            logger.exception(f"Error in learning update: {e}")
            
            # Return a fallback result
            return {
                "insights": ["Error in learning update."],
                "recommendations": [],
                "updated_context": context,
            }
    
    async def _update_experiences(
        self,
        metacognition_result: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        """
        Update experiences based on metacognition result.
        
        Args:
            metacognition_result: Result of metacognitive reflection
            context: Context information
        """
        # Create a new experience
        experience = {
            "timestamp": time.time(),
            "input": context.get("input", ""),
            "reasoning_mechanism": context.get("reasoning_mechanism", "unknown"),
            "confidence": metacognition_result.get("confidence", 0.0),
            "quality": metacognition_result.get("evaluation", {}).get("quality", "unknown"),
            "issues": metacognition_result.get("evaluation", {}).get("issues", []),
        }
        
        # Add to experiences
        self.experiences.append(experience)
        
        # Enforce maximum experiences
        if len(self.experiences) > self.max_experiences:
            self.experiences = self.experiences[-self.max_experiences:]
    
    async def _update_strategies(
        self,
        strategy_recommendation: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        """
        Update strategies based on strategy recommendation.
        
        Args:
            strategy_recommendation: Strategy recommendation
            context: Context information
        """
        # Check if there's a strategy recommendation
        if not strategy_recommendation:
            return
        
        # Create a strategy update
        strategy_update = {
            "timestamp": time.time(),
            "previous_mechanism": context.get("reasoning_mechanism", "unknown"),
            "recommended_mechanism": strategy_recommendation.get("recommended_mechanism"),
            "reasoning_depth": strategy_recommendation.get("reasoning_depth"),
            "use_multiple_mechanisms": strategy_recommendation.get("use_multiple_mechanisms", False),
            "explanation": strategy_recommendation.get("explanation", ""),
        }
        
        # Add to strategy history
        self.strategy_history.append(strategy_update)
        
        # Enforce maximum history
        if len(self.strategy_history) > self.max_experiences:
            self.strategy_history = self.strategy_history[-self.max_experiences:]
    
    async def _update_performance_metrics(
        self,
        confidence: float,
        evaluation: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        """
        Update performance metrics.
        
        Args:
            confidence: Confidence in the reasoning
            evaluation: Evaluation of the reasoning
            context: Context information
        """
        # Update confidence history
        self.performance_metrics["confidence_history"].append(confidence)
        
        # Enforce maximum history
        if len(self.performance_metrics["confidence_history"]) > self.max_experiences:
            self.performance_metrics["confidence_history"] = self.performance_metrics["confidence_history"][-self.max_experiences:]
        
        # Update reasoning quality history
        quality = evaluation.get("quality", "unknown")
        quality_value = {"high": 1.0, "medium": 0.5, "low": 0.0, "unknown": 0.0}.get(quality, 0.0)
        self.performance_metrics["reasoning_quality_history"].append(quality_value)
        
        # Enforce maximum history
        if len(self.performance_metrics["reasoning_quality_history"]) > self.max_experiences:
            self.performance_metrics["reasoning_quality_history"] = self.performance_metrics["reasoning_quality_history"][-self.max_experiences:]
        
        # Update strategy effectiveness
        mechanism = context.get("reasoning_mechanism", "unknown")
        if mechanism not in self.performance_metrics["strategy_effectiveness"]:
            self.performance_metrics["strategy_effectiveness"][mechanism] = {
                "count": 0,
                "confidence_sum": 0.0,
                "quality_sum": 0.0,
            }
        
        self.performance_metrics["strategy_effectiveness"][mechanism]["count"] += 1
        self.performance_metrics["strategy_effectiveness"][mechanism]["confidence_sum"] += confidence
        self.performance_metrics["strategy_effectiveness"][mechanism]["quality_sum"] += quality_value
    
    async def _generate_insights(
        self,
        metacognition_result: Dict[str, Any],
        context: Dict[str, Any],
    ) -> List[str]:
        """
        Generate learning insights.
        
        Args:
            metacognition_result: Result of metacognitive reflection
            context: Context information
            
        Returns:
            List of learning insights
        """
        insights = []
        
        # Add insight about current performance
        confidence = metacognition_result.get("confidence", 0.0)
        quality = metacognition_result.get("evaluation", {}).get("quality", "unknown")
        
        insights.append(f"Current reasoning performance: {quality} quality with {confidence:.2f} confidence.")
        
        # Add insight about performance trend
        if len(self.performance_metrics["confidence_history"]) >= 5:
            recent_confidence = self.performance_metrics["confidence_history"][-5:]
            avg_confidence = sum(recent_confidence) / len(recent_confidence)
            
            if avg_confidence > 0.7:
                insights.append("Recent reasoning confidence has been consistently high.")
            elif avg_confidence < 0.4:
                insights.append("Recent reasoning confidence has been consistently low.")
            else:
                insights.append("Recent reasoning confidence has been moderate.")
        
        # Add insight about strategy effectiveness
        if self.performance_metrics["strategy_effectiveness"]:
            # Find most effective strategy
            most_effective = None
            highest_avg_confidence = 0.0
            
            for mechanism, metrics in self.performance_metrics["strategy_effectiveness"].items():
                if metrics["count"] >= 3:  # Minimum sample size
                    avg_confidence = metrics["confidence_sum"] / metrics["count"]
                    if avg_confidence > highest_avg_confidence:
                        highest_avg_confidence = avg_confidence
                        most_effective = mechanism
            
            if most_effective:
                insights.append(f"The most effective reasoning mechanism has been {most_effective} with average confidence of {highest_avg_confidence:.2f}.")
        
        # Add insight about learning progress
        if len(self.experiences) >= 10:
            early_confidence = sum(exp["confidence"] for exp in self.experiences[:5]) / 5
            recent_confidence = sum(exp["confidence"] for exp in self.experiences[-5:]) / 5
            
            if recent_confidence > early_confidence + 0.1:
                insights.append("Learning progress: Confidence has improved over time.")
            elif early_confidence > recent_confidence + 0.1:
                insights.append("Learning progress: Confidence has decreased over time.")
            else:
                insights.append("Learning progress: Confidence has remained stable over time.")
        
        return insights
    
    async def _generate_recommendations(
        self,
        metacognition_result: Dict[str, Any],
        context: Dict[str, Any],
    ) -> List[str]:
        """
        Generate learning recommendations.
        
        Args:
            metacognition_result: Result of metacognitive reflection
            context: Context information
            
        Returns:
            List of learning recommendations
        """
        recommendations = []
        
        # Get strategy recommendation
        strategy_recommendation = metacognition_result.get("strategy_recommendation", {})
        
        # Add recommendation about reasoning mechanism
        if strategy_recommendation.get("recommended_mechanism"):
            recommended_mechanism = strategy_recommendation["recommended_mechanism"]
            current_mechanism = context.get("reasoning_mechanism", "unknown")
            
            if recommended_mechanism != current_mechanism:
                recommendations.append(f"Try using {recommended_mechanism} reasoning for similar problems in the future.")
        
        # Add recommendation about multiple mechanisms
        if strategy_recommendation.get("use_multiple_mechanisms", False):
            recommendations.append("Consider using multiple reasoning mechanisms for complex problems.")
        
        # Add recommendation based on issues
        issues = metacognition_result.get("evaluation", {}).get("issues", [])
        
        if issues:
            if any("premises" in issue.lower() for issue in issues):
                recommendations.append("Focus on identifying clear premises in future reasoning.")
            
            if any("conclusion" in issue.lower() for issue in issues):
                recommendations.append("Work on drawing clear conclusions from premises.")
            
            if any("observations" in issue.lower() for issue in issues):
                recommendations.append("Pay more attention to identifying specific observations.")
            
            if any("pattern" in issue.lower() for issue in issues):
                recommendations.append("Practice recognizing patterns in observations.")
            
            if any("hypotheses" in issue.lower() for issue in issues):
                recommendations.append("Generate multiple hypotheses to explain observations.")
            
            if any("explanation" in issue.lower() for issue in issues):
                recommendations.append("Focus on selecting the most likely explanation based on evidence.")
            
            if any("domain" in issue.lower() for issue in issues):
                recommendations.append("Clearly identify source and target domains for analogies.")
            
            if any("mappings" in issue.lower() for issue in issues):
                recommendations.append("Establish clear mappings between domains in analogical reasoning.")
            
            if any("causal relationships" in issue.lower() for issue in issues):
                recommendations.append("Work on identifying clear cause-effect relationships.")
        
        # Add recommendation based on confidence
        confidence = metacognition_result.get("confidence", 0.0)
        
        if confidence < 0.5:
            recommendations.append("For low-confidence reasoning, consider gathering more information or using multiple approaches.")
        
        return recommendations
    
    def _update_context(
        self,
        context: Dict[str, Any],
        strategy_recommendation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update context based on strategy recommendation.
        
        Args:
            context: Context information
            strategy_recommendation: Strategy recommendation
            
        Returns:
            Updated context
        """
        # Create a copy of the context
        updated_context = context.copy()
        
        # Update reasoning mechanism if recommended
        if strategy_recommendation.get("recommended_mechanism"):
            updated_context["reasoning_mechanism"] = strategy_recommendation["recommended_mechanism"]
        
        # Update reasoning depth if recommended
        if strategy_recommendation.get("reasoning_depth") is not None:
            updated_context["reasoning_depth"] = strategy_recommendation["reasoning_depth"]
        
        # Update multiple mechanisms flag if recommended
        if "use_multiple_mechanisms" in strategy_recommendation:
            updated_context["use_multiple_mechanisms"] = strategy_recommendation["use_multiple_mechanisms"]
        
        return updated_context
