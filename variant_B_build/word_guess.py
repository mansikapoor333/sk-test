# Given a dictionary of 4-letter words and a secret target, implement a CLI guessing game. Up to 5 valid guesses.
# Invalid words (not in dict) rejected without consuming a turn. Hint: 1=correct position,
# 0=correct letter wrong position, -=not in word.

import random
import sys

DICTIONARY = {
    "bear", "bird", "cake", "door", "fish", "game", "hand", "jump", "kite", "love",
}


class WordGame:
    def __init__(self, dictionary: set, target: str = None):
        self.dictionary = dictionary
        self.target = target or random.choice(list(dictionary))
        self.attempts = 0
        self.max_attempts = 5

    def guess(self, word: str) -> str:
        if word not in self.dictionary:
            return "INVALID"
        self.attempts += 1
        if word == self.target:
            return "WIN"
        hint = self._generate_hint(word)
        if self.attempts >= self.max_attempts:
            return f"{hint} GAME_OVER"
        return hint

    def _generate_hint(self, word: str) -> str:
        target = list(self.target)
        hint = ["-"] * len(word)
        used = [False] * len(target)
        # First pass: exact matches
        for i, c in enumerate(word):
            if c == target[i]:
                hint[i] = "1"
                used[i] = True
        # Second pass: wrong position
        for i, c in enumerate(word):
            if hint[i] == "1": continue
            for j, tc in enumerate(target):
                if not used[j] and c == tc:
                    hint[i] = "0"
                    used[j] = True
                    break
        return "".join(hint)


def play(dictionary: set = DICTIONARY, target: str = None) -> None:
    game = WordGame(dictionary, target)
    while True:
        try:
            word = input().strip()
        except EOFError:
            break
        if not word:
            break
        result = game.guess(word)
        print(result)
        if result == "WIN" or "GAME_OVER" in result:
            break


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    play(target=target)

