import io
from typing import Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

class ExcelExporter:
    """
    Exports comprehensive Prompt Evaluation, 15-Dimension Scoring,
    Prompt-Specific Synthetic Dataset, and Before/After Comparison into a polished multi-tab Excel workbook.
    """

    # Color Palette
    PRIMARY_COLOR = "1E3A8A"      # Deep Navy
    SECONDARY_COLOR = "3B82F6"    # Royal Blue
    ACCENT_COLOR = "0D9488"       # Teal
    SUCCESS_COLOR = "16A34A"      # Green
    WARNING_COLOR = "D97706"      # Amber
    DANGER_COLOR = "DC2626"       # Crimson
    HEADER_FILL = "1E293B"        # Slate 800
    ZEBRA_FILL = "F8FAFC"         # Slate 50
    CARD_BG = "F1F5F9"            # Slate 100
    BORDER_COLOR = "CBD5E1"       # Slate 300

    @classmethod
    def generate_workbook(cls, workflow_result: Dict[str, Any]) -> io.BytesIO:
        wb = openpyxl.Workbook()
        # Remove default sheet
        wb.remove(wb.active)

        # 1. Executive Summary Sheet
        cls._create_summary_sheet(wb, workflow_result)

        # 2. Synthetic Dataset Table Sheet
        cls._create_synthetic_dataset_sheet(wb, workflow_result)

        # 3. 15-Dimension Evaluation Sheet
        cls._create_dimensions_sheet(wb, workflow_result)

        # 4. Prompt Comparison Sheet
        cls._create_comparison_sheet(wb, workflow_result)

        # 5. Prompt Analysis & Semantics Sheet
        cls._create_analysis_sheet(wb, workflow_result)

        # 6. All Datasets Sheet (every generated dataset, one row per test case)
        cls._create_all_datasets_sheet(wb, workflow_result)

        # Save to BytesIO stream
        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        return stream

    @classmethod
    def _create_summary_sheet(cls, wb: openpyxl.Workbook, data: Dict[str, Any]):
        ws = wb.create_sheet(title="Executive Summary")
        ws.views.sheetView[0].showGridLines = True

        # Styles
        title_font = Font(name="Calibri", size=18, bold=True, color="FFFFFF")
        section_font = Font(name="Calibri", size=13, bold=True, color=cls.PRIMARY_COLOR)
        bold_font = Font(name="Calibri", size=11, bold=True)
        regular_font = Font(name="Calibri", size=11)
        kpi_value_font = Font(name="Calibri", size=20, bold=True, color="FFFFFF")
        kpi_label_font = Font(name="Calibri", size=10, bold=True, color="E2E8F0")

        header_fill = PatternFill(start_color=cls.PRIMARY_COLOR, end_color=cls.PRIMARY_COLOR, fill_type="solid")
        card_fill = PatternFill(start_color=cls.CARD_BG, end_color=cls.CARD_BG, fill_type="solid")
        kpi_orig_fill = PatternFill(start_color="475569", end_color="475569", fill_type="solid")
        kpi_imp_fill = PatternFill(start_color=cls.SUCCESS_COLOR, end_color=cls.SUCCESS_COLOR, fill_type="solid")
        kpi_diff_fill = PatternFill(start_color=cls.SECONDARY_COLOR, end_color=cls.SECONDARY_COLOR, fill_type="solid")

        thin_border = Border(
            left=Side(style="thin", color=cls.BORDER_COLOR),
            right=Side(style="thin", color=cls.BORDER_COLOR),
            top=Side(style="thin", color=cls.BORDER_COLOR),
            bottom=Side(style="thin", color=cls.BORDER_COLOR)
        )

        # Header Title Banner
        ws.merge_cells("A1:H2")
        title_cell = ws["A1"]
        title_cell.value = "PROMPT EVALUATION & SYNTHETIC DATASET REPORT"
        title_cell.font = title_font
        title_cell.fill = header_fill
        title_cell.alignment = Alignment(horizontal="center", vertical="center")

        # Metadata Section
        ws["A4"].value = "FRONTEND METADATA & TASK CONTEXT"
        ws["A4"].font = section_font

        metadata_rows = [
            ("Prompt ID", data.get("prompt_id", "PROMPT-001")),
            ("Department", data.get("department", "N/A").capitalize()),
            ("Task Type", data.get("task_type", "N/A").title()),
            ("Dataset Size", f"{data.get('dataset_size', 20)} test cases generated"),
            ("Status", data.get("status", "COMPLETED")),
        ]

        row_idx = 5
        for label, val in metadata_rows:
            ws.cell(row=row_idx, column=1, value=label).font = bold_font
            ws.cell(row=row_idx, column=1).fill = card_fill
            ws.cell(row=row_idx, column=1).border = thin_border

            ws.merge_cells(start_row=row_idx, start_column=2, end_row=row_idx, end_column=4)
            val_cell = ws.cell(row=row_idx, column=2, value=val)
            val_cell.font = regular_font
            val_cell.border = thin_border
            row_idx += 1

        # KPI Score Cards
        orig_score = data.get("overall_original_score", 0.0)
        imp_score = data.get("overall_improved_score", 0.0)
        diff_score = data.get("score_difference", 0.0)

        # Original Card
        ws.merge_cells("F4:F5")
        c1 = ws["F4"]
        c1.value = f"{orig_score} / 10"
        c1.font = kpi_value_font
        c1.fill = kpi_orig_fill
        c1.alignment = Alignment(horizontal="center", vertical="center")
        ws["F6"].value = "ORIGINAL SCORE"
        ws["F6"].font = bold_font
        ws["F6"].alignment = Alignment(horizontal="center")

        # Improved Card
        ws.merge_cells("G4:G5")
        c2 = ws["G4"]
        c2.value = f"{imp_score} / 10"
        c2.font = kpi_value_font
        c2.fill = kpi_imp_fill
        c2.alignment = Alignment(horizontal="center", vertical="center")
        ws["G6"].value = "IMPROVED SCORE"
        ws["G6"].font = bold_font
        ws["G6"].alignment = Alignment(horizontal="center")

        # Delta Card
        ws.merge_cells("H4:H5")
        c3 = ws["H4"]
        c3.value = f"+{diff_score}" if diff_score > 0 else f"{diff_score}"
        c3.font = kpi_value_font
        c3.fill = kpi_diff_fill
        c3.alignment = Alignment(horizontal="center", vertical="center")
        ws["H6"].value = "NET GAIN"
        ws["H6"].font = bold_font
        ws["H6"].alignment = Alignment(horizontal="center")

        # Synthetic Dataset Summary Section
        ws["A11"].value = "SYNTHETIC DATASET DISTRIBUTION"
        ws["A11"].font = section_font

        ds_summary = data.get("dataset_summary", {})
        diff_dist = ds_summary.get("difficulty_distribution", {})
        cat_dist = ds_summary.get("category_distribution", {})

        ws["A12"].value = "Difficulty Tier"
        ws["B12"].value = "Test Cases"
        ws["C12"].value = "Percentage"
        ws["D12"].value = "Target Coverage"

        for col in ["A12", "B12", "C12", "D12"]:
            ws[col].font = bold_font
            ws[col].fill = card_fill
            ws[col].border = thin_border

        total_cases = ds_summary.get("dataset_size", 20)
        diff_rows = [
            ("Easy", diff_dist.get("Easy", 0), "Standard happy path & baseline operations"),
            ("Medium", diff_dist.get("Medium", 0), "Multi-constraint & realistic complex payloads"),
            ("Hard", diff_dist.get("Hard", 0), "Edge cases, boundary conditions & malformed inputs"),
        ]

        cur_row = 13
        for name, count, target in diff_rows:
            pct = f"{(count / max(1, total_cases) * 100):.1f}%"
            ws.cell(row=cur_row, column=1, value=name).font = regular_font
            ws.cell(row=cur_row, column=2, value=count).font = regular_font
            ws.cell(row=cur_row, column=3, value=pct).font = regular_font
            ws.cell(row=cur_row, column=4, value=target).font = regular_font
            for c in range(1, 5):
                ws.cell(row=cur_row, column=c).border = thin_border
            cur_row += 1

        # Dynamic Category Distribution
        ws["F11"].value = "Category Breakdown"
        ws["G11"].value = "Count"
        ws["H11"].value = "Domain Focus"

        for col in ["F11", "G11", "H11"]:
            ws[col].font = bold_font
            ws[col].fill = card_fill
            ws[col].border = thin_border

        cat_row = 12
        for cat_name, count in cat_dist.items():
            ws.cell(row=cat_row, column=6, value=cat_name).font = regular_font
            ws.cell(row=cat_row, column=7, value=count).font = regular_font
            ws.cell(row=cat_row, column=8, value=f"{data.get('department', '').title()} Scenario").font = regular_font
            for c in range(6, 9):
                ws.cell(row=cat_row, column=c).border = thin_border
            cat_row += 1

        # Original Prompt Box
        next_sec_row = max(cur_row, cat_row) + 2
        ws.cell(row=next_sec_row, column=1, value="ORIGINAL SUBMITTED PROMPT").font = section_font
        ws.merge_cells(start_row=next_sec_row+1, start_column=1, end_row=next_sec_row+4, end_column=8)
        orig_box = ws.cell(row=next_sec_row+1, column=1, value=data.get("original_prompt", ""))
        orig_box.font = regular_font
        orig_box.alignment = Alignment(wrap_text=True, vertical="top")
        orig_box.fill = card_fill

        # Auto column widths
        ws.column_dimensions['A'].width = 24
        ws.column_dimensions['B'].width = 18
        ws.column_dimensions['C'].width = 16
        ws.column_dimensions['D'].width = 45
        ws.column_dimensions['E'].width = 6
        ws.column_dimensions['F'].width = 28
        ws.column_dimensions['G'].width = 14
        ws.column_dimensions['H'].width = 30

    @classmethod
    def _create_synthetic_dataset_sheet(cls, wb: openpyxl.Workbook, data: Dict[str, Any]):
        ws = wb.create_sheet(title="Synthetic Dataset")
        ws.views.sheetView[0].showGridLines = True

        headers = [
            "Test Case ID",
            "Input Scenario / Payload",
            "Expected Output",
            "Difficulty",
            "Category",
            "Edge Case",
            "Notes & Evaluation Criteria"
        ]

        header_fill = PatternFill(start_color=cls.PRIMARY_COLOR, end_color=cls.PRIMARY_COLOR, fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        regular_font = Font(name="Calibri", size=10)
        bold_font = Font(name="Calibri", size=10, bold=True)

        easy_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")    # Light green
        med_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")     # Light amber
        hard_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")    # Light red
        zebra_fill = PatternFill(start_color=cls.ZEBRA_FILL, end_color=cls.ZEBRA_FILL, fill_type="solid")

        thin_border = Border(
            left=Side(style="thin", color=cls.BORDER_COLOR),
            right=Side(style="thin", color=cls.BORDER_COLOR),
            top=Side(style="thin", color=cls.BORDER_COLOR),
            bottom=Side(style="thin", color=cls.BORDER_COLOR)
        )

        # Write Headers
        for col_idx, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
        ws.row_dimensions[1].height = 28

        # Write Rows
        test_cases = data.get("synthetic_dataset", {}).get("test_cases", [])
        for row_idx, tc in enumerate(test_cases, start=2):
            diff = tc.get("difficulty", "Medium")
            diff_fill = easy_fill if diff == "Easy" else (hard_fill if diff == "Hard" else med_fill)
            row_fill = zebra_fill if row_idx % 2 == 0 else PatternFill(fill_type=None)

            c1 = ws.cell(row=row_idx, column=1, value=tc.get("test_case_id", ""))
            c1.font = bold_font
            c1.alignment = Alignment(horizontal="center", vertical="top")

            c2 = ws.cell(row=row_idx, column=2, value=tc.get("input", ""))
            c2.font = regular_font
            c2.alignment = Alignment(wrap_text=True, vertical="top")

            c3 = ws.cell(row=row_idx, column=3, value=tc.get("expected_output", ""))
            c3.font = regular_font
            c3.alignment = Alignment(wrap_text=True, vertical="top")

            c4 = ws.cell(row=row_idx, column=4, value=diff)
            c4.font = bold_font
            c4.fill = diff_fill
            c4.alignment = Alignment(horizontal="center", vertical="top")

            c5 = ws.cell(row=row_idx, column=5, value=tc.get("category", ""))
            c5.font = regular_font
            c5.alignment = Alignment(horizontal="center", vertical="top")

            c6 = ws.cell(row=row_idx, column=6, value="YES" if tc.get("edge_case") else "NO")
            c6.font = bold_font
            c6.alignment = Alignment(horizontal="center", vertical="top")

            c7 = ws.cell(row=row_idx, column=7, value=tc.get("notes", ""))
            c7.font = regular_font
            c7.alignment = Alignment(wrap_text=True, vertical="top")

            for c in [c1, c2, c3, c4, c5, c6, c7]:
                c.border = thin_border
                if c not in [c4]:
                    if row_idx % 2 == 0:
                        c.fill = row_fill

            ws.row_dimensions[row_idx].height = 65

        # Freeze top row & enable filter
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = f"A1:G{max(2, len(test_cases)+1)}"

        # Column widths
        ws.column_dimensions['A'].width = 16
        ws.column_dimensions['B'].width = 45
        ws.column_dimensions['C'].width = 45
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 25
        ws.column_dimensions['F'].width = 12
        ws.column_dimensions['G'].width = 40

    @classmethod
    def _create_all_datasets_sheet(cls, wb: openpyxl.Workbook, data: Dict[str, Any]):
        ws = wb.create_sheet(title="All Datasets")
        ws.views.sheetView[0].showGridLines = True

        headers = [
            "Dataset #",
            "Test Case ID",
            "Input Scenario / Payload",
            "Expected Output",
            "Difficulty",
            "Category",
            "Edge Case",
            "Notes & Evaluation Criteria",
            "LLM Score (0-10)",
            "LLM Verdict"
        ]
        widths = [11, 16, 60, 50, 12, 28, 11, 50, 14, 14]

        header_fill = PatternFill(start_color=cls.PRIMARY_COLOR, end_color=cls.PRIMARY_COLOR, fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        regular_font = Font(name="Calibri", size=10)
        bold_font = Font(name="Calibri", size=10, bold=True)
        thin_border = Border(
            left=Side(style="thin", color=cls.BORDER_COLOR),
            right=Side(style="thin", color=cls.BORDER_COLOR),
            top=Side(style="thin", color=cls.BORDER_COLOR),
            bottom=Side(style="thin", color=cls.BORDER_COLOR)
        )

        for col_idx, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
            ws.column_dimensions[get_column_letter(col_idx)].width = widths[col_idx - 1]
        ws.row_dimensions[1].height = 28

        datasets = data.get("synthetic_datasets") or [
            {"dataset_index": 1, "test_cases": data.get("synthetic_dataset", {}).get("test_cases", [])}
        ]

        row_idx = 2
        for ds in datasets:
            for tc in ds.get("test_cases", []):
                values = [
                    ds.get("dataset_index", 1),
                    tc.get("test_case_id", ""),
                    tc.get("input", ""),
                    tc.get("expected_output", ""),
                    tc.get("difficulty", "Medium"),
                    tc.get("category", ""),
                    "YES" if tc.get("edge_case") else "NO",
                    tc.get("notes", ""),
                    tc.get("llm_score") if tc.get("llm_score") is not None else "N/A",
                    tc.get("llm_verdict", "UNGRADED")
                ]
                for col_idx, value in enumerate(values, start=1):
                    cell = ws.cell(row=row_idx, column=col_idx, value=value)
                    cell.font = bold_font if col_idx in (1, 2, 10) else regular_font
                    cell.alignment = Alignment(
                        wrap_text=col_idx in (3, 4, 8),
                        vertical="top",
                        horizontal="center" if col_idx in (1, 2, 5, 7, 9, 10) else "left"
                    )
                    cell.border = thin_border
                row_idx += 1

        ws.freeze_panes = "A2"
        ws.auto_filter.ref = f"A1:J{max(2, row_idx - 1)}"

        cls._create_difficulty_grades_sheet(wb, data)

    @classmethod
    def _create_difficulty_grades_sheet(cls, wb: openpyxl.Workbook, data: Dict[str, Any]):
        ws = wb.create_sheet(title="Difficulty Grades")
        ws.views.sheetView[0].showGridLines = True

        headers = ["Difficulty", "Test Cases", "Graded", "Passing", "Pass Rate (%)", "Average LLM Score"]
        widths = [16, 14, 12, 12, 16, 20]

        header_fill = PatternFill(start_color=cls.PRIMARY_COLOR, end_color=cls.PRIMARY_COLOR, fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        regular_font = Font(name="Calibri", size=10)
        bold_font = Font(name="Calibri", size=10, bold=True)
        thin_border = Border(
            left=Side(style="thin", color=cls.BORDER_COLOR),
            right=Side(style="thin", color=cls.BORDER_COLOR),
            top=Side(style="thin", color=cls.BORDER_COLOR),
            bottom=Side(style="thin", color=cls.BORDER_COLOR)
        )

        for col_idx, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
            ws.column_dimensions[get_column_letter(col_idx)].width = widths[col_idx - 1]
        ws.row_dimensions[1].height = 28

        validation = data.get("test_case_validation", {}) or {}
        by_difficulty = validation.get("coverage_by_difficulty", {}) or {}
        rows = [
            (d, by_difficulty.get(d, {}))
            for d in ["Easy", "Medium", "Hard"]
        ]
        rows.append(("All", {
            "cases": validation.get("total_test_cases", 0),
            "graded": validation.get("graded_cases", 0),
            "passing": validation.get("passing_cases", 0),
            "pass_rate": validation.get("pass_rate", 0.0),
            "avg_score": validation.get("avg_score")
        }))

        for row_idx, (label, block) in enumerate(rows, start=2):
            values = [
                label,
                block.get("cases", 0),
                block.get("graded", 0),
                block.get("passing", 0),
                block.get("pass_rate", 0.0),
                block.get("avg_score") if block.get("avg_score") is not None else "N/A"
            ]
            for col_idx, value in enumerate(values, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.font = bold_font if col_idx == 1 or label == "All" else regular_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = thin_border

        ws.freeze_panes = "A2"

    @classmethod
    def _create_dimensions_sheet(cls, wb: openpyxl.Workbook, data: Dict[str, Any]):
        ws = wb.create_sheet(title="15-Dimension Evaluation")
        ws.views.sheetView[0].showGridLines = True

        headers = [
            "Dimension Name",
            "Original Score (0-10)",
            "Improved Score (0-10)",
            "Score Delta",
            "Reasoning & Assessment",
            "Identified Issue / Weakness",
            "Engineering Recommendation"
        ]

        header_fill = PatternFill(start_color=cls.PRIMARY_COLOR, end_color=cls.PRIMARY_COLOR, fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        regular_font = Font(name="Calibri", size=10)
        bold_font = Font(name="Calibri", size=10, bold=True)
        zebra_fill = PatternFill(start_color=cls.ZEBRA_FILL, end_color=cls.ZEBRA_FILL, fill_type="solid")

        thin_border = Border(
            left=Side(style="thin", color=cls.BORDER_COLOR),
            right=Side(style="thin", color=cls.BORDER_COLOR),
            top=Side(style="thin", color=cls.BORDER_COLOR),
            bottom=Side(style="thin", color=cls.BORDER_COLOR)
        )

        for col_idx, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
        ws.row_dimensions[1].height = 28

        comp_dims = data.get("comparison", {}).get("dimensions_comparison", {})
        orig_dims = data.get("evaluation", {}).get("dimensions", {})
        imp_dims = data.get("re_evaluation", {}).get("dimensions", {})

        row_idx = 2
        for key, orig_data in orig_dims.items():
            name = orig_data.get("name", key.replace("_", " ").title())
            orig_s = orig_data.get("score", 0)
            imp_s = imp_dims.get(key, {}).get("score", orig_s)
            diff = imp_s - orig_s

            c1 = ws.cell(row=row_idx, column=1, value=name)
            c1.font = bold_font

            c2 = ws.cell(row=row_idx, column=2, value=orig_s)
            c2.font = bold_font
            c2.alignment = Alignment(horizontal="center")

            c3 = ws.cell(row=row_idx, column=3, value=imp_s)
            c3.font = bold_font
            c3.alignment = Alignment(horizontal="center")

            c4 = ws.cell(row=row_idx, column=4, value=f"+{diff}" if diff > 0 else f"{diff}")
            c4.font = bold_font
            c4.alignment = Alignment(horizontal="center")
            if diff > 0:
                c4.fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")

            c5 = ws.cell(row=row_idx, column=5, value=orig_data.get("reasoning", ""))
            c5.font = regular_font
            c5.alignment = Alignment(wrap_text=True)

            c6 = ws.cell(row=row_idx, column=6, value=orig_data.get("identified_issue", ""))
            c6.font = regular_font
            c6.alignment = Alignment(wrap_text=True)

            c7 = ws.cell(row=row_idx, column=7, value=orig_data.get("recommendation", ""))
            c7.font = regular_font
            c7.alignment = Alignment(wrap_text=True)

            for c in [c1, c2, c3, c4, c5, c6, c7]:
                c.border = thin_border
                if row_idx % 2 == 0 and c != c4:
                    c.fill = zebra_fill

            ws.row_dimensions[row_idx].height = 45
            row_idx += 1

        ws.freeze_panes = "A2"
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 18
        ws.column_dimensions['C'].width = 18
        ws.column_dimensions['D'].width = 14
        ws.column_dimensions['E'].width = 40
        ws.column_dimensions['F'].width = 35
        ws.column_dimensions['G'].width = 40

    @classmethod
    def _create_comparison_sheet(cls, wb: openpyxl.Workbook, data: Dict[str, Any]):
        ws = wb.create_sheet(title="Prompt Comparison")
        ws.views.sheetView[0].showGridLines = True

        section_font = Font(name="Calibri", size=13, bold=True, color=cls.PRIMARY_COLOR)
        bold_font = Font(name="Calibri", size=11, bold=True)
        regular_font = Font(name="Calibri", size=10)
        card_fill = PatternFill(start_color=cls.CARD_BG, end_color=cls.CARD_BG, fill_type="solid")

        # Side-by-side prompt texts
        ws["A1"].value = "ORIGINAL USER PROMPT"
        ws["A1"].font = section_font
        ws.merge_cells("A2:D20")
        c_orig = ws["A2"]
        c_orig.value = data.get("original_prompt", "")
        c_orig.font = regular_font
        c_orig.alignment = Alignment(wrap_text=True, vertical="top")
        c_orig.fill = card_fill

        ws["E1"].value = "OPTIMIZED IMPROVED PROMPT"
        ws["E1"].font = section_font
        ws.merge_cells("E2:H20")
        c_imp = ws["E2"]
        c_imp.value = data.get("improved_prompt", "")
        c_imp.font = regular_font
        c_imp.alignment = Alignment(wrap_text=True, vertical="top")
        c_imp.fill = PatternFill(start_color="F0FDF4", end_color="F0FDF4", fill_type="solid")

        # Explanation of Changes
        ws["A22"].value = "ENGINEERING ENHANCEMENTS APPLIED"
        ws["A22"].font = section_font

        metadata = data.get("improvement_metadata", {})
        changes = metadata.get("explanation_of_changes", [])

        cur_row = 23
        for change in changes:
            ws.cell(row=cur_row, column=1, value=f"• {change}").font = regular_font
            ws.merge_cells(start_row=cur_row, start_column=1, end_row=cur_row, end_column=8)
            cur_row += 1

        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 25
        ws.column_dimensions['D'].width = 25
        ws.column_dimensions['E'].width = 25
        ws.column_dimensions['F'].width = 25
        ws.column_dimensions['G'].width = 25
        ws.column_dimensions['H'].width = 25

    @classmethod
    def _create_analysis_sheet(cls, wb: openpyxl.Workbook, data: Dict[str, Any]):
        ws = wb.create_sheet(title="Prompt Semantics & Analysis")
        ws.views.sheetView[0].showGridLines = True

        section_font = Font(name="Calibri", size=12, bold=True, color=cls.PRIMARY_COLOR)
        bold_font = Font(name="Calibri", size=10, bold=True)
        regular_font = Font(name="Calibri", size=10)
        card_fill = PatternFill(start_color=cls.CARD_BG, end_color=cls.CARD_BG, fill_type="solid")
        thin_border = Border(
            left=Side(style="thin", color=cls.BORDER_COLOR),
            right=Side(style="thin", color=cls.BORDER_COLOR),
            top=Side(style="thin", color=cls.BORDER_COLOR),
            bottom=Side(style="thin", color=cls.BORDER_COLOR)
        )

        analysis = data.get("analysis", {})

        items = [
            ("Core Intent", analysis.get("prompt_intent", "")),
            ("User Objective", analysis.get("user_objective", "")),
            ("Expected Output", analysis.get("expected_output", "")),
            ("Output Format", analysis.get("output_format", "")),
            ("Complexity Level", analysis.get("complexity", "")),
            ("Target Audience", analysis.get("target_audience", "")),
            ("Explicit Requirements", "\n• " + "\n• ".join(analysis.get("explicit_requirements", []))),
            ("Implicit Requirements", "\n• " + "\n• ".join(analysis.get("implicit_requirements", []))),
            ("Constraints & Rules", "\n• " + "\n• ".join(analysis.get("constraints", []))),
            ("Missing Information", "\n• " + "\n• ".join(analysis.get("missing_information", []))),
            ("Ambiguities Detected", "\n• " + "\n• ".join(analysis.get("ambiguities", []))),
            ("Potential Failure Modes", "\n• " + "\n• ".join(analysis.get("potential_failure_modes", []))),
            ("Edge Cases Identified", "\n• " + "\n• ".join(analysis.get("edge_cases", []))),
        ]

        row = 1
        for title, content in items:
            ws.cell(row=row, column=1, value=title).font = bold_font
            ws.cell(row=row, column=1).fill = card_fill
            ws.cell(row=row, column=1).border = thin_border

            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=6)
            c_val = ws.cell(row=row, column=2, value=content)
            c_val.font = regular_font
            c_val.alignment = Alignment(wrap_text=True, vertical="top")
            c_val.border = thin_border
            ws.row_dimensions[row].height = max(25, 18 * max(1, str(content).count('\n') + 1))
            row += 1

        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 30
        ws.column_dimensions['C'].width = 30
        ws.column_dimensions['D'].width = 30
        ws.column_dimensions['E'].width = 30
        ws.column_dimensions['F'].width = 30
