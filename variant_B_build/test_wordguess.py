"""Tests for word_guess.WordGame and play CLI."""

import runpy
import sys
import unittest
from unittest.mock import patch

from word_guess import WordGame, play


SMALL_DICT = {"bear", "cake", "fish", "bird"}


def _inputs(*words):
  """Build a mocked input sequence that ends the interactive loop."""
  return list(words) + [EOFError]


class TestWordGameGuess(unittest.TestCase):
  """Core guess/hint behavior."""

  def test_invalid_word_returns_invalid_without_using_turn(self):
    game = WordGame(SMALL_DICT, target="bear")
    self.assertEqual(game.guess("zzzz"), "INVALID")
    self.assertEqual(game.attempts, 0)
    self.assertEqual(game.guess("fish"), "----")
    self.assertEqual(game.attempts, 1)

  def test_correct_guess_returns_win(self):
    game = WordGame(SMALL_DICT, target="bear")
    self.assertEqual(game.guess("bear"), "WIN")
    self.assertEqual(game.attempts, 1)

  def test_exact_position_only_hint(self):
    game = WordGame({"bear", "belt"}, target="bear")
    self.assertEqual(game.guess("belt"), "11--")

  def test_wrong_position_hint(self):
    game = WordGame(SMALL_DICT, target="bear")
    self.assertEqual(game.guess("cake"), "-0-0")

  def test_exact_and_wrong_position_hint(self):
    game = WordGame(SMALL_DICT, target="bear")
    self.assertEqual(game.guess("bird"), "1-0-")

  def test_no_matching_letters(self):
    game = WordGame(SMALL_DICT, target="bear")
    self.assertEqual(game.guess("fish"), "----")

  def test_mixed_exact_and_wrong_position(self):
    game = WordGame({"bear", "bare"}, target="bear")
    self.assertEqual(game.guess("bare"), "1000")

  def test_duplicate_letters_matched_once(self):
    game = WordGame({"book", "obob"}, target="book")
    self.assertEqual(game.guess("obob"), "001-")

  def test_game_over_on_fifth_valid_guess(self):
    game = WordGame(SMALL_DICT, target="bear")
    wrong = ["cake", "fish", "bird", "cake"]
    for word in wrong:
      self.assertNotIn("GAME_OVER", game.guess(word))
    self.assertEqual(game.guess("fish"), "---- GAME_OVER")
    self.assertEqual(game.attempts, 5)

  def test_win_before_max_attempts(self):
    game = WordGame(SMALL_DICT, target="bear")
    game.guess("cake")
    game.guess("fish")
    self.assertEqual(game.guess("bear"), "WIN")
    self.assertEqual(game.attempts, 3)

  @patch("word_guess.random.choice", return_value="fish")
  def test_random_target_when_not_provided(self, mock_choice):
    game = WordGame(SMALL_DICT)
    mock_choice.assert_called_once()
    self.assertEqual(game.target, "fish")


class TestEdgeCases(unittest.TestCase):
  """Empty inputs, win/loss boundaries, and attempt counting."""

  def test_empty_guess_is_invalid_and_does_not_use_turn(self):
    game = WordGame(SMALL_DICT, target="bear")
    self.assertEqual(game.guess(""), "INVALID")
    self.assertEqual(game.attempts, 0)

  def test_empty_target_string_falls_back_to_random_choice(self):
    with patch("word_guess.random.choice", return_value="bear") as mock_choice:
      game = WordGame(SMALL_DICT, target="")
    mock_choice.assert_called_once()
    self.assertEqual(game.target, "bear")

  def test_empty_target_and_empty_guess_in_dictionary_wins(self):
    game = WordGame({""}, target="seed")
    game.target = ""
    self.assertEqual(game.guess(""), "WIN")

  def test_win_on_first_guess(self):
    game = WordGame(SMALL_DICT, target="fish")
    self.assertEqual(game.guess("fish"), "WIN")
    self.assertEqual(game.attempts, 1)

  def test_win_on_fifth_guess_beats_game_over(self):
    game = WordGame(SMALL_DICT, target="bear")
    game.guess("cake")
    game.guess("fish")
    game.guess("bird")
    game.guess("cake")
    self.assertEqual(game.guess("bear"), "WIN")
    self.assertEqual(game.attempts, 5)

  def test_all_five_guesses_wrong_returns_game_over_not_win(self):
    game = WordGame(SMALL_DICT, target="bear")
    wrong_guesses = ["cake", "fish", "bird", "cake", "fish"]
    results = [game.guess(word) for word in wrong_guesses]

    self.assertNotIn("WIN", results)
    self.assertEqual(results[-1], "---- GAME_OVER")
    self.assertEqual(game.attempts, 5)

  def test_invalid_guesses_do_not_count_toward_game_over(self):
    game = WordGame(SMALL_DICT, target="bear")
    sequence = ["zzzz", "", "cake", "nope", "fish", "bad", "bird", "x", "cake", "fish"]
    results = [game.guess(word) for word in sequence]

    self.assertEqual(results.count("INVALID"), 5)
    self.assertEqual(results[-1], "---- GAME_OVER")
    self.assertEqual(game.attempts, 5)

  def test_close_guess_is_not_win(self):
    game = WordGame({"bear", "bare"}, target="bear")
    result = game.guess("bare")
    self.assertEqual(result, "1000")
    self.assertNotEqual(result, "WIN")

class TestPlayCli(unittest.TestCase):
  """Interactive play() loop."""

  def test_play_win_prints_and_stops(self):
    with patch("builtins.input", side_effect=_inputs("cake", "bear")), patch(
      "builtins.print"
    ) as mock_print:
      play(SMALL_DICT, target="bear")
    mock_print.assert_any_call("-0-0")
    mock_print.assert_any_call("WIN")
    self.assertEqual(mock_print.call_count, 2)

  def test_play_game_over_prints_and_stops(self):
    guesses = ["cake", "fish", "bird", "cake", "fish"]
    with patch("builtins.input", side_effect=_inputs(*guesses)), patch(
      "builtins.print"
    ) as mock_print:
      play(SMALL_DICT, target="bear")
    self.assertEqual(mock_print.call_args_list[-1][0][0], "---- GAME_OVER")

  def test_play_invalid_word_does_not_end_game(self):
    with patch("builtins.input", side_effect=_inputs("zzzz", "bear")), patch(
      "builtins.print"
    ) as mock_print:
      play(SMALL_DICT, target="bear")
    mock_print.assert_any_call("INVALID")
    mock_print.assert_any_call("WIN")

  def test_play_empty_line_exits_without_calling_guess(self):
    with patch("builtins.input", side_effect=[""]), patch(
      "builtins.print"
    ) as mock_print:
      play(SMALL_DICT, target="bear")
    mock_print.assert_not_called()

  def test_play_eof_exits(self):
    with patch("builtins.input", side_effect=EOFError), patch(
      "builtins.print"
    ) as mock_print:
      play(SMALL_DICT, target="bear")
    mock_print.assert_not_called()

  def test_play_all_wrong_guesses_end_with_game_over(self):
    guesses = ["cake", "fish", "bird", "cake", "fish"]
    with patch("builtins.input", side_effect=_inputs(*guesses)), patch(
      "builtins.print"
    ) as mock_print:
      play(SMALL_DICT, target="bear")
    printed = [call.args[0] for call in mock_print.call_args_list]
    self.assertNotIn("WIN", printed)
    self.assertEqual(printed[-1], "---- GAME_OVER")


class TestMainEntrypoint(unittest.TestCase):
  """Module __main__ guard."""

  def test_main_with_fixed_target(self):
    with patch("builtins.input", side_effect=_inputs("bear")), patch(
      "builtins.print"
    ) as mock_print:
      with patch.object(sys, "argv", ["word_guess.py", "bear"]):
        runpy.run_path("word_guess.py", run_name="__main__")
    mock_print.assert_called_once_with("WIN")

  def test_main_without_target_uses_random(self):
    with patch("word_guess.random.choice", return_value="cake"), patch(
      "builtins.input", side_effect=_inputs("cake")
    ), patch("builtins.print") as mock_print:
      with patch.object(sys, "argv", ["word_guess.py"]):
        runpy.run_path("word_guess.py", run_name="__main__")
    mock_print.assert_called_once_with("WIN")


if __name__ == "__main__":
  unittest.main()
