from models.schemas import ActionRequest


class ActionValidator:

    def validate(
        self,
        action_request: ActionRequest,
        tool_registry
    ):
        reasons = []

        # -----------------------------
        # Validate tool existence
        # -----------------------------

        if not tool_registry.exists(
            action_request.tool
        ):
            reasons.append(
                f"Unknown tool: "
                f"{action_request.tool}"
            )

            return {
                "valid": False,
                "reasons": reasons,
                "risk": 25
            }

        tool = tool_registry.get_tool(
            action_request.tool
        )

        # -----------------------------
        # Protected tool
        # -----------------------------

        if tool.get("protected", False):
            reasons.append(
                f"Tool '{action_request.tool}' "
                "accesses a protected capability."
            )

        # -----------------------------
        # Approval requirement
        # -----------------------------

        if tool.get(
            "approval_required",
            False
        ):
            reasons.append(
                f"Tool '{action_request.tool}' "
                "requires governance approval."
            )

        return {
            "valid": True,
            "reasons": reasons,
            "risk": tool.get("risk", 0)
        }