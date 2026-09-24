from evaluation.adversarial_scenarios import (
    ADVERSARIAL_SCENARIOS
)

from evaluation.evaluator import (
    SecurityEvaluator
)

from evaluation.metrics import (
    BinaryMetrics
)


def test_adversarial_scenarios_exist():

    assert len(
        ADVERSARIAL_SCENARIOS
    ) == 20


def test_adversarial_evaluation_runs():

    evaluator = SecurityEvaluator()

    results = evaluator.evaluate_adversarial(
        ADVERSARIAL_SCENARIOS
    )

    assert len(results) == 20


def test_metrics_are_generated():

    evaluator = SecurityEvaluator()

    results = evaluator.evaluate_adversarial(
        ADVERSARIAL_SCENARIOS
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

    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert "accuracy" in metrics


def test_metric_values_are_valid():

    evaluator = SecurityEvaluator()

    results = evaluator.evaluate_adversarial(
        ADVERSARIAL_SCENARIOS
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

    assert 0 <= metrics["precision"] <= 1
    assert 0 <= metrics["recall"] <= 1
    assert 0 <= metrics["f1"] <= 1
    assert 0 <= metrics["accuracy"] <= 1


def test_every_scenario_has_prediction():

    evaluator = SecurityEvaluator()

    results = evaluator.evaluate_adversarial(
        ADVERSARIAL_SCENARIOS
    )

    for result in results:

        assert result["decision"] in {
            "ALLOW",
            "MONITOR",
            "APPROVAL",
            "BLOCK"
        }
        