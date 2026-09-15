from math import log2
import pytest

from harness.observability.redaction.default_entropy_detector import DefaultEntropyDetector


@pytest.fixture
def detector():
    return DefaultEntropyDetector()


def test_returns_zero_for_empty_string(detector):
    assert detector.entropy("") == 0.0


def test_returns_zero_for_single_character(detector):
    assert detector.entropy("a") == 0.0


def test_returns_zero_for_repeated_character(detector):
    assert detector.entropy("aaaaaaaaa") == 0.0


def test_returns_one_for_two_equally_distributed_characters(detector):
    assert detector.entropy("abababab") == pytest.approx(1.0)


def test_returns_two_for_four_equally_distributed_characters(detector):
    assert detector.entropy("abcdabcd") == pytest.approx(2.0)


def test_returns_log2_of_five_for_five_equally_distributed_characters(detector):
    assert detector.entropy("abcde") == pytest.approx(log2(5))