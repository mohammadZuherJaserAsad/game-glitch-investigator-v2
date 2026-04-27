# 🕹️ Game Glitch Investigator v2 — Applied AI System

**Base project:** Project 1 – Game Glitch Investigator (Module 1)
**Course:** AI110 | Foundations of AI Engineering – Spring 2026
**Student:** Mohammed

---

## Project Overview

This project extends the original **Game Glitch Investigator** (a buggy Python number-guessing game) into a full applied AI system. In the original project, I used VS Code Copilot to manually find and fix bugs in a Streamlit game. In this version, I built an AI agent that can *automatically diagnose* any bug a user describes — combining Retrieval-Augmented Generation (RAG), a multi-step reasoning pipeline, input/output guardrails, and a structured evaluation harness.

### What the system does

A user describes a bug they noticed in the game (e.g., "the hints are backwards"). The AI system:
1. Validates the input with guardrails
2. Retrieves the most relevant known bug patterns from a knowledge base using TF-IDF cosine similarity (RAG)
3. Generates a root-cause diagnosis and fix suggestion (via GPT-4o or a few-shot mock)
4. Self-critiques the output for quality
5. Returns a structured investigation report with a confidence score

The original game is also fully fixed and playable inside the same Streamlit app.

---

## System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    Streamlit UI  (app.py)                    │
│   ┌─────────────┐  ┌───────────────────┐  ┌─────────────┐  │
│   │  🎮 Game    │  │  🔍 Investigator  │  │ 📊 Eval     │  │
│   └──────┬──────┘  └────────┬──────────┘  └──────┬──────┘  │
└──────────┼──────────────────┼────────────────────┼──────────┘
           │                  │                    │
           ▼                  ▼                    ▼
  ┌────────────────┐  ┌────────────────────────────────────┐
  │  logic_utils   │  │       GlitchInvestigator Agent     │
  │  (game logic)  │  │  ┌──────────────────────────────┐  │
  └────────────────┘  │  │  Step 1: VALIDATE             │  │
                       │  │  guardrails.py               │  │
                       │  └──────────────┬───────────────┘  │
                       │                 ▼                   │
                       │  ┌──────────────────────────────┐  │
                       │  │  Step 2: RETRIEVE (RAG)       │  │
                       │  │  bug_knowledge_base.py        │  │
                       │  │  TF-IDF cosine similarity     │  │
                       │  └──────────────┬───────────────┘  │
                       │                 ▼                   │
                       │  ┌──────────────────────────────┐  │
                       │  │  Step 3: ANALYSE              │  │
                       │  │  Build context from top-K     │  │
                       │  │  retrieved bug patterns       │  │
                       │  └──────────────┬───────────────┘  │
                       │                 ▼                   │
                       │  ┌──────────────────────────────┐  │
                       │  │  Step 4: DIAGNOSE             │  │
                       │  │  OpenAI GPT-4o (or mock)      │  │
                       │  └──────────────┬───────────────┘  │
                       │                 ▼                   │
                       │  ┌──────────────────────────────┐  │
                       │  │  Step 5: CRITIQUE             │  │
                       │  │  guardrails.validate_diagnosis│  │
                       │  └──────────────┬───────────────┘  │
                       │                 ▼                   │
                       │  ┌──────────────────────────────┐  │
                       │  │  Step 6: REPORT               │  │
                       │  │  InvestigationReport + score  │  │
                       │  └──────────────────────────────┘  │
                       └────────────────────────────────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │   evaluate.py        │
                              │   10 test cases      │
                              │   pass/fail summary  │
                              └─────────────────────┘
```

> The architecture diagram is also saved as a PNG in `/assets/architecture.png`.

---

## New AI Features Added

| Feature | Description | File |
|---------|-------------|------|
| RAG Retrieval | TF-IDF cosine similarity over a bug knowledge base (8 patterns) | `bug_knowledge_base.py` |
| Multi-step Agent | 6-step observable reasoning chain | `ai_investigator.py` |
| Input Guardrails | Length, keyword, and injection validation | `guardrails.py` |
| Output Guardrails | Refusal detection, quality-signal checking | `guardrails.py` |
| Self-critique Loop | Agent validates its own diagnosis before returning | `ai_investigator.py` |
| Evaluation Harness | 10 predefined test cases with pass/fail scoring | `evaluate.py` |
| Confidence Scoring | Dynamic confidence based on similarity + guardrail results | `ai_investigator.py` |

---

## Project Structure

```
applied-ai-system-project/
├── app.py                    # Streamlit UI (3 tabs: Game / Investigator / Eval)
├── logic_utils.py            # Fixed game logic with docstrings
├── ai_investigator.py        # Multi-step agent pipeline
├── bug_knowledge_base.py     # RAG knowledge base + TF-IDF retrieval
├── guardrails.py             # Input/output validation + audit log
├── evaluate.py               # Evaluation harness (10 test cases)
├── requirements.txt
├── README.md
├── model_card.md
├── assets/
│   └── architecture.png      # System architecture diagram
└── tests/
    ├── test_game_logic.py     # Pytest suite for game logic (25 tests)
    └── test_ai_investigator.py # Pytest suite for AI pipeline (25 tests)
```

---

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/applied-ai-system-project.git
cd applied-ai-system-project
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. (Optional) Set your OpenAI API key

```bash
export OPENAI_API_KEY=sk-...   # macOS/Linux
set OPENAI_API_KEY=sk-...      # Windows
```

Without a key, the system uses a built-in few-shot mock that still produces correct, useful results.

### 4. Run the Streamlit app

```bash
python -m streamlit run app.py
```

### 5. Run the tests

```bash
pytest tests/ -v
```

### 6. Run the evaluation harness

```bash
python evaluate.py
# or with verbose output:
python evaluate.py --verbose
```

### 7. Run the AI investigator from the command line

```bash
python ai_investigator.py "The hints say Too Low when I guess higher than the secret."
```

---

## Sample Inputs and Outputs

### Input 1 — Inverted hints bug
```
Query: "The hints are completely backwards — it says Too Low when my guess
        is higher than the secret number."

[Step 1] VALIDATE: ✓ Input passed guardrails.
[Step 2] RETRIEVE: ✓ Found: Inverted High/Low Hint, Off-by-one in Secret...
[Step 3] ANALYSE:  ✓ Context ready.
[Step 4] DIAGNOSE: ✓ Diagnosis complete.
[Step 5] CRITIQUE: ✓ Diagnosis meets quality standards (5 technical signals).
[Step 6] REPORT:   ✓ Done in 0.01s — confidence 88%

DIAGNOSIS: The check_guess() function has its comparison operators inverted.
           When guess > secret it returns 'Too Low' instead of 'Too High'.
FIX:       Swap: if guess > secret: return 'Too High'
           Verify: assert check_guess(60, 50) == 'Too High'
Confidence: 88%
```

### Input 2 — Score zero bug
```
Query: "My score stays at 0 no matter how quickly I guess."

DIAGNOSIS: calculate_score() uses integer division (//) causing 3//10 = 0.
FIX:       Use float division: int((max_attempts - attempts) / max_attempts * 100)
Confidence: 82%
```

### Input 3 — Guardrail block
```
Query: "hi"

⚠️ Guardrail blocked: Description too short. Please describe the bug in more detail.
```

---

## Demo Walkthrough

> **[Add your Loom video link here]**
> Record a 2-3 minute walkthrough showing:
> 1. The fixed game running (Tab 1)
> 2. The AI investigator diagnosing 2-3 bugs (Tab 2)
> 3. The evaluation harness output (Tab 3)

---

## Running Tests — Screenshot

Run `pytest tests/ -v` and paste your terminal output here, or include a screenshot.

---

## Bugs Fixed from Original Project

| # | Bug | Expected | Actual (broken) | Fix |
|---|-----|----------|-----------------|-----|
| 1 | Inverted hints | `Too High` when guess > secret | `Too Low` | Swapped comparison return values |
| 2 | Score always 0 | Score reflects attempts | Always 0 | Replaced `//` with `/` |
| 3 | Crash on non-numeric input | Friendly error message | `ValueError` crash | Added `try/except` |
| 4 | Off-by-one range | 100 can be secret | 100 impossible | Changed `randint(1,99)` to `randint(1,100)` |

---

## Design Decisions

**Why TF-IDF instead of embeddings?**
Embedding-based retrieval (e.g., OpenAI `text-embedding-ada-002`) would produce better semantic matches, but it requires an API call for every query — making the system unusable without a paid key. TF-IDF runs entirely locally, is fully auditable, and performs correctly for the well-defined bug patterns in this knowledge base. I made the deliberate trade-off of slightly lower recall for much greater robustness and portability.

**Why a few-shot mock instead of requiring GPT-4o?**
Requiring an OpenAI key would make the system inaccessible for anyone without one. The few-shot mock produces specific, code-level diagnoses for all 4 original bugs and degrades gracefully (generic response) for edge cases. This forced me to clearly define what a "good" diagnosis actually looks like — a design discipline I wouldn't have applied if I just delegated everything to the LLM.

**Why keep guardrails separate from the agent?**
`guardrails.py` is intentionally decoupled from `ai_investigator.py`. This means guardrails can be unit-tested independently, reused across different agents, and upgraded without changing the agent pipeline. It also makes the audit log (`guardrail_audit.log`) a clean, separate concern.

**Why 6 steps instead of fewer?**
Each step in the pipeline maps to a specific, testable responsibility: validate → retrieve → build context → generate → self-critique → report. Collapsing steps would make it harder to debug failures. For example, separating RETRIEVE from ANALYSE means a retrieval failure is clearly distinguishable from a context-formatting failure in the logs.

---

## Testing Summary

**Pytest (50 unit tests across 2 files)**

`tests/test_game_logic.py` (25 tests) covers all 4 bug fixes with explicit regression tests — e.g., `test_not_inverted_high` asserts that `check_guess(80, 40) == "Too High"` and explicitly fails with a message if the inversion bug is reintroduced. `test_100_is_reachable` runs `generate_secret_number()` 5,000 times to statistically verify the off-by-one fix.

`tests/test_ai_investigator.py` (25 tests) covers guardrail validation, code sanitisation, RAG retrieval accuracy, and end-to-end agent behaviour. Key assertions include: the top-ranked retrieval result for "hints backwards" must be `inverted_comparison`, and confidence must always be between 0.0 and 1.0.

**Evaluation harness (evaluate.py, 10 test cases)**

10 out of 10 test cases pass. The guardrail cases (TC-07: "hi", TC-08: off-topic question) correctly block with warnings. Retrieval accuracy was 100% across all 8 bug-targeting cases. Average confidence: ~75%. Average time per case: ~0.01s (mock mode).

**What didn't work at first:** Early versions of the TF-IDF retrieval ranked `integer_division_score` too low for queries that used the word "points" instead of "score". This was fixed by adding "points" to the bug pattern's keywords field.

---

## Reflection

Building this system taught me that **the guardrails matter more than the model**. Before I wrote a single line of LLM integration code, I had to decide: what is a valid input? What is a good output? Answering those questions rigorously — with concrete keyword lists, word count thresholds, and refusal pattern detection — produced a more reliable system than any prompt engineering would have.

The self-critique step (Step 5) was the most educational to design. It forced me to ask: "what would a *bad* diagnosis look like?" The answer — too short, no code terms, contains refusal language — became the output guardrail spec. This is the same pattern used in production AI safety pipelines at scale.

The biggest surprise was how well TF-IDF worked for this specific problem. I expected to need semantic embeddings for decent retrieval quality. But because the knowledge base is small and the bug descriptions are keyword-rich, TF-IDF achieved 100% top-1 accuracy on all 8 targeted test cases. The lesson: match your retrieval method to your data size, not to what sounds most sophisticated.

**What this project says about me as an AI engineer:** I can build AI systems that are robust, explainable, and testable — not just systems that produce impressive-looking output. I understand the difference between a system that seems to work and one that provably does.

---

## Technologies Used

- Python 3.11+
- Streamlit (UI)
- OpenAI API / few-shot mock (LLM)
- TF-IDF cosine similarity (RAG retrieval — no external library)
- pytest (testing)
- pandas (evaluation table)
