from typing import Any, Dict

from core.governance_engine import GovernanceEngine

from agents.tool_registry import ToolRegistry
from security.action_validator import ActionValidator

from approval.approval_workflow import ApprovalWorkflow

from services.audit_service import AuditService

from models.schemas import (
    GovernanceRequest,
    ActionRequest,
    Decision,
    EntityType,
    ApprovalStatus,
)


class GovernanceGateway:

    def __init__(
        self,
        governance_engine=None,
        tool_registry=None,
        action_validator=None,
        approval_workflow=None,
        audit_service=None,
    ):

        # ==================================================
        # CORE SERVICES
        # ==================================================

        self.engine = (
            governance_engine
            or GovernanceEngine()
        )

        self.tool_registry = (
            tool_registry
            or ToolRegistry()
        )

        self.action_validator = (
            action_validator
            or ActionValidator()
        )

        self.approval_workflow = (
            approval_workflow
            or ApprovalWorkflow()
        )

        # ==================================================
        # AUDIT SERVICE
        # ==================================================

        self.audit_service = (
            audit_service
            or AuditService()
        )

        # ==================================================
        # PENDING ACTION APPROVALS
        # ==================================================

        self.pending_actions: Dict[
            str, Dict[str, Any]
        ] = {}

        # ==================================================
        # PENDING QWEN APPROVALS
        #
        # These approvals happen BEFORE Qwen receives
        # the user's request.
        # ==================================================

        self.pending_qwen: Dict[
            str, Dict[str, Any]
        ] = {}

    # ==================================================
    # GENERIC GOVERNANCE
    # ==================================================

    def process(
        self,
        request: GovernanceRequest
    ):

        result = self.engine.evaluate(
            request
        )

        # --------------------------------------------------
        # AUDIT GOVERNANCE DECISION
        # --------------------------------------------------

        self.audit_service.log_event(
            request_id=request.request_id,
            entity_type=request.entity_type,
            entity_id=request.user_id,
            action=request.action,
            risk_score=result.risk_score,
            risk_level=result.risk_level,
            decision=result.decision,
            threats=result.threats,
            policies=result.violated_policies,
            approval_status=result.approval_status,
            details={
                "role": request.role,
                "resource": request.resource,
                "parameters": request.parameters,
            }
        )

        return result

    # ==================================================
    # PRE-QWEN GOVERNANCE GATE
    #
    # USER
    #   ↓
    # GOVERNANCE
    #   ↓
    # LOW      → ALLOW
    # MEDIUM   → APPROVAL / PENDING
    # HIGH     → BLOCK
    #   ↓
    # QWEN3:8B
    # ==================================================

    def process_qwen_request(
        self,
        request_id: str,
        user_id: str,
        role: str,
        prompt: str,
        parameters=None,
    ):

        if parameters is None:
            parameters = {}

        # --------------------------------------------------
        # Build governance request for Qwen inference
        # --------------------------------------------------

        governance_request = GovernanceRequest(
            request_id=request_id,
            user_id=user_id,
            role=role,
            entity_type=EntityType.SLM,
            prompt=prompt,
            action=None,
            resource="qwen3:8b",
            parameters=parameters,
            context={
                "source": "PRE_QWEN_GATE",
                "model": "qwen3:8b",
            },
        )

        # --------------------------------------------------
        # Run existing deterministic governance engine
        # --------------------------------------------------

        result = self.engine.evaluate(
            governance_request
        )

        # ==================================================
        # HIGH RISK / BLOCK
        # ==================================================

        if result.decision == Decision.BLOCK:

            self.audit_service.log_event(
                request_id=request_id,
                entity_type=EntityType.SLM,
                entity_id="qwen3:8b",
                action="qwen_inference",
                risk_score=result.risk_score,
                risk_level=result.risk_level,
                decision=Decision.BLOCK,
                threats=result.threats,
                policies=result.violated_policies,
                approval_status=(
                    result.approval_status
                ),
                details={
                    "stage": "PRE_QWEN_GOVERNANCE",
                    "prompt": prompt,
                    "role": role,
                    "user_id": user_id,
                    "model": "qwen3:8b",
                    "qwen_executed": False,
                    "reason": result.reasons,
                }
            )

            return {
                "status": "BLOCKED",
                "allowed": False,
                "qwen_allowed": False,
                "executed": False,
                "decision": "BLOCK",
                "request_id": request_id,
                "risk_score": result.risk_score,
                "risk_level": result.risk_level.value,
                "threats": result.threats,
                "violated_policies": (
                    result.violated_policies
                ),
                "reasons": result.reasons,
            }

        # ==================================================
        # MEDIUM RISK / APPROVAL
        # ==================================================

        if result.decision == Decision.APPROVAL:

            # ----------------------------------------------
            # Generate an approval identifier.
            #
            # Qwen itself must NOT receive the prompt yet.
            # ----------------------------------------------

            approval_id = (
                f"QWEN-APPROVAL-{request_id}"
            )

            self.pending_qwen[
                approval_id
            ] = {
                "request_id": request_id,
                "user_id": user_id,
                "role": role,
                "prompt": prompt,
                "parameters": parameters,
                "governance_result": result,
            }

            # ----------------------------------------------
            # Audit pending Qwen approval
            # ----------------------------------------------

            self.audit_service.log_event(
                request_id=request_id,
                entity_type=EntityType.SLM,
                entity_id="qwen3:8b",
                action="qwen_inference",
                risk_score=result.risk_score,
                risk_level=result.risk_level,
                decision=Decision.APPROVAL,
                threats=result.threats,
                policies=result.violated_policies,
                approval_status=ApprovalStatus.PENDING,
                details={
                    "stage": "PRE_QWEN_PENDING_APPROVAL",
                    "approval_id": approval_id,
                    "prompt": prompt,
                    "role": role,
                    "user_id": user_id,
                    "model": "qwen3:8b",
                    "qwen_executed": False,
                    "reasons": result.reasons,
                }
            )

            return {
                "status": "PENDING_APPROVAL",
                "allowed": False,
                "qwen_allowed": False,
                "executed": False,
                "decision": "APPROVAL",
                "approval_id": approval_id,
                "request_id": request_id,
                "risk_score": result.risk_score,
                "risk_level": result.risk_level.value,
                "threats": result.threats,
                "violated_policies": (
                    result.violated_policies
                ),
                "reasons": result.reasons,
            }

        # ==================================================
        # LOW RISK / ALLOW
        # ==================================================

        self.audit_service.log_event(
            request_id=request_id,
            entity_type=EntityType.SLM,
            entity_id="qwen3:8b",
            action="qwen_inference",
            risk_score=result.risk_score,
            risk_level=result.risk_level,
            decision=Decision.ALLOW,
            threats=result.threats,
            policies=result.violated_policies,
            approval_status=(
                result.approval_status
            ),
            details={
                "stage": "PRE_QWEN_GOVERNANCE",
                "prompt": prompt,
                "role": role,
                "user_id": user_id,
                "model": "qwen3:8b",
                "qwen_executed": False,
                "governance": "ALLOWED",
                "reasons": result.reasons,
            }
        )

        return {
            "status": "ALLOWED",
            "allowed": True,
            "qwen_allowed": True,
            "executed": False,
            "decision": "ALLOW",
            "request_id": request_id,
            "risk_score": result.risk_score,
            "risk_level": result.risk_level.value,
            "threats": result.threats,
            "violated_policies": (
                result.violated_policies
            ),
            "reasons": result.reasons,
        }

    # ==================================================
    # APPROVE PRE-QWEN REQUEST
    #
    # IMPORTANT:
    # Approval here means:
    #
    # "The user has permitted Qwen to process this
    #  particular request."
    #
    # It does NOT automatically execute a tool action.
    # ==================================================

    def approve_qwen_request(
        self,
        approval_id: str,
        approver_id: str,
    ):

        pending = self.pending_qwen.get(
            approval_id
        )

        if pending is None:

            return {
                "status": "BLOCKED",
                "allowed": False,
                "qwen_allowed": False,
                "executed": False,
                "decision": "BLOCK",
                "approval_id": approval_id,
                "reason": (
                    "Qwen approval request not found."
                ),
            }

        governance_result = pending[
            "governance_result"
        ]

        # --------------------------------------------------
        # HIGH-RISK SAFETY RECHECK
        # --------------------------------------------------

        if (
            governance_result.risk_score
            >= 61
        ):

            self.pending_qwen.pop(
                approval_id,
                None
            )

            self.audit_service.log_event(
                request_id=pending[
                    "request_id"
                ],
                entity_type=EntityType.SLM,
                entity_id="qwen3:8b",
                action="qwen_inference",
                risk_score=(
                    governance_result.risk_score
                ),
                risk_level=(
                    governance_result.risk_level
                ),
                decision=Decision.BLOCK,
                threats=(
                    governance_result.threats
                ),
                policies=(
                    governance_result
                    .violated_policies
                ),
                approval_status=(
                    ApprovalStatus.DENIED
                ),
                details={
                    "stage": "PRE_QWEN_APPROVAL_RECHECK",
                    "approval_id": approval_id,
                    "approver_id": approver_id,
                    "qwen_executed": False,
                    "reason": (
                        "High-risk request cannot "
                        "be approved."
                    ),
                }
            )

            return {
                "status": "BLOCKED",
                "allowed": False,
                "qwen_allowed": False,
                "executed": False,
                "decision": "BLOCK",
                "approval_id": approval_id,
                "reason": (
                    "High-risk request cannot "
                    "be approved."
                ),
            }

        # --------------------------------------------------
        # AUDIT APPROVAL
        # --------------------------------------------------

        self.audit_service.log_event(
            request_id=pending[
                "request_id"
            ],
            entity_type=EntityType.SLM,
            entity_id="qwen3:8b",
            action="qwen_inference",
            risk_score=(
                governance_result.risk_score
            ),
            risk_level=(
                governance_result.risk_level
            ),
            decision=Decision.ALLOW,
            threats=(
                governance_result.threats
            ),
            policies=(
                governance_result
                .violated_policies
            ),
            approval_status=(
                ApprovalStatus.APPROVED
            ),
            details={
                "stage": "PRE_QWEN_APPROVED",
                "approval_id": approval_id,
                "approver_id": approver_id,
                "prompt": pending["prompt"],
                "role": pending["role"],
                "user_id": pending["user_id"],
                "model": "qwen3:8b",
                "qwen_executed": False,
            }
        )

        # --------------------------------------------------
        # Remove approval context.
        # The Qwen caller will now be allowed to invoke
        # the model using this approved request.
        # --------------------------------------------------

        self.pending_qwen.pop(
            approval_id,
            None
        )

        return {
            "status": "APPROVED",
            "allowed": True,
            "qwen_allowed": True,
            "executed": False,
            "decision": "ALLOW",
            "approval_id": approval_id,
            "request_id": pending[
                "request_id"
            ],
            "prompt": pending[
                "prompt"
            ],
        }

    # ==================================================
    # DENY PRE-QWEN REQUEST
    # ==================================================

    def deny_qwen_request(
        self,
        approval_id: str,
        approver_id: str,
    ):

        pending = self.pending_qwen.get(
            approval_id
        )

        if pending is None:

            return {
                "status": "BLOCKED",
                "allowed": False,
                "qwen_allowed": False,
                "executed": False,
                "decision": "BLOCK",
                "approval_id": approval_id,
                "reason": (
                    "Qwen approval request not found."
                ),
            }

        governance_result = pending[
            "governance_result"
        ]

        self.audit_service.log_event(
            request_id=pending[
                "request_id"
            ],
            entity_type=EntityType.SLM,
            entity_id="qwen3:8b",
            action="qwen_inference",
            risk_score=(
                governance_result.risk_score
            ),
            risk_level=(
                governance_result.risk_level
            ),
            decision=Decision.BLOCK,
            threats=(
                governance_result.threats
            ),
            policies=(
                governance_result
                .violated_policies
            ),
            approval_status=(
                ApprovalStatus.DENIED
            ),
            details={
                "stage": "PRE_QWEN_DENIED",
                "approval_id": approval_id,
                "approver_id": approver_id,
                "prompt": pending["prompt"],
                "role": pending["role"],
                "user_id": pending["user_id"],
                "model": "qwen3:8b",
                "qwen_executed": False,
            }
        )

        self.pending_qwen.pop(
            approval_id,
            None
        )

        return {
            "status": "BLOCKED",
            "allowed": False,
            "qwen_allowed": False,
            "executed": False,
            "decision": "BLOCK",
            "approval_id": approval_id,
            "reason": (
                "User denied permission "
                "for Qwen to process "
                "the request."
            ),
        }

    # ==================================================
    # GET PENDING QWEN APPROVALS
    # ==================================================

    def get_pending_qwen_approvals(self):

        approvals = []

        for (
            approval_id,
            pending
        ) in self.pending_qwen.items():

            governance_result = pending[
                "governance_result"
            ]

            approvals.append({

                "approval_id": approval_id,

                "request_id": pending[
                    "request_id"
                ],

                "user_id": pending[
                    "user_id"
                ],

                "role": pending[
                    "role"
                ],

                "model": "qwen3:8b",

                "action": "qwen_inference",

                "prompt": pending[
                    "prompt"
                ],

                "risk_score": (
                    governance_result.risk_score
                ),

                "risk_level": (
                    governance_result
                    .risk_level.value
                ),

                "reasons": (
                    governance_result.reasons
                ),

                "status": "PENDING",
            })

        return approvals

    # ==================================================
    # ACTION GOVERNANCE + EXECUTION
    # ==================================================

    def process_action(
        self,
        action_request,
        role="AGENT",
    ):

        # --------------------------------------------------
        # 1. TOOL VALIDATION
        # --------------------------------------------------

        validation = (
            self.action_validator.validate(
                action_request,
                self.tool_registry
            )
        )

        if not validation["valid"]:

            risk_score = validation.get(
                "risk",
                25
            )

            reasons = validation.get(
                "reasons",
                [
                    "Action validation failed."
                ]
            )

            self.audit_service.log_event(
                request_id=(
                    action_request.request_id
                ),
                entity_type=EntityType.AGENT,
                entity_id=(
                    action_request.agent_id
                ),
                action=action_request.tool,
                risk_score=risk_score,
                risk_level="HIGH",
                decision=Decision.BLOCK,
                threats=[],
                policies=[],
                approval_status=(
                    ApprovalStatus.NOT_REQUIRED
                ),
                details={
                    "resource": (
                        action_request.resource
                    ),
                    "parameters": (
                        action_request.parameters
                    ),
                    "stage": "ACTION_VALIDATION",
                    "reasons": reasons,
                    "executed": False,
                }
            )

            return {
                "status": "BLOCKED",
                "executed": False,
                "decision": "BLOCK",
                "request_id": (
                    action_request.request_id
                ),
                "risk_score": risk_score,
                "risk_level": "HIGH",
                "permission": "DENY",
                "threats": [],
                "reasons": reasons,
            }

        # --------------------------------------------------
        # 2. GOVERNANCE EVALUATION
        # --------------------------------------------------

        governance_result = (
            self.engine.evaluate_action(
                action_request,
                agent_role=role
            )
        )

        # --------------------------------------------------
        # 3. BLOCK
        # --------------------------------------------------

        if (
            governance_result.decision
            == Decision.BLOCK
        ):

            self.audit_service.log_event(
                request_id=(
                    action_request.request_id
                ),
                entity_type=EntityType.AGENT,
                entity_id=(
                    action_request.agent_id
                ),
                action=action_request.tool,
                risk_score=(
                    governance_result.risk_score
                ),
                risk_level=(
                    governance_result.risk_level
                ),
                decision=Decision.BLOCK,
                threats=(
                    governance_result.threats
                ),
                policies=(
                    governance_result.violated_policies
                ),
                approval_status=(
                    governance_result.approval_status
                ),
                details={
                    "resource": (
                        action_request.resource
                    ),
                    "parameters": (
                        action_request.parameters
                    ),
                    "stage": "GOVERNANCE",
                    "executed": False,
                }
            )

            return {
                "status": "BLOCKED",
                "executed": False,
                "decision": "BLOCK",
                "request_id": (
                    governance_result.request_id
                ),
                "risk_score": (
                    governance_result.risk_score
                ),
                "risk_level": (
                    governance_result
                    .risk_level.value
                ),
                "permission": (
                    governance_result.permission
                ),
                "threats": (
                    governance_result.threats
                ),
                "reasons": (
                    governance_result.reasons
                ),
            }

        # --------------------------------------------------
        # 4. APPROVAL REQUIRED
        # --------------------------------------------------

        if (
            governance_result.decision
            == Decision.APPROVAL
        ):

            approval = (
                self.approval_workflow
                .create_approval(
                    governance_result,
                    action_request
                )
            )

            if approval is None:

                self.audit_service.log_event(
                    request_id=(
                        action_request.request_id
                    ),
                    entity_type=EntityType.AGENT,
                    entity_id=(
                        action_request.agent_id
                    ),
                    action=action_request.tool,
                    risk_score=(
                        governance_result.risk_score
                    ),
                    risk_level=(
                        governance_result.risk_level
                    ),
                    decision=Decision.BLOCK,
                    threats=(
                        governance_result.threats
                    ),
                    policies=(
                        governance_result
                        .violated_policies
                    ),
                    approval_status=(
                        ApprovalStatus.NOT_REQUIRED
                    ),
                    details={
                        "stage": "APPROVAL_CREATION",
                        "error": (
                            "Approval creation failed."
                        ),
                        "executed": False,
                    }
                )

                return {
                    "status": "BLOCKED",
                    "executed": False,
                    "decision": "BLOCK",
                    "request_id": (
                        action_request.request_id
                    ),
                    "reasons": [
                        "Approval creation failed."
                    ],
                }

            # --------------------------------------------------
            # STORE EXACT ACTION CONTEXT
            # --------------------------------------------------

            self.pending_actions[
                approval.approval_id
            ] = {
                "action_request": action_request,
                "governance_result": (
                    governance_result
                ),
            }

            # --------------------------------------------------
            # AUDIT PENDING APPROVAL
            # --------------------------------------------------

            self.audit_service.log_event(
                request_id=(
                    action_request.request_id
                ),
                entity_type=EntityType.AGENT,
                entity_id=(
                    action_request.agent_id
                ),
                action=action_request.tool,
                risk_score=(
                    governance_result.risk_score
                ),
                risk_level=(
                    governance_result.risk_level
                ),
                decision=Decision.APPROVAL,
                threats=(
                    governance_result.threats
                ),
                policies=(
                    governance_result
                    .violated_policies
                ),
                approval_status=(
                    ApprovalStatus.PENDING
                ),
                details={
                    "approval_id": (
                        approval.approval_id
                    ),
                    "resource": (
                        action_request.resource
                    ),
                    "parameters": (
                        action_request.parameters
                    ),
                    "stage": "PENDING_APPROVAL",
                    "executed": False,
                }
            )

            return {
                "status": "PENDING_APPROVAL",
                "executed": False,
                "decision": "APPROVAL",

                "approval_id": (
                    approval.approval_id
                ),

                "request_id": (
                    governance_result.request_id
                ),

                "agent_id": (
                    action_request.agent_id
                ),

                "action": (
                    action_request.tool
                ),

                "resource": (
                    action_request.resource
                ),

                "parameters": (
                    action_request.parameters
                ),

                "risk_score": (
                    governance_result.risk_score
                ),

                "risk_level": (
                    governance_result
                    .risk_level.value
                ),

                "reasons": (
                    governance_result.reasons
                ),
            }

        # --------------------------------------------------
        # 5. ALLOW
        # --------------------------------------------------

        if (
            governance_result.decision
            == Decision.ALLOW
        ):

            execution_result = (
                self.approval_workflow
                .executor
                .execute(
                    action_request,
                    governance_result
                )
            )

            executed = execution_result.get(
                "executed",
                False
            )

            self.audit_service.log_event(
                request_id=(
                    action_request.request_id
                ),
                entity_type=EntityType.AGENT,
                entity_id=(
                    action_request.agent_id
                ),
                action=action_request.tool,
                risk_score=(
                    governance_result.risk_score
                ),
                risk_level=(
                    governance_result.risk_level
                ),
                decision=Decision.ALLOW,
                threats=(
                    governance_result.threats
                ),
                policies=(
                    governance_result
                    .violated_policies
                ),
                approval_status=(
                    governance_result.approval_status
                ),
                details={
                    "resource": (
                        action_request.resource
                    ),
                    "parameters": (
                        action_request.parameters
                    ),
                    "stage": "EXECUTION",
                    "execution_status": (
                        execution_result.get(
                            "status"
                        )
                    ),
                    "executed": executed,
                }
            )

            return {
                "status": (
                    execution_result.get(
                        "status"
                    )
                ),
                "executed": executed,
                "decision": "ALLOW",
                "request_id": (
                    governance_result.request_id
                ),
                "risk_score": (
                    governance_result.risk_score
                ),
                "risk_level": (
                    governance_result
                    .risk_level.value
                ),
                "result": (
                    execution_result.get(
                        "result"
                    )
                ),
                "reason": (
                    execution_result.get(
                        "reason"
                    )
                ),
            }

        # --------------------------------------------------
        # 6. DEFENSIVE FALLBACK
        # --------------------------------------------------

        self.audit_service.log_event(
            request_id=(
                action_request.request_id
            ),
            entity_type=EntityType.AGENT,
            entity_id=(
                action_request.agent_id
            ),
            action=action_request.tool,
            risk_score=0,
            risk_level="LOW",
            decision=Decision.BLOCK,
            threats=[],
            policies=[],
            approval_status=(
                ApprovalStatus.NOT_REQUIRED
            ),
            details={
                "stage": "DEFENSIVE_FALLBACK",
                "executed": False,
            }
        )

        return {
            "status": "BLOCKED",
            "executed": False,
            "decision": "BLOCK",
            "request_id": (
                action_request.request_id
            ),
            "reasons": [
                "Unknown governance decision."
            ],
        }

    # ==================================================
    # GET PENDING ACTION APPROVALS
    # ==================================================

    def get_pending_approvals(self):

        approvals = []

        for (
            approval_id,
            context
        ) in self.pending_actions.items():

            approval = (
                self.approval_workflow
                .approval_manager
                .get_request(
                    approval_id
                )
            )

            if approval is None:
                continue

            if approval.status.value != "PENDING":
                continue

            action_request = context[
                "action_request"
            ]

            governance_result = context[
                "governance_result"
            ]

            approvals.append({

                "approval_id": (
                    approval.approval_id
                ),

                "request_id": (
                    approval.request_id
                ),

                "agent_id": (
                    action_request.agent_id
                ),

                "action": (
                    action_request.tool
                ),

                "resource": (
                    action_request.resource
                ),

                "parameters": (
                    action_request.parameters
                ),

                "risk_score": (
                    governance_result.risk_score
                ),

                "risk_level": (
                    governance_result
                    .risk_level.value
                ),

                "reason": (
                    approval.reason
                ),

                "status": (
                    approval.status.value
                ),
            })

        return approvals

    # ==================================================
    # GET ALL PENDING APPROVALS
    #
    # Includes:
    #   1. Action approvals
    #   2. Pre-Qwen approvals
    # ==================================================

    def get_all_pending_approvals(self):

        return {
            "qwen": self.get_pending_qwen_approvals(),
            "actions": self.get_pending_approvals(),
        }

    # ==================================================
    # HUMAN APPROVAL — ACTION
    # ==================================================

    def approve_action(
        self,
        approval_id,
        approver_id,
    ):

        pending = (
            self.pending_actions.get(
                approval_id
            )
        )

        if pending is None:

            return {
                "status": "BLOCKED",
                "executed": False,
                "decision": "BLOCK",
                "approval_id": approval_id,
                "reason": (
                    "Approval request not found."
                ),
            }

        action_request = pending[
            "action_request"
        ]

        governance_result = pending[
            "governance_result"
        ]

        result = (
            self.approval_workflow
            .approve_and_execute(
                approval_id=approval_id,
                approver_id=approver_id,
                action_request=action_request,
                governance_result=governance_result,
            )
        )

        executed = result.get(
            "executed",
            False
        )

        self.audit_service.log_event(
            request_id=(
                action_request.request_id
            ),
            entity_type=EntityType.AGENT,
            entity_id=(
                action_request.agent_id
            ),
            action=action_request.tool,
            risk_score=(
                governance_result.risk_score
            ),
            risk_level=(
                governance_result.risk_level
            ),
            decision=(
                Decision.ALLOW
                if executed
                else Decision.BLOCK
            ),
            threats=(
                governance_result.threats
            ),
            policies=(
                governance_result
                .violated_policies
            ),
            approval_status=(
                ApprovalStatus.APPROVED
            ),
            details={
                "approval_id": approval_id,
                "approver_id": approver_id,
                "stage": "APPROVAL_EXECUTION",
                "execution_status": (
                    result.get("status")
                ),
                "executed": executed,
            }
        )

        self.pending_actions.pop(
            approval_id,
            None
        )

        return {
            "status": result.get(
                "status",
                "BLOCKED"
            ),
            "executed": executed,
            "decision": (
                "ALLOW"
                if executed
                else "BLOCK"
            ),
            "approval_id": approval_id,
            "result": result,
        }

    # ==================================================
    # HUMAN DENIAL — ACTION
    # ==================================================

    def deny_action(
        self,
        approval_id,
        approver_id,
    ):

        pending = (
            self.pending_actions.get(
                approval_id
            )
        )

        if pending is None:

            return {
                "status": "BLOCKED",
                "executed": False,
                "decision": "BLOCK",
                "approval_id": approval_id,
                "reason": (
                    "Approval request not found."
                ),
            }

        action_request = pending[
            "action_request"
        ]

        governance_result = pending[
            "governance_result"
        ]

        result = (
            self.approval_workflow
            .deny(
                approval_id=approval_id,
                approver_id=approver_id,
            )
        )

        self.audit_service.log_event(
            request_id=(
                action_request.request_id
            ),
            entity_type=EntityType.AGENT,
            entity_id=(
                action_request.agent_id
            ),
            action=action_request.tool,
            risk_score=(
                governance_result.risk_score
            ),
            risk_level=(
                governance_result.risk_level
            ),
            decision=Decision.BLOCK,
            threats=(
                governance_result.threats
            ),
            policies=(
                governance_result
                .violated_policies
            ),
            approval_status=(
                ApprovalStatus.DENIED
            ),
            details={
                "approval_id": approval_id,
                "approver_id": approver_id,
                "stage": "APPROVAL_DENIED",
                "executed": False,
            }
        )

        self.pending_actions.pop(
            approval_id,
            None
        )

        return result