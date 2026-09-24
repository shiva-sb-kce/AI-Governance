import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def load_json(relative_path):
    path = BASE_DIR / relative_path

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def test_roles():
    roles = load_json("config/roles.json")

    assert "USER" in roles
    assert "AGENT" in roles
    assert "ADMIN" in roles
    assert "SYSTEM" in roles


def test_tools():
    tools = load_json("config/tools.json")

    assert "read_file" in tools
    assert "delete_file" in tools
    assert "execute_command" in tools


def test_policies():
    policies = load_json("policies/policies.json")

    assert "POLICY-001" in policies
    assert "POLICY-004" in policies
    assert "POLICY-006" in policies