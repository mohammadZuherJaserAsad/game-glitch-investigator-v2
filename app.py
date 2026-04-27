"""
app.py
------
Streamlit UI for the Game Glitch Investigator v2.

Tabs:
  🎮 Play Game        – the fixed number-guessing game
  🔍 AI Investigator  – RAG + agent bug diagnosis tool
  📊 Evaluation       – run the test harness from the browser
"""

import streamlit as st

from logic_utils import (
    generate_secret_number,
    check_guess,
    validate_input,
    calculate_score,
    get_hint_message,
)
from ai_investigator import GlitchInvestigator
from guardrails import validate_bug_report

st.set_page_config(page_title="Game Glitch Investigator v2", page_icon="🕹️", layout="centered")


def _init_game_state() -> None:
    """Initialise all game session-state keys if not already present."""
    defaults = {
        "secret": generate_secret_number(),
        "attempts": 0,
        "max_attempts": 10,
        "game_over": False,
        "won": False,
        "score": 0,
        "last_hint": "",
        "history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


_init_game_state()

tab_game, tab_ai, tab_eval = st.tabs(["🎮 Play Game", "🔍 AI Investigator", "📊 Evaluation"])

# ── TAB 1: Play Game ──────────────────────────────────────────────────────
with tab_game:
    st.title("🕹️ Number Guessing Game")
    st.caption("Guess a number between 1 and 100. You have 10 attempts.")

    col_attempts, col_score = st.columns(2)
    col_attempts.metric("Attempts used", st.session_state.attempts)
    col_score.metric("Score", st.session_state.score)

    if st.session_state.game_over:
        if st.session_state.won:
            st.success(f"🎉 You got it in {st.session_state.attempts} attempt(s)! Score: {st.session_state.score}")
        else:
            st.error(f"💀 Out of attempts! The secret was **{st.session_state.secret}**.")

    if not st.session_state.game_over:
        with st.form("guess_form", clear_on_submit=True):
            raw = st.text_input("Your guess:", placeholder="Enter a number 1–100")
            submitted = st.form_submit_button("Guess")

        if submitted and raw:
            is_valid, value, err_msg = validate_input(raw)
            if not is_valid:
                st.warning(err_msg)
            else:
                st.session_state.attempts += 1
                attempts_left = st.session_state.max_attempts - st.session_state.attempts
                hint = get_hint_message(value, st.session_state.secret, attempts_left)
                st.session_state.last_hint = hint
                st.session_state.history.append((value, hint))

                if check_guess(value, st.session_state.secret) == "Correct!":
                    st.session_state.game_over = True
                    st.session_state.won = True
                    st.session_state.score = calculate_score(st.session_state.attempts, st.session_state.max_attempts)
                    st.rerun()
                elif st.session_state.attempts >= st.session_state.max_attempts:
                    st.session_state.game_over = True
                    st.rerun()

    if st.session_state.attempts > 0 and st.session_state.last_hint:
        st.info(f"💬 {st.session_state.last_hint}")

    if st.session_state.history:
        with st.expander("Guess history"):
            for g, h in st.session_state.history:
                st.write(f"  • **{g}** → {h}")

    if st.button("🔄 New Game"):
        for key in ("secret", "attempts", "game_over", "won", "score", "last_hint", "history"):
            del st.session_state[key]
        st.rerun()

# ── TAB 2: AI Investigator ────────────────────────────────────────────────
with tab_ai:
    st.title("🔍 AI Bug Investigator")
    st.markdown("Describe a bug you noticed in the game. The AI agent will retrieve similar known bugs, diagnose the root cause, and suggest a fix.")

    with st.expander("ℹ️ How it works"):
        st.markdown("""
**6-step agent pipeline:**

1. **VALIDATE** – Guardrails check your input is a real bug description.
2. **RETRIEVE** – TF-IDF RAG searches the bug knowledge base for similar patterns.
3. **ANALYSE** – Retrieved context is packaged into a structured prompt.
4. **DIAGNOSE** – LLM (or few-shot mock) generates a root-cause explanation.
5. **CRITIQUE** – Self-check: is the diagnosis specific and actionable?
6. **REPORT** – Confidence score + full structured report.

Set `OPENAI_API_KEY` in your environment to use GPT-4o; otherwise the system uses a deterministic few-shot mock.
        """)

    bug_input = st.text_area("Describe the bug:", height=120,
        placeholder="e.g. 'The hints are completely backwards — when I guess higher than the secret it says Too Low instead of Too High.'")

    if st.button("🕵️ Investigate", type="primary"):
        if not bug_input.strip():
            st.warning("Please enter a bug description first.")
        else:
            is_valid, msg = validate_bug_report(bug_input)
            if not is_valid:
                st.error(f"⚠️ Guardrail blocked: {msg}")
            else:
                with st.spinner("Agent is investigating…"):
                    agent = GlitchInvestigator(verbose=False)
                    report = agent.investigate(bug_input)

                st.subheader("Investigation Report")
                col_conf, col_time = st.columns(2)
                col_conf.metric("Confidence", f"{report.confidence:.0%}")
                col_time.metric("Time", f"{report.elapsed_seconds:.2f}s")

                if report.warnings:
                    for w in report.warnings:
                        st.warning(w)

                st.markdown("#### 🧠 Diagnosis")
                st.write(report.diagnosis)
                st.markdown("#### 🔧 Suggested Fix")
                st.write(report.suggested_fix)

                if report.retrieved_bugs:
                    st.markdown("#### 📚 Similar Known Bugs (RAG)")
                    for bug in report.retrieved_bugs:
                        score = bug.get("similarity_score", 0)
                        with st.expander(f"[{score:.2f}] {bug['title']}"):
                            st.write(f"**Category:** {bug['category']}")
                            st.write(f"**Description:** {bug['description']}")
                            st.code(bug["code_before"], language="python")
                            st.caption("→ Fixed:")
                            st.code(bug["code_after"], language="python")

                st.markdown("#### 🪞 Self-Critique")
                st.caption(report.self_critique)

                with st.expander("Agent steps"):
                    for step in report.steps:
                        icon = "✅" if step.status == "ok" else ("⚠️" if step.status == "warning" else "❌")
                        st.write(f"{icon} **Step {step.step_number} – {step.name}**: {step.detail}")

    st.markdown("---")
    st.caption("Try one of these example queries:")
    for ex in [
        "The hints say Too Low when I guess higher than the secret number.",
        "My score is always 0 even when I guess in 2 tries.",
        "The game crashes when I type letters into the input box.",
        "The number 100 never seems to appear as the secret.",
    ]:
        st.button(ex, key=f"ex_{ex[:20]}")

# ── TAB 3: Evaluation ─────────────────────────────────────────────────────
with tab_eval:
    st.title("📊 System Evaluation")
    st.markdown("Run the full evaluation harness against 10 predefined test cases to verify the AI system's reliability.")

    if st.button("▶️ Run Evaluation", type="primary"):
        import io, contextlib
        from evaluate import run_evaluation, print_summary

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            results = run_evaluation(verbose=False)
            exit_code = print_summary(results)

        st.code(buf.getvalue(), language="text")

        passed = sum(1 for r in results if r.passed)
        total = len(results)
        if passed == total:
            st.success(f"🎉 All {total} tests passed!")
        else:
            st.warning(f"{total - passed} test(s) failed out of {total}.")

        import pandas as pd
        rows = [{"ID": r.case.id, "Status": "✓ PASS" if r.passed else "✗ FAIL",
                 "Confidence": f"{r.actual_confidence:.0%}", "Top Bug": r.top_bug_id or "—",
                 "Time (s)": r.elapsed, "Tags": ", ".join(r.case.tags)} for r in results]
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
