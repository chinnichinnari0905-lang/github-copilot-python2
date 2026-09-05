from flask import Flask, jsonify, render_template, request

import sudoku_logic

app = Flask(__name__)

CURRENT = {
    'puzzle': None,
    'solution': None,
    'locked_cells': None,
    'difficulty': None,
    'hints_used': 0,
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty')
    try:
        if difficulty is not None:
            puzzle, solution, locked_cells = (
                sudoku_logic.generate_puzzle_for_difficulty(difficulty)
            )
            normalized_difficulty = difficulty.strip().lower()
            clues = sudoku_logic.DIFFICULTY_CLUES[normalized_difficulty]
        else:
            clues = int(request.args.get('clues', 35))
            puzzle, solution = sudoku_logic.generate_puzzle(clues)
            locked_cells = sudoku_logic.create_prefilled_mask(puzzle)
            normalized_difficulty = None
    except (TypeError, ValueError) as error:
        return jsonify({'error': str(error)}), 400

    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['locked_cells'] = locked_cells
    CURRENT['difficulty'] = normalized_difficulty
    CURRENT['hints_used'] = 0
    return jsonify({
        'puzzle': puzzle,
        'locked_cells': locked_cells,
        'difficulty': normalized_difficulty,
        'clues': clues,
    })

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board') if isinstance(data, dict) else None
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    if (
        not isinstance(board, list)
        or len(board) != sudoku_logic.SIZE
        or any(
            not isinstance(row, list) or len(row) != sudoku_logic.SIZE
            for row in board
        )
    ):
        return jsonify({'error': 'Board must be a 9x9 grid'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            value = board[i][j]
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or not sudoku_logic.MIN_VALUE <= value <= sudoku_logic.MAX_VALUE
                or value != solution[i][j]
            ):
                incorrect.append([i, j])
    complete = (
        not incorrect
        and sudoku_logic.validate_completed_board(board)
        and board == solution
    )
    return jsonify({'incorrect': incorrect, 'complete': complete})


@app.route('/hint', methods=['POST'])
def hint():
    data = request.json
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    locked_cells = CURRENT.get('locked_cells')
    if puzzle is None or solution is None or locked_cells is None:
        return jsonify({'error': 'No game in progress'}), 400
    board = data.get('board') if isinstance(data, dict) else None
    if (
        not isinstance(board, list)
        or len(board) != sudoku_logic.SIZE
        or any(
            not isinstance(row, list) or len(row) != sudoku_logic.SIZE
            for row in board
        )
    ):
        return jsonify({'error': 'Board must be a 9x9 grid'}), 400

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if not locked_cells[row][col] and board[row][col] == sudoku_logic.EMPTY:
                locked_cells[row][col] = True
                puzzle[row][col] = solution[row][col]
                CURRENT['hints_used'] += 1
                return jsonify({
                    'row': row,
                    'col': col,
                    'value': solution[row][col],
                    'hints_used': CURRENT['hints_used'],
                })

    return jsonify({'error': 'No empty cells remain'}), 400

if __name__ == '__main__':
    app.run(debug=True)