#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

FORBIDDEN_STRINGS = [
    "AZURE_CLIENT_SECRET",
    "client_secret",
    "notes/lab06-values.env",
    "lab06-values.env",
]


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def has_workflow_dispatch(doc: dict) -> bool:
    value = doc.get(True) if True in doc else doc.get("on")
    if isinstance(value, str):
        return value == "workflow_dispatch"
    if isinstance(value, list):
        return "workflow_dispatch" in value
    if isinstance(value, dict):
        return "workflow_dispatch" in value
    return False


def find_uses(node, target: str) -> bool:
    if isinstance(node, dict):
        return any(find_uses(v, target) for v in node.values())
    if isinstance(node, list):
        return any(find_uses(v, target) for v in node)
    return isinstance(node, str) and target in node


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_workflow_guardrails.py <lab_dir>")
        return 2

    lab_dir = Path(sys.argv[1]).resolve()
    repo_root = lab_dir.parents[1]
    workflows_dir = repo_root / ".github" / "workflows"
    errors: list[dict[str, str]] = []

    workflow_files = [
        workflows_dir / "lab06-oidc-smoke-test.yml",
        workflows_dir / "validate-lab06-content.yml",
        workflows_dir / "package-lab06-content.yml",
        workflows_dir / "deploy-lab06-test.yml",
    ]

    docs: dict[str, dict] = {}
    for wf in workflow_files:
        if not wf.exists():
            errors.append({"path": rel(wf, repo_root), "message": "Required workflow file is missing."})
            continue
        text = wf.read_text(encoding="utf-8", errors="ignore")
        for forbidden in FORBIDDEN_STRINGS:
            if forbidden in text:
                errors.append({"path": rel(wf, repo_root), "message": f"Forbidden string found in workflow: {forbidden}"})
        try:
            docs[wf.name] = yaml.safe_load(text) or {}
        except Exception as exc:
            errors.append({"path": rel(wf, repo_root), "message": f"Invalid YAML: {exc}"})

    for name in ["lab06-oidc-smoke-test.yml", "deploy-lab06-test.yml"]:
        doc = docs.get(name, {})
        triggers = doc.get(True, doc.get("on", {}))
        if not isinstance(triggers, dict) or set(triggers) != {"workflow_dispatch"}:
            errors.append({"path": f".github/workflows/{name}", "message": "Cloud workflows must be manual-only."})
        if doc.get("permissions", {}).get("id-token") != "write" or not find_uses(doc, "azure/login@v2"):
            errors.append({"path": f".github/workflows/{name}", "message": "Cloud workflows must use Azure OIDC login."})
        for job in doc.get("jobs", {}).values():
            environment = job.get("environment")
            if isinstance(environment, dict):
                environment = environment.get("name")
            if environment != "sentinel-test":
                errors.append({"path": f".github/workflows/{name}", "message": "Cloud jobs must use the sentinel-test environment."})

    smoke = docs.get("lab06-oidc-smoke-test.yml", {})
    if smoke:
        if not has_workflow_dispatch(smoke):
            errors.append({"path": ".github/workflows/lab06-oidc-smoke-test.yml", "message": "Smoke-test workflow must support workflow_dispatch."})
        permissions = smoke.get("permissions", {})
        if permissions.get("id-token") != "write":
            errors.append({"path": ".github/workflows/lab06-oidc-smoke-test.yml", "message": "Smoke-test workflow must request permissions.id-token: write."})
        if not find_uses(smoke, "azure/login@v2"):
            errors.append({"path": ".github/workflows/lab06-oidc-smoke-test.yml", "message": "Smoke-test workflow must use azure/login@v2."})
        if not find_uses(smoke, "sentinel-test"):
            errors.append({"path": ".github/workflows/lab06-oidc-smoke-test.yml", "message": "Smoke-test workflow must reference the sentinel-test environment."})
        if not find_uses(smoke, "actions/upload-artifact"):
            errors.append({"path": ".github/workflows/lab06-oidc-smoke-test.yml", "message": "Smoke-test workflow must upload an artifact."})

    validate = docs.get("validate-lab06-content.yml", {})
    if validate:
        for expected in [
            "validate_repo.py",
            "validate_deployable_json.py",
            "validate_detection_metadata.py",
            "validate_workflow_guardrails.py",
            "validate_readme_evidence.py",
        ]:
            if not find_uses(validate, expected):
                errors.append({"path": ".github/workflows/validate-lab06-content.yml", "message": f"Validation workflow must run {expected}."})

    package = docs.get("package-lab06-content.yml", {})
    if package:
        if not find_uses(package, "build_package.py"):
            errors.append({"path": ".github/workflows/package-lab06-content.yml", "message": "Package workflow must run build_package.py."})
        if not find_uses(package, "actions/upload-artifact"):
            errors.append({"path": ".github/workflows/package-lab06-content.yml", "message": "Package workflow must upload the dist artifact."})

    if errors:
        print("Workflow guardrail validation failed.")
        print(json.dumps({"errors": errors}, indent=2))
        return 1

    print("Workflow guardrail validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
