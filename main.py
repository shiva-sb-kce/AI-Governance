from typing import Any, Dict, Optional
from dataclasses import asdict
from enum import Enum
import json
import urllib.request

from audit.audit_logger import AuditLogger

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from services.audit_service import AuditService
from core.gateway import GovernanceGateway
from monitoring.dashboard import DashboardService
from behavior_gateway import BehaviorGateway

from integrations.qwen_agent import QwenAgent

from models.schemas import (
    GovernanceRequest,
    ActionRequest,
    EntityType,
)

from evaluation.adversarial_scenarios import (
    ADVERSARIAL_SCENARIOS
)

from evaluation.evaluator import (
    SecurityEvaluator
)

from evaluation.metrics import (
    BinaryMetrics
)

from evaluation.evaluation_report import (
    EvaluationReport
)

from integrations.integration_manager import (
    IntegrationManager
)

from services.secured_ai_service import (
    SecuredAIService
)


# ======================================================
# APPLICATION
# ======================================================

app = FastAPI(
    title="Unified AI Governance and Security Platform",
    description=(
        "Offline deterministic governance "
        "for LLMs, SLMs and AI agents."
    ),
    version="1.0.0",
)


# ======================================================
# STATIC DASHBOARD
# ======================================================

app.mount(
    "/dashboard-ui",
    StaticFiles(
        directory="frontend",
        html=True
    ),
    name="dashboard-ui"
)


# ======================================================
# SERVICES
# ======================================================

audit_service = AuditService()

audit_logger = AuditLogger()

gateway = GovernanceGateway(
    audit_service=audit_service
)

qwen_agent = QwenAgent(
    gateway
)

dashboard = DashboardService()

integration_manager = IntegrationManager(
    gateway
)

secured_ai = SecuredAIService(
    gateway
)

behavior_gateway = BehaviorGateway(
    gateway
)


# ======================================================
# API SCHEMAS
# ======================================================

class GovernanceAPIRequest(BaseModel):

    request_id: str
    user_id: str
    role: str
    entity_type: EntityType

    prompt: str = ""

    action: Optional[str] = None

    resource: Optional[str] = None

    parameters: Dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )

    context: Dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )


class ActionAPIRequest(BaseModel):

    request_id: str

    agent_id: str

    role: str = "AGENT"

    tool: str

    resource: Optional[str] = None

    parameters: Dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )


class ApprovalAPIRequest(BaseModel):

    approver_id: str


class AIModelAPIRequest(BaseModel):

    request_id: str

    user_id: str

    role: str = "USER"

    prompt: str

    context: Dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )


class QwenActionAPIRequest(BaseModel):

    instruction: str

    request_id: str

    agent_id: str = "qwen-agent"


# ======================================================
# ROOT
# ======================================================

@app.get("/")
def root():

    return {
        "platform": (
            "Unified AI Governance "
            "and Security Platform"
        ),

        "status": "online",

        "mode": "offline",

        "llm_required": False,

        "internet_required": False,

        "dashboard": "/dashboard-ui/",

        "docs": "/docs",

        "supported_entities": [
            "LLM",
            "SLM",
            "AGENT"
        ]
    }


# ======================================================
# HEALTH
# ======================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",

        "governance_engine": "ready",

        "mode": "offline",

        "components": {
            "gateway": "ready",
            "dashboard": "ready",
            "integration_manager": "ready",
            "security_evaluation": "ready",
            "qwen_agent": "ready"
        }
    }


# ======================================================
# QWEN HEALTH
# ======================================================

@app.get("/ai/qwen/health")
def qwen_health():

    try:

        request = urllib.request.Request(
            "http://localhost:11434/api/tags",
            method="GET"
        )

        with urllib.request.urlopen(
            request,
            timeout=3
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        models = data.get(
            "models",
            []
        )

        qwen_available = any(
            str(model.get("name", "")).startswith(
                "qwen3:8b"
            )
            for model in models
        )

        return {
            "status": "online",
            "provider": "Ollama",
            "model": "qwen3:8b",
            "model_available": qwen_available,
            "endpoint": "http://localhost:11434"
        }

    except Exception as exc:

        return {
            "status": "offline",
            "provider": "Ollama",
            "model": "qwen3:8b",
            "model_available": False,
            "endpoint": "http://localhost:11434",
            "error": str(exc)
        }


# ======================================================
# GOVERNANCE ENDPOINT
# ======================================================

@app.post("/govern")
def govern(
    request: GovernanceAPIRequest
):

    try:

        governance_request = GovernanceRequest(
            request_id=request.request_id,
            user_id=request.user_id,
            role=request.role,
            entity_type=request.entity_type,
            prompt=request.prompt,
            action=request.action,
            resource=request.resource,
            parameters=request.parameters,
            context=request.context,
        )

        result = gateway.process(
            governance_request
        )

        return {
            "request_id": result.request_id,

            "decision": result.decision.value,

            "risk_score": result.risk_score,

            "risk_level": result.risk_level.value,

            "permission": result.permission,

            "approval_required": (
                result.approval_required
            ),

            "approval_status": (
                result.approval_status.value
            ),

            "threats": result.threats,

            "violated_policies": (
                result.violated_policies
            ),

            "reasons": result.reasons,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# LLM GOVERNANCE
# ======================================================

@app.post("/ai/llm")
def process_llm(
    request: AIModelAPIRequest
):

    try:

        result = (
            integration_manager.process_llm(
                prompt=request.prompt,
                request_id=request.request_id,
                user_id=request.user_id,
                role=request.role,
                **request.context
            )
        )

        return result

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# SLM GOVERNANCE
# ======================================================

@app.post("/ai/slm")
def process_slm(
    request: AIModelAPIRequest
):

    try:

        result = (
            integration_manager.process_slm(
                prompt=request.prompt,
                request_id=request.request_id,
                user_id=request.user_id,
                role=request.role,
                **request.context
            )
        )

        return result

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# AGENT ACTION ENDPOINT
# ======================================================

@app.post("/action")
def action(
    request: ActionAPIRequest
):

    try:

        action_request = ActionRequest(
            action_id=(
                f"ACT-{request.request_id}"
            ),

            request_id=request.request_id,

            agent_id=request.agent_id,

            tool=request.tool,

            resource=request.resource,

            parameters=request.parameters,
        )

        result = gateway.process_action(
            action_request=action_request,
            role=request.role,
        )

        return result

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# QWEN AGENT
# ======================================================

@app.post("/ai/qwen")
def qwen_action(
    request: QwenActionAPIRequest
):

    try:

        result = qwen_agent.propose_action(
            instruction=request.instruction,
            request_id=request.request_id,
            agent_id=request.agent_id or "qwen-agent"
        )

        return result

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# PENDING APPROVALS
# ======================================================

@app.get("/approval/pending")
def get_pending_approvals():

    try:

        approvals = (
            gateway.get_pending_approvals()
        )

        return {
            "count": len(approvals),
            "approvals": approvals
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# APPROVE ACTION
# ======================================================

@app.post(
    "/approval/{approval_id}/approve"
)
def approve(
    approval_id: str,
    request: ApprovalAPIRequest,
):

    try:

        result = gateway.approve_action(
            approval_id=approval_id,
            approver_id=request.approver_id,
        )

        return result

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# DENY ACTION
# ======================================================

@app.post(
    "/approval/{approval_id}/deny"
)
def deny(
    approval_id: str,
    request: ApprovalAPIRequest,
):

    try:

        result = gateway.deny_action(
            approval_id=approval_id,
            approver_id=request.approver_id,
        )

        return result

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# DASHBOARD SUMMARY
# ======================================================

@app.get("/dashboard")
def get_dashboard():

    try:

        return dashboard.get_summary()

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# RECENT DASHBOARD EVENTS
# ======================================================

@app.get("/dashboard/recent")
def get_recent_events(
    limit: int = 20
):

    try:

        if limit < 1:
            limit = 1

        if limit > 100:
            limit = 100

        return {
            "events": (
                dashboard.get_recent_events(
                    limit
                )
            )
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# SECURITY EVALUATION
# ======================================================

@app.get("/evaluation/security")
def security_evaluation():

    try:

        evaluator = SecurityEvaluator()

        results = (
            evaluator.evaluate_adversarial(
                ADVERSARIAL_SCENARIOS
            )
        )

        expected = [
            result["expected_malicious"]
            for result in results
        ]

        predicted = [
            result["predicted_malicious"]
            for result in results
        ]

        metrics = BinaryMetrics.calculate(
            expected,
            predicted
        )

        return {
            "status": "success",
            "metrics": metrics,
            "scenarios": results
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# EVALUATION SUMMARY
# ======================================================

@app.get("/evaluation")
def get_evaluation():

    try:

        return EvaluationReport.generate()

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# SECURED LLM PIPELINE
# ======================================================

@app.post("/ai/llm/execute")
def execute_llm(
    request: AIModelAPIRequest
):

    try:

        governance_request = GovernanceRequest(
            request_id=request.request_id,
            user_id=request.user_id,
            role=request.role,
            entity_type=EntityType.LLM,
            prompt=request.prompt,
            context=request.context
        )

        return secured_ai.process(
            governance_request
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# SECURED SLM PIPELINE
# ======================================================

@app.post("/ai/slm/execute")
def execute_slm(
    request: AIModelAPIRequest
):

    try:

        governance_request = GovernanceRequest(
            request_id=request.request_id,
            user_id=request.user_id,
            role=request.role,
            entity_type=EntityType.SLM,
            prompt=request.prompt,
            context=request.context
        )

        return secured_ai.process(
            governance_request
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# AI BEHAVIOR SCENARIOS
# ======================================================

@app.get("/behavior/scenarios")
def get_behavior_scenarios():

    try:

        return {
            "count": len(
                behavior_gateway.list_scenarios()
            ),

            "scenarios": (
                behavior_gateway.list_scenarios()
            )
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# RUN BEHAVIOR DEMO
# ======================================================

@app.post("/behavior/demo/{scenario}")
def run_behavior_demo(
    scenario: str
):

    try:

        return behavior_gateway.run_demo(
            scenario
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# INGEST OBSERVED AI BEHAVIOR
# ======================================================

@app.post("/behavior/ingest")
def ingest_ai_behavior(
    request: ActionAPIRequest
):

    try:

        result = behavior_gateway.ingest(
            request_id=request.request_id,
            agent_id=request.agent_id,
            role=request.role,
            tool=request.tool,
            resource=request.resource,
            parameters=request.parameters,
        )

        return {
            "source": "AI_BEHAVIOR",

            "request_id": (
                request.request_id
            ),

            "agent_id": (
                request.agent_id
            ),

            "action": (
                request.tool
            ),

            "resource": (
                request.resource
            ),

            "governance": result,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# RECENT AI BEHAVIOR
# ======================================================

@app.get("/behavior/recent")
def get_recent_behavior(
    limit: int = 15
):

    try:

        if limit < 1:
            limit = 1

        if limit > 100:
            limit = 100

        # IMPORTANT:
        # BehaviorGateway writes to AuditService.
        # Therefore read from AuditService here,
        # not from the persistent AuditLogger.

        events = audit_service.get_events()

        normalized_events = []

        for event in events:

            try:
                event_copy = asdict(event)

            except Exception:
                event_copy = dict(event)

            if not event_copy.get("action"):
                continue

            # ------------------------------------------
            # Decision
            # ------------------------------------------

            decision = event_copy.get(
                "decision"
            )

            if isinstance(
                decision,
                Enum
            ):

                decision = decision.value

            elif isinstance(
                decision,
                dict
            ):

                decision = (
                    decision.get("value")
                    or decision.get("name")
                    or ""
                )

            decision = str(
                decision or ""
            ).upper()

            event_copy["decision"] = decision

            # ------------------------------------------
            # Execution status
            # ------------------------------------------

            execution_status = (
                event_copy.get(
                    "execution_status"
                )
            )

            if isinstance(
                execution_status,
                Enum
            ):

                execution_status = (
                    execution_status.value
                )

            elif isinstance(
                execution_status,
                dict
            ):

                execution_status = (
                    execution_status.get("status")
                    or execution_status.get("value")
                    or ""
                )

            execution_status = str(
                execution_status or ""
            ).upper()

            # ------------------------------------------
            # Normalize execution
            # ------------------------------------------

            details = event_copy.get(
                "details",
                {}
            )

            if not isinstance(details, dict):
                details = {}

            # Gateway records whether the action actually executed
            executed = details.get(
                "executed"
            )

            if executed is True:

                execution_status = "EXECUTED"

            elif executed is False and decision == "BLOCK":

                execution_status = "BLOCKED"

            elif decision == "APPROVAL":

                if not execution_status:
                    execution_status = "PENDING_APPROVAL"

            elif decision == "BLOCK":

                if not execution_status:
                    execution_status = "BLOCKED"

            elif decision == "ALLOW":

                if not execution_status:
                    execution_status = "EXECUTION_NOT_RECORDED"

            else:

                if not execution_status:
                    execution_status = "-"

            event_copy[
                "execution_status"
            ] = execution_status

            # ------------------------------------------
            # Normalize agent ID and resource
            # ------------------------------------------

            # Action events store the agent ID as entity_id
            agent_id = event_copy.get(
                "entity_id"
            )

            if agent_id:
                event_copy[
                    "agent_id"
                ] = agent_id

            # Resource is stored inside details
            details = event_copy.get(
                "details",
                {}
            )

            if isinstance(details, dict):

                resource = details.get(
                    "resource"
                )

                if resource:
                    event_copy[
                        "resource"
                    ] = resource

            normalized_events.append(
                event_copy
            )

            if len(normalized_events) >= limit:
                break

        return {
            "count": len(
                normalized_events
            ),

            "events": normalized_events
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# AUDIT LOGS
# ======================================================

@app.get("/audit")
def get_audit_logs():

    try:

        events = audit_logger.read_all()

        return {
            "count": len(events),
            "events": events
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# RECENT AUDIT LOGS
# ======================================================

@app.get("/audit/recent")
def get_recent_audit_logs(
    limit: int = 15
):

    try:

        if limit < 1:
            limit = 1

        if limit > 100:
            limit = 100

        events = audit_logger.read_all()

        recent_events = (
            events[-limit:][::-1]
        )

        return {
            "count": len(recent_events),
            "events": recent_events
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ======================================================
# AUDIT BY REQUEST
# ======================================================

@app.get(
    "/audit/request/{request_id}"
)
def get_audit_by_request(
    request_id: str
):

    try:

        events = audit_logger.find_by_request(
            request_id
        )

        return {
            "request_id": request_id,
            "count": len(events),
            "events": events
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )