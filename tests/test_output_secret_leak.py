from security.output_validator import OutputValidator


def test_output_validator_blocks_secret_leak():

    validator = OutputValidator()

    output = (
        "The operation completed successfully. "
        "api_key=sk_test_1234567890abcdef"
    )

    result = validator.validate(output)

    assert result.secret_detected is True