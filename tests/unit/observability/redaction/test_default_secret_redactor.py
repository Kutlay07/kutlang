import pytest

from harness.observability.redaction.default_entropy_detector import (
    DefaultEntropyDetector,
)
from harness.observability.redaction.default_secret_redactor import (
    DefaultSecretRedactor,
)


@pytest.fixture
def redactor():
    return DefaultSecretRedactor(DefaultEntropyDetector())


def test_redacts_api_key(redactor):
    text = "API_KEY=sk-abcdefghijklmnopqrstuvwxyz123456"

    result = redactor.redact(text)

    assert "[REDACTED.API_KEY]" in result
    assert "sk-abcdefghijklmnopqrstuvwxyz123456" not in result


def test_returns_text_unchanged_when_no_secret_is_present(redactor):
    text = "Hello, this is a completely normal tool output."

    result = redactor.redact(text)

    assert result == text


def test_redaction_is_idempotent(redactor):
    text = "API_KEY=sk-abcdefghijklmnopqrstuvwxyz123456"

    once = redactor.redact(text)
    twice = redactor.redact(once)

    assert twice == once


def test_redacts_multiple_secrets_in_same_text(redactor):
    text = (
        "API_KEY=sk-firstsecret123456 "
        "API_KEY=sk-secondsecret789012"
    )

    result = redactor.redact(text)

    assert result.count("[REDACTED.API_KEY]") == 2
    assert "sk-firstsecret123456" not in result
    assert "sk-secondsecret789012" not in result


def test_does_not_redact_normal_long_text(redactor):
    text = (
        "The quick brown fox jumps over the lazy dog. "
        "This is a normal sentence containing many characters "
        "and should remain completely unchanged."
    )

    result = redactor.redact(text)

    assert result == text


def test_redacts_bearer_token(redactor):
    text = "Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456"

    result = redactor.redact(text)

    assert "Authorization: Bearer [REDACTED.BEARER_TOKEN]" == result
    assert "abcdefghijklmnopqrstuvwxyz123456" not in result


def test_redacts_private_key(redactor):
    private_key_label = "PRIVATE " + "KEY"
    rsa_private_key_label = "RSA PRIVATE " + "KEY"
    openssh_private_key_label = "OPENSSH PRIVATE " + "KEY"

    text1 = (
        "-----BEGIN "
        + private_key_label
        + "-----\n"
        "fake-private-key-content\n"
        "-----END "
        + private_key_label
        + "-----"
    )

    text2 = (
        "-----BEGIN "
        + rsa_private_key_label
        + "-----\n"
        "fake-private-key-content\n"
        "-----END "
        + rsa_private_key_label
        + "-----"
    )

    text3 = (
        "-----BEGIN "
        + openssh_private_key_label
        + "-----\n"
        "fake-private-key-content\n"
        "-----END "
        + openssh_private_key_label
        + "-----"
    )

    result1 = redactor.redact(text1)
    result2 = redactor.redact(text2)
    result3 = redactor.redact(text3)

    assert result1 == "[REDACTED.PRIVATE_KEY]"
    assert "fake-private-key-content" not in result1

    assert result2 == "[REDACTED.PRIVATE_KEY]"
    assert "fake-private-key-content" not in result2

    assert result3 == "[REDACTED.PRIVATE_KEY]"
    assert "fake-private-key-content" not in result3


def test_redacts_multiple_private_keys(redactor):
    private_key_label = "PRIVATE " + "KEY"
    rsa_private_key_label = "RSA PRIVATE " + "KEY"

    text = (
        "-----BEGIN "
        + private_key_label
        + "-----\n"
        "fake-private-key-content\n"
        "-----END "
        + private_key_label
        + "-----\n"
        "-----BEGIN "
        + rsa_private_key_label
        + "-----\n"
        "fake-private-key-content\n"
        "-----END "
        + rsa_private_key_label
        + "-----"
    )

    result = redactor.redact(text)

    assert result == "[REDACTED.PRIVATE_KEY]\n[REDACTED.PRIVATE_KEY]"
    assert "fake-private-key-content" not in result


def test_redacts_realistic_jwt_like_value(redactor):
    jwt_header = "eyJ" + "hbGciOiJIUzI1NiJ9"
    jwt_payload = "eyJ" + "zdWIiOiIxMjM0NTYifQ"
    jwt_signature = "fake" + "Signature123456789"

    text = (
        f'token = "{jwt_header}.'
        f"{jwt_payload}."
        f'{jwt_signature}"'
    )

    result = redactor.redact(text)

    assert result == 'token = "[REDACTED.JWT]"'


def test_does_not_redact_non_jwt_three_segment_value(redactor):
    text = "version.1.2"

    result = redactor.redact(text)

    assert result == text


def test_does_not_redact_three_segments_without_valid_jwt_header(redactor):
    text = "value = abc.def.ghi"

    result = redactor.redact(text)

    assert result == text


def test_does_not_redact_jwt_without_alg(redactor):
    jwt_header_without_alg = "eyJ" + "zdWIiOiIxMjM0NTYifQ"
    jwt_payload = "eyJ" + "zdWIiOiIxMjM0NTYifQ"
    jwt_signature = "signature" + "123"

    text = (
        f'token = "{jwt_header_without_alg}.'
        f"{jwt_payload}."
        f'{jwt_signature}"'
    )

    result = redactor.redact(text)

    assert result == text


def test_redacts_multiple_jwts(redactor):
    jwt_header = "eyJ" + "hbGciOiJIUzI1NiJ9"
    first_payload = "eyJ" + "zdWIiOiIxMjM0NTYifQ"
    second_payload = "eyJ" + "zdWIiOiI1Njc4OTAifQ"
    first_signature = "signature" + "123"
    second_signature = "signature" + "456"

    text = (
        f"first = {jwt_header}.{first_payload}.{first_signature} "
        f"second = {jwt_header}.{second_payload}.{second_signature}"
    )

    result = redactor.redact(text)

    assert result.count("[REDACTED.JWT]") == 2
    assert "signature123" not in result
    assert "signature456" not in result


def test_redacts_high_entropy_candidate(redactor):
    text = "a8Kx91QmZ7pL2vN4sT8w"

    result = redactor.redact(text)

    assert result == "[REDACTED.SECRET]"


def test_does_not_redact_low_entropy_candidate(redactor):
    text = "aaaaaaaaaaaaaaaaaaaa"

    result = redactor.redact(text)

    assert result == text


def test_redacts_same_secret_two_times(redactor):
    text = (
        "first=a8Kx91QmZ7pL2vN4sT8w "
        "second=a8Kx91QmZ7pL2vN4sT8w"
    )

    result = redactor.redact(text)

    assert result.count("[REDACTED.SECRET]") == 2


def test_does_not_redact_long_normal_text(redactor):
    text = "long_long_long_long_normal_text"

    result = redactor.redact(text)

    assert result == text


def test_does_not_redact_normal_english_text(redactor):
    text = "this_is_a_very_long_normal_identifier_value"

    result = redactor.redact(text)

    assert result == text


def test_does_not_redact_high_entropy_single_class_candidate(redactor):
    text = "abcdefghijklmnopqrst"

    result = redactor.redact(text)

    assert result == text


def test_does_not_redact_digit_only_candidate(redactor):
    text = "12345678901234567890"

    result = redactor.redact(text)

    assert result == text


def test_redacts_high_entropy_mixed_class_candidate(redactor):
    text = "a8Kx91QmZ7pL2vN4sT8w"

    result = redactor.redact(text)

    assert result == "[REDACTED.SECRET]"


def test_redacts_high_entropy_candidate_with_special_character(redactor):
    text = "a8Kx91QmZ7pL2vN4sT8!"

    result = redactor.redact(text)

    assert result == "[REDACTED.SECRET]"


def test_redacts_realistic_secret_formats(redactor):
    stripe_secret = "sk_" + "live_" + "a8Kx91QmZ7pL2vN4sT8w"
    github_secret = "ghp_" + "a8Kx91QmZ7pL2vN4sT8w"

    secrets = [
        stripe_secret,
        github_secret,
        "a8Kx91QmZ7pL2vN4sT8w!@#",
        "p@ssw0rd-9KxL2mN7QvR4tY8",
    ]

    for secret in secrets:
        result = redactor.redact(secret)
        assert result == "[REDACTED.SECRET]"


def test_does_not_redact_normal_identifiers(redactor):
    values = [
        "abcdefghijklmnopqrst",
        "12345678901234567890",
        "this_is_a_very_long_normal_identifier",
        "normal-development-environment-variable",
        "user-service-production-configuration",
    ]

    for value in values:
        result = redactor.redact(value)
        assert result == value