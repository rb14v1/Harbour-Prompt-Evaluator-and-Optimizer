import openpyxl
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from .models import PromptEvaluation, SyntheticDataset, SyntheticTestCase
from .services.llm_client import llm_client
from .services.preprocessor import Preprocessor
from .services.analyzer import Analyzer
from .services.evaluator import Evaluator, EVALUATION_DIMENSIONS
from .services.dataset_generator import DatasetGenerator
from .services.dataset_validator import DatasetValidator
from .services.scorer import Scorer
from .services.improver import Improver
from .services.revalidator import Revalidator
from .services.langgraph_workflow import execute_evaluation_workflow
from .services.excel_exporter import ExcelExporter

# Disable external network calls during automated test runs
llm_client.client = None

class PreprocessorTests(TestCase):
    def test_preprocessor_cleans_whitespace_and_preserves_original(self):
        raw = "   Create a   JWT auth  system\n\n\n\nwith Node.js.   "
        res = Preprocessor.process(raw)
        self.assertEqual(res["original_prompt"], raw)
        self.assertIn("Create a JWT auth system", res["processed_prompt"])
        self.assertNotIn("\n\n\n", res["processed_prompt"])


class AnalyzerTests(TestCase):
    def test_analyzer_preserves_authoritative_metadata(self):
        dept = "software"
        task = "create content"
        prompt = "Create technical documentation for a JWT authentication system using Node.js and Express."
        analysis = Analyzer.analyze(dept, task, prompt, prompt)

        self.assertIn("prompt_intent", analysis)
        self.assertIn("explicit_requirements", analysis)
        self.assertIn("output_format", analysis)
        self.assertIn("edge_cases", analysis)
        self.assertIn("potential_failure_modes", analysis)


class EvaluatorTests(TestCase):
    def test_evaluator_evaluates_exact_15_dimensions(self):
        dept = "software"
        task = "code generation"
        prompt = "Write a JWT authentication middleware in Express with token expiry."
        analysis = Analyzer.analyze(dept, task, prompt, prompt)
        res = Evaluator.evaluate(dept, task, prompt, analysis)

        dims = res.get("dimensions", {})
        self.assertEqual(len(dims), 15)

        for item in EVALUATION_DIMENSIONS:
            k = item["key"]
            self.assertIn(k, dims)
            score = dims[k]["score"]
            self.assertTrue(0 <= score <= 10)
            self.assertIn("reasoning", dims[k])
            self.assertIn("identified_issue", dims[k])
            self.assertIn("recommendation", dims[k])

        overall = res.get("overall_score", 0)
        self.assertTrue(0 <= overall <= 10)


class DatasetGeneratorAndValidatorTests(TestCase):
    def test_synthetic_dataset_generation_and_validation(self):
        dept = "software"
        task = "create content"
        prompt = "Create technical documentation for a JWT authentication system using Node.js and Express."
        analysis = Analyzer.analyze(dept, task, prompt, prompt)

        target_size = 20
        raw_dataset = DatasetGenerator.generate(
            department=dept,
            task_type=task,
            original_prompt=prompt,
            processed_prompt=prompt,
            analysis=analysis,
            dataset_size=target_size,
            prompt_id="PROMPT-TEST-001"
        )

        self.assertEqual(raw_dataset["dataset_size"], target_size)
        self.assertEqual(len(raw_dataset["test_cases"]), target_size)

        # Validate dataset
        validated_dataset, report = DatasetValidator.validate_and_repair(
            dataset=raw_dataset,
            target_size=target_size,
            department=dept,
            task_type=task,
            prompt=prompt,
            prompt_id="PROMPT-TEST-001"
        )

        self.assertTrue(report["is_valid"])
        self.assertEqual(validated_dataset["dataset_size"], target_size)

        # Check difficulty distribution
        diffs = report["difficulty_distribution"]
        self.assertGreater(diffs["Easy"], 0)
        self.assertGreater(diffs["Medium"], 0)
        self.assertGreater(diffs["Hard"], 0)

        # Check required fields
        for tc in validated_dataset["test_cases"]:
            self.assertIn("test_case_id", tc)
            self.assertIn("input", tc)
            self.assertIn("expected_output", tc)
            self.assertIn("difficulty", tc)
            self.assertIn("category", tc)
            self.assertIn("notes", tc)
            self.assertTrue(tc["difficulty"] in ["Easy", "Medium", "Hard"])


class ImproverAndRevalidatorTests(TestCase):
    def test_improver_and_revalidator_workflow(self):
        dept = "marketing"
        task = "email drafting"
        prompt = "Write an email to launch our new AI analytics feature."
        analysis = Analyzer.analyze(dept, task, prompt, prompt)
        eval_res = Evaluator.evaluate(dept, task, prompt, analysis)

        imp_res = Improver.improve(dept, task, prompt, prompt, analysis, eval_res)
        improved_prompt = imp_res["improved_prompt"]
        self.assertTrue(len(improved_prompt) > len(prompt))
        self.assertIn("ROLE", improved_prompt.upper())

        # Re-evaluate
        reeval = Revalidator.reevaluate(dept, task, improved_prompt, eval_res)
        self.assertEqual(len(reeval["dimensions"]), 15)
        self.assertGreaterEqual(reeval["overall_score"], eval_res["overall_score"])


class ExcelExporterTests(TestCase):
    def test_excel_export_creates_valid_workbook(self):
        dept = "finance"
        task = "summarization"
        prompt = "Summarize Q3 financial earnings with key EBIT margins and YoY growth."
        workflow_res = execute_evaluation_workflow(dept, task, prompt, dataset_size=5, prompt_id="PROMPT-XLS")

        stream = ExcelExporter.generate_workbook(workflow_res)
        wb = openpyxl.load_workbook(stream)

        sheet_names = wb.sheetnames
        self.assertIn("Executive Summary", sheet_names)
        self.assertIn("Synthetic Dataset", sheet_names)
        self.assertIn("15-Dimension Evaluation", sheet_names)
        self.assertIn("Prompt Comparison", sheet_names)
        self.assertIn("Prompt Semantics & Analysis", sheet_names)

        # Verify dataset rows
        ds_sheet = wb["Synthetic Dataset"]
        # Header + 5 rows = 6 rows
        self.assertGreaterEqual(ds_sheet.max_row, 6)


class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_evaluate_api_success_default_5_datasets(self):
        payload = {
            "department": "software",
            "task_type": "create content",
            "prompt": "Create technical documentation for a JWT authentication system using Node.js and Express.",
            # dataset_size omitted to verify default 5 cases; num_datasets=1 avoids 99 extra LLM calls
            "num_datasets": 1
        }
        response = self.client.post("/api/evaluate/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data["department"], "software")
        self.assertEqual(data["task_type"], "create content")
        self.assertEqual(len(data["evaluation"]["dimensions"]), 15)
        self.assertEqual(data["synthetic_dataset"]["dataset_size"], 5)
        self.assertEqual(len(data["synthetic_dataset"]["test_cases"]), 5)
        self.assertEqual(len(data["synthetic_datasets"]), 1)
        self.assertIn("improved_prompt", data)
        self.assertIn("comparison", data)

        # Verify DB persistence
        eval_id = data["id"]
        eval_obj = PromptEvaluation.objects.get(pk=eval_id)
        self.assertEqual(eval_obj.synthetic_dataset.dataset_size, 5)
        self.assertEqual(eval_obj.synthetic_dataset.test_cases.count(), 5)

        # Test GET details
        detail_res = self.client.get(f"/api/evaluations/{eval_id}/")
        self.assertEqual(detail_res.status_code, status.HTTP_200_OK)

        # Test Export Excel
        excel_res = self.client.get(f"/api/evaluations/{eval_id}/export-excel/")
        self.assertEqual(excel_res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            excel_res["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    def test_evaluate_api_persists_multiple_datasets(self):
        payload = {
            "department": "software",
            "task_type": "create content",
            "prompt": "Create technical documentation for a JWT authentication system using Node.js and Express.",
            "dataset_size": 5,
            "num_datasets": 3
        }
        response = self.client.post("/api/evaluate/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(len(data["synthetic_datasets"]), 3)
        self.assertEqual([d["dataset_index"] for d in data["synthetic_datasets"]], [1, 2, 3])

        eval_obj = PromptEvaluation.objects.get(pk=data["id"])
        self.assertEqual(eval_obj.datasets.count(), 3)
        self.assertEqual(eval_obj.synthetic_dataset.dataset_index, 1)
        self.assertEqual(SyntheticTestCase.objects.filter(dataset__evaluation=eval_obj).count(), 15)

    def test_evaluate_api_missing_fields(self):
        response = self.client.post("/api/evaluate/", {"prompt": "test"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("details", data)
        self.assertIn("department", data["details"])
        self.assertIn("task_type", data["details"])
