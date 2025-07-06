from typing import Sequence


def hallucination_rate(results: Sequence[bool]) -> float:
    """Calculate the hallucination rate as a percentage.

    Args:
    ----
        results: A sequence of booleans, where True indicates a hallucination.

    Returns:
    -------
        The percentage of hallucinations. Returns 0.0 if the sequence is empty.

    """
    if not results:
        return 0.0

    hallucination_count: int = sum(1 for result in results if result)
    total_items: int = len(results)

    return (hallucination_count / total_items) * 100.0
