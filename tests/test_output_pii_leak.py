from security.output_validator import OutputValidator


def test_output_validator_detects_pii_leak():

    validator = OutputValidator()

    output = (
        "Customer information: "
        "email: test@example.com, "
        "phone: +91 9876543210"
    )

    result = validator.validate(output)

    assert result.pii_detected is True