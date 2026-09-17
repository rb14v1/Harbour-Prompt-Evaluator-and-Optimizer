"""
Centralized Configuration for Prompt Evaluator
Change values in .env file and they will be used throughout the entire project
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ========== QUALITY THRESHOLD ==========
# Change this in .env file: THRESHOLD=9.5
# It will automatically update everywhere in the project
QUALITY_THRESHOLD = float(os.getenv('THRESHOLD', '9.5'))

# Description:
# - 7.0  = Easy (most prompts pass)
# - 8.0  = Medium (some need improvement)
# - 8.5  = Strict (many need improvement)
# - 9.5  = Very Strict (only excellent prompts pass) ← CURRENT
# - 10.0 = Impossible (all need improvement)

# ========== QUALITY SCORING LEVELS ==========
QUALITY_SCORES = {
    "Poor": 2.5,
    "Moderate": 5.0,
    "Good": 7.5,
    "Excellent": 10.0
}

# ========== EVALUATION SETTINGS ==========
# Change in .env file: MAX_ITERATIONS=3
MAX_ITERATIONS = int(os.getenv('MAX_ITERATIONS', '3'))
DEFAULT_API_TIMEOUT = 300000  # Milliseconds (300 seconds = 5 minutes)

# ========== QUALITY DIMENSIONS ==========
QUALITY_DIMENSIONS = [
    'clarity',
    'specificity',
    'context',
    'completeness',
    'requirements',
    'constraints',
    'expected_output',
    'actionability'
]

# ========== STATUS CHOICES ==========
EVALUATION_STATUS = {
    'READY': 'Ready',
    'NEEDS_IMPROVEMENT': 'Needs Manual Review',
    'IN_PROGRESS': 'In Progress'
}
