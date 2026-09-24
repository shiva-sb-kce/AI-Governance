import ast
from pathlib import Path


FORBIDDEN_IMPORTS = {
    "openai",
    "anthropic",
    "google",
    "google.generativeai",
    "google.genai",
    "langchain",
    "langchain_core",
    "langchain_community",
    "requests",
    "httpx",
    "urllib3",
}


GOVERNANCE_DIRS = [
    "core",
    "security",
    "approval",
    "agents",
    "models",
]


def get_import_root(node):

    if isinstance(node, ast.Import):

        return [
            alias.name.split(".")[0]
            for alias in node.names
        ]

    if isinstance(node, ast.ImportFrom):

        if node.module:
            return [
                node.module.split(".")[0]
            ]

    return []


def test_governance_core_has_no_external_ai_or_network_dependency():

    project_root = Path(__file__).resolve().parents[1]

    violations = []

    for directory in GOVERNANCE_DIRS:

        directory_path = (
            project_root / directory
        )

        if not directory_path.exists():
            continue

        for python_file in directory_path.rglob(
            "*.py"
        ):

            source = python_file.read_text(
                encoding="utf-8"
            )

            tree = ast.parse(
                source,
                filename=str(python_file)
            )

            for node in ast.walk(tree):

                imported_modules = (
                    get_import_root(node)
                )

                for module in imported_modules:

                    if module in {
                        item.split(".")[0]
                        for item in FORBIDDEN_IMPORTS
                    }:

                        violations.append(
                            f"{python_file}: "
                            f"{module}"
                        )

    assert violations == [], (
        "External AI/network dependency "
        "detected in governance core:\n"
        + "\n".join(violations)
    )