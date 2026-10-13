"""
Integrated Flask Backend - Claude vs Project Comparison
Integrates with your project's Validator, Improver, and Scoring Engine
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import sys
from datetime import datetime
from anthropic import Anthropic
import openpyxl
import dotenv
from openpyxl.styles import Font, PatternFill, Alignment
from io import BytesIO

# Add your project to path
PROJECT_PATH = r"c:\Users\admin\Downloads\project\prompt-evaluator-and-optimizer\backend"
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)
dotenv.load_dotenv(r"c:\Users\admin\Downloads\project\prompt-evaluator-and-optimizer\backend\.env")

# Import your project agents
try:
    from evaluator.agents.validator import ValidatorAgent
    from evaluator.agents.improver import ImproverAgent
    from evaluator.agents.analyzer import AnalyzerAgent
    from evaluator.agents.preprocessor import PreprocessorAgent
    from evaluator.agents.scoring_engine import ScoringEngine
    PROJECT_AVAILABLE = True
    print("✓ Project agents loaded successfully")
except Exception as e:
    PROJECT_AVAILABLE = False
    print(f"⚠ Project agents not available: {str(e)}")

app = Flask(__name__)

# Initialize Anthropic client
api_key = os.environ.get('ANTHROPIC_API_KEY')
if not api_key:
    print("⚠ WARNING: ANTHROPIC_API_KEY not found in .env")
else:
    print("✓ ANTHROPIC_API_KEY loaded")

client = Anthropic(api_key=api_key) if api_key else None

# Initialize your project agents
if PROJECT_AVAILABLE:
    validator = ValidatorAgent()
    improver = ImproverAgent()
    analyzer = AnalyzerAgent()
    preprocessor = PreprocessorAgent()
    scoring_engine = ScoringEngine(threshold=7.0)
else:
    validator = improver = analyzer = preprocessor = scoring_engine = None

# System prompt for Claude with 8-dimension awareness
CLAUDE_IMPROVER_PROMPT = """You are an expert prompt engineer with deep knowledge of prompt quality evaluation.

You must improve a prompt considering these 8 CRITICAL DIMENSIONS:

1. **CLARITY** - Is the request unambiguous and easy to understand?
2. **SPECIFICITY** - Is enough detail provided to guide accurate execution?
3. **CONTEXT** - Is relevant background information included?
4. **COMPLETENESS** - Are all necessary information components present?
5. **REQUIREMENTS** - Are success criteria and expectations explicit?
6. **CONSTRAINTS** - Are limitations or boundaries defined?
7. **EXPECTED_OUTPUT** - Is the desired output format/structure clear?
8. **ACTIONABILITY** - Can the prompt be executed immediately as written?

YOUR TASK:
Rewrite the prompt to maximize scores on ALL 8 dimensions. Address any gaps in:
- Missing clarity (use clearer language)
- Lack of specificity (add concrete details, examples, numbers)
- Missing context (add background and purpose)
- Incompleteness (add all required information)
- Unclear requirements (define explicit success criteria)
- Undefined constraints (set boundaries and limits)
- Vague output format (specify exact format and structure)
- Poor actionability (make it immediately executable)

Return ONLY the improved prompt, nothing else. Do not add explanations or meta-commentary."""

def improve_with_claude(deficient_prompt: str) -> str:
    """Call Claude to improve prompt with 8-dimension awareness"""
    if not client:
        return "ERROR: Claude API not configured"

    try:
        message = client.messages.create(
            model="claude-opus-5-5",
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": f"{CLAUDE_IMPROVER_PROMPT}\n\nPROMPT TO IMPROVE:\n{deficient_prompt}"
                }
            ]
        )
        return message.content[0].text.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"

def improve_with_project(deficient_prompt: str, metadata=None) -> dict:
    """Use your project's Improver Agent"""
    if not PROJECT_AVAILABLE:
        return {"error": "Project agents not available"}

    try:
        # Step 1: Preprocess
        preprocessed = preprocessor.process(deficient_prompt)
        processed_prompt = preprocessed["processed_prompt"]

        # Step 2: Analyze
        analysis = analyzer.analyze(processed_prompt)

        # Step 3: Validate
        validation = validator.validate(processed_prompt, analysis=analysis, metadata=metadata or {})

        # Step 4: Score
        scoring = scoring_engine.calculate_scores(validation)

        # Step 5: Improve (if needed)
        if scoring["overall_score"] < 7.0:
            improvement = improver.improve(
                deficient_prompt,
                analysis=analysis,
                validation=validation,
                scoring=scoring,
                iteration=1,
                metadata=metadata or {}
            )
            improved_prompt = improvement.get("improved_prompt", deficient_prompt)

            # Re-validate improved prompt
            validation_improved = validator.validate(improved_prompt, metadata=metadata or {})
            scoring_improved = scoring_engine.calculate_scores(validation_improved)
        else:
            improved_prompt = processed_prompt
            validation_improved = validation
            scoring_improved = scoring

        return {
            "improved_prompt": improved_prompt,
            "validation": validation_improved,
            "scoring": scoring_improved
        }
    except Exception as e:
        return {"error": str(e)}

def generate_excel_comparison(claude_result, project_result, user_prompt):
    """Generate Excel file with dimension scores comparison"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Comparison"

    # Headers
    dimensions = ['clarity', 'specificity', 'context', 'completeness',
                  'requirements', 'constraints', 'expected_output', 'actionability']

    # Title
    ws['A1'] = "PROMPT IMPROVEMENT COMPARISON"
    ws['A1'].font = Font(size=14, bold=True)
    ws.merge_cells('A1:E1')

    # Original prompt
    ws['A3'] = "Original Prompt:"
    ws['A4'] = user_prompt
    ws['A4'].alignment = Alignment(wrap_text=True)
    ws.row_dimensions[4].height = 60

    # Headers for comparison
    ws['A7'] = "Dimension"
    ws['B7'] = "Claude Score"
    ws['C7'] = "Project Score"
    ws['D7'] = "Difference"
    ws['E7'] = "Winner"

    for col in ['A', 'B', 'C', 'D', 'E']:
        ws[f'{col}7'].font = Font(bold=True, color="FFFFFF")
        ws[f'{col}7'].fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

    # Dimension scores
    row = 8
    for dim in dimensions:
        claude_score = claude_result.get("scores", {}).get(dim, 0)
        project_score = project_result.get("scores", {}).get(dim, 0)
        difference = round(claude_score - project_score, 2)
        winner = "Claude" if claude_score > project_score else ("Project" if project_score > claude_score else "Tie")

        ws[f'A{row}'] = dim.replace('_', ' ').title()
        ws[f'B{row}'] = claude_score
        ws[f'C{row}'] = project_score
        ws[f'D{row}'] = difference
        ws[f'E{row}'] = winner

        row += 1

    # Overall scores
    row += 1
    ws[f'A{row}'] = "OVERALL SCORE"
    ws[f'A{row}'].font = Font(bold=True)
    ws[f'B{row}'] = round(sum([claude_result.get("scores", {}).get(d, 0) for d in dimensions]) / len(dimensions), 2)
    ws[f'C{row}'] = round(sum([project_result.get("scores", {}).get(d, 0) for d in dimensions]) / len(dimensions), 2)
    ws[f'B{row}'].font = Font(bold=True)
    ws[f'C{row}'].font = Font(bold=True)

    # Improved prompts
    row += 3
    ws[f'A{row}'] = "Claude Improved Prompt:"
    ws[f'A{row}'].font = Font(bold=True)
    row += 1
    ws[f'A{row}'] = claude_result.get("improved_prompt", "")
    ws[f'A{row}'].alignment = Alignment(wrap_text=True)
    ws.row_dimensions[row].height = 80

    row += 3
    ws[f'A{row}'] = "Project Improved Prompt:"
    ws[f'A{row}'].font = Font(bold=True)
    row += 1
    ws[f'A{row}'] = project_result.get("improved_prompt", "")
    ws[f'A{row}'].alignment = Alignment(wrap_text=True)
    ws.row_dimensions[row].height = 80

    # Auto-adjust column widths
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 15

    # Save to bytes
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output

@app.route('/')
def index():
    return render_template('integrated.html')

@app.route('/api/compare-prompt', methods=['POST'])
def compare_prompt():
    """API endpoint to compare Claude vs Project improvements"""
    data = request.json
    user_prompt = data.get('prompt', '').strip()

    if not user_prompt:
        return jsonify({'error': 'Prompt is empty'}), 400

    if not client or not PROJECT_AVAILABLE:
        return jsonify({'error': 'Required services not configured'}), 500

    # Get Claude improvement
    claude_improved = improve_with_claude(user_prompt)

    # Get Project improvement
    project_result = improve_with_project(user_prompt)

    if 'error' in project_result:
        return jsonify({'error': project_result['error']}), 500

    project_improved = project_result.get("improved_prompt", user_prompt)
    project_validation = project_result.get("validation", {})
    project_scoring = project_result.get("scoring", {})

    # Score Claude improvement
    claude_validation = validator.validate(claude_improved)
    claude_scoring = scoring_engine.calculate_scores(claude_validation)

    # Score Project improvement
    claude_scores = claude_scoring.get("dimension_scores", {})
    project_scores = project_scoring.get("dimension_scores", {})

    response = {
        "user_prompt": user_prompt,
        "claude": {
            "improved_prompt": claude_improved,
            "scores": claude_scores,
            "overall_score": claude_scoring.get("overall_score", 0)
        },
        "project": {
            "improved_prompt": project_improved,
            "scores": project_scores,
            "overall_score": project_scoring.get("overall_score", 0)
        },
        "timestamp": datetime.now().isoformat()
    }

    return jsonify(response)

@app.route('/api/download-excel', methods=['POST'])
def download_excel():
    """Generate and download Excel comparison"""
    data = request.json

    claude_result = data.get('claude', {})
    project_result = data.get('project', {})
    user_prompt = data.get('user_prompt', '')

    excel_file = generate_excel_comparison(claude_result, project_result, user_prompt)

    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'prompt_comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "claude_available": client is not None,
        "project_agents_available": PROJECT_AVAILABLE
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("INTEGRATED PROMPT IMPROVER")
    print("="*60)
    print(f"Claude API: {'✓ Available' if client else '⚠ Not configured'}")
    print(f"Project Agents: {'✓ Available' if PROJECT_AVAILABLE else '⚠ Not available'}")
    print("\nOpen browser: http://localhost:5000")
    print("="*60 + "\n")

    if not client or not PROJECT_AVAILABLE:
        print("⚠ WARNING: Some services are not configured")
        print("  Claude: Set ANTHROPIC_API_KEY")
        print("  Project: Ensure agents are importable from backend/evaluator/agents/")

    app.run(debug=True, port=5000)
