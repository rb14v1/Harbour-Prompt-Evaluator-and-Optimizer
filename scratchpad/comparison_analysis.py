"""
Compare Claude-generated prompts with original project's approach.
Analyzes dimension coverage and quality metrics.
"""

import json
import re
from collections import defaultdict

# 8 dimensions from CLAUDE.md
DIMENSIONS = [
    "clarity",
    "specificity",
    "context",
    "completeness",
    "requirements",
    "constraints",
    "expected_output",
    "actionability"
]

def detect_dimension_presence(text):
    """Detect which dimensions are present in a prompt"""
    text_lower = text.lower()
    detected = {dim: False for dim in DIMENSIONS}

    # Clarity indicators
    if any(word in text_lower for word in ["clearly", "specific", "exact", "precise", "understand"]):
        detected["clarity"] = True

    # Specificity indicators
    if any(word in text_lower for word in ["exact", "specific", "detailed", "example", "particular", "include:", "focus:"]):
        detected["specificity"] = True

    # Context indicators
    if any(word in text_lower for word in ["context", "background", "current", "existing", "currently"]):
        detected["context"] = True

    # Completeness indicators
    if any(word in text_lower for word in ["all", "complete", "entire", "comprehensive", "full"]):
        detected["completeness"] = True

    # Requirements indicators
    if any(word in text_lower for word in ["require", "must", "should", "need", "requirement"]):
        detected["requirements"] = True

    # Constraints indicators
    if any(word in text_lower for word in ["constraint", "limit", "maximum", "minimum", "without"]):
        detected["constraints"] = True

    # Expected output indicators
    if any(word in text_lower for word in ["output", "format", "return", "provide", "deliverable", "result", "produce"]):
        detected["expected_output"] = True

    # Actionability indicators
    if any(word in text_lower for word in ["immediately", "ready", "deploy", "execute", "action", "step"]):
        detected["actionability"] = True

    return detected

def calculate_metrics(deficient, improved):
    """Calculate quality metrics for comparison"""
    def_dims = detect_dimension_presence(deficient)
    imp_dims = detect_dimension_presence(improved)

    def_coverage = sum(def_dims.values()) / len(DIMENSIONS)
    imp_coverage = sum(imp_dims.values()) / len(DIMENSIONS)

    length_ratio = len(improved) / max(len(deficient), 1)
    coverage_improvement = imp_coverage - def_coverage

    return {
        "deficient_dimensions_found": sum(def_dims.values()),
        "improved_dimensions_found": sum(imp_dims.values()),
        "coverage_improvement": coverage_improvement,
        "length_increase": length_ratio,
        "dimensions_detail": {
            "deficient": def_dims,
            "improved": imp_dims
        }
    }

def load_dataset():
    """Load the generated dataset"""
    with open("dataset_50_samples.json", "r") as f:
        return json.load(f)

def analyze_all():
    """Analyze all 50 samples"""
    dataset = load_dataset()

    all_metrics = []
    dimension_stats = defaultdict(lambda: {"added": 0, "total": 0})

    for sample in dataset:
        deficient = sample["original_deficient_prompt"]
        improved = sample["claude_improved_prompt"]

        metrics = calculate_metrics(deficient, improved)
        all_metrics.append(metrics)

        # Track dimension improvements
        for dim in DIMENSIONS:
            dimension_stats[dim]["total"] += 1
            if (not metrics["dimensions_detail"]["deficient"][dim] and
                metrics["dimensions_detail"]["improved"][dim]):
                dimension_stats[dim]["added"] += 1

    return all_metrics, dimension_stats

def generate_report():
    """Generate comparison report"""
    all_metrics, dimension_stats = analyze_all()

    report = {
        "analysis_date": "2026-09-28",
        "total_samples": 50,
        "summary": {
            "avg_dimensions_in_deficient": sum(m["deficient_dimensions_found"] for m in all_metrics) / len(all_metrics),
            "avg_dimensions_in_improved": sum(m["improved_dimensions_found"] for m in all_metrics) / len(all_metrics),
            "avg_coverage_improvement": sum(m["coverage_improvement"] for m in all_metrics) / len(all_metrics),
            "avg_length_increase": sum(m["length_increase"] for m in all_metrics) / len(all_metrics),
        },
        "dimension_improvements": {
            dim: {
                "added_in_samples": dimension_stats[dim]["added"],
                "percentage": (dimension_stats[dim]["added"] / dimension_stats[dim]["total"] * 100)
            }
            for dim in DIMENSIONS
        },
        "metrics_distribution": {
            "coverage_improvement_stats": {
                "min": min(m["coverage_improvement"] for m in all_metrics),
                "max": max(m["coverage_improvement"] for m in all_metrics),
                "avg": sum(m["coverage_improvement"] for m in all_metrics) / len(all_metrics),
            },
            "length_increase_stats": {
                "min": min(m["length_increase"] for m in all_metrics),
                "max": max(m["length_increase"] for m in all_metrics),
                "avg": sum(m["length_increase"] for m in all_metrics) / len(all_metrics),
            }
        }
    }

    return report

if __name__ == "__main__":
    report = generate_report()

    # Save report
    with open("comparison_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("=" * 60)
    print("COMPARISON ANALYSIS: Claude-Generated vs Original Project")
    print("=" * 60)
    print(f"\nTotal Samples Analyzed: {report['total_samples']}")
    print(f"\nDimension Coverage:")
    print(f"  Deficient prompts avg dimensions: {report['summary']['avg_dimensions_in_deficient']:.2f}/8")
    print(f"  Improved prompts avg dimensions:  {report['summary']['avg_dimensions_in_improved']:.2f}/8")
    print(f"  Average improvement: {report['summary']['avg_coverage_improvement']:.2f} dimensions")
    print(f"\nPrompt Expansion:")
    print(f"  Average length increase: {report['summary']['avg_length_increase']:.2f}x")

    print(f"\nDimensions Added by Claude (across all samples):")
    for dim, stat in report['dimension_improvements'].items():
        print(f"  {dim.upper():18} - Added to {stat['added_in_samples']}/50 samples ({stat['percentage']:.1f}%)")

    print(f"\n✓ Full report saved to: comparison_report.json")
