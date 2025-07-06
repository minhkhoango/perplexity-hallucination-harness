import asyncio
import os
import sys
from enum import Enum
from pathlib import Path
from typing import Any

import httpx
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# --- Local Modules ---
from src.dataset import QAItem, load_qa_dataset
from src.metrics import hallucination_rate

# --- Constants ---
PPLX_API_URL = "https://api.perplexity.ai/chat/completions"
PPLX_MODEL = "sonar"  # "llama-3.1-sonar-small-128k-online"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
GPT4O_MINI_MODEL = "gpt-4.1"


class ExperimentMode(str, Enum):
    """Define available experiment modes."""

    BASELINE = "baseline"
    PROMPT_TUNED = "prompt-tuned"
    RAG_ASSISTED = "rag-assisted"


# --- Setup ---
load_dotenv()
app = typer.Typer()
console = Console()

# --- API Keys & Headers ---
PPLX_API_KEY = os.getenv("PPLX_KEY")
OPENAI_API_KEY = os.getenv("GPT4O_MINI_KEY")

PPLX_HEADERS: dict[str, str] = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": f"Bearer {PPLX_API_KEY}",
}

OPENAI_HEADERS: dict[str, str] = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}",
}


# --- Core API Functions ---
async def query_perplexity(
    client: httpx.AsyncClient, question: str, mode: ExperimentMode
) -> str:
    """Query the Perplexity API with a given question."""
    system_prompt = ""
    user_question = question

    if mode == ExperimentMode.BASELINE:
        system_prompt = (
            "You are a helpful AI assistant. Answer the user's question, then"
            "translate it to Vietnamese."
        )
    elif mode == ExperimentMode.PROMPT_TUNED:
        system_prompt = (
            "You are a hyper-precise bilingual expert. You will strictly follow a "
            "two-part format. First, provide a complete, factual answer in English "
            "inside <english_answer> XML tags. Second, provide a direct and accurate "
            "translation of that English answer into Vietnamese inside "
            "<vietnamese_translation> XML tags. Do not add any other commentary. "
            "Here is an example of the required format:\n\n"
            "EXAMPLE QUESTION: What is a CPU?\n"
            "EXAMPLE RESPONSE:\n"
            "<english_answer>\nA CPU, or Central Processing Unit, is the primary "
            "component of a computer that executes instructions.\n"
            "</english_answer>\n"
            "<vietnamese_translation>\n"
            "CPU, hay Bộ xử lý trung tâm, là thành phần chính của máy tính thực hiện "
            "các lệnh.\n"
            "</vietnamese_translation>"
        )
    elif mode == ExperimentMode.RAG_ASSISTED:
        system_prompt = (
            "You are a hyper-precise bilingual expert. Use ONLY the provided context "
            "to answer the question. Strictly follow the two-part format: first, "
            "the English answer in <english_answer> tags. Second, the Vietnamese "
            "translation in <vietnamese_translation> tags."
        )

    payload: dict[str, Any] = {
        "model": PPLX_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question},
        ],
    }
    try:
        response = await client.post(
            PPLX_API_URL, json=payload, headers=PPLX_HEADERS, timeout=120.0
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"An unexpected error occurred in Perplexity query: {e}"


async def is_hallucinated(
    client: httpx.AsyncClient, question: str, correct_answer: str, model_answer: str
) -> bool:
    """Use GPT-4o-mini to fact-check if the model's answer is a hallucination."""
    prompt = (
        "You are a meticulous fact-checker. Compare the 'Model Answer' to the "
        "'Ground Truth Answer'. A hallucination is a significant factual error, "
        "contradiction, or failure to follow the translation instruction in EITHER "
        "the English or Vietnamese part. Respond with ONLY 'YES' if it's a "
        "hallucination or 'NO' if it is factually consistent and correctly "
        "formatted/translated.\n\n"
        f'Question: "{question}"\n\n'
        f'Ground Truth Answer: "{correct_answer}"\n\n'
        f'Model Answer: "{model_answer}"'
    )
    payload: dict[str, Any] = {
        "model": GPT4O_MINI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 5,
    }
    try:
        response = await client.post(
            OPENAI_API_URL, json=payload, headers=OPENAI_HEADERS, timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"].strip().upper()
        return "YES" in content
    except Exception as e:
        console.print(f"[bold red]GPT-4o Mini fact-check failed: {e}[/bold red]")
        return True


# --- Orchestration ---


async def evaluate_item(
    client: httpx.AsyncClient, item: QAItem, mode: ExperimentMode
) -> tuple[QAItem, str, bool]:
    """Run the full evaluation pipeline for a single Q&A item based on the mode."""
    question_payload = item["question"]

    if mode == ExperimentMode.RAG_ASSISTED:
        context = item["answer"]
        question_payload = (
            f"CONTEXT:\n---\n{context}\n---\n\n" f"QUESTION: {item['question']}"
        )

    model_answer = await query_perplexity(client, question_payload, mode)
    hallucination_result = await is_hallucinated(
        client, item["question"], item["answer"], model_answer
    )
    return (item, model_answer, hallucination_result)


@app.command()
def evaluate(
    mode: ExperimentMode = typer.Option(
        ExperimentMode.BASELINE,
        "--mode",
        "-m",
        help="The experiment mode to run.",
        case_sensitive=False,
    ),
    data_path: Path = typer.Option(
        "data/qa.jsonl", "--data", "-d", help="Path to the QA dataset."
    ),
    limit: int = typer.Option(
        -1, "--limit", "-l", help="Limit the number of questions to evaluate."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Print full question and answer details."
    ),
) -> None:
    """Evaluate Perplexity AI on a mixed-language dataset for hallucinations."""
    if not PPLX_API_KEY or not OPENAI_API_KEY:
        console.print(
            "[bold red]Error: PPLX_KEY and GPT4O_KEY environment variables"
            "must be set.[/bold red]"
        )
        sys.exit(1)

    console.print("[bold green]🚀 Starting Guided Missile Evaluation[/bold green]")
    console.print(f"Mode: [bold yellow]{mode.value}[/bold yellow]")

    try:
        dataset = list(load_qa_dataset(data_path))
        if limit > 0:
            dataset = dataset[:limit]
    except FileNotFoundError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)

    asyncio.run(run_evaluation_tasks(dataset, verbose, mode))


async def run_evaluation_tasks(
    dataset: list[QAItem], verbose: bool, mode: ExperimentMode
) -> None:
    """Run all tasks and display results."""
    hallucination_results: list[bool] = []

    all_results: list[tuple[QAItem, str, bool]] = []

    async with httpx.AsyncClient() as client:
        tasks = [evaluate_item(client, item, mode) for item in dataset]
        with console.status(
            f"[bold yellow]Evaluating in {mode.value} mode...[/bold yellow]"
        ):
            all_results = await asyncio.gather(*tasks)

    # Display results based on verbosity
    if verbose:
        table = Table(title="Verbose Evaluation Results", show_lines=True)
        table.add_column("Question", style="cyan", no_wrap=False)
        table.add_column("Ground Truth", style="green", no_wrap=False)
        table.add_column("Model Answer", style="white", no_wrap=False)
        table.add_column("Hallucination?", style="magenta", justify="center")
        for item, model_answer, is_hallucinated_result in all_results:
            hallucination_results.append(is_hallucinated_result)
            table.add_row(
                item["question"],
                item["answer"],
                model_answer,
                "[bold red]YES[/bold red]"
                if is_hallucinated_result
                else "[bold green]NO[/bold green]",
            )
        console.print(table)
    else:
        console.print("\n[bold]Quick Results:[/bold]")
        for i, (item, _, is_hallucinated_result) in enumerate(all_results):
            hallucination_results.append(is_hallucinated_result)
            status_icon = (
                "[bold red]✖ FAIL[/]"
                if is_hallucinated_result
                else "[bold green]✔ PASS[/]"
            )
            console.print(f"{status_icon} - Q{i+1}: {item['question'][:80]}...")

    # Final Report
    final_rate = hallucination_rate([res[2] for res in all_results])
    console.print("\n" + "=" * 40 + "\n")
    summary_table = Table(title=f"📊 Final Report ({mode.value})", show_header=False)
    summary_table.add_row("Total Questions Evaluated:", str(len(dataset)))
    summary_table.add_row(
        "Total Hallucinations Detected:", str(sum(res[2] for res in all_results))
    )
    summary_table.add_row(
        "[bold yellow]Hallucination Rate:[/bold yellow]",
        f"[bold yellow]{final_rate:.2f}%[/bold yellow]",
    )
    console.print(summary_table)


if __name__ == "__main__":
    app()
