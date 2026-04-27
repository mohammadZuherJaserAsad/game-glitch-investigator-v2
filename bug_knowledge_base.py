"""
bug_knowledge_base.py
---------------------
Structured knowledge base of common Python game bugs used by the RAG pipeline.

Each entry represents a known bug pattern with:
  - id          : unique slug
  - title       : short human-readable name
  - description : what the bug is and why it occurs
  - symptoms    : observable behaviours that signal this bug
  - keywords    : terms used during retrieval (TF-IDF matching)
  - fix         : plain-language description of the correct fix
  - code_before : example of buggy code
  - code_after  : example of the corrected code
  - category    : bug category (logic / crash / state / display)

This module also exposes a `retrieve_similar_bugs()` function that uses
TF-IDF cosine similarity to return the K most relevant bugs for a given
user query — forming the "R" in RAG.
"""

from __future__ import annotations

import math
import re
from typing import Any

# ---------------------------------------------------------------------------
# Knowledge base
# ---------------------------------------------------------------------------

BUG_PATTERNS: list[dict[str, Any]] = [
    {
        "id": "inverted_comparison",
        "title": "Inverted High/Low Hint",
        "description": (
            "The comparison operators are swapped so 'Too High' and 'Too Low' "
            "hints are reversed. Guessing above the secret returns 'Too Low' "
            "instead of 'Too High'."
        ),
        "symptoms": [
            "hint says Too Low when guess is above secret",
            "hint says Too High when guess is below secret",
            "hints are always wrong",
            "direction is backwards",
            "wrong hint message",
        ],
        "keywords": [
            "hint", "too high", "too low", "wrong direction", "inverted",
            "comparison", "backwards", "guess", "greater", "less",
        ],
        "fix": (
            "Swap the comparison: use `if guess > secret: return 'Too High'` "
            "and `if guess < secret: return 'Too Low'`."
        ),
        "code_before": (
            "if guess > secret:\n"
            "    return 'Too Low'   # WRONG\n"
            "elif guess < secret:\n"
            "    return 'Too High'  # WRONG"
        ),
        "code_after": (
            "if guess > secret:\n"
            "    return 'Too High'\n"
            "elif guess < secret:\n"
            "    return 'Too Low'"
        ),
        "category": "logic",
    },
    {
        "id": "off_by_one_range",
        "title": "Off-by-One in Secret Number Range",
        "description": (
            "random.randint(1, 99) excludes 100, making it impossible to "
            "guess 100. The correct call is random.randint(1, 100)."
        ),
        "symptoms": [
            "100 never appears",
            "number 100 cannot be the secret",
            "range is wrong",
            "missing highest value",
            "off by one",
        ],
        "keywords": [
            "randint", "range", "100", "off by one", "secret number",
            "random", "generate", "boundary", "inclusive",
        ],
        "fix": "Change `random.randint(1, 99)` to `random.randint(1, 100)`.",
        "code_before": "secret = random.randint(1, 99)",
        "code_after":  "secret = random.randint(1, 100)",
        "category": "logic",
    },
    {
        "id": "integer_division_score",
        "title": "Score Always Zero (Integer Division Bug)",
        "description": (
            "Using `//` (integer division) when calculating the score causes "
            "it to round down to 0 for any reasonable number of attempts "
            "(e.g. 3 // 10 == 0)."
        ),
        "symptoms": [
            "score is always 0",
            "score never changes",
            "score stays at zero",
            "points not awarded",
            "score not updating",
        ],
        "keywords": [
            "score", "zero", "integer division", "floor division", "//",
            "points", "calculate", "attempts", "reward",
        ],
        "fix": (
            "Replace integer division with float division: "
            "`ratio = (max_attempts - attempts) / max_attempts` "
            "then `return int(ratio * 100)`."
        ),
        "code_before": "score = (max_attempts - attempts) // max_attempts * 100",
        "code_after":  "score = int((max_attempts - attempts) / max_attempts * 100)",
        "category": "logic",
    },
    {
        "id": "unhandled_non_numeric_input",
        "title": "Crash on Non-Numeric Input",
        "description": (
            "Calling `int(user_input)` without a try/except block raises a "
            "ValueError and crashes the app when the user types letters or "
            "leaves the field empty."
        ),
        "symptoms": [
            "game crashes on letters",
            "ValueError",
            "app crashes on empty input",
            "typing letters breaks game",
            "invalid input causes error",
            "crash non-numeric",
        ],
        "keywords": [
            "ValueError", "int()", "crash", "non-numeric", "letters",
            "empty input", "try except", "validate", "parse",
        ],
        "fix": (
            "Wrap `int(user_input)` in a try/except ValueError block and "
            "return an error message instead of crashing."
        ),
        "code_before": (
            "guess = int(user_input)  # crashes if user_input is 'abc'"
        ),
        "code_after": (
            "try:\n"
            "    guess = int(user_input)\n"
            "except ValueError:\n"
            "    return False, None, 'Please enter a valid number.'"
        ),
        "category": "crash",
    },
    {
        "id": "session_state_not_initialised",
        "title": "Session State Not Initialised (Streamlit)",
        "description": (
            "Accessing `st.session_state['secret']` before it is set causes "
            "a KeyError on the first page load. State variables must be "
            "initialised with a guard clause."
        ),
        "symptoms": [
            "KeyError on first load",
            "session state error",
            "AttributeError session",
            "game resets on refresh",
            "state not persisted",
            "streamlit refresh breaks game",
        ],
        "keywords": [
            "session_state", "KeyError", "streamlit", "initialise",
            "init", "first load", "refresh", "persist",
        ],
        "fix": (
            "Add `if 'secret' not in st.session_state:` guards at the top "
            "of the script to initialise all state variables before use."
        ),
        "code_before": (
            "secret = st.session_state['secret']  # KeyError on first run"
        ),
        "code_after": (
            "if 'secret' not in st.session_state:\n"
            "    st.session_state['secret'] = generate_secret_number()\n"
            "secret = st.session_state['secret']"
        ),
        "category": "state",
    },
    {
        "id": "score_not_reset_on_new_game",
        "title": "Score Carries Over Between Games",
        "description": (
            "When the player starts a new game, the attempt counter and score "
            "are not reset in session state, so old values persist."
        ),
        "symptoms": [
            "score carries over",
            "attempts not reset",
            "new game same score",
            "attempts keep counting",
            "game does not reset",
        ],
        "keywords": [
            "reset", "new game", "attempts", "counter", "score", "carry over",
            "session_state", "restart",
        ],
        "fix": (
            "When the 'New Game' button is clicked, reset all relevant "
            "session state keys: attempts, score, game_over, and secret."
        ),
        "code_before": (
            "if st.button('New Game'):\n"
            "    st.session_state['secret'] = generate_secret_number()"
        ),
        "code_after": (
            "if st.button('New Game'):\n"
            "    st.session_state['secret'] = generate_secret_number()\n"
            "    st.session_state['attempts'] = 0\n"
            "    st.session_state['game_over'] = False\n"
            "    st.session_state['score'] = 0"
        ),
        "category": "state",
    },
    {
        "id": "guess_accepted_after_game_over",
        "title": "Guesses Accepted After Game Over",
        "description": (
            "The game continues to accept and process guesses after the "
            "player has won or run out of attempts because there is no "
            "`game_over` guard around the input handler."
        ),
        "symptoms": [
            "can guess after winning",
            "game keeps going after correct",
            "guesses still accepted",
            "game does not stop",
            "input not disabled",
        ],
        "keywords": [
            "game over", "guard", "win", "attempts", "disable",
            "stop", "input", "finished",
        ],
        "fix": (
            "Wrap the guess-processing block with "
            "`if not st.session_state.get('game_over', False):`."
        ),
        "code_before": (
            "if st.button('Guess'):\n"
            "    process_guess()"
        ),
        "code_after": (
            "if not st.session_state.get('game_over', False):\n"
            "    if st.button('Guess'):\n"
            "        process_guess()"
        ),
        "category": "logic",
    },
    {
        "id": "hint_shown_before_first_guess",
        "title": "Hint Displayed Before First Guess",
        "description": (
            "A residual hint from a previous game is shown on screen before "
            "the player makes their first guess in a new session."
        ),
        "symptoms": [
            "hint shown at start",
            "message before first guess",
            "old hint visible",
            "hint on page load",
        ],
        "keywords": [
            "hint", "display", "first guess", "initial", "page load",
            "empty state", "message",
        ],
        "fix": (
            "Only render the hint widget when `st.session_state['attempts'] > 0`."
        ),
        "code_before": "st.write(st.session_state['last_hint'])",
        "code_after": (
            "if st.session_state.get('attempts', 0) > 0:\n"
            "    st.write(st.session_state['last_hint'])"
        ),
        "category": "display",
    },
]

# ---------------------------------------------------------------------------
# TF-IDF Retrieval helpers
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    """Lowercase and split text into word tokens."""
    return re.findall(r"[a-z0-9]+", text.lower())


def _build_document(bug: dict[str, Any]) -> str:
    """Combine all searchable fields of a bug entry into one string."""
    parts = [
        bug["title"],
        bug["description"],
        " ".join(bug["symptoms"]),
        " ".join(bug["keywords"]),
        bug["fix"],
    ]
    return " ".join(parts)


def _tf(tokens: list[str]) -> dict[str, float]:
    """Compute term frequency for a list of tokens."""
    counts: dict[str, int] = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    total = max(len(tokens), 1)
    return {t: c / total for t, c in counts.items()}


def _idf(corpus: list[list[str]]) -> dict[str, float]:
    """Compute inverse document frequency across a corpus of token lists."""
    n = len(corpus)
    df: dict[str, int] = {}
    for doc in corpus:
        for term in set(doc):
            df[term] = df.get(term, 0) + 1
    return {term: math.log(n / (1 + freq)) for term, freq in df.items()}


def _cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """Compute cosine similarity between two TF-IDF vectors."""
    common = set(vec_a) & set(vec_b)
    if not common:
        return 0.0
    dot = sum(vec_a[t] * vec_b[t] for t in common)
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def retrieve_similar_bugs(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    """Retrieve the top-K most relevant bugs for a given query using TF-IDF.

    This is the retrieval component of the RAG pipeline. It converts both
    the query and every knowledge-base document into TF-IDF vectors and
    returns the entries with the highest cosine similarity.

    Args:
        query: Natural-language description of a bug or symptom.
        top_k: Maximum number of results to return.

    Returns:
        List of bug-pattern dicts sorted by relevance (most relevant first),
        each augmented with a "similarity_score" float field.
    """
    corpus_docs = [_tokenize(_build_document(bug)) for bug in BUG_PATTERNS]
    query_tokens = _tokenize(query)

    idf_weights = _idf(corpus_docs + [query_tokens])

    def tfidf_vec(tokens: list[str]) -> dict[str, float]:
        tf_vals = _tf(tokens)
        return {t: tf_vals[t] * idf_weights.get(t, 0.0) for t in tf_vals}

    query_vec = tfidf_vec(query_tokens)
    scored: list[tuple[float, dict[str, Any]]] = []
    for bug, doc_tokens in zip(BUG_PATTERNS, corpus_docs):
        doc_vec = tfidf_vec(doc_tokens)
        score = _cosine_similarity(query_vec, doc_vec)
        result = dict(bug)
        result["similarity_score"] = round(score, 4)
        scored.append((score, result))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored[:top_k]]
