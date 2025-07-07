# 🎯 Perplexity Sonar: Live Performance & Hallucination Harness

[▶ 2-minute YouTube demo showing this harness in action](https://www.youtube.com/watch?v=og_VEZ8FUBc)

This repository is not a static benchmark. It is a live test harness designed to track the real-time performance and volatility of Perplexity's Sonar models on high-stakes bilingual queries.

The key finding is that performance is **highly dynamic**. The "best" prompting strategy changes, and only a continuous evaluation system can provide a true signal of production-readiness.

### Latest Snapshot (Results are dynamic and will change)

| Mode             | Hallucination Rate* | Key Insight                  |
|------------------|---------------------|------------------------------|
| **Baseline** | **~55%** | The raw model's current state. |
| **Prompt‑tuned** | **~60%** | *Degrades* performance.      |
| **RAG‑assisted** | **30% - 45%** | Best method, but volatile.   |

\* Judged by **GPT-4.1**. The purpose of this tool is to run these evaluations continuously to navigate the performance shifts. The code is structured to be plugged directly into a CI/CD pipeline to catch regressions before they reach production.

---

## 🚀 Quick Start

### 1. Setup

```bash
# Clone the repository
git clone [https://github.com/minhkhoango/perplexity-hallucination-harness.git](https://github.com/minhkhoango/perplexity-hallucination-harness.git)
cd perplexity-hallucination-harness

# Install dependencies using the Makefile
make install

# Create and configure your environment file with API keys
cp .env.example .env
# Then edit .env with your keys
```

### 2. Run Evaluations

Use the simple `make` commands to run the different evaluation modes.

```bash
# Run the baseline evaluation
make run

# Run the prompt-tuned evaluation
make run-prompt-tuned

# Run the RAG-assisted evaluation
make run-rag-assisted
```

### 3. Development & Testing

The Makefile includes commands for linting, formatting, and testing.

```bash
# Lint and format the code
make lint
make format

# Run the test suite
make test
