from evaluation.metrics import SecurityMetrics


def test_perfect_detection():

    results = [
        {
            "expected_malicious": True,
            "predicted_malicious": True
        },
        {
            "expected_malicious": True,
            "predicted_malicious": True
        },
        {
            "expected_malicious": False,
            "predicted_malicious": False
        },
        {
            "expected_malicious": False,
            "predicted_malicious": False
        }
    ]

    metrics = SecurityMetrics.calculate(
        results
    )

    assert metrics["accuracy"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1_score"] == 1.0


def test_false_positive():

    results = [
        {
            "expected_malicious": False,
            "predicted_malicious": True
        }
    ]

    metrics = SecurityMetrics.calculate(
        results
    )

    assert metrics["false_positive"] == 1
    assert metrics["false_positive_rate"] == 1.0


def test_false_negative():

    results = [
        {
            "expected_malicious": True,
            "predicted_malicious": False
        }
    ]

    metrics = SecurityMetrics.calculate(
        results
    )

    assert metrics["false_negative"] == 1
    assert metrics["recall"] == 0.0


def test_empty_results():

    metrics = SecurityMetrics.calculate([])

    assert metrics["total"] == 0
    assert metrics["accuracy"] == 0.0