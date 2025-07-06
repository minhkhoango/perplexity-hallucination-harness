from src.metrics import hallucination_rate


def test_hallucination_rate_empty() -> None:
    """Test that an empty list returns 0%."""
    assert hallucination_rate([]) == 0.0


def test_hallucination_rate_none() -> None:
    """Test that a list with no hallucinations returns 0%."""
    assert hallucination_rate([False, False, False]) == 0.0


def test_hallucination_rate_all() -> None:
    """Test that a list with all hallucinations returns 100%."""
    assert hallucination_rate([True, True, True]) == 100.0


def test_hallucination_rate_mixed() -> None:
    """Test a mixed list of results."""
    assert hallucination_rate([True, False, True, False, False]) == 40.0


def test_hallucination_rate_single_item() -> None:
    """Test with a single item."""
    assert hallucination_rate([True]) == 100.0
    assert hallucination_rate([False]) == 0.0
