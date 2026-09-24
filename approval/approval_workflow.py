from agents.executor import SecureExecutor
from approval.approval_manager import ApprovalManager
from audit.audit_logger import AuditLogger

from models.schemas import Decision


class ApprovalWorkflow:

    def __init__(
        self,
        approval_manager=None,
        executor=None,
        audit_logger=None
    ):
        self.approval_manager = (
            approval_manager
            or ApprovalManager()
        )

        self.executor = (
            executor
            or SecureExecutor()
        )

        self.audit_logger = (
            audit_logger
            or AuditLogger()
        )

    # ==================================================
    # CREATE APPROVAL
    # ==================================================

    def create_approval(
        self,
        governance_result,
        action_request
    ):

        if governance_result.decision != Decision.APPROVAL:
            return None

        approval = (
            self.approval_manager.create_request(
                request_id=action_request.request_id,
                action=action_request.tool,
                resource=action_request.resource,
                risk_score=governance_result.risk_score,
                risk_level=governance_result.risk_level,
                reason="; ".join(
                    governance_result.reasons
                ),
                agent_id=action_request.agent_id,
                parameters=action_request.parameters,
            )
        )

        self.audit_logger.log(
            event_type="APPROVAL_CREATED",
            request_id=action_request.request_id,
            decision="APPROVAL",
            entity_type="agent",
            entity_id=action_request.agent_id,
            action=action_request.tool,
            resource=action_request.resource,
            risk_score=governance_result.risk_score,
            risk_level=(
                governance_result.risk_level.value
            ),
            approval_id=approval.approval_id,
            reasons=governance_result.reasons
        )

        return approval

    # ==================================================
    # APPROVE AND EXECUTE
    # ==================================================

    def approve_and_execute(
        self,
        approval_id,
        approver_id,
        action_request,
        governance_result
    ):

        approval = (
            self.approval_manager.get_request(
                approval_id
            )
        )

        if approval is None:

            self.audit_logger.log(
                event_type="APPROVAL_FAILURE",
                request_id=action_request.request_id,
                decision="BLOCK",
                entity_type="agent",
                entity_id=action_request.agent_id,
                action=action_request.tool,
                resource=action_request.resource,
                approval_id=approval_id,
                execution_status="NOT_EXECUTED",
                reasons=[
                    "Approval does not exist."
                ]
            )

            return {
                "executed": False,
                "status": "BLOCKED",
                "reason": "Approval does not exist."
            }

        # ----------------------------------------------
        # Verify exact approved action BEFORE execution
        # ----------------------------------------------

        if (
            approval.request_id
            != action_request.request_id
            or approval.action
            != action_request.tool
            or approval.resource
            != action_request.resource
            or approval.agent_id
            != action_request.agent_id
            or approval.parameters
            != action_request.parameters
        ):

            self.audit_logger.log(
                event_type="APPROVAL_MISMATCH",
                request_id=action_request.request_id,
                decision="BLOCK",
                entity_type="agent",
                entity_id=action_request.agent_id,
                action=action_request.tool,
                resource=action_request.resource,
                approval_id=approval_id,
                execution_status="NOT_EXECUTED",
                reasons=[
                    "Approved action does not match "
                    "the submitted action."
                ]
            )

            return {
                "executed": False,
                "status": "BLOCKED",
                "reason": (
                    "Approved action does not match "
                    "the submitted action."
                )
            }

        # ----------------------------------------------
        # Grant approval
        # ----------------------------------------------

        approved = self.approval_manager.approve(
            approval_id,
            approver_id
        )

        if not approved:

            self.audit_logger.log(
                event_type="APPROVAL_FAILURE",
                request_id=action_request.request_id,
                decision="BLOCK",
                entity_type="agent",
                entity_id=action_request.agent_id,
                action=action_request.tool,
                resource=action_request.resource,
                approval_id=approval_id,
                execution_status="NOT_EXECUTED",
                reasons=[
                    "Approval could not be granted."
                ]
            )

            return {
                "executed": False,
                "status": "BLOCKED",
                "reason": (
                    "Approval could not be granted."
                )
            }

        # ----------------------------------------------
        # Convert APPROVAL -> ALLOW
        # ----------------------------------------------

        governance_result.decision = Decision.ALLOW

        execution_result = self.executor.execute(
            action_request,
            governance_result
        )

        self.audit_logger.log(
            event_type="EXECUTION",
            request_id=action_request.request_id,
            decision="ALLOW",
            entity_type="agent",
            entity_id=action_request.agent_id,
            action=action_request.tool,
            resource=action_request.resource,
            risk_score=governance_result.risk_score,
            risk_level=(
                governance_result.risk_level.value
            ),
            approval_id=approval_id,
            execution_status=(
                execution_result.get("status")
            ),
            reasons=[
                "Human approval verified.",
                "Action authorized for execution."
            ]
        )

        return execution_result

    # ==================================================
    # DENY APPROVAL
    # ==================================================

    def deny(
        self,
        approval_id,
        approver_id
    ):

        approval = (
            self.approval_manager.get_request(
                approval_id
            )
        )

        if approval is None:

            return {
                "executed": False,
                "status": "BLOCKED",
                "decision": "BLOCK",
                "reason": (
                    "Approval request not found."
                )
            }

        # ----------------------------------------------
        # Approval must still be pending
        # ----------------------------------------------

        if approval.status.value != "PENDING":

            return {
                "executed": False,
                "status": "BLOCKED",
                "decision": "BLOCK",
                "reason": (
                    "Approval request is no longer pending."
                )
            }

        denied = self.approval_manager.deny(
            approval_id,
            approver_id
        )

        if not denied:

            return {
                "executed": False,
                "status": "BLOCKED",
                "decision": "BLOCK",
                "reason": (
                    "Approval could not be denied."
                )
            }

        # ----------------------------------------------
        # Audit denial
        # ----------------------------------------------

        self.audit_logger.log(
            event_type="APPROVAL_DENIED",
            request_id=approval.request_id,
            decision="BLOCK",
            entity_type="agent",
            entity_id=approval.agent_id,
            action=approval.action,
            resource=approval.resource,
            risk_score=approval.risk_score,
            risk_level=approval.risk_level.value,
            approval_id=approval_id,
            execution_status="NOT_EXECUTED",
            reasons=[
                "Human approval denied.",
                "Action was not executed."
            ],
            metadata={
                "approver_id": approver_id
            }
        )

        return {
            "executed": False,
            "status": "DENIED",
            "decision": "BLOCK",
            "approval_id": approval_id,
            "request_id": approval.request_id,
            "approver_id": approver_id,
            "reason": (
                "Human approval denied. "
                "Action was not executed."
            )
        }