import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

TOOLS_FILE = BASE_DIR / "config" / "tools.json"


class ToolRegistry:

    def __init__(self):
        self.tools = self._load_tools()

    @staticmethod
    def _load_tools():
        with open(TOOLS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    def exists(self, tool_name):
        return tool_name in self.tools

    def get_tool(self, tool_name):
        return self.tools.get(tool_name)

    def get_risk(self, tool_name):
        tool = self.get_tool(tool_name)

        if tool is None:
            return None

        return tool.get("risk", 0)

    def requires_approval(self, tool_name):
        tool = self.get_tool(tool_name)

        if tool is None:
            return False

        return tool.get(
            "approval_required",
            False
        )

    def is_protected(self, tool_name):
        tool = self.get_tool(tool_name)

        if tool is None:
            return False

        return tool.get(
            "protected",
            False
        )