from agents.tool_registry import ToolRegistry
from models.schemas import ActionRequest
from security.action_validator import ActionValidator


def create_action(tool):
    return ActionRequest(
        action_id="ACT-001",
        request_id="REQ-001",
        agent_id="agent-001",
        tool=tool,
        resource="data.csv"
    )


def test_valid_read_action():
    validator = ActionValidator()
    registry = ToolRegistry()

    result = validator.validate(
        create_action("read_file"),
        registry
    )

    assert result["valid"] is True
    assert result["risk"] == 10


def test_unknown_tool():
    validator = ActionValidator()
    registry = ToolRegistry()

    result = validator.validate(
        create_action("unknown_tool"),
        registry
    )

    assert result["valid"] is False
    assert result["risk"] == 25


def test_delete_action_is_protected():
    validator = ActionValidator()
    registry = ToolRegistry()

    result = validator.validate(
        create_action("delete_file"),
        registry
    )

    assert result["valid"] is True
    assert result["risk"] == 80

    assert any(
        "protected" in reason
        for reason in result["reasons"]
    )


def test_execute_command_is_protected():
    validator = ActionValidator()
    registry = ToolRegistry()

    result = validator.validate(
        create_action("execute_command"),
        registry
    )

    assert result["valid"] is True
    assert result["risk"] == 90