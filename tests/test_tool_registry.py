from agents.tool_registry import ToolRegistry


def test_registered_tool_exists():
    registry = ToolRegistry()

    assert registry.exists("read_file") is True


def test_unknown_tool_does_not_exist():
    registry = ToolRegistry()

    assert registry.exists("launch_nuclear_reactor") is False


def test_get_tool_configuration():
    registry = ToolRegistry()

    tool = registry.get_tool("delete_file")

    assert tool is not None
    assert tool["risk"] == 80


def test_tool_risk():
    registry = ToolRegistry()

    assert registry.get_risk(
        "execute_command"
    ) == 90


def test_unknown_tool_risk():
    registry = ToolRegistry()

    assert registry.get_risk(
        "unknown_tool"
    ) is None


def test_delete_requires_approval():
    registry = ToolRegistry()

    assert registry.requires_approval(
        "delete_file"
    ) is True


def test_read_does_not_require_approval():
    registry = ToolRegistry()

    assert registry.requires_approval(
        "read_file"
    ) is False


def test_delete_is_protected():
    registry = ToolRegistry()

    assert registry.is_protected(
        "delete_file"
    ) is True


def test_read_is_not_protected():
    registry = ToolRegistry()

    assert registry.is_protected(
        "read_file"
    ) is False