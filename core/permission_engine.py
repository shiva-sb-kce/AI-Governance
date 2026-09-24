import json
from pathlib import Path

from models.schemas import PermissionResult


BASE_DIR = Path(__file__).resolve().parents[1]

ROLES_FILE = BASE_DIR / "config" / "roles.json"
TOOLS_FILE = BASE_DIR / "config" / "tools.json"


class PermissionEngine:
    def __init__(self):
        self.roles = self._load_json(ROLES_FILE)
        self.tools = self._load_json(TOOLS_FILE)

    @staticmethod
    def _load_json(path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def check_permission(
        self,
        role,
        action,
        resource=None
    ):
        role = role.upper()

        if role not in self.roles:
            return PermissionResult(
                allowed=False,
                requires_approval=False,
                permission="DENY",
                role=role,
                action=action,
                resource=resource,
                reasons=[
                    f"Unknown role: {role}"
                ]
            )

        if action not in self.tools:
            return PermissionResult(
                allowed=False,
                requires_approval=False,
                permission="DENY",
                role=role,
                action=action,
                resource=resource,
                reasons=[
                    f"Unknown tool/action: {action}"
                ]
            )

        role_permissions = self.roles[role]
        tool_config = self.tools[action]

        required_permission = tool_config.get(
            "required_permission"
        )

        has_permission = role_permissions.get(
            required_permission,
            False
        )

        if not has_permission:
            return PermissionResult(
                allowed=False,
                requires_approval=False,
                permission="DENY",
                role=role,
                action=action,
                resource=resource,
                reasons=[
                    f"Role '{role}' does not have "
                    f"permission '{required_permission}'."
                ]
            )

        approval_required = tool_config.get(
            "approval_required",
            False
        )

        if approval_required:
            return PermissionResult(
                allowed=False,
                requires_approval=True,
                permission="APPROVAL",
                role=role,
                action=action,
                resource=resource,
                reasons=[
                    f"Action '{action}' requires "
                    "human approval."
                ]
            )

        return PermissionResult(
            allowed=True,
            requires_approval=False,
            permission="ALLOW",
            role=role,
            action=action,
            resource=resource,
            reasons=[
                f"Role '{role}' is authorized "
                f"to perform '{action}'."
            ]
        )