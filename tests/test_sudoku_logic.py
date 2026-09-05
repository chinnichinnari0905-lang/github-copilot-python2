import sudoku_logic


VALID_SOLUTION = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


def assert_valid_board(board):
    expected_values = set(range(1, sudoku_logic.SIZE + 1))

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(set(row) == expected_values for row in board)
    assert all(
        {board[row][column] for row in range(sudoku_logic.SIZE)}
        == expected_values
        for column in range(sudoku_logic.SIZE)
    )
    assert all(
        {
            board[row][column]
            for row in range(box_row, box_row + 3)
            for column in range(box_column, box_column + 3)
        }
        == expected_values
        for box_row in range(0, sudoku_logic.SIZE, 3)
        for box_column in range(0, sudoku_logic.SIZE, 3)
    )


def test_create_empty_board_has_expected_shape_and_values():
    board = sudoku_logic.create_empty_board()

    assert len(board) == 9
    assert all(len(row) == 9 for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_deep_copy_does_not_share_nested_rows():
    copied_board = sudoku_logic.deep_copy(VALID_SOLUTION)

    copied_board[0][0] = 0

    assert VALID_SOLUTION[0][0] == 5


def test_is_safe_accepts_valid_move_and_rejects_row_column_and_box_conflicts():
    board = sudoku_logic.deep_copy(VALID_SOLUTION)
    board[0][0] = sudoku_logic.EMPTY

    assert sudoku_logic.is_safe(board, 0, 0, 5)
    assert not sudoku_logic.is_safe(board, 0, 0, 3)
    assert not sudoku_logic.is_safe(board, 0, 0, 6)
    assert not sudoku_logic.is_safe(board, 0, 0, 8)


def test_fill_board_creates_a_valid_complete_board():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board)
    assert_valid_board(board)


def test_fill_board_solves_a_partially_filled_board():
    board = sudoku_logic.deep_copy(VALID_SOLUTION)
    board[0][0] = sudoku_logic.EMPTY
    board[4][4] = sudoku_logic.EMPTY

    assert sudoku_logic.fill_board(board)
    assert board == VALID_SOLUTION


def test_solve_board_solves_a_board_in_place():
    board = sudoku_logic.deep_copy(VALID_SOLUTION)
    board[0][0] = sudoku_logic.EMPTY

    assert sudoku_logic.solve_board(board)
    assert board == VALID_SOLUTION


def test_valid_completed_puzzle_has_exactly_one_solution():
    assert sudoku_logic.count_solutions(VALID_SOLUTION) == 1
    assert sudoku_logic.has_unique_solution(VALID_SOLUTION)


def test_unsolvable_puzzle_has_zero_solutions():
    puzzle = sudoku_logic.create_empty_board()
    puzzle[0][:8] = list(range(1, 9))
    puzzle[1][8] = 9

    assert sudoku_logic.count_solutions(puzzle) == 0
    assert not sudoku_logic.has_unique_solution(puzzle)


def test_puzzle_with_multiple_solutions_is_capped_at_two():
    puzzle = sudoku_logic.create_empty_board()

    assert sudoku_logic.count_solutions(puzzle) == 2
    assert not sudoku_logic.has_unique_solution(puzzle)


def test_count_solutions_stops_at_requested_limit():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.count_solutions(board, limit=2) == 2
    assert board == sudoku_logic.create_empty_board()


def test_generate_complete_board_is_valid():
    board = sudoku_logic.generate_complete_board()

    assert sudoku_logic.validate_completed_board(board)


def test_generated_puzzles_are_dynamic_not_a_predefined_board():
    first_puzzle, first_solution = sudoku_logic.generate_puzzle(clues=40)
    second_puzzle, second_solution = sudoku_logic.generate_puzzle(clues=40)

    assert first_puzzle != second_puzzle or first_solution != second_solution
    assert first_solution != VALID_SOLUTION or first_puzzle != VALID_SOLUTION
    assert sudoku_logic.count_solutions(first_puzzle, limit=2) == 1
    assert sudoku_logic.count_solutions(second_puzzle, limit=2) == 1


def test_remove_cells_leaves_requested_number_of_clues():
    board = sudoku_logic.deep_copy(VALID_SOLUTION)

    sudoku_logic.remove_cells(board, clues=35)

    assert sum(cell != sudoku_logic.EMPTY for row in board for cell in row) == 35


def test_generate_puzzle_returns_puzzle_and_complete_solution_with_requested_clues():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=40)

    assert_valid_board(solution)
    assert all(
        puzzle[row][column] in (sudoku_logic.EMPTY, solution[row][column])
        for row in range(sudoku_logic.SIZE)
        for column in range(sudoku_logic.SIZE)
    )
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 40
    assert sudoku_logic.has_unique_solution(puzzle)


def test_generate_puzzle_default_has_default_number_of_clues():
    puzzle, _ = sudoku_logic.generate_puzzle()

    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35


def test_difficulty_clue_counts_are_ordered():
    assert (
        sudoku_logic.DIFFICULTY_CLUES["easy"]
        > sudoku_logic.DIFFICULTY_CLUES["medium"]
        > sudoku_logic.DIFFICULTY_CLUES["hard"]
    )


def test_difficulty_puzzles_have_unique_solutions_and_prefilled_masks():
    for difficulty in ("easy", "medium", "hard"):
        for _ in range(2):
            puzzle, solution, prefilled = (
                sudoku_logic.generate_puzzle_for_difficulty(difficulty)
            )

            assert_valid_board(solution)
            assert sudoku_logic.count_solutions(puzzle, limit=2) == 1
            assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == sum(
                cell
                for row in prefilled
                for cell in row
            )
            assert prefilled == sudoku_logic.create_prefilled_mask(puzzle)
            assert all(
                puzzle[row][col] != sudoku_logic.EMPTY
                for row in range(sudoku_logic.SIZE)
                for col in range(sudoku_logic.SIZE)
                if prefilled[row][col]
            )
            assert all(
                puzzle[row][col] == sudoku_logic.EMPTY
                for row in range(sudoku_logic.SIZE)
                for col in range(sudoku_logic.SIZE)
                if not prefilled[row][col]
            )


def test_difficulty_puzzles_have_more_clues_at_lower_difficulty():
    clue_counts = {}
    for difficulty in ("easy", "medium", "hard"):
        puzzle, _, _ = sudoku_logic.generate_puzzle_for_difficulty(difficulty)
        clue_counts[difficulty] = sum(
            cell != sudoku_logic.EMPTY for row in puzzle for cell in row
        )

    assert clue_counts["easy"] > clue_counts["medium"] > clue_counts["hard"]


def test_generated_easy_medium_and_hard_style_puzzles_are_unique():
    for clues in (45, 40, 35):
        puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)

        assert sudoku_logic.validate_completed_board(solution)
        assert sudoku_logic.count_solutions(puzzle, limit=2) == 1


def test_validate_completed_board_rejects_duplicate_values():
    invalid_board = sudoku_logic.deep_copy(VALID_SOLUTION)
    invalid_board[0][0] = invalid_board[0][1]

    assert not sudoku_logic.validate_completed_board(invalid_board)
