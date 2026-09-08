from __future__ import annotations

# Multi-rover grid simulator.
# Commands: CREATE, MOVE, LEFT, RIGHT, PRINT (each line: COMMAND rover_id [args...]).
# Scenario 1 (blocking=False): rovers can share a cell.
# Scenario 2 (blocking=True): MOVE is ignored if another rover occupies the target cell.


class Rover:
    DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # N, E, S, W
    DIR_NAMES = ("N", "E", "S", "W")

    def __init__(self, rover_id: str, x: int = 0, y: int = 0, direction: int = 0):
        self.id = rover_id
        self.x = x
        self.y = y
        self.dir = direction


class Solution:
    def __init__(self, blocking: bool = False):
        self.blocking = blocking
        self.rovers: dict[str, Rover] = {}
        self.commands = {
            "CREATE": self.create,
            "MOVE": self.move,
            "LEFT": self.left,
            "RIGHT": self.right,
            "PRINT": self.print_rover,
        }

    def _parse_direction(self, name: str) -> int:
        return Rover.DIR_NAMES.index(name.upper())

    def _get_rover(self, args: list[str]) -> Rover | None:
        if not args:
            return None
        return self.rovers.get(args[0])

    def _is_occupied(self, x: int, y: int, exclude_id: str) -> bool:
        for rover_id, rover in self.rovers.items():
            if rover_id != exclude_id and rover.x == x and rover.y == y:
                return True
        return False

    def create(self, args: list[str]):
        if not args:
            return
        rover_id = args[0]
        if rover_id in self.rovers:
            return
        x, y, direction = 0, 0, 0
        if len(args) >= 4:
            x, y = int(args[1]), int(args[2])
            direction = self._parse_direction(args[3])
        self.rovers[rover_id] = Rover(rover_id, x, y, direction)

    def move(self, args: list[str]):
        rover = self._get_rover(args)
        if not rover:
            return
        dx, dy = Rover.DIRECTIONS[rover.dir]
        new_x, new_y = rover.x + dx, rover.y + dy
        if self.blocking and self._is_occupied(new_x, new_y, rover.id):
            return
        rover.x, rover.y = new_x, new_y

    def left(self, args: list[str]):
        rover = self._get_rover(args)
        if rover:
            rover.dir = (rover.dir - 1) % 4

    def right(self, args: list[str]):
        rover = self._get_rover(args)
        if rover:
            rover.dir = (rover.dir + 1) % 4

    def print_rover(self, args: list[str]):
        rover = self._get_rover(args)
        if rover:
            print(f"{rover.id}: ({rover.x}, {rover.y}) {Rover.DIR_NAMES[rover.dir]}")

    def execute(self, line: str):
        parts = line.strip().split()
        if not parts:
            return
        handler = self.commands.get(parts[0].upper())
        if handler:
            handler(parts[1:])

    def position(self, rover_id: str) -> tuple[int, int] | None:
        rover = self.rovers.get(rover_id)
        if rover is None:
            return None
        return (rover.x, rover.y)

    def positions(self) -> dict[str, tuple[int, int]]:
        return {rover_id: (rover.x, rover.y) for rover_id, rover in self.rovers.items()}

    @staticmethod
    def robot_sim(_commands: str = "", blocking: bool = False) -> dict[str, tuple[int, int]]:
        sim = Solution(blocking=blocking)
        while True:
            try:
                command = input().strip()
            except EOFError:
                break
            if not command:
                break
            sim.execute(command)
        return sim.positions()


if __name__ == "__main__":
    # Demo: no blocking (scenario 1). Use Solution(blocking=True) for scenario 2.
    solution = Solution(blocking=False)
    print(solution.robot_sim(""))
