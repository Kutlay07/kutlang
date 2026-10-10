import pytest

from harness.tools.output_budget import OutputBudget


def test_output_budget_returns_all_lines_when_output_fits_budget():
    budget = OutputBudget(max_chars=100)

    lines = ["hello", "world"]

    result = budget.enforce(lines)

    assert result == lines


def test_output_budget_includes_truncation_notice_with_counts():
    lines = ["a" * 30, "b" * 30, "c" * 30, "d" * 30]

    budget = OutputBudget(max_chars=100)

    result = budget.enforce(lines)

    assert result[-1].startswith("[truncated:")
    assert "2/4 lines" in result[-1]


def test_output_budget_does_not_add_notice_when_output_fits_exactly():
    lines = ["1234", "5678"]

    budget = OutputBudget(max_chars=len("\n".join(lines)))

    result = budget.enforce(lines)

    assert result == lines


def test_output_budget_returns_empty_output_without_truncation_notice():
    budget = OutputBudget(max_chars=10)

    result = budget.enforce([])

    assert result == []


def test_output_budget_never_returns_partial_line():
    lines = [
        "1234567890",
        "abcdefghij",
        "qwertyuiop",
    ]

    budget = OutputBudget(max_chars=100)

    result = budget.enforce(lines)

    normal_lines = result[:-1]

    assert all(line in lines for line in normal_lines)


def test_output_budget_rejects_non_positive_max_chars():
    with pytest.raises(ValueError):
        OutputBudget(max_chars=0)


def test_output_budget_does_not_split_a_line_that_exceeds_budget():
    budget = OutputBudget(max_chars=5)

    lines = ["123456"]

    result = budget.enforce(lines)

    assert result == []


def test_output_budget_never_exceeds_max_chars():
    budget = OutputBudget(max_chars=20)

    lines = [
        "1234567890",
        "abcdefghij",
        "qwertyuiop",
    ]

    result = budget.enforce(lines)

    assert len("\n".join(result)) <= 20


def test_output_budget_does_not_mutate_input():
    budget = OutputBudget(max_chars=50)

    lines = ["a" * 30, "b" * 30]
    original = lines.copy()

    budget.enforce(lines)

    assert lines == original


def test_output_budget_preserves_text_within_limit():
    budget = OutputBudget(max_chars=20)

    content = "a\r\n\r\nb\r\n"

    result = budget.enforce_text(content)

    assert content == result


def test_output_budget_truncates_text():
    budget = OutputBudget(max_chars=20)

    content = "x" * 30

    result = budget.enforce_text(content)

    assert result == "x" * 8 + "\n[truncated]"


def test_output_budget_returns_compact_notice_when_full_notice_does_not_fit():
    budget = OutputBudget(max_chars=4)

    result = budget.enforce_text("12345")

    assert result == "…"


def test_output_budget_enforces_returns_marker_for_one_character_limit():
    budget = OutputBudget(max_chars=1)

    result = budget.enforce_text("12")

    assert len(result) <= 1
    assert result == "…"
