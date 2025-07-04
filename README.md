# 🎯 Perplexity Guided‑Missile — VI/EN Hallucination Harness

> “Measure first, then obliterate the error.”  
> *Built by Khoa as Missile #1 of 3 on 26 Jun 2025.*

[▶ 90‑second Loom demo](https://www.loom.com/share/5bdfbfba770a4574bff589c56d3ec417?sid=3d66ecea-2c81-462e-b1ab-06af4e2deb7d)

| Mode             | Hallucination Rate* |
|------------------|---------------------|
| **Baseline** (`sonar`)        | **60 %** |
| **Prompt‑tuned**             | **50 %** |
| **RAG‑assisted**             | **55 %** |

\* 20 high‑difficulty mixed Vietnamese / English questions, judged by **GPT‑4.1**.  
The code is structured so Perplexity engineers can swap in bigger Sonar models or plug this straight into CI to catch regressions before they reach production.

---

## 🚀 Quick start

```bash
# 1 clone & install
git clone https://github.com/<your‑handle>/perplexity-guided-missile.git
cd perplexity-guided-missile
poetry install

# 2 add secrets
cp .env.example .env          # then edit
# PPLX_KEY="<your Perplexity API key>"
# GPT4O_KEY="<your OpenAI key>"

# 3 run an evaluation (baseline by default)
poetry run evaluate --mode baseline        # quick summary view
poetry run evaluate --mode prompt-tuned    # engineered prompt
poetry run evaluate --mode rag-assisted    # ground‑truth context injected

# optional flags
#   --limit 10        evaluate only first 10 Qs
#   --verbose / -v    print full table with answers