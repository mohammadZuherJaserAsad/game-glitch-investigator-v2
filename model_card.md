# Model Card — Game Glitch Investigator v2

**Project:** Applied AI System (Project 4 — AI110 Spring 2026)
**Student:** Mohammed
**Base project:** Project 1 – Game Glitch Investigator

---

## 1. Base Project and Original Scope

### What the original project was

The original Game Glitch Investigator (Project 1, Module 1) was a Python number-guessing game built with Streamlit. An AI pair programmer (VS Code Copilot) had generated the game code, but the code contained deliberate bugs: inverted hints, a score that always returned zero, a crash on non-numeric input, and an off-by-one error in the random number range.

My task was to:
- Run the game and observe the bugs
- Use Copilot to explain and diagnose each bug
- Fix the bugs manually, informed by AI suggestions
- Write pytest tests to verify the fixes
- Document the process in a reflection

### What was added in this project (Project 4)

Rather than just having a fixed game, I built an *AI system* that automates the entire debugging workflow. The system takes a user's bug description as input and returns a structured diagnosis with a suggested fix — powered by RAG retrieval and a multi-step agent.

---

## 2. System Description

### Dataset / Knowledge Base

The system uses a hand-crafted **bug knowledge base** (`bug_knowledge_base.py`) containing 8 structured bug patterns, each with:
- A title and description
- Observable symptoms
- Retrieval keywords
- A fix description with before/after code examples
- A category tag (logic / crash / state / display)

This knowledge base was designed to cover the bugs present in the original starter code, plus common Streamlit state management bugs that students frequently encounter.

**Intended purpose:** Automated first-line diagnosis of Python game bugs described in plain language.

### Algorithmic Approach

The system uses **TF-IDF cosine similarity** for retrieval:
1. Every bug pattern's fields are concatenated into a single document string.
2. At query time, both the query and all documents are converted to TF-IDF vectors.
3. Cosine similarity is computed between the query vector and each document vector.
4. The top-K most similar bugs are returned as RAG context.

No external ML libraries (scikit-learn, etc.) are used — the TF-IDF math is implemented from scratch using Python's `math` module, making the retrieval fully transparent and auditable.

For generation, the system calls OpenAI's GPT-4o via a structured prompt containing the user's query and the retrieved context. A few-shot mock is used as a fallback when no API key is available.

---

## 3. AI Collaboration — How AI Was Used During Development

### Helpful AI suggestions

**Suggestion 1 — Guardrail structure:** When I asked Copilot "how should I validate AI-generated bug diagnoses?", it suggested checking for refusal patterns (e.g., "as an AI", "I cannot") as well as minimum word count and presence of technical code terms. This was directly implemented in `guardrails.validate_diagnosis()` as the `_REFUSAL_PATTERNS` and `_QUALITY_SIGNALS` lists. I accepted this suggestion because it was specific, testable, and improved output quality measurably.

**Suggestion 2 — TF-IDF from scratch:** Copilot suggested implementing the retrieval without scikit-learn to keep dependencies minimal and make the algorithm fully explainable. This was a good suggestion — it forced me to understand the math and made the code more portable. I accepted and implemented it.

### Flawed AI suggestion (rejected)

**Flawed suggestion — Embedding-based retrieval:** At one point, Copilot suggested using OpenAI's `text-embedding-ada-002` model for retrieval instead of TF-IDF. While this would produce higher-quality semantic matches, it would have introduced a hard dependency on a paid API call for every query, including at evaluation time. This made the system fragile and inaccessible without an API key. I rejected this suggestion and kept TF-IDF, which runs locally and produces correct results for the well-defined bug patterns in the knowledge base. The lesson: AI suggestions often optimise for power at the expense of simplicity and robustness.

---

## 4. Testing Results

The system was evaluated using `evaluate.py`, which runs 10 predefined test cases covering:
- 6 real bug descriptions (expected to pass guardrails and retrieve correctly)
- 2 guardrail edge cases (too short, off-topic)
- 2 additional state/display bugs

**Expected evaluation results:**

| Category | Pass Rate |
|----------|-----------|
| Logic bugs (hints, score, range) | 3/3 |
| Crash bugs | 1/1 |
| State bugs | 2/2 |
| Guardrail blocks | 2/2 |
| Display bugs | 1/1 |
| Display/reset bugs | 1/1 |
| **Total** | **10/10** |

Pytest coverage: 50 tests across `test_game_logic.py` (25) and `test_ai_investigator.py` (25).

---

## 5. Limitations and Biases

### Known limitations

1. **Small knowledge base:** The retrieval can only identify bugs that are present in the 8-pattern knowledge base. Novel bugs not represented will be retrieved with low confidence and the diagnosis may be generic.

2. **TF-IDF keyword sensitivity:** The retrieval depends on keyword overlap. A user who describes a bug using unusual vocabulary (e.g., "the answer feedback is the wrong direction") might get a lower similarity score than a user who says "hints are backwards", even if they're describing the same bug. Semantic embeddings would handle this better.

3. **Mock LLM limitations:** The few-shot mock selects from 4 fixed example responses based on keyword matching. It handles the 4 core bugs well but will produce generic responses for edge cases.

4. **No user history:** The system treats every query independently. A user who asks a follow-up question loses all previous context.

### Potential biases

- The knowledge base only covers bugs from the CodePath starter code. Real-world game bugs are far more varied.
- The quality signals in `validate_diagnosis()` were designed for Python debugging language. Diagnoses in other languages or domains might be incorrectly flagged as low quality.

### Future improvements

1. Add 20+ more bug patterns to the knowledge base.
2. Replace TF-IDF with a local embedding model (e.g., `sentence-transformers`) for semantic retrieval without API dependency.
3. Add multi-turn conversation so the agent can ask clarifying questions.
4. Integrate with a live code analysis tool (AST parsing) to directly inspect submitted code rather than relying on user descriptions.

---

## 6. Reflection on System Design

Building this system taught me that **responsible AI design means building in scepticism at every layer**. The guardrails module was the most important part of the project — not the LLM call. Without input validation, the agent would waste compute (and money) on off-topic queries. Without output validation, a vague or hallucinated diagnosis would be presented with the same confidence as a precise one.

The self-critique step (Step 5) was inspired by the "chain-of-thought + verification" pattern from Module 4. Even a simple rule-based check (is the diagnosis long enough? Does it mention code terms?) meaningfully filtered out low-quality responses during testing.

The biggest design decision was **working without a mandatory API key**. Making the few-shot mock a first-class citizen rather than a stub forced me to think about what the system actually needed to produce — specific, testable, code-level diagnoses — rather than relying on a black-box LLM to cover for vague design.

---

## 7. Ethics Checklist

| Question | Answer |
|----------|--------|
| Does the system make consequential decisions about people? | No — it suggests code fixes only. |
| Could a misdiagnosis cause harm? | Low risk — the worst outcome is a wasted debugging attempt. |
| Is the system's reasoning explainable? | Yes — all 6 agent steps are logged and visible in the UI. |
| Does the system disclose it uses AI? | Yes — the UI clearly labels the AI Investigator tab and explains the pipeline. |
| Were test cases diverse? | Partially — coverage could be improved with more edge cases and non-English bug descriptions. |
