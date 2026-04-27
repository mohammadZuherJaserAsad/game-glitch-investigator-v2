"""
test_game_logic.py — Pytest suite for logic_utils.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from logic_utils import check_guess, validate_input, calculate_score, generate_secret_number, get_hint_message


class TestCheckGuess:
    def test_too_high(self):
        assert check_guess(60, 50) == "Too High"
    def test_too_low(self):
        assert check_guess(30, 50) == "Too Low"
    def test_correct(self):
        assert check_guess(50, 50) == "Correct!"
    def test_boundary_100(self):
        assert check_guess(100, 99) == "Too High"
    def test_boundary_1(self):
        assert check_guess(1, 2) == "Too Low"
    def test_off_by_one_above(self):
        assert check_guess(51, 50) == "Too High"
    def test_off_by_one_below(self):
        assert check_guess(49, 50) == "Too Low"
    def test_not_inverted_high(self):
        """FIX VERIFICATION: high guess must NOT return 'Too Low' (starter bug)."""
        result = check_guess(80, 40)
        assert result != "Too Low", "Bug detected: hints are still inverted!"
        assert result == "Too High"
    def test_not_inverted_low(self):
        """FIX VERIFICATION: low guess must NOT return 'Too High' (starter bug)."""
        result = check_guess(10, 90)
        assert result != "Too High", "Bug detected: hints are still inverted!"
        assert result == "Too Low"


class TestValidateInput:
    def test_valid_integer(self):
        valid, value, msg = validate_input("42")
        assert valid is True and value == 42 and msg == ""
    def test_valid_with_spaces(self):
        valid, value, _ = validate_input("  75  ")
        assert valid is True and value == 75
    def test_letters_cause_no_crash(self):
        """FIX VERIFICATION: non-numeric input must NOT raise ValueError."""
        valid, value, msg = validate_input("abc")
        assert valid is False and value is None and "valid" in msg.lower()
    def test_empty_string(self):
        valid, value, msg = validate_input("")
        assert valid is False and value is None
    def test_negative_number(self):
        valid, value, msg = validate_input("-5")
        assert valid is False and "1 and 100" in msg
    def test_zero(self):
        assert not validate_input("0")[0]
    def test_101_out_of_range(self):
        assert not validate_input("101")[0]
    def test_boundary_1(self):
        valid, value, _ = validate_input("1")
        assert valid is True and value == 1
    def test_boundary_100(self):
        valid, value, _ = validate_input("100")
        assert valid is True and value == 100
    def test_float_string(self):
        assert not validate_input("3.14")[0]
    def test_whitespace_only(self):
        assert not validate_input("   ")[0]


class TestCalculateScore:
    def test_perfect_score_one_attempt(self):
        assert calculate_score(1, 10) == 90
    def test_score_not_zero_for_reasonable_attempts(self):
        """FIX VERIFICATION: score must NOT be 0 for 3 attempts out of 10."""
        score = calculate_score(3, 10)
        assert score != 0, "Bug detected: integer division still causing score = 0!"
        assert score == 70
    def test_zero_attempts_max_score(self):
        assert calculate_score(0, 10) == 100
    def test_all_attempts_used(self):
        assert calculate_score(10, 10) == 0
    def test_halfway(self):
        assert calculate_score(5, 10) == 50
    def test_score_in_valid_range(self):
        for attempts in range(1, 11):
            assert 0 <= calculate_score(attempts, 10) <= 100


class TestGenerateSecretNumber:
    def test_in_default_range(self):
        for _ in range(200):
            assert 1 <= generate_secret_number() <= 100
    def test_100_is_reachable(self):
        """FIX VERIFICATION: 100 must be possible (starter used randint(1,99))."""
        seen = {generate_secret_number() for _ in range(5000)}
        assert 100 in seen, "Bug detected: 100 is never generated (off-by-one in range)!"
    def test_custom_range(self):
        for _ in range(100):
            assert 5 <= generate_secret_number(5, 10) <= 10


class TestGetHintMessage:
    def test_correct_returns_celebration(self):
        msg = get_hint_message(50, 50, 5)
        assert "Correct" in msg or "🎉" in msg
    def test_high_guess_in_message(self):
        assert "Too High" in get_hint_message(70, 40, 5)
    def test_low_guess_in_message(self):
        assert "Too Low" in get_hint_message(20, 80, 5)
    def test_urgency_on_last_attempts(self):
        msg = get_hint_message(30, 50, 1)
        assert "⚠" in msg or "Last" in msg
