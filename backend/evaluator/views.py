from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction, models
from django.http import FileResponse
import logging
import traceback
import json
from io import BytesIO
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.cell.rich_text import CellRichText, TextBlock
 
from evaluator.models import EvaluationResult, Prompt, AgentOutput
from evaluator.serializers import (
    EvaluationResultSerializer,
    PromptSerializer,
    PromptEvaluationRequestSerializer,
    PromptEvaluationResponseSerializer
)
from evaluator.orchestrator import PromptEvaluationOrchestrator
from evaluator.config import QUALITY_THRESHOLD, QUALITY_DIMENSIONS
 
logger = logging.getLogger(__name__)
 
 
class PromptEvaluationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for evaluating prompts.
    """
    queryset = EvaluationResult.objects.all()
    serializer_class = EvaluationResultSerializer
    permission_classes = []  # Allow unauthenticated access for testing
 
    def add_cors_headers(self, response):
        """Add CORS headers to response - allow any localhost dev port"""
        origin = self.request.headers.get('Origin', '')
 
        # Allow any localhost origin (dev ports can vary: 5173, 5174, 5176, 5179, etc.)
        if origin.startswith('http://localhost:') or origin.startswith('http://127.0.0.1:'):
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response['Access-Control-Allow-Credentials'] = 'true'
 
        return response
 
    def highlight_keywords_in_text(self, text, keywords, highlight_color="FFFF00"):
        """Highlight specific keywords in text using RichText with background color"""
        if not text or not keywords:
            return text
 
        text = str(text)
 
        try:
            # Import here to avoid issues
            from openpyxl.cell.rich_text import CellRichText, TextBlock
            from openpyxl.styles import Font, PatternFill
 
            # Split text into words while preserving structure
            words = text.split()
            rich_parts = []
 
            for word in words:
                # Check if this word or any keyword is in the word (case-insensitive)
                word_lower = word.lower()
                is_keyword = False
 
                for keyword in keywords:
                    if keyword.lower() in word_lower:
                        is_keyword = True
                        break
 
                if is_keyword:
                    # Highlight this word with yellow background
                    font = Font(bold=True, color="000000")
                    fill = PatternFill(start_color=highlight_color, end_color=highlight_color, fill_type="solid")
                    rich_parts.append(TextBlock(font, word + " "))
                else:
                    # Normal text
                    rich_parts.append(TextBlock(Font(color="000000"), word + " "))
 
            if len(rich_parts) > 1:
                return CellRichText(*rich_parts)
            else:
                return text
        except Exception as e:
            logger.warning(f"Keyword highlighting failed: {e}")
            return text
 
    def highlight_important_keywords(self, text):
        """Intelligently highlight only IMPORTANT keywords in text using bold + color"""
        if not text:
            return text
 
        try:
            from openpyxl.cell.rich_text import CellRichText, TextBlock
            from openpyxl.styles import Font
 
            text = str(text)
 
            # IMPORTANT keywords by context (only critical ones)
            important_keywords = {
                # Issues/Problems
                'issue': 'FF0000',           # Red
                'problem': 'FF0000',
                'error': 'FF0000',
                'failed': 'FF0000',
                'fail': 'FF0000',
                'critical': 'FF0000',
 
                # Missing/Incomplete
                'missing': 'FF9900',         # Orange
                'lacks': 'FF9900',
                'unclear': 'FF9900',
                'undefined': 'FF9900',
                'ambiguous': 'FF9900',
                'vague': 'FF9900',
 
                # Action/Improvement
                'improve': '0066CC',         # Blue
                'clarify': '0066CC',
                'specify': '0066CC',
                'add': '0066CC',
                'expand': '0066CC',
                'define': '0066CC',
                'detail': '0066CC',
 
                # Quality/Success
                'excellent': '00CC00',       # Green
                'good': '00CC00',
                'perfect': '00CC00',
                'complete': '00CC00',
            }
 
            # Split and rebuild with highlighting
            import re
            parts = re.split(r'(\s+)', text)
            rich_parts = []
 
            for part in parts:
                if not part:
                    continue
 
                # Check if this part contains an important keyword
                part_lower = part.lower().strip('.,;:!?')
                found_keyword = False
 
                for keyword, color in important_keywords.items():
                    if keyword == part_lower or keyword in part_lower:
                        # HIGHLIGHT: Bold + colored text
                        font = Font(bold=True, color=color, size=11)
                        rich_parts.append(TextBlock(font, part))
                        found_keyword = True
                        break
 
                if not found_keyword:
                    # Normal text
                    rich_parts.append(TextBlock(Font(color="000000", size=11), part))
 
            if len(rich_parts) > 1:
                return CellRichText(*rich_parts)
            return text
 
        except Exception as e:
            logger.warning(f"Keyword highlighting error: {e}")
            return text
 
    def build_highlighted_text(self, text):
        """Build RichText with ONLY important keywords highlighted in yellow"""
        if not text:
            return text
 
        try:
            from openpyxl.cell.rich_text import CellRichText, TextBlock
            from openpyxl.styles import Font
            import re
 
            text = str(text)
 
            # Important keywords to highlight - EXTRACT IMPORTANT WORDS
            keywords = [
                'missing', 'lacks', 'unclear', 'undefined', 'ambiguous', 'vague', 'unspecified',
                'issue', 'problem', 'error', 'critical', 'failed', 'failure',
                'improve', 'clarify', 'specify', 'add', 'expand', 'detail', 'remove',
                'security breach', 'security breaches', 'detain', 'detaining', 'scene',
                'important', 'essential', 'required', 'urgent',
            ]
 
            # Sort by length (longest first) - match phrases before single words
            keywords_sorted = sorted(keywords, key=len, reverse=True)
 
            # Create regex pattern - match whole words or phrases
            keyword_pattern = '|'.join(re.escape(kw) for kw in keywords_sorted)
 
            # Split text by keywords, keeping them
            parts = re.split(f'({keyword_pattern})', text, flags=re.IGNORECASE)
 
            rich_parts = []
            for part in parts:
                if not part:
                    continue
 
                # Check if this is a keyword (case-insensitive match)
                is_keyword = any(part.lower() == kw.lower() for kw in keywords_sorted)
 
                if is_keyword:
                    # HIGHLIGHT: Orange/Gold bold text + underline (like highlighter marker)
                    font = Font(
                        bold=True,
                        color="FF6B00",  # Dark orange - stands out on white
                        size=11,
                        underline="single"
                    )
                    rich_parts.append(TextBlock(font, part))
                else:
                    # Normal: Black text
                    rich_parts.append(TextBlock(Font(color="000000", size=11), part))
 
            if len(rich_parts) > 1:
                return CellRichText(*rich_parts)
            return text
 
        except Exception as e:
            logger.warning(f"Highlighting failed: {e}")
            return text
 
    def create_highlighted_rich_text(self, text, keywords, color="FFC000"):
        """Create RichText with specific keywords highlighted in bold/colored"""
        if not text or not keywords:
            return text
 
        text_lower = text.lower()
        parts = []
        last_end = 0
 
        # Find all keyword occurrences
        occurrences = []
        for keyword in keywords:
            keyword_lower = keyword.lower()
            start = 0
            while True:
                pos = text_lower.find(keyword_lower, start)
                if pos == -1:
                    break
                occurrences.append((pos, pos + len(keyword)))
                start = pos + 1
 
        if not occurrences:
            return text
 
        # Sort and merge overlapping occurrences
        occurrences.sort()
        merged = []
        for start, end in occurrences:
            if merged and start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))
 
        # Build rich text with highlighted portions
        try:
            for start, end in merged:
                if start > last_end:
                    parts.append(TextBlock(Font(), text[last_end:start]))
 
                highlighted_font = Font(bold=True, color=color)
                parts.append(TextBlock(highlighted_font, text[start:end]))
                last_end = end
 
            if last_end < len(text):
                parts.append(TextBlock(Font(), text[last_end:]))
 
            return CellRichText(*parts) if len(parts) > 1 else text
        except Exception as e:
            logger.warning(f"Failed to create highlighted rich text: {str(e)}")
            return text
 
    def save_agent_outputs(self, evaluation_result, report):
        """Save individual agent outputs to AgentOutput table"""
        execution_history = report.get('execution_history', {})
        iterations = execution_history.get('iterations', [])
 
        print(f"\n✅ Saving agent outputs for evaluation {evaluation_result.id}")
        print(f"   Found {len(iterations)} iterations")
 
        for iteration_data in iterations:
            iteration_num = iteration_data.get('iteration', 0)
            stages = iteration_data.get('stages', {})
 
            print(f"   Iteration {iteration_num}: {len(stages)} agents")
 
            for agent_name, stage_data in stages.items():
                if agent_name not in ['preprocessor', 'classifier', 'analyzer', 'validator', 'scoring', 'improver', 'report']:
                    continue
 
                try:
                    input_data = stage_data.get('input', {})
                    output_data = stage_data.get('output', {})
 
                    # Determine status
                    agent_status = 'success'
                    error_msg = None
                    if isinstance(output_data, dict):
                        if output_data.get('status') == 'skipped':
                            agent_status = 'skipped'
                        elif 'error' in output_data or output_data.get('status') == 'failed':
                            agent_status = 'failed'
                            error_msg = output_data.get('error') or output_data.get('message')
 
                    agent_output = AgentOutput.objects.create(
                        evaluation_result=evaluation_result,
                        agent_name=agent_name,
                        iteration_number=iteration_num,
                        input_data=input_data if input_data else {},
                        output_data=output_data if output_data else {},
                        status=agent_status,
                        error_message=error_msg
                    )
                    print(f"     ✅ Saved {agent_name} - {agent_output.id}")
                except Exception as e:
                    print(f"     ❌ Error saving {agent_name}: {str(e)}")
                    logger.warning(f"Failed to save agent output for {agent_name}: {str(e)}")
 
    def options(self, request, *args, **kwargs):
        """Handle CORS preflight requests"""
        response = super().options(request, *args, **kwargs)
        return self.add_cors_headers(response)
 
    def get_queryset(self):
        """Filter results by current user if authenticated."""
        if self.request.user and self.request.user.is_authenticated:
            return EvaluationResult.objects.filter(prompt__user=self.request.user)
        return EvaluationResult.objects.all()  # Return all for testing
 
    @action(detail=False, methods=['post', 'options'])
    def evaluate(self, request):
        """
        Evaluate a new prompt.
 
        Request body:
        {
            "prompt": "Your prompt text here"
        }
        """
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = Response(status=status.HTTP_200_OK)
            return self.add_cors_headers(response)
 
        serializer = PromptEvaluationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
        prompt_text = serializer.validated_data['prompt']

        # Extract metadata from request (only include if explicitly provided)
        metadata = {}
        if request.data.get('user_role'):
            metadata['user_role'] = request.data.get('user_role')
        if request.data.get('task_type'):
            metadata['task_type'] = request.data.get('task_type')
        if request.data.get('output_format'):
            metadata['output_format'] = request.data.get('output_format')

        try:
            with transaction.atomic():
                # Create or get prompt (allow anonymous for testing)
                user = request.user if request.user.is_authenticated else None
                prompt_obj = Prompt.objects.create(
                    user=user,
                    original_prompt=prompt_text,
                    processed_prompt=prompt_text
                )

                # Run evaluation with 7.0 threshold (from .env or default)
                import os
                threshold = float(os.getenv('THRESHOLD', 7.0))
                orchestrator = PromptEvaluationOrchestrator(threshold=threshold)
                report = orchestrator.evaluate(prompt_text, metadata=metadata)
 
                # Store result
                result = EvaluationResult.objects.create(
                    prompt=prompt_obj,
                    original_prompt=report['original_prompt'],
                    final_prompt=report['final_prompt'],
                    initial_score=report['initial_evaluation']['overall_score'],
                    final_score=report['final_evaluation']['overall_score'],
                    improvements_made=report['improvements_made'],
                    iterations_required=report['iterations_required'],
                    summary=report['summary'],
                    status=report['status'],
                    full_report=report
                )
 
                # Save individual agent outputs to database
                self.save_agent_outputs(result, report)
 
                # Serialize the result model properly
                response_serializer = EvaluationResultSerializer(result)
                response = Response(response_serializer.data, status=status.HTTP_201_CREATED)
                return self.add_cors_headers(response)
 
        except Exception as e:
            error_msg = f"Evaluation failed: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            print(f"\n❌ ERROR: {error_msg}\n")
            response = Response(
                {"error": str(e), "detail": "See backend logs for details"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            return self.add_cors_headers(response)
 
    @action(detail=False, methods=['post'])
    def batch_evaluate(self, request):
        """
        Batch evaluate multiple prompts.
 
        Request body:
        {
            "prompts": ["prompt1", "prompt2", "prompt3"]
        }
        """
        prompts = request.data.get('prompts', [])
 
        if not isinstance(prompts, list) or len(prompts) == 0:
            return Response(
                {"error": "Please provide a list of prompts"},
                status=status.HTTP_400_BAD_REQUEST
            )
 
        try:
            import os
            threshold = float(os.getenv('THRESHOLD', 7.0))
            orchestrator = PromptEvaluationOrchestrator(threshold=threshold)
            results = []
 
            for prompt_text in prompts:
                try:
                    report = orchestrator.evaluate(prompt_text)
                    results.append(report)
                except Exception as e:
                    results.append({
                        "error": str(e),
                        "prompt": prompt_text
                    })
 
            return Response(results, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
 
    @action(detail=True, methods=['get', 'options'])
    def export_excel(self, request, pk=None):
        """Export evaluation results to single comprehensive Excel sheet."""
        try:
            result = self.get_object()
            report = result.full_report
 
            wb = Workbook()
            ws = wb.active
            ws.title = "Evaluation Report"
 
            # Set column widths
            ws.column_dimensions['A'].width = 30
            ws.column_dimensions['B'].width = 50
            ws.column_dimensions['C'].width = 15
            ws.column_dimensions['D'].width = 40
 
            # Define styles
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font = Font(bold=True, size=12, color="FFFFFF")
            section_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
            section_font = Font(bold=True, size=11)
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
 
            row = 1
 
            # ===== TITLE =====
            ws[f'A{row}'] = "PROMPT EVALUATION REPORT"
            ws[f'A{row}'].font = Font(bold=True, size=14, color="FFFFFF")
            ws[f'A{row}'].fill = PatternFill(start_color="003366", end_color="003366", fill_type="solid")
            ws.merge_cells(f'A{row}:D{row}')
            row += 1
 
            # ===== EXECUTIVE SUMMARY BOX =====
            ws[f'A{row}'] = "✓ QUICK SUMMARY (Read This First!)"
            ws[f'A{row}'].font = Font(bold=True, size=12, color="FFFFFF")
            ws[f'A{row}'].fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
            ws.merge_cells(f'A{row}:D{row}')
            row += 1
 
            initial_score = report.get('initial_evaluation', {}).get('overall_score', 0)
            final_score = report.get('final_evaluation', {}).get('overall_score', 0)
 
            # Score display with color coding
            ws[f'A{row}'] = "OVERALL SCORE"
            ws[f'A{row}'].font = Font(bold=True, size=11, color="FFFFFF")
            ws[f'B{row}'] = f"{final_score}/10"
            ws[f'B{row}'].font = Font(bold=True, size=14, color="FFFFFF")
 
            # Color code: Red < 6, Yellow 6-7.5, Green > 7.5
            if final_score >= 7.5:
                ws[f'B{row}'].fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")  # Green
            elif final_score >= 6:
                ws[f'B{row}'].fill = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")  # Yellow
            else:
                ws[f'B{row}'].fill = PatternFill(start_color="E74C3C", end_color="E74C3C", fill_type="solid")  # Red
 
            ws[f'C{row}'] = "STATUS"
            ws[f'C{row}'].font = Font(bold=True, color="FFFFFF")
            status_text = "Ready to Use" if final_score >= 7 else "Needs Review" if final_score >= 6 else "Needs Rewriting"
            ws[f'D{row}'] = status_text
            ws[f'D{row}'].font = Font(bold=True, size=11, color="FFFFFF")
            if final_score >= 7:
                ws[f'D{row}'].fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
            elif final_score >= 6:
                ws[f'D{row}'].fill = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")
            else:
                ws[f'D{row}'].fill = PatternFill(start_color="E74C3C", end_color="E74C3C", fill_type="solid")
            row += 1
 
            # Improvement summary
            improvement = final_score - initial_score
            ws[f'A{row}'] = "IMPROVEMENT"
            ws[f'A{row}'].font = Font(bold=True, color="FFFFFF")
            ws[f'B{row}'] = f"+{improvement:.1f}" if improvement >= 0 else f"{improvement:.1f}"
            ws[f'B{row}'].font = Font(bold=True, size=11)
            ws[f'B{row}'].fill = PatternFill(start_color="E7F3FF", end_color="E7F3FF", fill_type="solid")
            ws[f'C{row}'] = "ITERATIONS"
            ws[f'C{row}'].font = Font(bold=True, color="FFFFFF")
            ws[f'D{row}'] = report.get('iterations_required', 0)
            ws[f'D{row}'].font = Font(bold=True, size=11)
            ws[f'D{row}'].fill = PatternFill(start_color="E7F3FF", end_color="E7F3FF", fill_type="solid")
            row += 2
 
            # ===== TOP FINDINGS =====
            ws[f'A{row}'] = "⚡ TOP FINDINGS (What To Fix)"
            ws[f'A{row}'].font = Font(bold=True, size=12, color="FFFFFF")
            ws[f'A{row}'].fill = PatternFill(start_color="C00000", end_color="C00000", fill_type="solid")
            ws.merge_cells(f'A{row}:D{row}')
            row += 1
 
            # Extract top issues
            analysis = report.get('analysis', {}) or {}
            missing = analysis.get('missing_information', [])[:3]
            ambiguities = analysis.get('ambiguities', [])[:2]
 
            for i, issue in enumerate(missing[:3], 1):
                ws[f'A{row}'] = f"• MISSING: {issue}"
                ws[f'A{row}'].font = Font(bold=True, color="C00000", size=11)
                ws.merge_cells(f'A{row}:D{row}')
                row += 1
 
            for i, issue in enumerate(ambiguities[:2], 1):
                ws[f'A{row}'] = f"• UNCLEAR: {issue}"
                ws[f'A{row}'].font = Font(bold=True, color="FF6600", size=11)
                ws.merge_cells(f'A{row}:D{row}')
                row += 1
 
            row += 2
 
            # ===== PROMPTS =====
            ws[f'A{row}'] = "ORIGINAL PROMPT"
            ws[f'A{row}'].font = section_font
            ws[f'A{row}'].fill = section_fill
            ws.merge_cells(f'A{row}:D{row}')
            row += 1
 
            original_prompt = report.get('original_prompt', '')
            ws[f'A{row}'] = original_prompt
            ws[f'A{row}'].alignment = Alignment(wrap_text=True, vertical='top')
            ws.merge_cells(f'A{row}:D{row}')
            ws.row_dimensions[row].height = 60
            row += 2
 
            if report.get('final_prompt') != report.get('original_prompt'):
                ws[f'A{row}'] = "IMPROVED PROMPT"
                ws[f'A{row}'].font = section_font
                ws[f'A{row}'].fill = section_fill
                ws.merge_cells(f'A{row}:D{row}')
                row += 1
 
                final_prompt = report.get('final_prompt', '')
                ws[f'A{row}'] = final_prompt
                ws[f'A{row}'].alignment = Alignment(wrap_text=True, vertical='top')
                ws.merge_cells(f'A{row}:D{row}')
                ws.row_dimensions[row].height = 60
                row += 2
 
            # ===== CLASSIFICATION & ANALYSIS =====
            ws[f'A{row}'] = "CLASSIFICATION & ANALYSIS"
            ws[f'A{row}'].font = section_font
            ws[f'A{row}'].fill = section_fill
            ws.merge_cells(f'A{row}:D{row}')
            row += 1
 
            classification = report.get('classification', {})
            analysis = report.get('analysis', {})
 
            ws[f'A{row}'] = "Task Type"
            ws[f'B{row}'] = classification.get('task_type', 'N/A')
            ws[f'C{row}'] = "Complexity"
            ws[f'D{row}'] = classification.get('complexity', 'N/A')
            row += 1
 
            ws[f'A{row}'] = "Intent"
            intent_text = analysis.get('intent', 'N/A')
            ws[f'B{row}'] = intent_text
            ws[f'B{row}'].font = Font(bold=True, size=10)
            ws.merge_cells(f'B{row}:D{row}')
            ws[f'B{row}'].alignment = Alignment(wrap_text=True)
            row += 1
 
            ws[f'A{row}'] = "Missing Information"
            ws[f'A{row}'].font = Font(bold=True, size=11)
 
            missing_info_list = analysis.get('missing_information', [])
            if missing_info_list:
                missing_text = ", ".join(missing_info_list)
                ws[f'B{row}'] = self.build_highlighted_text(missing_text)
            else:
                ws[f'B{row}'] = "None"
            ws.merge_cells(f'B{row}:D{row}')
            ws[f'B{row}'].alignment = Alignment(wrap_text=True, vertical='top')
            ws.row_dimensions[row].height = 40
            row += 1
 
            ws[f'A{row}'] = "Ambiguities"
            ws[f'A{row}'].font = Font(bold=True, size=11)
 
            ambiguities_list = analysis.get('ambiguities', [])
            if ambiguities_list:
                ambig_text = ", ".join(ambiguities_list)
                ws[f'B{row}'] = self.build_highlighted_text(ambig_text)
            else:
                ws[f'B{row}'] = "None"
            ws.merge_cells(f'B{row}:D{row}')
            ws[f'B{row}'].alignment = Alignment(wrap_text=True, vertical='top')
            ws.row_dimensions[row].height = 40
            row += 2
 
            # ===== VALIDATION DIMENSIONS (SKIPPED - using quick summary instead) =====
            pass
            row += 0
 
            # (Skipped - dimension details are in the main report already)
 
            # ===== AGENT PIPELINE OUTPUTS =====
            ws[f'A{row}'] = "AGENT PIPELINE OUTPUTS"
            ws[f'A{row}'].font = section_font
            ws[f'A{row}'].fill = section_fill
            ws.merge_cells(f'A{row}:D{row}')
            row += 1
 
            # Get execution history with all agent outputs
            execution_history = report.get('execution_history', {})
            iterations = execution_history.get('iterations', [])
 
            if iterations:
                # Get first iteration stages (all agents run in iteration 0)
                stages = iterations[0].get('stages', {})
 
                agent_names_order = ['preprocessor', 'classifier', 'analyzer', 'validator', 'scoring', 'improver', 'report']
 
                for agent_name in agent_names_order:
                    if agent_name not in stages:
                        continue
 
                    ws[f'A{row}'] = f"{agent_name.upper()} - Input & Output"
                    ws[f'A{row}'].font = Font(bold=True, size=10, color="FFFFFF")
                    ws[f'A{row}'].fill = PatternFill(start_color="203864", end_color="203864", fill_type="solid")
                    ws.merge_cells(f'A{row}:D{row}')
                    row += 1
 
                    agent_stage = stages[agent_name]
 
                    # Show input
                    if 'input' in agent_stage:
                        ws[f'A{row}'] = "INPUT"
                        ws[f'A{row}'].font = Font(bold=True, size=9, italic=True)
                        input_val = agent_stage.get('input')
                        input_str = str(input_val)[:500]  # Limit to 500 chars for readability
                        ws[f'B{row}'] = input_str
                        ws[f'B{row}'].alignment = Alignment(wrap_text=True)
                        ws.merge_cells(f'B{row}:D{row}')
                        ws.row_dimensions[row].height = 25
                        row += 1
 
                    # Show output
                    if 'output' in agent_stage:
                        ws[f'A{row}'] = "OUTPUT"
                        ws[f'A{row}'].font = Font(bold=True, size=9, italic=True)
                        output_val = agent_stage.get('output')
 
                        # For dict outputs, show key-value pairs
                        if isinstance(output_val, dict):
                            output_str = str(output_val)[:500]
                        else:
                            output_str = str(output_val)[:500]
 
                        ws[f'B{row}'] = output_str
                        ws[f'B{row}'].alignment = Alignment(wrap_text=True)
                        ws.merge_cells(f'B{row}:D{row}')
                        ws.row_dimensions[row].height = 30
                        row += 1
 
                    # Handle skipped/status field
                    if 'status' in agent_stage:
                        ws[f'A{row}'] = "Status"
                        ws[f'A{row}'].font = Font(bold=True, size=9)
                        ws[f'B{row}'] = agent_stage.get('status')
                        row += 1
 
                    if 'reason' in agent_stage:
                        ws[f'A{row}'] = "Reason"
                        ws[f'A{row}'].font = Font(bold=True, size=9)
                        ws[f'B{row}'] = agent_stage.get('reason')
                        row += 1
 
                    row += 1
 
            # ===== IMPROVEMENTS HISTORY =====
            improvements = report.get('improvement_history', [])
            if improvements:
                ws[f'A{row}'] = "IMPROVEMENT HISTORY"
                ws[f'A{row}'].font = section_font
                ws[f'A{row}'].fill = section_fill
                ws.merge_cells(f'A{row}:D{row}')
                row += 1
 
                for i, imp in enumerate(improvements, 1):
                    ws[f'A{row}'] = f"Iteration {i}"
                    ws[f'A{row}'].font = Font(bold=True, italic=True)
                    ws.merge_cells(f'A{row}:D{row}')
                    row += 1
 
                    ws[f'A{row}'] = "Improved Prompt"
                    ws[f'B{row}'] = imp.get('improved_prompt', '')
                    ws[f'B{row}'].alignment = Alignment(wrap_text=True)
                    ws.merge_cells(f'B{row}:D{row}')
                    ws.row_dimensions[row].height = 50
                    row += 1
 
                    ws[f'A{row}'] = "Changes Made"
                    changes = ', '.join(imp.get('changes_made', []))
                    ws[f'B{row}'] = changes
                    ws[f'B{row}'].alignment = Alignment(wrap_text=True)
                    ws.merge_cells(f'B{row}:D{row}')
                    ws.row_dimensions[row].height = 40
                    row += 1
 
                    ws[f'A{row}'] = "Dimensions Addressed"
                    dims = ', '.join(imp.get('dimensions_addressed', []))
                    ws[f'B{row}'] = dims
                    ws.merge_cells(f'B{row}:D{row}')
                    row += 1
 
                    ws[f'A{row}'] = "Intent Preserved"
                    ws[f'B{row}'] = "Yes" if imp.get('intent_preserved') else "No"
                    row += 2
 
            # ===== KEY GAPS & RECOMMENDATIONS =====
            ws[f'A{row}'] = "KEY GAPS & RECOMMENDATIONS"
            ws[f'A{row}'].font = section_font
            ws[f'A{row}'].fill = section_fill
            ws.merge_cells(f'A{row}:D{row}')
            row += 1
 
            low_dims = report.get('final_evaluation', {}).get('low_scoring_dimensions', [])
            if low_dims:
                ws[f'A{row}'] = "Low Scoring Dimensions"
                ws[f'B{row}'] = ', '.join(low_dims)
                ws.merge_cells(f'B{row}:D{row}')
                row += 1
 
            ws[f'A{row}'] = "Summary"
            summary_text = report.get('summary', '')
            ws[f'B{row}'] = self.build_highlighted_text(summary_text)
            ws[f'B{row}'].alignment = Alignment(wrap_text=True)
            ws.merge_cells(f'B{row}:D{row}')
            ws.row_dimensions[row].height = 50
            row += 1
 
            # Save to bytes
            excel_file = BytesIO()
            wb.save(excel_file)
            excel_file.seek(0)
 
            # Return file
            filename = f"evaluation_{result.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            response = FileResponse(excel_file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return self.add_cors_headers(response)
 
        except EvaluationResult.DoesNotExist:
            response = Response(
                {"error": "Evaluation not found"},
                status=status.HTTP_404_NOT_FOUND
            )
            return self.add_cors_headers(response)
        except Exception as e:
            error_msg = f"Excel export failed: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            response = Response(
                {"error": "Export failed", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            return self.add_cors_headers(response)
 
 
class PromptHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing evaluation history.
    """
    queryset = EvaluationResult.objects.all()
    serializer_class = EvaluationResultSerializer
    permission_classes = []  # Allow unauthenticated access for testing
 
    def get_queryset(self):
        """Filter evaluations by current user if authenticated."""
        if self.request.user and self.request.user.is_authenticated:
            return EvaluationResult.objects.filter(prompt__user=self.request.user).order_by('-created_at')
        return EvaluationResult.objects.all().order_by('-created_at')  # Return all for testing
 
    @action(detail=True, methods=['get'])
    def evaluations(self, request, pk=None):
        """Get all evaluations for a specific prompt."""
        try:
            prompt = self.get_object()
            results = EvaluationResult.objects.filter(prompt=prompt)
            serializer = EvaluationResultSerializer(results, many=True)
            return Response(serializer.data)
        except Prompt.DoesNotExist:
            return Response(
                {"error": "Prompt not found"},
                status=status.HTTP_404_NOT_FOUND
            )
 
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics for user's prompts."""
        if not request.user.is_authenticated:
            return Response({
                "total_prompts": 0,
                "total_evaluations": 0,
                "average_score": 0.0,
                "prompts_ready": 0,
                "prompts_needing_review": 0,
                "message": "Authentication required for user stats"
            })
 
        user_prompts = self.get_queryset()
        user_results = EvaluationResult.objects.filter(prompt__user=request.user)
 
        stats = {
            "total_prompts": user_prompts.count(),
            "total_evaluations": user_results.count(),
            "average_score": 0.0,
            "prompts_ready": 0,
            "prompts_needing_review": 0
        }
 
        if user_results.exists():
            avg_score = user_results.values_list('final_score', flat=True).aggregate(
                models.Avg('final_score')
            )
            stats['average_score'] = float(avg_score.get('final_score__avg', 0.0) or 0.0)
            stats['prompts_ready'] = user_results.filter(status='ready').count()
            stats['prompts_needing_review'] = user_results.filter(status='needs_manual_review').count()
 
        return Response(stats)
 
    @action(detail=False, methods=['get'])
    def config(self, request):
        """Get application configuration (threshold, dimensions, etc)."""
        return Response({
            "quality_threshold": QUALITY_THRESHOLD,
            "quality_dimensions": QUALITY_DIMENSIONS,
            "max_iterations": 3
        })
 
 