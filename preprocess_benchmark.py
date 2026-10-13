"""
Preprocessing script for benchmark dataset.
Reads from data/raw/benchmark_dataset.json and outputs to data/processed/
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import re
from datetime import datetime


class BenchmarkPreprocessor:
    """Preprocesses benchmark dataset for quality and consistency."""

    def __init__(self, input_path: str, output_dir: str):
        self.input_path = input_path
        self.output_dir = output_dir
        self.data = None
        self.stats = {
            'total_examples': 0,
            'processed_examples': 0,
            'errors': 0,
            'warnings': [],
            'task_category_distribution': {},
            'complexity_distribution': {},
            'quality_distribution': {},
            'score_statistics': {'min': float('inf'), 'max': float('-inf'), 'avg': 0}
        }

    def load_raw_data(self) -> bool:
        """Load raw benchmark dataset."""
        try:
            with open(self.input_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.stats['total_examples'] = len(self.data.get('examples', []))
            print(f"[OK] Loaded {self.stats['total_examples']} examples from raw dataset")
            return True
        except Exception as e:
            print(f"[ERROR] Error loading data: {e}")
            return False

    def normalize_text(self, text: str) -> str:
        """Normalize text by removing extra whitespace and standardizing."""
        if not isinstance(text, str):
            return str(text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def validate_example(self, example: Dict) -> tuple[bool, str]:
        """Validate example has all required fields."""
        required_fields = ['id', 'prompt', 'task_type', 'complexity', 'expected_quality', 'expected_score']

        for field in required_fields:
            if field not in example:
                return False, f"Missing required field: {field}"

        # Validate field values
        if not isinstance(example['prompt'], str) or len(example['prompt'].strip()) == 0:
            return False, "Prompt is empty or invalid"

        valid_complexities = ['Simple', 'Moderate', 'Complex']
        if example['complexity'] not in valid_complexities:
            return False, f"Invalid complexity: {example['complexity']}"

        valid_qualities = ['Poor', 'Moderate', 'Good', 'Excellent']
        if example['expected_quality'] not in valid_qualities:
            return False, f"Invalid quality: {example['expected_quality']}"

        try:
            score = float(example['expected_score'])
            if not (0 <= score <= 10):
                return False, f"Score out of range [0-10]: {score}"
        except (ValueError, TypeError):
            return False, f"Invalid score format: {example['expected_score']}"

        return True, "Valid"

    def process_example(self, example: Dict) -> Dict:
        """Process and enrich a single example."""
        processed = {}

        # Copy and normalize fields
        processed['id'] = example['id'].strip()
        processed['prompt'] = self.normalize_text(example['prompt'])
        processed['task_type'] = example['task_type'].strip()
        processed['complexity'] = example['complexity'].strip()
        processed['expected_quality'] = example['expected_quality'].strip()
        processed['expected_score'] = float(example['expected_score'])

        # Add normalized fields
        processed['prompt_length'] = len(processed['prompt'].split())
        processed['prompt_char_count'] = len(processed['prompt'])

        # Copy optional fields
        if 'issues' in example and isinstance(example['issues'], list):
            processed['issues'] = [self.normalize_text(issue) for issue in example['issues']]
        else:
            processed['issues'] = []

        if 'low_dimensions' in example and isinstance(example['low_dimensions'], list):
            processed['low_dimensions'] = example['low_dimensions']
        else:
            processed['low_dimensions'] = []

        if 'strong_dimensions' in example and isinstance(example['strong_dimensions'], list):
            processed['strong_dimensions'] = example['strong_dimensions']
        else:
            processed['strong_dimensions'] = []

        # Calculate quality score mapping
        quality_mapping = {'Poor': 2.5, 'Moderate': 5.0, 'Good': 7.5, 'Excellent': 10.0}
        processed['quality_score_value'] = quality_mapping[processed['expected_quality']]

        # Add processing metadata
        processed['needs_optimization'] = processed['expected_score'] < 7.0
        processed['has_issues'] = len(processed['issues']) > 0

        return processed

    def update_statistics(self, example: Dict) -> None:
        """Update processing statistics."""
        # Task category distribution
        task_type = example['task_type']
        self.stats['task_category_distribution'][task_type] = \
            self.stats['task_category_distribution'].get(task_type, 0) + 1

        # Complexity distribution
        complexity = example['complexity']
        self.stats['complexity_distribution'][complexity] = \
            self.stats['complexity_distribution'].get(complexity, 0) + 1

        # Quality distribution
        quality = example['expected_quality']
        self.stats['quality_distribution'][quality] = \
            self.stats['quality_distribution'].get(quality, 0) + 1

        # Score statistics
        score = example['expected_score']
        self.stats['score_statistics']['min'] = min(self.stats['score_statistics']['min'], score)
        self.stats['score_statistics']['max'] = max(self.stats['score_statistics']['max'], score)

    def preprocess(self) -> bool:
        """Run full preprocessing pipeline."""
        if not self.load_raw_data():
            return False

        processed_examples = []

        print("\n[PROCESS] Preprocessing benchmark dataset...")
        for example in self.data.get('examples', []):
            # Validate
            is_valid, msg = self.validate_example(example)
            if not is_valid:
                self.stats['warnings'].append(f"ID {example.get('id', 'UNKNOWN')}: {msg}")
                self.stats['errors'] += 1
                continue

            # Process
            processed = self.process_example(example)
            processed_examples.append(processed)

            # Update stats
            self.update_statistics(processed)
            self.stats['processed_examples'] += 1

        # Calculate average score
        if processed_examples:
            avg_score = sum(ex['expected_score'] for ex in processed_examples) / len(processed_examples)
            self.stats['score_statistics']['avg'] = round(avg_score, 2)

        # Create output structure
        output_data = {
            'metadata': {
                'name': self.data.get('metadata', {}).get('name', 'Benchmark Dataset'),
                'version': self.data.get('metadata', {}).get('version', '1.0'),
                'created': self.data.get('metadata', {}).get('created', 'unknown'),
                'processed_date': datetime.now().isoformat(),
                'original_count': self.stats['total_examples'],
                'processed_count': self.stats['processed_examples'],
                'errors': self.stats['errors'],
                'validation_dimensions': 8,
                'task_categories': 9,
                'complexity_levels': 3,
                'quality_levels': 4
            },
            'statistics': self.stats,
            'examples': processed_examples
        }

        self.data = output_data

        print(f"[OK] Processed {self.stats['processed_examples']} examples")
        if self.stats['errors'] > 0:
            print(f"[WARNING] {self.stats['errors']} examples failed validation")

        return True

    def save_processed_data(self) -> bool:
        """Save processed dataset to output directory."""
        try:
            # Ensure output directory exists
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)

            output_file = os.path.join(self.output_dir, 'benchmark_dataset_processed.json')

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)

            print(f"[OK] Saved processed dataset to: {output_file}")
            return True
        except Exception as e:
            print(f"[ERROR] Error saving processed data: {e}")
            return False

    def print_summary(self) -> None:
        """Print preprocessing summary."""
        print("\n" + "="*60)
        print("PREPROCESSING SUMMARY")
        print("="*60)

        print(f"\nTotal Examples Processed: {self.stats['processed_examples']}")
        print(f"Validation Errors: {self.stats['errors']}")

        if self.stats['warnings']:
            print(f"\n[WARNING] Warnings ({len(self.stats['warnings'])}):")
            for warning in self.stats['warnings'][:5]:  # Show first 5
                print(f"  - {warning}")
            if len(self.stats['warnings']) > 5:
                print(f"  ... and {len(self.stats['warnings']) - 5} more")

        print("\n[STATS] Task Category Distribution:")
        for task_type, count in sorted(self.stats['task_category_distribution'].items()):
            pct = (count / self.stats['processed_examples']) * 100
            print(f"  {task_type}: {count} ({pct:.1f}%)")

        print("\n[STATS] Complexity Distribution:")
        for complexity, count in sorted(self.stats['complexity_distribution'].items()):
            pct = (count / self.stats['processed_examples']) * 100
            print(f"  {complexity}: {count} ({pct:.1f}%)")

        print("\n[STATS] Quality Distribution:")
        for quality, count in sorted(self.stats['quality_distribution'].items()):
            pct = (count / self.stats['processed_examples']) * 100
            print(f"  {quality}: {count} ({pct:.1f}%)")

        print("\n[STATS] Score Statistics:")
        stats = self.stats['score_statistics']
        print(f"  Min: {stats['min']:.2f}")
        print(f"  Max: {stats['max']:.2f}")
        print(f"  Average: {stats['avg']:.2f}")

        print("\n" + "="*60)


def main():
    """Main execution."""
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, 'data', 'raw', 'benchmark_dataset.json')
    output_dir = os.path.join(base_dir, 'data', 'processed')

    # Validate input file exists
    if not os.path.exists(input_path):
        print(f"[ERROR] Input file not found: {input_path}")
        return False

    print("[START] Beginning benchmark dataset preprocessing...")
    print(f"Input: {input_path}")
    print(f"Output: {output_dir}")

    # Create preprocessor
    preprocessor = BenchmarkPreprocessor(input_path, output_dir)

    # Run preprocessing
    if not preprocessor.preprocess():
        return False

    # Save results
    if not preprocessor.save_processed_data():
        return False

    # Print summary
    preprocessor.print_summary()

    print("\n[SUCCESS] Preprocessing completed successfully!")
    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
