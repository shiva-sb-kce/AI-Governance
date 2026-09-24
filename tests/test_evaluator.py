from evaluation.evaluator import SecurityEvaluator
from evaluation.scenarios import SCENARIOS


def test_all_scenarios_run():

    evaluator = SecurityEvaluator()

    results = evaluator.evaluate_all(
        SCENARIOS
    )

    assert len(results) == len(
        SCENARIOS
    )


def test_scenarios_have_expected_decisions():

    for scenario in SCENARIOS:

        assert scenario.expected_decision in {
            "ALLOW",
            "MONITOR",
            "APPROVAL",
            "BLOCK"
        }


def test_safe_scenario_is_allowed():

    evaluator = SecurityEvaluator()

    scenario = SCENARIOS[0]

    result = evaluator.evaluate_scenario(
        scenario
    )

    assert result["actual"] == "ALLOW"


def test_injection_scenario_is_blocked():

    evaluator = SecurityEvaluator()

    scenario = next(
        scenario
        for scenario in SCENARIOS
        if scenario.scenario_id == "INJ-001"
    )

    result = evaluator.evaluate_scenario(
        scenario
    )

    assert result["actual"] == "BLOCK"


def test_agent_delete_is_blocked():

    evaluator = SecurityEvaluator()

    scenario = next(
        scenario
        for scenario in SCENARIOS
        if scenario.scenario_id == "AGENT-002"
    )

    result = evaluator.evaluate_scenario(
        scenario
    )

    assert result["actual"] == "BLOCK"


def test_evaluation_metrics():

    evaluator = SecurityEvaluator()

    results = evaluator.evaluate_all(
        SCENARIOS
    )

    metrics = evaluator.calculate_metrics(
        results
    )

    assert metrics["total"] == len(
        SCENARIOS
    )

    assert 0 <= metrics["accuracy"] <= 1