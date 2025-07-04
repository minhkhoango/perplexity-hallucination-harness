import json
from pathlib import Path
from typing import TypedDict, Generator

class QAItem(TypedDict):
    """A typed dictionary representing a Question-Answer pair."""
    question: str
    answer: str

def load_qa_dataset(path: Path) -> Generator[QAItem, None, None]:
    """
    Loads the question-answer dataset from a JSONL file.

    Args:
        path: The path to the .jsonl file.
        
    Yields:
        A generator of QAItem objects.
    """
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at path: {path}")

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    # Explicitly cast to QAItem for type checkers
                    data: QAItem = json.loads(line)
                    yield data
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Warning: Skipping malformed line: {line.strip()} | Error: {e}")
                    continue