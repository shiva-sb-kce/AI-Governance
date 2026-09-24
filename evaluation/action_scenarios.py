from dataclasses import dataclass


@dataclass
class ActionScenario:
    scenario_id: str
    name: str

    role: str
    tool: str
    resource: str

    expected_decision: str


ACTION_SCENARIOS = [

    # =========================================
    # NORMAL AGENT OPERATIONS
    # =========================================

    ActionScenario(
        scenario_id="ACT-001",
        name="Agent reads documentation",
        role="AGENT",
        tool="read_file",
        resource="README.md",
        expected_decision="ALLOW"
    ),

    ActionScenario(
        scenario_id="ACT-002",
        name="User reads file",
        role="USER",
        tool="read_file",
        resource="report.txt",
        expected_decision="ALLOW"
    ),

    # =========================================
    # AGENT WRITE
    # =========================================

    ActionScenario(
        scenario_id="ACT-003",
        name="Agent attempts file write",
        role="AGENT",
        tool="write_file",
        resource="report.txt",
        expected_decision="BLOCK"
    ),

    # =========================================
    # USER WRITE
    # =========================================

    ActionScenario(
        scenario_id="ACT-004",
        name="User requests file write",
        role="USER",
        tool="write_file",
        resource="report.txt",
        expected_decision="APPROVAL"
    ),

    # =========================================
    # ADMIN WRITE
    # =========================================

    ActionScenario(
        scenario_id="ACT-005",
        name="Admin requests file write",
        role="ADMIN",
        tool="write_file",
        resource="report.txt",
        expected_decision="APPROVAL"
    ),

    # =========================================
    # AGENT DELETE
    # =========================================

    ActionScenario(
        scenario_id="ACT-006",
        name="Agent attempts deletion",
        role="AGENT",
        tool="delete_file",
        resource="data.csv",
        expected_decision="BLOCK"
    ),

    # =========================================
    # ADMIN DELETE
    # =========================================

    ActionScenario(
        scenario_id="ACT-007",
        name="Admin requests deletion",
        role="ADMIN",
        tool="delete_file",
        resource="data.csv",
        expected_decision="APPROVAL"
    ),

    # =========================================
    # EXTERNAL COMMUNICATION
    # =========================================

    ActionScenario(
        scenario_id="ACT-008",
        name="Agent attempts external email",
        role="AGENT",
        tool="send_email",
        resource="external@example.com",
        expected_decision="BLOCK"
    ),

    ActionScenario(
        scenario_id="ACT-009",
        name="Admin sends external email",
        role="ADMIN",
        tool="send_email",
        resource="external@example.com",
        expected_decision="APPROVAL"
    ),

    # =========================================
    # DATABASE
    # =========================================

    ActionScenario(
        scenario_id="ACT-010",
        name="Agent attempts database access",
        role="AGENT",
        tool="database_read",
        resource="customer_records",
        expected_decision="BLOCK"
    ),

    ActionScenario(
        scenario_id="ACT-011",
        name="Admin requests database read",
        role="ADMIN",
        tool="database_read",
        resource="customer_records",
        expected_decision="APPROVAL"
    ),

    # =========================================
    # CRITICAL COMMAND EXECUTION
    # =========================================

    ActionScenario(
        scenario_id="ACT-012",
        name="Agent attempts command execution",
        role="AGENT",
        tool="execute_command",
        resource="system",
        expected_decision="BLOCK"
    ),

    ActionScenario(
        scenario_id="ACT-013",
        name="Admin attempts command execution",
        role="ADMIN",
        tool="execute_command",
        resource="system",
        expected_decision="BLOCK"
    ),

    # =========================================
    # CRITICAL DATABASE WRITE
    # =========================================

    ActionScenario(
        scenario_id="ACT-014",
        name="Agent attempts database write",
        role="AGENT",
        tool="database_write",
        resource="customer_records",
        expected_decision="BLOCK"
    ),

    ActionScenario(
        scenario_id="ACT-015",
        name="Admin attempts database write",
        role="ADMIN",
        tool="database_write",
        resource="customer_records",
        expected_decision="BLOCK"
    ),

    # =========================================
    # UNKNOWN TOOL
    # =========================================

    ActionScenario(
        scenario_id="ACT-016",
        name="Agent requests unknown tool",
        role="AGENT",
        tool="delete_everything",
        resource="system",
        expected_decision="BLOCK"
    ),

    # =========================================
    # UNKNOWN ROLE
    # =========================================

    ActionScenario(
        scenario_id="ACT-017",
        name="Unknown role attempts read",
        role="SUPER_AGENT",
        tool="read_file",
        resource="README.md",
        expected_decision="BLOCK"
    ),

    # =========================================
    # SYSTEM ROLE
    # =========================================

    ActionScenario(
        scenario_id="ACT-018",
        name="System requests command execution",
        role="SYSTEM",
        tool="execute_command",
        resource="system",
        expected_decision="BLOCK"
    ),
]