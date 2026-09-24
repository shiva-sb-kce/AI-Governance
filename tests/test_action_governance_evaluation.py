from evaluation.action_evaluator import (
    ActionGovernanceEvaluator
)

from evaluation.action_scenarios import (
    ACTION_SCENARIOS
)


def test_action_scenarios_exist():

    assert len(
        ACTION_SCENARIOS
    ) == 18


def test_action_scenario_ids_unique():

    ids = [
        scenario.scenario_id
        for scenario in ACTION_SCENARIOS
    ]

    assert len(ids) == len(set(ids))


def test_action_evaluation_runs():

    evaluator = ActionGovernanceEvaluator()

    results = evaluator.evaluate_all(
        ACTION_SCENARIOS
    )

    assert len(results) == 18


def test_normal_agent_read_is_allowed():

    evaluator = ActionGovernanceEvaluator()

    scenario = next(
        s for s in ACTION_SCENARIOS
        if s.scenario_id == "ACT-001"
    )

    result = evaluator.evaluate(
        scenario
    )

    assert result["actual"] == "ALLOW"


def test_agent_write_is_blocked():

    evaluator = ActionGovernanceEvaluator()

    scenario = next(
        s for s in ACTION_SCENARIOS
        if s.scenario_id == "ACT-003"
    )

    result = evaluator.evaluate(
        scenario
    )

    assert result["actual"] == "BLOCK"


def test_admin_delete_requires_approval():

    evaluator = ActionGovernanceEvaluator()

    scenario = next(
        s for s in ACTION_SCENARIOS
        if s.scenario_id == "ACT-007"
    )

    result = evaluator.evaluate(
        scenario
    )

    assert result["actual"] == "APPROVAL"


def test_unknown_tool_is_blocked():

    evaluator = ActionGovernanceEvaluator()

    scenario = next(
        s for s in ACTION_SCENARIOS
        if s.scenario_id == "ACT-016"
    )

    result = evaluator.evaluate(
        scenario
    )

    assert result["actual"] == "BLOCK"