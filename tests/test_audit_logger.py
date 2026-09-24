from audit.audit_logger import AuditLogger


def test_log_event(tmp_path):

    logger = AuditLogger(
        log_file=tmp_path / "audit.jsonl"
    )

    event = logger.log(
        event_type="GOVERNANCE_DECISION",
        request_id="REQ-001",
        decision="BLOCK",
        entity_type="AGENT",
        entity_id="agent-001",
        action="execute_command",
        resource="system",
        risk_score=90,
        risk_level="CRITICAL",
        threats=["PROMPT_INJECTION"],
        violated_policies=["POLICY-001"],
        permission="DENY",
        reasons=[
            "Unauthorized action."
        ]
    )

    assert event["request_id"] == "REQ-001"
    assert event["decision"] == "BLOCK"
    assert event["risk"]["score"] == 90


def test_read_all_events(tmp_path):

    logger = AuditLogger(
        log_file=tmp_path / "audit.jsonl"
    )

    logger.log(
        event_type="GOVERNANCE_DECISION",
        request_id="REQ-001",
        decision="ALLOW"
    )

    logger.log(
        event_type="GOVERNANCE_DECISION",
        request_id="REQ-002",
        decision="BLOCK"
    )

    events = logger.read_all()

    assert len(events) == 2
    assert events[0]["request_id"] == "REQ-001"
    assert events[1]["request_id"] == "REQ-002"


def test_find_by_request(tmp_path):

    logger = AuditLogger(
        log_file=tmp_path / "audit.jsonl"
    )

    logger.log(
        event_type="INPUT_INSPECTION",
        request_id="REQ-001"
    )

    logger.log(
        event_type="GOVERNANCE_DECISION",
        request_id="REQ-001",
        decision="BLOCK"
    )

    logger.log(
        event_type="GOVERNANCE_DECISION",
        request_id="REQ-002",
        decision="ALLOW"
    )

    events = logger.find_by_request(
        "REQ-001"
    )

    assert len(events) == 2

    assert all(
        event["request_id"] == "REQ-001"
        for event in events
    )


def test_find_by_decision(tmp_path):

    logger = AuditLogger(
        log_file=tmp_path / "audit.jsonl"
    )

    logger.log(
        event_type="DECISION",
        request_id="REQ-001",
        decision="BLOCK"
    )

    logger.log(
        event_type="DECISION",
        request_id="REQ-002",
        decision="ALLOW"
    )

    logger.log(
        event_type="DECISION",
        request_id="REQ-003",
        decision="BLOCK"
    )

    blocked = logger.find_by_decision(
        "BLOCK"
    )

    assert len(blocked) == 2

    assert all(
        event["decision"] == "BLOCK"
        for event in blocked
    )


def test_log_contains_timestamp(tmp_path):

    logger = AuditLogger(
        log_file=tmp_path / "audit.jsonl"
    )

    event = logger.log(
        event_type="TEST",
        request_id="REQ-001"
    )

    assert "timestamp" in event
    assert event["timestamp"] is not None