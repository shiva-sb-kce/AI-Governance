import uuid
from copy import deepcopy
from datetime import datetime, timezone

from models.schemas import (
    ApprovalRequest,
    ApprovalStatus
)


class ApprovalManager:

    def __init__(self):
        self._requests = {}

    # =========================================
    # CREATE APPROVAL
    # =========================================

    def create_request(
        self,
        request_id,
        action,
        resource,
        risk_score,
        risk_level,
        reason,
        agent_id=None,
        parameters=None
    ):

        approval_id = (
            f"APR-{uuid.uuid4().hex[:8].upper()}"
        )

        approval = ApprovalRequest(
            approval_id=approval_id,

            request_id=request_id,

            action=action,

            resource=resource,

            risk_score=risk_score,

            risk_level=risk_level,

            reason=reason,

            # ---------------------------------
            # Bind approval to agent
            # ---------------------------------

            agent_id=agent_id,

            # ---------------------------------
            # Store immutable snapshot of params
            # ---------------------------------

            parameters=deepcopy(
                parameters or {}
            ),

            status=ApprovalStatus.PENDING
        )

        self._requests[approval_id] = approval

        return approval

    # =========================================
    # GET APPROVAL
    # =========================================

    def get_request(
        self,
        approval_id
    ):

        return self._requests.get(
            approval_id
        )

    # =========================================
    # CHECK EXACT ACTION BINDING
    # =========================================

    def matches_request(
        self,
        approval_id,
        request_id,
        action,
        resource,
        agent_id=None,
        parameters=None
    ):

        approval = self.get_request(
            approval_id
        )

        if approval is None:
            return False

        # ---------------------------------
        # Request identity
        # ---------------------------------

        if approval.request_id != request_id:
            return False

        # ---------------------------------
        # Tool/action
        # ---------------------------------

        if approval.action != action:
            return False

        # ---------------------------------
        # Resource
        # ---------------------------------

        if approval.resource != resource:
            return False

        # ---------------------------------
        # Agent identity
        # ---------------------------------

        if approval.agent_id != agent_id:
            return False

        # ---------------------------------
        # Exact parameter snapshot
        # ---------------------------------

        approved_parameters = (
            approval.parameters or {}
        )

        requested_parameters = (
            parameters or {}
        )

        if (
            approved_parameters
            != requested_parameters
        ):
            return False

        return True

    # =========================================
    # APPROVE
    # =========================================

    def approve(
        self,
        approval_id,
        approver_id
    ):

        approval = self.get_request(
            approval_id
        )

        if approval is None:
            return False

        if (
            approval.status
            != ApprovalStatus.PENDING
        ):
            return False

        approval.status = (
            ApprovalStatus.APPROVED
        )

        approval.approved_by = approver_id

        approval.approved_at = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        return True

    # =========================================
    # DENY
    # =========================================

    def deny(
        self,
        approval_id,
        approver_id
    ):

        approval = self.get_request(
            approval_id
        )

        if approval is None:
            return False

        if (
            approval.status
            != ApprovalStatus.PENDING
        ):
            return False

        approval.status = (
            ApprovalStatus.DENIED
        )

        approval.approved_by = approver_id

        approval.approved_at = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        return True

    # =========================================
    # VERIFY APPROVAL
    # =========================================

    def is_approved(
        self,
        approval_id,
        request_id,
        action,
        resource,
        agent_id=None,
        parameters=None
    ):

        approval = self.get_request(
            approval_id
        )

        if approval is None:
            return False

        # ---------------------------------
        # Must actually be approved
        # ---------------------------------

        if (
            approval.status
            != ApprovalStatus.APPROVED
        ):
            return False

        # ---------------------------------
        # Verify exact request binding
        # ---------------------------------

        return self.matches_request(
            approval_id=approval_id,
            request_id=request_id,
            action=action,
            resource=resource,
            agent_id=agent_id,
            parameters=parameters
        )

    # =========================================
    # LIST PENDING
    # =========================================

    def list_pending(self):

        return [
            approval
            for approval in self._requests.values()
            if (
                approval.status
                == ApprovalStatus.PENDING
            )
        ]