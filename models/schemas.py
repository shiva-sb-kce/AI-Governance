from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class EntityType(str, Enum):
    USER = "user"
    LLM = "llm"
    SLM = "slm"
    AGENT = "agent"
    SYSTEM = "system"


class Decision(str, Enum):
    ALLOW = "ALLOW"
    MONITOR = "MONITOR"
    APPROVAL = "APPROVAL"
    BLOCK = "BLOCK"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ApprovalStatus(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"


@dataclass
class GovernanceRequest:
    request_id: str
    user_id: str
    role: str
    entity_type: EntityType

    prompt: str = ""

    action: Optional[str] = None
    resource: Optional[str] = None
    parameters: Dict[str, Any] = field(
        default_factory=dict
    )

    context: Dict[str, Any] = field(
        default_factory=dict
    )

    timestamp: Optional[str] = None


@dataclass
class InspectionResult:
    injection_detected: bool = False
    jailbreak_detected: bool = False
    pii_detected: bool = False
    secret_detected: bool = False

    detected_patterns: List[str] = field(
        default_factory=list
    )

    detected_pii: List[str] = field(
        default_factory=list
    )

    indicators: List[str] = field(
        default_factory=list
    )

    severity: int = 0

    reasons: List[str] = field(
        default_factory=list
    )


@dataclass
class PolicyResult:
    violated_policies: List[str] = field(
        default_factory=list
    )

    mandatory_decision: Optional[Decision] = None

    policy_risk: int = 0

    reasons: List[str] = field(
        default_factory=list
    )


@dataclass
class RiskResult:
    threat_score: int = 0
    data_score: int = 0
    permission_score: int = 0
    action_score: int = 0

    risk_score: int = 0

    risk_level: RiskLevel = RiskLevel.LOW

    factors: Dict[str, int] = field(
        default_factory=dict
    )

    reasons: List[str] = field(
        default_factory=list
    )


@dataclass
class PermissionResult:
    allowed: bool = False
    requires_approval: bool = False

    permission: str = "DENY"

    role: Optional[str] = None
    action: Optional[str] = None
    resource: Optional[str] = None

    reasons: List[str] = field(
        default_factory=list
    )


@dataclass
class GovernanceResult:
    request_id: str

    decision: Decision

    risk_score: int

    risk_level: RiskLevel

    threats: List[str] = field(
        default_factory=list
    )

    violated_policies: List[str] = field(
        default_factory=list
    )

    permission: str = "DENY"

    reasons: List[str] = field(
        default_factory=list
    )

    approval_required: bool = False

    approval_status: ApprovalStatus = (
        ApprovalStatus.NOT_REQUIRED
    )

    audit_id: Optional[str] = None


@dataclass
class ActionRequest:
    action_id: str
    request_id: str

    agent_id: str
    tool: str

    resource: Optional[str] = None

    parameters: Dict[str, Any] = field(
        default_factory=dict
    )

    timestamp: Optional[str] = None


@dataclass
class ApprovalRequest:
    approval_id: str
    request_id: str

    action: str
    resource: Optional[str]

    risk_score: int
    risk_level: RiskLevel

    reason: str

    # -----------------------------------------
    # Approval binding
    # -----------------------------------------

    agent_id: Optional[str] = None

    parameters: Dict[str, Any] = field(
        default_factory=dict
    )

    status: ApprovalStatus = (
        ApprovalStatus.PENDING
    )

    approved_by: Optional[str] = None

    approved_at: Optional[str] = None


@dataclass
class AuditEvent:
    audit_id: str
    request_id: str

    timestamp: str

    entity_type: EntityType
    entity_id: str

    action: Optional[str]

    risk_score: int
    risk_level: RiskLevel

    threats: List[str] = field(
        default_factory=list
    )

    policies: List[str] = field(
        default_factory=list
    )

    decision: Decision = Decision.BLOCK

    approval_status: ApprovalStatus = (
        ApprovalStatus.NOT_REQUIRED
    )

    details: Dict[str, Any] = field(
        default_factory=dict
    )