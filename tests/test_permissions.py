from core.permission_engine import PermissionEngine


def test_user_can_read_file():
    engine = PermissionEngine()

    result = engine.check_permission(
        role="USER",
        action="read_file"
    )

    assert result.permission == "ALLOW"
    assert result.allowed is True
    assert result.requires_approval is False


def test_user_cannot_delete_file():
    engine = PermissionEngine()

    result = engine.check_permission(
        role="USER",
        action="delete_file"
    )

    assert result.permission == "DENY"
    assert result.allowed is False
    assert result.requires_approval is False


def test_agent_can_read_file():
    engine = PermissionEngine()

    result = engine.check_permission(
        role="AGENT",
        action="read_file"
    )

    assert result.permission == "ALLOW"
    assert result.allowed is True


def test_agent_cannot_execute_command():
    engine = PermissionEngine()

    result = engine.check_permission(
        role="AGENT",
        action="execute_command"
    )

    assert result.permission == "DENY"
    assert result.allowed is False


def test_admin_delete_requires_approval():
    engine = PermissionEngine()

    result = engine.check_permission(
        role="ADMIN",
        action="delete_file"
    )

    assert result.permission == "APPROVAL"
    assert result.allowed is False
    assert result.requires_approval is True


def test_unknown_role_is_denied():
    engine = PermissionEngine()

    result = engine.check_permission(
        role="HACKER",
        action="read_file"
    )

    assert result.permission == "DENY"
    assert result.allowed is False


def test_unknown_action_is_denied():
    engine = PermissionEngine()

    result = engine.check_permission(
        role="USER",
        action="format_everything"
    )

    assert result.permission == "DENY"
    assert result.allowed is False