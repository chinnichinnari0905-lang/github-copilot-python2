import copy
import random


SIZE = 9
BOX_SIZE = 3
EMPTY = 0
MIN_VALUE = 1
MAX_VALUE = SIZE
DIFFICULTY_CLUES = {
    "easy": 45,
    "medium": 40,
    "hard": 35,
}

Board = list[list[int]]


def deep_copy(board: Board) -> Board:
    """Return an independent copy of a Sudoku board."""
    return copy.deepcopy(board)


def create_empty_board() -> Board:
    """Create a blank 9x9 Sudoku board."""
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board: Board, row: int, col: int, value: int) -> bool:
    """Return whether value can be placed at row and col."""
    for index in range(SIZE):
        if board[row][index] == value or board[index][col] == value:
            return False

    start_row = row - row % BOX_SIZE
    start_col = col - col % BOX_SIZE
    for box_row in range(start_row, start_row + BOX_SIZE):
        for box_col in range(start_col, start_col + BOX_SIZE):
            if board[box_row][box_col] == value:
                return False

    return True


def _candidate_values(board: Board, row: int, col: int) -> list[int]:
    return [
        value
        for value in range(MIN_VALUE, MAX_VALUE + 1)
        if is_safe(board, row, col, value)
    ]


def _find_empty_cell(board: Board) -> tuple[int, int, list[int]] | None:
    best_cell = None
    best_candidates = None
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                candidates = _candidate_values(board, row, col)
                if best_candidates is None or len(candidates) < len(best_candidates):
                    best_cell = row, col
                    best_candidates = candidates
                    if not candidates:
                        return row, col, candidates
    if best_cell is None or best_candidates is None:
        return None
    return best_cell[0], best_cell[1], best_candidates


def _has_valid_givens(board: Board) -> bool:
    """Return whether all non-empty values obey Sudoku constraints."""
    if len(board) != SIZE or any(len(row) != SIZE for row in board):
        return False

    for row in board:
        if any(value < EMPTY or value > MAX_VALUE for value in row):
            return False

    for row in range(SIZE):
        values = [value for value in board[row] if value != EMPTY]
        if len(values) != len(set(values)):
            return False
    for col in range(SIZE):
        values = [
            board[row][col] for row in range(SIZE) if board[row][col] != EMPTY
        ]
        if len(values) != len(set(values)):
            return False
    for start_row in range(0, SIZE, BOX_SIZE):
        for start_col in range(0, SIZE, BOX_SIZE):
            values = [
                board[row][col]
                for row in range(start_row, start_row + BOX_SIZE)
                for col in range(start_col, start_col + BOX_SIZE)
                if board[row][col] != EMPTY
            ]
            if len(values) != len(set(values)):
                return False
    return True


def solve_board(board: Board) -> bool:
    """Solve board in place and return whether a solution exists."""
    empty_cell = _find_empty_cell(board)
    if empty_cell is None:
        return validate_completed_board(board)

    row, col, candidates = empty_cell
    random.shuffle(candidates)
    for value in candidates:
        if is_safe(board, row, col, value):
            board[row][col] = value
            if solve_board(board):
                return True
            board[row][col] = EMPTY

    return False


def fill_board(board: Board) -> bool:
    """Compatibility alias for the original board-filling API."""
    return solve_board(board)


def count_solutions(board: Board, limit: int = 2) -> int:
    """Count board solutions, stopping once limit solutions are found."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    if not _has_valid_givens(board):
        return 0

    working_board = deep_copy(board)

    def count_from_current_board() -> int:
        empty_cell = _find_empty_cell(working_board)
        if empty_cell is None:
            return 1 if validate_completed_board(working_board) else 0

        row, col, candidates = empty_cell
        total = 0
        for value in candidates:
            working_board[row][col] = value
            total += count_from_current_board()
            working_board[row][col] = EMPTY
            if total >= limit:
                return limit
        return total

    return count_from_current_board()


def has_unique_solution(board: Board) -> bool:
    """Return whether board has exactly one valid solution."""
    return count_solutions(board, limit=2) == 1


def generate_complete_board() -> Board:
    """Generate and return a complete valid Sudoku board."""
    board = create_empty_board()
    solve_board(board)
    return board


def remove_cells(board: Board, clues: int) -> None:
    """Remove cells in place until the board contains clues values."""
    if not 0 <= clues <= SIZE * SIZE:
        raise ValueError("clues must be between 0 and 81")

    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)
    for row, col in cells[: SIZE * SIZE - clues]:
        board[row][col] = EMPTY


def generate_puzzle(clues: int = 35) -> tuple[Board, Board]:
    """Generate a puzzle and its complete solution with one solution."""
    if not 0 <= clues <= SIZE * SIZE:
        raise ValueError("clues must be between 0 and 81")

    solution = generate_complete_board()
    puzzle = deep_copy(solution)
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)

    for row, col in cells:
        if sum(cell != EMPTY for current_row in puzzle for cell in current_row) <= clues:
            break
        original_value = puzzle[row][col]
        puzzle[row][col] = EMPTY
        if not has_unique_solution(puzzle):
            puzzle[row][col] = original_value

    return puzzle, solution


def create_prefilled_mask(puzzle: Board) -> list[list[bool]]:
    """Return a mask identifying the non-empty, prefilled puzzle cells."""
    if len(puzzle) != SIZE or any(len(row) != SIZE for row in puzzle):
        raise ValueError("puzzle must be a 9x9 board")
    return [[cell != EMPTY for cell in row] for row in puzzle]


def generate_puzzle_for_difficulty(
    difficulty: str,
) -> tuple[Board, Board, list[list[bool]]]:
    """Generate a uniquely solvable puzzle and its prefilled-cell mask."""
    normalized_difficulty = difficulty.strip().lower()
    try:
        clues = DIFFICULTY_CLUES[normalized_difficulty]
    except KeyError as error:
        supported = ", ".join(DIFFICULTY_CLUES)
        raise ValueError(
            f"unsupported difficulty {difficulty!r}; choose {supported}"
        ) from error

    puzzle, solution = generate_puzzle(clues=clues)
    return puzzle, solution, create_prefilled_mask(puzzle)


def validate_completed_board(board: Board) -> bool:
    """Return whether board is a complete, valid Sudoku solution."""
    if len(board) != SIZE or any(len(row) != SIZE for row in board):
        return False

    expected_values = set(range(MIN_VALUE, MAX_VALUE + 1))
    if any(set(row) != expected_values for row in board):
        return False

    for col in range(SIZE):
        if {board[row][col] for row in range(SIZE)} != expected_values:
            return False

    for start_row in range(0, SIZE, BOX_SIZE):
        for start_col in range(0, SIZE, BOX_SIZE):
            values = {
                board[row][col]
                for row in range(start_row, start_row + BOX_SIZE)
                for col in range(start_col, start_col + BOX_SIZE)
            }
            if values != expected_values:
                return False

    return True
