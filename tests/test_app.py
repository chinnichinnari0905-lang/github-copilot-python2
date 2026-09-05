import sudoku_logic
from app import CURRENT, app


def test_index_renders_game_page():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Sudoku Game" in response.data


def test_new_game_returns_requested_puzzle_shape_and_clue_count():
    client = app.test_client()

    response = client.get("/new?clues=40")

    assert response.status_code == 200
    puzzle = response.get_json()["puzzle"]
    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 40
    assert "solution" not in response.get_json()
    assert response.get_json()["locked_cells"] == sudoku_logic.create_prefilled_mask(puzzle)


def test_new_game_supports_named_difficulty():
    client = app.test_client()

    response = client.get("/new?difficulty=easy")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["difficulty"] == "easy"
    assert payload["clues"] == sudoku_logic.DIFFICULTY_CLUES["easy"]
    assert payload["locked_cells"] == sudoku_logic.create_prefilled_mask(
        payload["puzzle"]
    )


def test_new_game_rejects_unknown_difficulty():
    client = app.test_client()

    response = client.get("/new?difficulty=expert")

    assert response.status_code == 400
    assert "unsupported difficulty" in response.get_json()["error"]


def test_new_game_rejects_invalid_clues():
    client = app.test_client()

    response = client.get("/new?clues=not-a-number")

    assert response.status_code == 400
    assert "invalid literal" in response.get_json()["error"]


def test_check_reports_no_incorrect_cells_for_current_solution():
    client = app.test_client()
    new_game_response = client.get("/new?clues=40")
    puzzle = new_game_response.get_json()["puzzle"]
    solution = CURRENT["solution"]
    response = client.post("/check", json={"board": solution})

    assert puzzle != solution
    assert response.status_code == 200
    assert response.get_json() == {"incorrect": [], "complete": True}


def test_check_reports_coordinates_that_differ_from_solution():
    client = app.test_client()
    client.get("/new")
    current = CURRENT["solution"]
    board = sudoku_logic.deep_copy(current)
    board[0][0] = (board[0][0] % sudoku_logic.SIZE) + 1

    response = client.post("/check", json={"board": board})

    assert response.status_code == 200
    assert response.get_json() == {"incorrect": [[0, 0]], "complete": False}


def test_check_marks_incomplete_cells_without_revealing_solution():
    client = app.test_client()
    client.get("/new?difficulty=easy")

    response = client.post("/check", json={"board": sudoku_logic.create_empty_board()})

    payload = response.get_json()
    assert response.status_code == 200
    assert len(payload["incorrect"]) > 0
    assert payload["complete"] is False
    assert "solution" not in payload
    assert "value" not in payload


def test_check_does_not_complete_for_invalid_cell_values():
    client = app.test_client()
    client.get("/new?difficulty=easy")
    board = sudoku_logic.deep_copy(CURRENT["solution"])
    board[0][0] = 0

    response = client.post("/check", json={"board": board})

    assert response.status_code == 200
    assert response.get_json()["complete"] is False
    assert response.get_json()["incorrect"] == [[0, 0]]


def test_check_requires_a_game_in_progress(monkeypatch):
    monkeypatch.setitem(CURRENT, "puzzle", None)
    monkeypatch.setitem(CURRENT, "solution", None)
    client = app.test_client()

    response = client.post("/check", json={"board": sudoku_logic.create_empty_board()})

    assert response.status_code == 400
    assert response.get_json() == {"error": "No game in progress"}


def test_hint_returns_one_cell_without_exposing_solution():
    client = app.test_client()
    new_game = client.get("/new?difficulty=easy").get_json()

    response = client.post("/hint", json={"board": new_game["puzzle"]})

    assert response.status_code == 200
    hint = response.get_json()
    assert set(hint) == {"row", "col", "value", "hints_used"}
    assert new_game["locked_cells"][hint["row"]][hint["col"]] is False
    assert hint["hints_used"] == 1


def test_hint_does_not_overwrite_an_existing_user_entry():
    client = app.test_client()
    new_game = client.get("/new?difficulty=easy").get_json()
    board = sudoku_logic.deep_copy(new_game["puzzle"])
    editable = next(
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if not new_game["locked_cells"][row][col]
    )
    board[editable[0]][editable[1]] = 1

    response = client.post("/hint", json={"board": board})

    assert response.status_code == 200
    hint = response.get_json()
    assert (hint["row"], hint["col"]) != editable


def test_hint_rejects_request_when_no_empty_cells_remain():
    client = app.test_client()
    client.get("/new?difficulty=easy")
    board = sudoku_logic.deep_copy(CURRENT["solution"])

    response = client.post("/hint", json={"board": board})

    assert response.status_code == 400
    assert response.get_json() == {"error": "No empty cells remain"}
