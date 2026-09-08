#!/usr/bin/env python3
"""Interactive robot grid simulator controlled by keyboard."""

from __future__ import annotations

import sys
import termios
import tty


class Robot:
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    def position(self) -> tuple[int, int]:
        return (self.x, self.y)


class Simulator:
    GRID_SIZE = 11
    CENTER = GRID_SIZE // 2

    HELP = """
Controls:
  Arrow keys  Move up / down / left / right
  w a s d     Move up / left / down / right
  ?           Show this help
  q           Quit
"""

    def __init__(self):
        self.robot = Robot(self.CENTER, self.CENTER)

    def _render(self) -> str:
        lines = [
            "Robot Simulator",
            f"Position: ({self.robot.x - self.CENTER}, {self.robot.y - self.CENTER})",
            "",
        ]
        for row in range(self.GRID_SIZE):
            row_chars = []
            for col in range(self.GRID_SIZE):
                if row == self.robot.y and col == self.robot.x:
                    row_chars.append("R")
                elif row == self.CENTER and col == self.CENTER:
                    row_chars.append("+")
                else:
                    row_chars.append(".")
            lines.append(" ".join(row_chars))
        lines.extend(["", "Press ? for help, q to quit"])
        return "\n".join(lines)

    def _apply_key(self, key: str) -> bool:
        """Handle one key. Return False to exit."""
        moves = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
            "w": (0, -1),
            "s": (0, 1),
            "a": (-1, 0),
            "d": (1, 0),
        }
        if key in moves:
            dx, dy = moves[key]
            self.robot.move(dx, dy)
        elif key == "?":
            print(self.HELP)
            input("Press Enter to continue...")
        elif key == "q":
            return False
        return True

    def _read_key(self) -> str:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch != "\x1b":
                return ch.lower()

            # Arrow keys arrive as ESC [ A/B/C/D
            seq = sys.stdin.read(2)
            arrow_map = {"A": "up", "B": "down", "C": "right", "D": "left"}
            return arrow_map.get(seq[-1], "")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def run(self) -> tuple[int, int]:
        if not sys.stdin.isatty():
            return self._run_line_mode()

        print(self.HELP.strip())
        running = True
        while running:
            print("\033[2J\033[H", end="")
            print(self._render())
            key = self._read_key()
            running = self._apply_key(key)
        return self.robot.position()

    def _run_line_mode(self) -> tuple[int, int]:
        """Fallback when stdin is piped (tests / non-interactive)."""
        print(self.HELP.strip())
        aliases = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
        }
        while True:
            try:
                line = input("> ").strip().lower()
            except EOFError:
                break
            if not line:
                break
            if line == "q":
                break
            if line == "?":
                print(self.HELP)
                continue
            if line in aliases:
                dx, dy = aliases[line]
                self.robot.move(dx, dy)
                print(f"Position: {self.robot.position()}")
            else:
                print("Unknown command. Press ? for help.")
        return self.robot.position()


def main() -> None:
    sim = Simulator()
    x, y = sim.run()
    center = Simulator.CENTER
    print(f"Final position: ({x - center}, {y - center})")


if __name__ == "__main__":
    main()
