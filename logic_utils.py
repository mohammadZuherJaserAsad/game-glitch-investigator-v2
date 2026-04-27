"""
logic_utils.py
--------------
Core game logic for the Number Guessing Game.

All functions are pure (no Streamlit state dependencies) so they can be
imported by the AI Investigator, tests, and the Streamlit UI independently.

Bugs fixed from the original starter code:
  1. check_guess: comparison was inverted ("Too High" / "Too Low" were swapped).
  2. generate_secret_number: range was (1, 99) — now correctly (1, 100) inclusive.
  3. calculate_score: integer division caused score to always round to 0.
  4. validate_input: did not handle non-numeric strings, causing a crash.
"""

import random


def generate_secret_number(low: int = 1, high: int = 100) -> int:
    """Generate a random secret number within the given inclusive range.

    Args:
        low: Lower bound of the range (inclusive). Defaults to 1.
        high: Upper bound of the range (inclusive). Defaults to 100.

    Returns:
        A random integer between low and high (inclusive).

    # FIX: Original code used random.randint(1, 99), excluding 100.
    # AGENT MODE helped identify this off-by-one error and updated the range.
    """
    return random.randint(low, high)


def check_guess(guess: int, secret: int) -> str:
    """Compare a player's guess to the secret number and return a hint.

    Args:
        guess: The player's integer guess.
        secret: The secret number to guess.

    Returns:
        "Too High"  if the guess is above the secret.
        "Too Low"   if the guess is below the secret.
        "Correct!"  if the guess matches the secret exactly.

    # FIX: Original code had the comparison backwards:
    #   if guess > secret: return "Too Low"   <-- WRONG
    #   if guess < secret: return "Too High"  <-- WRONG
    # Copilot (inline chat) identified the inversion and suggested the correct logic.
    # Verified by running: check_guess(60, 50) -> should be "Too High".
    """
    if guess > secret:
        return "Too High"
    elif guess < secret:
        return "Too Low"
    else:
        return "Correct!"


def validate_input(user_input: str) -> tuple[bool, int | None, str]:
    """Validate and parse a player's raw string input into an integer guess.

    Args:
        user_input: Raw string typed by the player.

    Returns:
        A tuple of (is_valid, parsed_int_or_None, error_message_or_empty_string).

    Examples:
        >>> validate_input("42")
        (True, 42, "")
        >>> validate_input("abc")
        (False, None, "Please enter a valid number.")
        >>> validate_input("-5")
        (False, None, "Guess must be between 1 and 100.")

    # FIX: Original code called int() directly on user input without a try/except,
    # causing a ValueError crash on non-numeric input.
    # Copilot suggested wrapping in try/except and adding range validation.
    """
    if not user_input or user_input.strip() == "":
        return False, None, "Please enter a number."
    try:
        value = int(user_input.strip())
    except ValueError:
        return False, None, "Please enter a valid number."
    if value < 1 or value > 100:
        return False, None, "Guess must be between 1 and 100."
    return True, value, ""


def calculate_score(attempts: int, max_attempts: int = 10) -> int:
    """Calculate a score based on how efficiently the player guessed.

    A lower attempt count yields a higher score. The maximum score is 100.

    Args:
        attempts: Number of guesses the player used.
        max_attempts: Maximum guesses allowed (default 10).

    Returns:
        Integer score between 0 and 100.

    # FIX: Original code used integer division (//) which collapsed all scores
    # to 0 for any reasonable attempt count (e.g. 3 // 10 == 0).
    # Changed to float division then int() rounding for correct behaviour.
    """
    if attempts <= 0:
        return 100
    ratio = max(0.0, (max_attempts - attempts) / max_attempts)
    return int(ratio * 100)


def get_hint_message(guess: int, secret: int, attempts_left: int) -> str:
    """Return a descriptive hint message combining direction and urgency.

    Args:
        guess: The player's current guess.
        secret: The secret number.
        attempts_left: Remaining guesses allowed.

    Returns:
        A human-readable hint string.
    """
    direction = check_guess(guess, secret)
    if direction == "Correct!":
        return "🎉 Correct! You guessed it!"
    urgency = ""
    if attempts_left <= 2:
        urgency = " ⚠️ Last chances!"
    elif attempts_left <= 4:
        urgency = " Be careful!"
    return f"{direction}{urgency}"
