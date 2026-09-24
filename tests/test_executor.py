from agents.executor import SecureExecutor

from models.schemas import (
    ActionRequest,
    Decision,
    GovernanceResult,
    RiskLevel
)


def make_result(decision):
    return GovernanceResult(
        request_id="REQ-001",
        decision=decision,
        risk_score=0,
        risk_level=RiskLevel.LOW
    )


def make_action(
    tool,
    resource="test.txt",
    parameters=None
):
    return ActionRequest(
        action_id="ACT-001",
        request_id="REQ-001",
        agent_id="agent-001",
        tool=tool,
        resource=resource,
        parameters=parameters or {}
    )


def test_blocked_action_never_executes(tmp_path):
    executor = SecureExecutor(
        sandbox_dir=tmp_path
    )

    action = make_action(
        "write_file"
    )

    result = executor.execute(
        action,
        make_result(Decision.BLOCK)
    )

    assert result["executed"] is False
    assert result["status"] == "BLOCKED"

    assert not (
        tmp_path / "test.txt"
    ).exists()


def test_approval_action_does_not_execute(tmp_path):
    executor = SecureExecutor(
        sandbox_dir=tmp_path
    )

    action = make_action(
        "write_file"
    )

    result = executor.execute(
        action,
        make_result(Decision.APPROVAL)
    )

    assert result["executed"] is False
    assert result["status"] == "BLOCKED"

    assert not (
        tmp_path / "test.txt"
    ).exists()


def test_allowed_write_executes(tmp_path):
    executor = SecureExecutor(
        sandbox_dir=tmp_path
    )

    action = make_action(
        "write_file",
        parameters={
            "content": "Hello Governance"
        }
    )

    result = executor.execute(
        action,
        make_result(Decision.ALLOW)
    )

    assert result["executed"] is True
    assert result["status"] == "SUCCESS"

    file_path = tmp_path / "test.txt"

    assert file_path.exists()
    assert file_path.read_text(
        encoding="utf-8"
    ) == "Hello Governance"


def test_allowed_read_executes(tmp_path):
    file_path = tmp_path / "test.txt"

    file_path.write_text(
        "Offline AI Governance",
        encoding="utf-8"
    )

    executor = SecureExecutor(
        sandbox_dir=tmp_path
    )

    action = make_action(
        "read_file"
    )

    result = executor.execute(
        action,
        make_result(Decision.ALLOW)
    )

    assert result["executed"] is True
    assert result["result"] == (
        "Offline AI Governance"
    )


def test_unknown_tool_does_not_execute(tmp_path):
    executor = SecureExecutor(
        sandbox_dir=tmp_path
    )

    action = make_action(
        "execute_command"
    )

    result = executor.execute(
        action,
        make_result(Decision.ALLOW)
    )

    assert result["executed"] is False
    assert result["status"] == "BLOCKED"


def test_path_traversal_is_blocked(tmp_path):
    executor = SecureExecutor(
        sandbox_dir=tmp_path
    )

    action = make_action(
        "write_file",
        resource="../outside.txt",
        parameters={
            "content": "malicious"
        }
    )

    result = executor.execute(
        action,
        make_result(Decision.ALLOW)
    )

    assert result["executed"] is False
    assert result["status"] == "BLOCKED"