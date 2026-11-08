"""Offline tests for deployment decisions and Security Hub response failures."""
import contextlib
import importlib.util
import io
import json
import shutil
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
LAB06 = ROOT / "labs/06-entra-id-detection-engineering-gated-content-pipeline"
LAB07 = ROOT / "labs/07-aws-guardduty-detection-response"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WhatIfTests(unittest.TestCase):
    def setUp(self):
        self.gate = load_module("evaluate_whatif", LAB06 / "scripts/evaluate_whatif.py")

    def evaluate(self, payload):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "whatif.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with patch.object(sys, "argv", ["evaluate_whatif.py", str(path)]):
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    return self.gate.main()

    def test_create_modify_and_nochange_pass(self):
        for kind in ["Create", "Modify", "NoChange"]:
            with self.subTest(kind=kind):
                self.assertEqual(self.evaluate({"changes": [{"resourceId": "/example", "changeType": kind}]}), 0)

    def test_delete_and_incomplete_predictions_block(self):
        for kind in ["Delete", "Ignore", "Unsupported", "Deploy", "Unexpected"]:
            with self.subTest(kind=kind):
                self.assertEqual(self.evaluate({"changes": [{"resourceId": "/example", "changeType": kind}]}), 1)

    def test_missing_or_malformed_changes_block(self):
        for payload in [[], {}, {"changes": {}}, {"changes": [None]}, {"changes": [{}]}]:
            with self.subTest(payload=payload):
                self.assertEqual(self.evaluate(payload), 1)

    def test_failed_operation_blocks_even_with_empty_changes(self):
        self.assertEqual(self.evaluate({"status": "Failed", "changes": []}), 1)
        self.assertEqual(self.evaluate({"error": {"code": "Denied"}, "changes": []}), 1)

    def test_successful_empty_changes_pass(self):
        self.assertEqual(self.evaluate({"status": "Succeeded", "changes": []}), 0)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.validator = load_module("validate_workflow_guardrails", LAB06 / "scripts/validate_workflow_guardrails.py")
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.lab = self.root / "labs/lab06"
        self.lab.mkdir(parents=True)
        shutil.copytree(ROOT / ".github", self.root / ".github")
        self.deploy = self.root / ".github/workflows/deploy-lab06-test.yml"

    def validate(self):
        with patch.object(sys, "argv", ["validate_workflow_guardrails.py", str(self.lab)]):
            with contextlib.redirect_stdout(io.StringIO()):
                return self.validator.main()

    def test_current_workflows_pass(self):
        self.assertEqual(self.validate(), 0)

    def test_automatic_deployment_trigger_is_rejected(self):
        self.deploy.write_text(self.deploy.read_text().replace("  workflow_dispatch:", "  workflow_dispatch:\n  push:"))
        self.assertEqual(self.validate(), 1)

    def test_missing_deployment_environment_is_rejected(self):
        self.deploy.write_text(self.deploy.read_text().replace("    environment: sentinel-test", "    # sentinel-test"))
        self.assertEqual(self.validate(), 1)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.builder = load_module("build_package", LAB06 / "scripts/build_package.py")
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.lab = Path(self.temporary.name) / "lab"
        self.manifest = self.lab / "pipeline/manifests/content-manifest.json"
        self.manifest.parent.mkdir(parents=True)
        (self.lab / "README.md").write_text("Example lab", encoding="utf-8")

    def build(self, files):
        self.manifest.write_text(json.dumps({"packageIncludes": files}), encoding="utf-8")
        with patch.object(sys, "argv", ["build_package.py", str(self.lab)]):
            with contextlib.redirect_stdout(io.StringIO()):
                return self.builder.main()

    def test_only_requested_files_are_packaged(self):
        self.assertEqual(self.build(["README.md"]), 0)
        archive = next((self.lab / "dist").glob("*.zip"))
        with ZipFile(archive) as package:
            self.assertEqual(package.namelist(), ["README.md"])
            self.assertEqual(package.read("README.md"), b"Example lab")

    def test_missing_input_leaves_no_partial_package(self):
        self.assertEqual(self.build(["README.md", "missing.md"]), 1)
        self.assertFalse((self.lab / "dist").exists())

    def test_outside_files_and_duplicates_are_rejected(self):
        outside = self.lab.parent / "private.txt"
        outside.write_text("local only", encoding="utf-8")
        for files in [["../private.txt"], [str(outside)], ["README.md", "README.md"], []]:
            with self.subTest(files=files):
                self.assertEqual(self.build(files), 1)
                self.assertFalse((self.lab / "dist").exists())


class LambdaTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        boto3 = types.SimpleNamespace(client=Mock(return_value=self.client))
        with patch.dict(sys.modules, {"boto3": boto3}):
            self.handler = load_module("response_handler", LAB07 / "automation/response/lambda_handler.py")
        self.event = {"detail": {"findings": [{"Id": "example-finding", "ProductArn": "example-product"}]}}

    def test_success_updates_exact_finding_and_reports_notified(self):
        self.client.batch_update_findings.return_value = {"UnprocessedFindings": []}
        with contextlib.redirect_stdout(io.StringIO()) as output:
            result = self.handler.lambda_handler(self.event, None)
        self.assertTrue(result["ok"])
        arguments = self.client.batch_update_findings.call_args.kwargs
        self.assertEqual(arguments["FindingIdentifiers"], self.event["detail"]["findings"])
        self.assertEqual(arguments["Workflow"], {"Status": "NOTIFIED"})
        self.assertEqual(json.loads(output.getvalue())["workflow_status"], "NOTIFIED")

    def test_rejected_update_raises_without_success_log(self):
        self.client.batch_update_findings.return_value = {"UnprocessedFindings": [{"ErrorCode": "AccessDenied"}]}
        with contextlib.redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(RuntimeError):
                self.handler.lambda_handler(self.event, None)
        self.assertEqual(output.getvalue(), "")

    def test_api_error_propagates(self):
        self.client.batch_update_findings.side_effect = RuntimeError("Throttled")
        with self.assertRaisesRegex(RuntimeError, "Throttled"):
            self.handler.lambda_handler(self.event, None)

    def test_empty_event_makes_no_api_call(self):
        with self.assertRaises(KeyError):
            self.handler.lambda_handler({}, None)
        self.client.batch_update_findings.assert_not_called()


if __name__ == "__main__":
    unittest.main()
