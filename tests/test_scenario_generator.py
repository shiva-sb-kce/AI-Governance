from evaluation.scenario_generator import (
    build_extended_corpus
)


def test_extended_corpus_exists():

    scenarios = build_extended_corpus()

    assert len(scenarios) == 36


def test_scenario_ids_are_unique():

    scenarios = build_extended_corpus()

    ids = [
        scenario.scenario_id
        for scenario in scenarios
    ]

    assert len(ids) == len(set(ids))


def test_scenarios_have_prompts():

    scenarios = build_extended_corpus()

    for scenario in scenarios:

        assert scenario.prompt
        assert isinstance(
            scenario.prompt,
            str
        )


def test_scenarios_have_labels():

    scenarios = build_extended_corpus()

    for scenario in scenarios:

        assert isinstance(
            scenario.malicious,
            bool
        )