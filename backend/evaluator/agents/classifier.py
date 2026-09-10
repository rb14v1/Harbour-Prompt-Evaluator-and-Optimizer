import os
import json
import re
from typing import Dict, Any, Tuple, List
from pathlib import Path
from openai import AzureOpenAI


class ClassifierAgent:
    """
    Classifies prompts by task type and complexity using hybrid approach:
    1. Pattern-based classification with keywords
    2. Complexity calculation from text metrics
    3. LLM fallback for ambiguous cases
    """

    TASK_CATEGORIES = [
        "Create Content",
        "Create Code",
        "Research",
        "Deep Research / Analysis",
        "Plan and Organize",
        "Ideate",
        "Summarize",
        "Explain",
        "Optimize"
    ]

    COMPLEXITY_LEVELS = ["Simple", "Moderate", "Complex"]

    # Keywords for each task category
    CATEGORY_KEYWORDS = {
        "Create Content": [
            "write", "blog", "article", "post", "newsletter", "email", "social media",
            "press release", "whitepaper", "guide", "tutorial", "documentation",
            "product description", "copy", "content", "compose"
        ],
        "Create Code": [
            "code", "function", "api", "script", "program", "application", "build",
            "implement", "develop", "python", "javascript", "java", "sql", "react",
            "algorithm", "library", "module", "class", "method"
        ],
        "Research": [
            "research", "find", "look up", "investigate", "search", "discover",
            "gather information", "find data", "explore", "literature review"
        ],
        "Deep Research / Analysis": [
            "analyze", "analysis", "comprehensive", "detailed", "in-depth", "study",
            "examination", "investigation", "competitive analysis", "market analysis",
            "strategic analysis", "evaluate", "compare", "assessment"
        ],
        "Plan and Organize": [
            "plan", "organize", "schedule", "roadmap", "timeline", "project plan",
            "strategy", "structure", "outline", "create plan", "organize"
        ],
        "Ideate": [
            "brainstorm", "ideas", "ideate", "concept", "generate", "think of",
            "come up with", "creative", "innovation", "suggest", "proposal"
        ],
        "Summarize": [
            "summarize", "summary", "abstract", "condense", "brief", "overview",
            "executive summary", "recap", "digest", "highlight"
        ],
        "Explain": [
            "explain", "clarify", "describe", "define", "teach", "how to",
            "understand", "learning", "education", "tutorial", "guide"
        ],
        "Optimize": [
            "optimize", "improve", "performance", "efficiency", "better", "faster",
            "reduce", "increase", "enhance", "refactor", "speed up", "scale"
        ]
    }

    def __init__(self, use_llm: bool = True, use_dataset: bool = True):
        self.name = "Classifier Agent"
        self.use_llm = use_llm
        self.use_dataset = use_dataset
        self.dataset_examples = {}  # category -> list of examples
        self.dynamic_keywords = self.CATEGORY_KEYWORDS.copy()

        # Load classification dataset for improved accuracy
        if use_dataset:
            self._load_classification_dataset()
            self._extract_dynamic_keywords()

        if use_llm:
            try:
                self.client = AzureOpenAI(
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
                )
                self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
            except Exception:
                self.use_llm = False

    def _load_classification_dataset(self) -> None:
        """Load classification dataset from JSON file."""
        try:
            # Try multiple possible paths
            possible_paths = [
                Path(__file__).parent.parent.parent.parent / "data" / "raw" / "classification_dataset.json",
                Path(__file__).parent.parent.parent.parent / "classification_dataset.json",
                Path("data/raw/classification_dataset.json"),
                Path("classification_dataset.json"),
            ]

            dataset_path = None
            for path in possible_paths:
                if path.exists():
                    dataset_path = path
                    break

            if not dataset_path:
                print(f"[INFO] Classification dataset not found. Using hardcoded keywords.")
                return

            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract examples by category
            for category_info in data.get('task_categories', []):
                category = category_info['name']
                examples = category_info.get('examples', [])
                self.dataset_examples[category] = [ex['prompt'] for ex in examples]

            print(f"[INFO] Loaded classification dataset: {len(self.dataset_examples)} categories")

        except Exception as e:
            print(f"[WARNING] Failed to load dataset: {e}")

    def _extract_dynamic_keywords(self) -> None:
        """Extract keywords dynamically from dataset examples."""
        try:
            if not self.dataset_examples:
                return

            # Extract common terms from each category
            for category, prompts in self.dataset_examples.items():
                if category not in self.dynamic_keywords:
                    self.dynamic_keywords[category] = []

                # Extract words that appear frequently in this category
                word_freq = {}
                for prompt in prompts:
                    words = re.findall(r'\b[a-z]+\b', prompt.lower())
                    for word in words:
                        if len(word) > 3:  # Only consider words > 3 chars
                            word_freq[word] = word_freq.get(word, 0) + 1

                # Add frequent words to keywords (appearing in 2+ prompts)
                for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True):
                    if freq >= 2 and word not in self.dynamic_keywords[category]:
                        self.dynamic_keywords[category].append(word)

            print(f"[INFO] Extracted dynamic keywords from dataset")

        except Exception as e:
            print(f"[WARNING] Failed to extract dynamic keywords: {e}")

    def _calculate_similarity_score(self, prompt: str, category: str, examples: List[str]) -> float:
        """Calculate similarity between prompt and category examples."""
        if not examples:
            return 0.0

        prompt_words = set(re.findall(r'\b[a-z]+\b', prompt.lower()))
        if not prompt_words:
            return 0.0

        # Compare with each example
        similarities = []
        for example in examples:
            example_words = set(re.findall(r'\b[a-z]+\b', example.lower()))
            if not example_words:
                continue

            # Jaccard similarity
            intersection = len(prompt_words & example_words)
            union = len(prompt_words | example_words)
            similarity = intersection / union if union > 0 else 0.0
            similarities.append(similarity)

        # Return average similarity with examples
        return sum(similarities) / len(similarities) if similarities else 0.0

    def classify(self, processed_prompt: str) -> Dict[str, Any]:
        """
        Classify prompt into task category and assess complexity.

        Args:
            processed_prompt: Normalized prompt text

        Returns:
            Classification with task type, complexity, confidence, and reasoning
        """
        try:
            # Step 1: Pattern-based classification
            task_type, pattern_confidence, pattern_reasoning = self._classify_by_pattern(
                processed_prompt
            )

            # Step 2: Complexity assessment
            complexity, complexity_reasoning = self._assess_complexity(processed_prompt)

            # Step 3: If pattern confidence is low, use LLM for verification
            if pattern_confidence < 0.75 and self.use_llm:
                llm_result = self._classify_with_llm(processed_prompt)
                # Use LLM result if its confidence is higher
                if llm_result.get('confidence', 0) > pattern_confidence:
                    return {
                        "task_type": llm_result['task_type'],
                        "complexity": complexity,
                        "confidence": llm_result['confidence'],
                        "reasoning": f"LLM verified: {llm_result['reasoning']}. Complexity: {complexity_reasoning}",
                        "classification_method": "llm_verified"
                    }

            return {
                "task_type": task_type,
                "complexity": complexity,
                "confidence": pattern_confidence,
                "reasoning": f"{pattern_reasoning}. Complexity: {complexity_reasoning}",
                "classification_method": "pattern_based"
            }

        except Exception as e:
            return {
                "task_type": "Unknown",
                "complexity": "Moderate",
                "confidence": 0.0,
                "reasoning": f"Classification failed: {str(e)}",
                "classification_method": "error"
            }

    def _classify_by_pattern(self, prompt: str) -> Tuple[str, float, str]:
        """
        Classify using keyword pattern matching + dataset similarity.

        Returns:
            (task_type, confidence_score, reasoning)
        """
        prompt_lower = prompt.lower()
        scores = {}
        reasoning_parts = []

        # Method 1: Keyword matching (using dynamic keywords from dataset if available)
        keywords_to_use = self.dynamic_keywords if self.use_dataset else self.CATEGORY_KEYWORDS

        for category, keywords in keywords_to_use.items():
            keyword_matches = sum(1 for keyword in keywords if keyword in prompt_lower)
            scores[category] = {'keyword_score': keyword_matches}

        # Method 2: Similarity matching with dataset examples
        if self.use_dataset and self.dataset_examples:
            for category, examples in self.dataset_examples.items():
                similarity = self._calculate_similarity_score(prompt, category, examples)
                if category in scores:
                    scores[category]['similarity_score'] = similarity
                else:
                    scores[category] = {'similarity_score': similarity}

        # Combine scores (weighted average)
        combined_scores = {}
        for category, score_dict in scores.items():
            keyword_score = score_dict.get('keyword_score', 0) / max(1, len(keywords_to_use.get(category, [])))
            similarity_score = score_dict.get('similarity_score', 0)

            # Weight: 40% keywords, 60% similarity (if dataset available)
            if self.use_dataset and 'similarity_score' in score_dict:
                combined = (keyword_score * 0.4) + (similarity_score * 0.6)
            else:
                combined = keyword_score

            combined_scores[category] = combined

        # Get top 2 categories
        sorted_scores = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        top_category, top_score = sorted_scores[0]
        second_category, second_score = sorted_scores[1] if len(sorted_scores) > 1 else (None, 0)

        # Calculate confidence
        if top_score > 0:
            # Normalize confidence
            confidence = min(1.0, top_score)

            # Penalize if very close to second place
            if second_score > 0:
                ratio = (top_score - second_score) / max(top_score, 0.1)
                confidence *= min(1.0, (ratio + 1) / 2)  # Scale to 0.5-1.0

            # Add bonus for strong matches
            if top_score > 0.7:
                confidence = min(1.0, confidence * 1.1)
        else:
            confidence = 0.2
            top_category = "Research"

        # Build reasoning
        if self.use_dataset and self.dataset_examples:
            reasoning_parts.append(f"Matched '{top_category}' with dataset similarity")
        else:
            keyword_count = scores[top_category].get('keyword_score', 0)
            reasoning_parts.append(f"Matched '{top_category}' with {keyword_count} keyword indicators")

        if top_score == 0:
            reasoning = "No strong matches; defaulting to Research"
            top_category = "Research"
            confidence = 0.3
        else:
            reasoning = "; ".join(reasoning_parts)

        return top_category, confidence, reasoning

    def _assess_complexity(self, prompt: str) -> Tuple[str, str]:
        """
        Assess complexity based on text metrics.

        Returns:
            (complexity_level, reasoning)
        """
        word_count = len(prompt.split())
        sentence_count = len(re.split(r'[.!?]+', prompt))

        # Complexity indicators
        has_code_markers = '```' in prompt or 'code' in prompt.lower()
        has_constraints = any(kw in prompt.lower() for kw in
                             ['constraint', 'limit', 'max', 'min', 'requirement'])
        has_examples = 'example' in prompt.lower() or 'e.g.' in prompt.lower()
        has_format = any(kw in prompt.lower() for kw in
                        ['format', 'json', 'xml', 'csv', 'structure'])

        # Scoring system
        complexity_score = 0

        # Length factor (0-3 points)
        if word_count < 15:
            complexity_score += 0
        elif word_count < 50:
            complexity_score += 1
        elif word_count < 150:
            complexity_score += 2
        else:
            complexity_score += 3

        # Detail indicators (0-3 points)
        if has_constraints:
            complexity_score += 1
        if has_examples:
            complexity_score += 1
        if has_format:
            complexity_score += 1
        if has_code_markers:
            complexity_score += 0.5

        # Determine level
        if complexity_score < 2:
            complexity = "Simple"
        elif complexity_score < 4:
            complexity = "Moderate"
        else:
            complexity = "Complex"

        reasoning = (
            f"Word count: {word_count}, "
            f"Constraints: {has_constraints}, "
            f"Examples: {has_examples}, "
            f"Format spec: {has_format} → {complexity}"
        )

        return complexity, reasoning

    def _classify_with_llm(self, prompt: str) -> Dict[str, Any]:
        """
        Fallback LLM-based classification for ambiguous cases.

        Returns:
            Classification result from LLM
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": f"Classify this prompt:\n\n{prompt}"
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )

            response_text = response.choices[0].message.content
            result = self._parse_llm_response(response_text)
            return result

        except Exception as e:
            return {
                "task_type": "Unknown",
                "complexity": "Moderate",
                "confidence": 0.0,
                "reasoning": f"LLM classification failed: {str(e)}"
            }

    def _get_system_prompt(self) -> str:
        """Return system prompt for LLM classification."""
        categories = ", ".join(self.TASK_CATEGORIES)
        complexity = ", ".join(self.COMPLEXITY_LEVELS)

        return f"""You are an expert prompt classifier. Classify the given prompt into ONE of these categories:
{categories}

Also assess complexity level: {complexity}

Return valid JSON with these fields:
- task_type: one of the categories above
- complexity: one of the complexity levels
- confidence: number between 0.0 and 1.0 indicating how sure you are
- reasoning: brief explanation of your classification

Example output:
{{"task_type": "Create Code", "complexity": "Moderate", "confidence": 0.92, "reasoning": "Request to write a sorting function with specific requirements."}}

Be precise and concise in your reasoning."""

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        try:
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                result = json.loads(json_str)

                # Validate and normalize
                result['confidence'] = max(0.0, min(1.0, float(result.get('confidence', 0.5))))
                result['task_type'] = result.get('task_type', 'Research')
                result['complexity'] = result.get('complexity', 'Moderate')
                result['reasoning'] = result.get('reasoning', 'Classification completed')

                # Ensure valid category
                if result['task_type'] not in self.TASK_CATEGORIES:
                    result['task_type'] = 'Research'
                    result['confidence'] *= 0.8

                if result['complexity'] not in self.COMPLEXITY_LEVELS:
                    result['complexity'] = 'Moderate'

                return result
        except (json.JSONDecodeError, ValueError):
            pass

        return {
            "task_type": "Research",
            "complexity": "Moderate",
            "confidence": 0.3,
            "reasoning": "Could not parse LLM response"
        }

    def get_category_info(self, category: str) -> Dict[str, Any]:
        """Get information about a specific task category."""
        keywords = self.CATEGORY_KEYWORDS.get(category, [])
        return {
            "category": category,
            "keywords": keywords,
            "keyword_count": len(keywords)
        }
