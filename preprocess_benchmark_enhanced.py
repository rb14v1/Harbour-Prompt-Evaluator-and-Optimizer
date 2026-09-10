"""
Enhanced preprocessing for benchmark dataset with meaningful transformations.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import re
from datetime import datetime
from collections import Counter


class EnhancedBenchmarkPreprocessor:
    """Enhanced preprocessing with data transformations, enrichment, and analysis."""

    def __init__(self, input_path: str, output_dir: str):
        self.input_path = input_path
        self.output_dir = output_dir
        self.data = None
        self.stats = {
            'total_examples': 0,
            'processed_examples': 0,
            'errors': 0,
            'text_normalizations': 0,
            'enrichments': 0,
        }

    def load_raw_data(self) -> bool:
        """Load raw benchmark dataset."""
        try:
            with open(self.input_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.stats['total_examples'] = len(self.data.get('examples', []))
            print(f"[OK] Loaded {self.stats['total_examples']} examples")
            return True
        except Exception as e:
            print(f"[ERROR] Error loading data: {e}")
            return False

    def extract_keywords(self, text: str) -> List[str]:
        """Extract key technical terms from prompt."""
        keywords = []
        # Technical keywords pattern
        tech_patterns = [
            r'\b(python|javascript|typescript|java|go|rust|sql|api|rest|graphql|microservice)\b',
            r'\b(database|cache|redis|elasticsearch|mongodb|postgresql)\b',
            r'\b(machine learning|ai|nlp|deep learning|neural|tensorflow)\b',
            r'\b(authentication|authorization|security|encryption|jwt)\b',
            r'\b(docker|kubernetes|devops|ci/cd|deployment)\b',
            r'\b(react|vue|angular|frontend|backend|fullstack)\b',
        ]

        for pattern in tech_patterns:
            matches = re.findall(pattern, text.lower())
            keywords.extend(matches)

        return list(set(keywords))

    def calculate_prompt_complexity_score(self, prompt: str, task_type: str,
                                         issues: List[str], dimensions: List[str]) -> float:
        """Calculate detailed complexity score based on multiple factors."""
        score = 0.0

        # Base on length
        word_count = len(prompt.split())
        if word_count < 10:
            score += 1.0  # Very short
        elif word_count < 30:
            score += 2.5  # Short
        elif word_count < 100:
            score += 4.0  # Medium
        else:
            score += 5.0  # Long/detailed

        # Keywords presence
        keywords = self.extract_keywords(prompt)
        score += len(keywords) * 0.5

        # Issues count (negative factor)
        score -= len(issues) * 0.3

        # Low dimensions count (negative factor)
        score -= len(dimensions) * 0.2

        # Clamp to 0-10
        return max(0.0, min(10.0, score))

    def enrich_prompt_metadata(self, example: Dict) -> Dict:
        """Enrich prompt with detailed metadata."""
        prompt = example.get('prompt', '')

        # Text statistics
        words = prompt.split()
        sentences = re.split(r'[.!?]+', prompt)

        enrichment = {
            'text_stats': {
                'word_count': len(words),
                'sentence_count': len([s for s in sentences if s.strip()]),
                'char_count': len(prompt),
                'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
                'has_code': '```' in prompt or 'code' in prompt.lower(),
                'has_examples': 'example' in prompt.lower() or 'e.g.' in prompt.lower(),
                'has_numbers': bool(re.search(r'\d', prompt)),
                'has_special_chars': bool(re.search(r'[^a-zA-Z0-9\s]', prompt)),
            },
            'keywords': self.extract_keywords(prompt),
            'prompt_quality_indicators': {
                'has_clear_intent': len(words) > 5 and not prompt.endswith('?'),
                'has_specific_requirements': 'implement' in prompt.lower() or 'create' in prompt.lower(),
                'has_constraints': any(kw in prompt.lower() for kw in ['constraint', 'limit', 'max', 'min']),
                'has_examples': 'example' in prompt.lower(),
                'has_format_spec': any(kw in prompt.lower() for kw in ['format', 'json', 'xml', 'csv']),
                'is_actionable': any(verb in prompt.lower() for verb in ['write', 'create', 'build', 'analyze', 'design']),
            }
        }

        return enrichment

    def calculate_issue_severity(self, issues: List[str]) -> Dict[str, Any]:
        """Analyze and categorize issue severity."""
        severity_categories = {
            'clarity': [],
            'specificity': [],
            'context': [],
            'completeness': [],
            'actionability': [],
        }

        issue_keywords = {
            'clarity': ['vague', 'unclear', 'ambiguous', 'confusing'],
            'specificity': ['specific', 'details', 'undefined', 'not defined', 'missing'],
            'context': ['context', 'background', 'scope'],
            'completeness': ['missing', 'incomplete', 'all needed', 'required'],
            'actionability': ['actionable', 'implement', 'steps', 'path'],
        }

        for issue in issues:
            issue_lower = issue.lower()
            for category, keywords in issue_keywords.items():
                if any(kw in issue_lower for kw in keywords):
                    severity_categories[category].append(issue)
                    break

        return {
            'issue_count': len(issues),
            'categorized_issues': severity_categories,
            'primary_issue_type': max(severity_categories, key=lambda k: len(severity_categories[k])),
            'issue_density': len(issues) / 5,  # Normalized
        }

    def create_improvement_suggestions(self, example: Dict, enrichment: Dict) -> List[str]:
        """Generate specific improvement suggestions."""
        suggestions = []
        issues = example.get('issues', [])

        if len(issues) == 0:
            return ['No improvements needed - prompt is well-formulated']

        # Map issues to suggestions
        for issue in issues[:3]:  # Top 3 issues
            if 'specificity' in issue.lower():
                suggestions.append('Add concrete details, examples, and specific requirements')
            elif 'clarity' in issue.lower():
                suggestions.append('Rephrase to be more direct and unambiguous')
            elif 'context' in issue.lower():
                suggestions.append('Include business context, domain info, and problem background')
            elif 'completeness' in issue.lower():
                suggestions.append('Specify input/output formats, constraints, and success criteria')
            elif 'audience' in issue.lower():
                suggestions.append('Define target audience and expertise level')
            elif 'format' in issue.lower():
                suggestions.append('Specify desired output format (JSON, markdown, code, etc.)')
            else:
                suggestions.append(f'Address: {issue}')

        return suggestions

    def process_example(self, example: Dict) -> Dict:
        """Process and enrich a single example."""
        processed = example.copy()

        # Normalize text fields
        processed['prompt'] = re.sub(r'\s+', ' ', example['prompt']).strip()

        # Enrich with metadata
        enrichment = self.enrich_prompt_metadata(example)
        processed['enrichment'] = enrichment

        # Add issue severity analysis
        processed['issue_analysis'] = self.calculate_issue_severity(
            example.get('issues', [])
        )

        # Calculate prompt quality indicators
        processed['calculated_complexity_score'] = self.calculate_prompt_complexity_score(
            processed['prompt'],
            example.get('task_type', ''),
            example.get('issues', []),
            example.get('low_dimensions', [])
        )

        # Add improvement suggestions
        processed['improvement_suggestions'] = self.create_improvement_suggestions(
            example, enrichment
        )

        # Add processing flags
        processed['metadata'] = {
            'processed': True,
            'processing_date': datetime.now().isoformat(),
            'needs_significant_improvement': processed['calculated_complexity_score'] < 4.0,
            'needs_minor_improvement': 4.0 <= processed['calculated_complexity_score'] < 7.0,
            'quality_is_good': processed['calculated_complexity_score'] >= 7.0,
        }

        self.stats['enrichments'] += 1
        return processed

    def preprocess(self) -> bool:
        """Run full preprocessing pipeline."""
        if not self.load_raw_data():
            return False

        processed_examples = []

        print("\n[PROCESS] Preprocessing with enrichment...")
        for idx, example in enumerate(self.data.get('examples', []), 1):
            try:
                processed = self.process_example(example)
                processed_examples.append(processed)
                self.stats['processed_examples'] += 1
            except Exception as e:
                print(f"[WARNING] Error processing example {example.get('id', idx)}: {e}")
                self.stats['errors'] += 1

        # Create output structure
        output_data = {
            'metadata': {
                'name': self.data.get('metadata', {}).get('name', 'Benchmark Dataset'),
                'version': '2.0-enhanced',
                'created': self.data.get('metadata', {}).get('created', 'unknown'),
                'processed_date': datetime.now().isoformat(),
                'processing_type': 'enhanced_enrichment',
                'original_count': self.stats['total_examples'],
                'processed_count': self.stats['processed_examples'],
            },
            'examples': processed_examples
        }

        self.data = output_data

        print(f"[OK] Processed {self.stats['processed_examples']} examples with enrichment")
        if self.stats['errors'] > 0:
            print(f"[WARNING] {self.stats['errors']} examples had processing warnings")

        return True

    def save_processed_data(self, filename: str = 'benchmark_dataset_enhanced.json') -> bool:
        """Save processed dataset."""
        try:
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            output_file = os.path.join(self.output_dir, filename)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)

            print(f"[OK] Saved to: {output_file}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save: {e}")
            return False

    def print_sample_output(self) -> None:
        """Print sample of enriched data."""
        if not self.data or not self.data.get('examples'):
            return

        sample = self.data['examples'][0]
        print("\n" + "="*70)
        print("ENRICHED DATA SAMPLE")
        print("="*70)
        print(f"\nID: {sample['id']}")
        print(f"Prompt: {sample['prompt']}")
        print(f"Task Type: {sample['task_type']}")
        print(f"Complexity: {sample['complexity']}")
        print(f"Expected Score: {sample['expected_score']}")

        print(f"\n[NEW] Calculated Complexity Score: {sample.get('calculated_complexity_score', 'N/A'):.2f}")

        print(f"\n[NEW] Text Stats:")
        stats = sample.get('enrichment', {}).get('text_stats', {})
        print(f"  - Word Count: {stats.get('word_count', 'N/A')}")
        print(f"  - Sentence Count: {stats.get('sentence_count', 'N/A')}")
        print(f"  - Avg Word Length: {stats.get('avg_word_length', 'N/A'):.2f}")
        print(f"  - Has Examples: {stats.get('has_examples', False)}")
        print(f"  - Has Code: {stats.get('has_code', False)}")

        print(f"\n[NEW] Keywords Extracted: {', '.join(sample.get('enrichment', {}).get('keywords', []))}")

        print(f"\n[NEW] Quality Indicators:")
        indicators = sample.get('enrichment', {}).get('prompt_quality_indicators', {})
        for key, val in indicators.items():
            print(f"  - {key}: {val}")

        print(f"\n[NEW] Issue Analysis:")
        analysis = sample.get('issue_analysis', {})
        print(f"  - Total Issues: {analysis.get('issue_count', 'N/A')}")
        print(f"  - Primary Issue Type: {analysis.get('primary_issue_type', 'N/A')}")

        print(f"\n[NEW] Improvement Suggestions:")
        suggestions = sample.get('improvement_suggestions', [])
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")

        print(f"\n[NEW] Processing Metadata:")
        meta = sample.get('metadata', {})
        print(f"  - Needs Significant Improvement: {meta.get('needs_significant_improvement', 'N/A')}")
        print(f"  - Needs Minor Improvement: {meta.get('needs_minor_improvement', 'N/A')}")
        print(f"  - Quality is Good: {meta.get('quality_is_good', 'N/A')}")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, 'data', 'raw', 'benchmark_dataset.json')
    output_dir = os.path.join(base_dir, 'data', 'processed')

    if not os.path.exists(input_path):
        print(f"[ERROR] Input file not found: {input_path}")
        return False

    print("[START] Enhanced preprocessing with data enrichment...")
    print(f"Input: {input_path}")
    print(f"Output: {output_dir}")

    preprocessor = EnhancedBenchmarkPreprocessor(input_path, output_dir)

    if not preprocessor.preprocess():
        return False

    if not preprocessor.save_processed_data():
        return False

    preprocessor.print_sample_output()

    print("\n" + "="*70)
    print("[SUCCESS] Enhanced preprocessing completed!")
    print("="*70)
    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
