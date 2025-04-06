"""
Perception layer for the cognitive architecture.
"""

from typing import Dict, List, Any, Optional, Union
import re
import logging

# Initialize logger
logger = logging.getLogger(__name__)


class Perception:
    """
    Perception layer for processing inputs.
    
    This class is responsible for processing input text, extracting features,
    recognizing context, and focusing attention on relevant information.
    """
    
    def __init__(
        self,
        feature_extraction: bool = True,
        context_recognition: bool = True,
        attention_mechanism: bool = True,
        max_features: int = 10,
    ):
        """
        Initialize the perception layer.
        
        Args:
            feature_extraction: Whether to extract features from input
            context_recognition: Whether to recognize context
            attention_mechanism: Whether to use attention mechanisms
            max_features: Maximum number of features to extract
        """
        self.feature_extraction = feature_extraction
        self.context_recognition = context_recognition
        self.attention_mechanism = attention_mechanism
        self.max_features = max_features
    
    async def process(
        self,
        input_text: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Process input text.
        
        Args:
            input_text: Input text to process
            context: Context information
            
        Returns:
            Processing results including extracted features and insights
        """
        result = {
            "original_input": input_text,
            "processed_input": input_text,
        }
        
        # Extract features if enabled
        if self.feature_extraction:
            features = await self._extract_features(input_text)
            result["features"] = features
        
        # Recognize context if enabled
        if self.context_recognition:
            context_info = await self._recognize_context(input_text, context)
            result["context_info"] = context_info
        
        # Apply attention mechanisms if enabled
        if self.attention_mechanism:
            attention_focus = await self._focus_attention(input_text, context)
            result["attention_focus"] = attention_focus
        
        # Generate insights from the processed input
        insights = await self._generate_insights(result)
        result["insights"] = insights
        
        return result
    
    async def _extract_features(self, input_text: str) -> Dict[str, Any]:
        """
        Extract features from input text.
        
        Args:
            input_text: Input text to process
            
        Returns:
            Extracted features
        """
        features = {}
        
        # Extract entities (simple approach)
        entities = self._extract_entities(input_text)
        features["entities"] = entities[:self.max_features]
        
        # Extract keywords
        keywords = self._extract_keywords(input_text)
        features["keywords"] = keywords[:self.max_features]
        
        # Detect question type
        question_type = self._detect_question_type(input_text)
        features["question_type"] = question_type
        
        # Detect sentiment (simple approach)
        sentiment = self._detect_sentiment(input_text)
        features["sentiment"] = sentiment
        
        # Detect complexity
        complexity = self._detect_complexity(input_text)
        features["complexity"] = complexity
        
        return features
    
    async def _recognize_context(
        self,
        input_text: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Recognize context from input text and context information.
        
        Args:
            input_text: Input text to process
            context: Context information
            
        Returns:
            Recognized context information
        """
        context_info = {}
        
        # Check for conversation history
        if "conversation_history" in context:
            context_info["has_history"] = True
            context_info["history_length"] = len(context["conversation_history"])
        else:
            context_info["has_history"] = False
        
        # Check for references to previous messages
        context_info["references_history"] = self._has_history_references(input_text)
        
        # Check for domain-specific context
        context_info["domain"] = self._detect_domain(input_text)
        
        # Check for task-specific context
        context_info["task_type"] = self._detect_task_type(input_text, context)
        
        return context_info
    
    async def _focus_attention(
        self,
        input_text: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Focus attention on relevant parts of the input.
        
        Args:
            input_text: Input text to process
            context: Context information
            
        Returns:
            Attention focus information
        """
        attention_focus = {}
        
        # Identify main topic
        main_topic = self._identify_main_topic(input_text)
        attention_focus["main_topic"] = main_topic
        
        # Identify key parts of the input
        key_parts = self._identify_key_parts(input_text)
        attention_focus["key_parts"] = key_parts
        
        # Identify parts to ignore
        parts_to_ignore = self._identify_parts_to_ignore(input_text, context)
        attention_focus["parts_to_ignore"] = parts_to_ignore
        
        return attention_focus
    
    async def _generate_insights(self, processed_data: Dict[str, Any]) -> List[str]:
        """
        Generate insights from processed data.
        
        Args:
            processed_data: Processed input data
            
        Returns:
            List of insights
        """
        insights = []
        
        # Add insights based on features
        if "features" in processed_data:
            features = processed_data["features"]
            
            # Add insight about question type
            if "question_type" in features and features["question_type"]:
                insights.append(f"This appears to be a {features['question_type']} question.")
            
            # Add insight about complexity
            if "complexity" in features:
                if features["complexity"] > 0.7:
                    insights.append("This is a complex query that may require detailed analysis.")
                elif features["complexity"] < 0.3:
                    insights.append("This is a straightforward query with clear parameters.")
            
            # Add insight about entities
            if "entities" in features and features["entities"]:
                insights.append(f"Key entities identified: {', '.join(features['entities'][:3])}.")
        
        # Add insights based on context
        if "context_info" in processed_data:
            context_info = processed_data["context_info"]
            
            # Add insight about domain
            if "domain" in context_info and context_info["domain"]:
                insights.append(f"This query relates to the domain of {context_info['domain']}.")
            
            # Add insight about history references
            if "references_history" in context_info and context_info["references_history"]:
                insights.append("This query references previous conversation context.")
        
        # Add insights based on attention focus
        if "attention_focus" in processed_data:
            attention_focus = processed_data["attention_focus"]
            
            # Add insight about main topic
            if "main_topic" in attention_focus and attention_focus["main_topic"]:
                insights.append(f"The main focus is on {attention_focus['main_topic']}.")
        
        return insights
    
    def _extract_entities(self, text: str) -> List[str]:
        """
        Extract entities from text (simple approach).
        
        Args:
            text: Text to process
            
        Returns:
            List of extracted entities
        """
        # Simple approach: look for capitalized words that aren't at the start of sentences
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        
        # Remove duplicates while preserving order
        seen = set()
        entities = [word for word in words if not (word in seen or seen.add(word))]
        
        return entities
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Text to process
            
        Returns:
            List of extracted keywords
        """
        # Simple approach: remove stop words and get remaining words
        stop_words = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "about", "as"}
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # Remove stop words and count occurrences
        word_counts = {}
        for word in words:
            if word not in stop_words:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Sort by count (descending)
        keywords = sorted(word_counts.keys(), key=lambda k: word_counts[k], reverse=True)
        
        return keywords
    
    def _detect_question_type(self, text: str) -> str:
        """
        Detect the type of question.
        
        Args:
            text: Text to process
            
        Returns:
            Question type
        """
        text_lower = text.lower()
        
        # Check for question marks
        if "?" not in text:
            return "statement"
        
        # Check for different question types
        if re.search(r'\b(what|who|where|which)\b', text_lower):
            return "factual"
        elif re.search(r'\b(why|how)\b', text_lower):
            return "explanatory"
        elif re.search(r'\b(can|could|would|will|should|do|does|is|are|am)\b', text_lower):
            return "yes/no"
        elif re.search(r'\b(compare|difference|similarities|versus|vs)\b', text_lower):
            return "comparative"
        elif re.search(r'\b(best|worst|most|least|top|ranking)\b', text_lower):
            return "evaluative"
        else:
            return "other"
    
    def _detect_sentiment(self, text: str) -> Dict[str, float]:
        """
        Detect sentiment in text (simple approach).
        
        Args:
            text: Text to process
            
        Returns:
            Sentiment scores
        """
        text_lower = text.lower()
        
        # Simple word lists for sentiment analysis
        positive_words = {"good", "great", "excellent", "amazing", "wonderful", "fantastic", "best", "better", "positive", "happy", "glad", "love", "like", "enjoy", "pleased"}
        negative_words = {"bad", "terrible", "awful", "horrible", "worst", "worse", "negative", "sad", "unhappy", "hate", "dislike", "disappointed", "poor", "problem", "issue"}
        
        # Count occurrences
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        total_count = positive_count + negative_count
        
        # Calculate scores
        if total_count == 0:
            return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}
        
        positive_score = positive_count / total_count if total_count > 0 else 0.0
        negative_score = negative_count / total_count if total_count > 0 else 0.0
        neutral_score = 1.0 - (positive_score + negative_score)
        
        return {
            "positive": positive_score,
            "negative": negative_score,
            "neutral": neutral_score,
        }
    
    def _detect_complexity(self, text: str) -> float:
        """
        Detect complexity of text.
        
        Args:
            text: Text to process
            
        Returns:
            Complexity score (0.0 to 1.0)
        """
        # Factors that contribute to complexity
        factors = []
        
        # Length factor
        length = len(text)
        length_factor = min(length / 500, 1.0)  # Normalize to 0-1
        factors.append(length_factor)
        
        # Sentence length factor
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len(sentences), 1)
        sentence_factor = min(avg_sentence_length / 25, 1.0)  # Normalize to 0-1
        factors.append(sentence_factor)
        
        # Word length factor
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
        word_factor = min((avg_word_length - 3) / 5, 1.0)  # Normalize to 0-1
        factors.append(max(0, word_factor))
        
        # Question complexity factor
        question_type = self._detect_question_type(text)
        question_factors = {
            "factual": 0.3,
            "yes/no": 0.2,
            "explanatory": 0.7,
            "comparative": 0.8,
            "evaluative": 0.9,
            "other": 0.5,
            "statement": 0.5,
        }
        factors.append(question_factors.get(question_type, 0.5))
        
        # Calculate overall complexity
        complexity = sum(factors) / len(factors)
        
        return complexity
    
    def _has_history_references(self, text: str) -> bool:
        """
        Check if text references conversation history.
        
        Args:
            text: Text to process
            
        Returns:
            True if text references history, False otherwise
        """
        text_lower = text.lower()
        
        # Check for references to previous messages
        reference_patterns = [
            r'\b(you|your|we) (said|mentioned|talked about|discussed|referred to)\b',
            r'\b(earlier|before|previously|last time)\b',
            r'\b(as|like) (you|we) (said|mentioned|discussed)\b',
            r'\b(continuing|following up|regarding|about) (our|the) (conversation|discussion|chat)\b',
            r'\b(the|that|those|these) (point|example|topic|issue|question)\b',
        ]
        
        for pattern in reference_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _detect_domain(self, text: str) -> str:
        """
        Detect the domain of the text.
        
        Args:
            text: Text to process
            
        Returns:
            Detected domain
        """
        text_lower = text.lower()
        
        # Define domain keywords
        domains = {
            "technology": ["computer", "software", "hardware", "programming", "code", "algorithm", "data", "internet", "web", "app", "application", "device", "technology", "tech", "digital"],
            "science": ["science", "scientific", "physics", "chemistry", "biology", "astronomy", "geology", "experiment", "hypothesis", "theory", "research"],
            "mathematics": ["math", "mathematics", "equation", "calculation", "algebra", "geometry", "calculus", "statistics", "probability", "number", "formula"],
            "business": ["business", "company", "corporation", "startup", "entrepreneur", "market", "finance", "investment", "stock", "profit", "revenue", "customer", "client"],
            "health": ["health", "medical", "medicine", "doctor", "hospital", "patient", "disease", "symptom", "treatment", "therapy", "diagnosis", "cure", "healthcare"],
            "education": ["education", "school", "university", "college", "student", "teacher", "professor", "course", "class", "lecture", "learn", "study", "academic"],
            "arts": ["art", "music", "painting", "drawing", "sculpture", "literature", "poetry", "novel", "film", "movie", "theater", "dance", "creative", "artistic"],
            "history": ["history", "historical", "ancient", "medieval", "century", "era", "period", "civilization", "empire", "kingdom", "war", "revolution"],
            "philosophy": ["philosophy", "philosophical", "ethics", "moral", "logic", "reasoning", "existence", "consciousness", "metaphysics", "epistemology"],
            "politics": ["politics", "political", "government", "policy", "law", "regulation", "election", "vote", "democracy", "republican", "democrat", "liberal", "conservative"],
        }
        
        # Count domain keywords
        domain_counts = {domain: 0 for domain in domains}
        for domain, keywords in domains.items():
            for keyword in keywords:
                if re.search(r'\b' + keyword + r'\b', text_lower):
                    domain_counts[domain] += 1
        
        # Find domain with highest count
        max_count = max(domain_counts.values())
        if max_count == 0:
            return "general"
        
        # Get all domains with the highest count
        top_domains = [domain for domain, count in domain_counts.items() if count == max_count]
        
        return top_domains[0] if len(top_domains) == 1 else "mixed"
    
    def _detect_task_type(self, text: str, context: Dict[str, Any]) -> str:
        """
        Detect the type of task.
        
        Args:
            text: Text to process
            context: Context information
            
        Returns:
            Task type
        """
        text_lower = text.lower()
        
        # Check for different task types
        if re.search(r'\b(explain|describe|elaborate|tell me about|what is|who is|where is)\b', text_lower):
            return "information"
        elif re.search(r'\b(how to|steps|procedure|process|method|guide|tutorial)\b', text_lower):
            return "instruction"
        elif re.search(r'\b(solve|calculate|compute|find|determine|evaluate)\b', text_lower):
            return "problem-solving"
        elif re.search(r'\b(compare|contrast|difference|similarity|versus|vs)\b', text_lower):
            return "comparison"
        elif re.search(r'\b(summarize|summary|brief|overview|recap)\b', text_lower):
            return "summarization"
        elif re.search(r'\b(analyze|analysis|examine|investigate|study|research)\b', text_lower):
            return "analysis"
        elif re.search(r'\b(create|generate|write|compose|draft|design)\b', text_lower):
            return "creation"
        elif re.search(r'\b(translate|conversion|convert|change)\b', text_lower):
            return "translation"
        elif re.search(r'\b(opinion|think|believe|view|perspective|stance)\b', text_lower):
            return "opinion"
        else:
            return "general"
    
    def _identify_main_topic(self, text: str) -> str:
        """
        Identify the main topic of the text.
        
        Args:
            text: Text to process
            
        Returns:
            Main topic
        """
        # Extract entities and keywords
        entities = self._extract_entities(text)
        keywords = self._extract_keywords(text)
        
        # Combine entities and keywords
        candidates = entities + [k for k in keywords if k not in [e.lower() for e in entities]]
        
        # Return the first candidate or empty string if none
        return candidates[0] if candidates else ""
    
    def _identify_key_parts(self, text: str) -> List[str]:
        """
        Identify key parts of the text.
        
        Args:
            text: Text to process
            
        Returns:
            List of key parts
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Identify key sentences (simple approach)
        key_parts = []
        
        # First sentence is often important
        if sentences and len(sentences) > 0:
            key_parts.append(sentences[0])
        
        # Last sentence is often important
        if sentences and len(sentences) > 1:
            key_parts.append(sentences[-1])
        
        # Sentences with question marks are important
        for sentence in sentences:
            if "?" in sentence and sentence not in key_parts:
                key_parts.append(sentence)
                break
        
        return key_parts
    
    def _identify_parts_to_ignore(self, text: str, context: Dict[str, Any]) -> List[str]:
        """
        Identify parts of the text to ignore.
        
        Args:
            text: Text to process
            context: Context information
            
        Returns:
            List of parts to ignore
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Identify sentences to ignore (simple approach)
        parts_to_ignore = []
        
        # Ignore pleasantries
        pleasantries = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "thanks", "thank you"]
        for sentence in sentences:
            if sentence.lower() in pleasantries or all(word in sentence.lower() for word in ["how", "are", "you"]):
                parts_to_ignore.append(sentence)
        
        return parts_to_ignore
