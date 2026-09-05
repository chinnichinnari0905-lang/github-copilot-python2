# GitHub Copilot Instructions — Flask Sudoku Project

## Project Goal

Build a maintainable, responsive and accessible Sudoku web application using Python Flask, HTML, CSS and JavaScript.

The application must extend the legacy Sudoku implementation while following modern software development practices.

## General Development Rules

- Write clean, readable and maintainable code.
- Prefer simple solutions over unnecessary complexity.
- Use meaningful variable, function and class names.
- Keep functions small and focused on one responsibility.
- Avoid duplicated logic.
- Add comments only where they improve understanding.
- Preserve existing working functionality unless there is a clear reason to change it.
- Do not make unrelated changes.
- Before implementing a major feature, explain the proposed approach.
- Prefer modular and reusable components.
- Handle errors gracefully.

## Python Standards

- Use modern Python syntax.
- Follow PEP 8 style.
- Use type hints where practical.
- Keep Sudoku logic separate from Flask route logic.
- Avoid putting business logic directly inside Flask routes.
- Use helper functions for reusable Sudoku operations.
- Do not use global mutable state unnecessarily.

## Sudoku Rules

The Sudoku board is 9x9.

Every row must contain numbers 1-9 without duplicates.

Every column must contain numbers 1-9 without duplicates.

Every 3x3 box must contain numbers 1-9 without duplicates.

Generated puzzles must have exactly one valid solution.

A puzzle with:
- zero solutions must be rejected
- more than one solution must be rejected
- exactly one solution may be accepted

Solution counting should stop as soon as two solutions are found.

## Difficulty

The application must support:

- Easy
- Medium
- Hard

Difficulty must control the number of prefilled cells.

Prefilled cells must be locked and must not be editable by the user.

## Game Features

Implement:

- Difficulty selector
- Sudoku puzzle generation
- Unique solution validation
- Timer
- Hint button
- Check button
- Completion message
- Top 10 leaderboard
- Player name
- Completion time
- Difficulty
- Number of hints used
- Local storage persistence
- Dark mode toggle

## Hint

The Hint button must:

- Fill one currently empty cell
- Insert the correct solution value
- Lock the hinted cell
- Increase the hint counter

## Check

The Check button must:

- Compare user-entered values with the correct solution
- Highlight incorrect entries
- Not modify correct entries
- Provide clear visual feedback

## Completion

When the user correctly completes the puzzle:

- Show a congratulatory completion message.
- Stop the timer.
- Save the score to localStorage.
- Update the Top 10 leaderboard.
- Store player name, time, difficulty and hints used.

## Leaderboard

The leaderboard must:

- Store at most 10 entries.
- Persist using browser localStorage.
- Survive page refreshes and browser restarts.
- Sort scores by fastest completion time.
- Display player name, time, difficulty and hints used.

## Frontend

Use semantic HTML where appropriate.

The UI must:

- Work on desktop and mobile.
- Support light mode and dark mode.
- Keep text readable.
- Keep buttons accessible.
- Maintain consistent spacing.
- Avoid layout shifts.

The Sudoku grid must visually distinguish the 3x3 boxes using alternating styling.

## Accessibility

Use:

- semantic HTML
- labels for controls
- keyboard-friendly controls
- sufficient contrast
- visible focus states
- descriptive button text
- accessible status messages where appropriate

## Testing

Testing is required before major refactoring.

Do not remove existing tests just to make them pass.

Tests should cover:

- board creation
- Sudoku validity
- safe moves
- solving
- solution counting
- unique solution generation
- puzzle generation
- difficulty behavior
- board validation

Run tests with:

python -m pytest -q

All tests should pass before moving to the next major development phase.

## GitHub Copilot Usage

Use Copilot as an assistant, not as an unquestioned authority.

For every major change:

1. Make the requirement explicit.
2. Ask Copilot to explain its approach when needed.
3. Review generated code.
4. Accept or reject suggestions intentionally.
5. Run tests.
6. Fix failures before moving forward.

Do not ask Copilot to rebuild the entire application in one step.

## Scope Control

When modifying code:

- Change only files necessary for the current task.
- Do not overwrite unrelated working functionality.
- Do not introduce unnecessary frameworks.
- Do not add dependencies unless required.
- Do not change the project architecture without explaining why.

## Important Requirement

The final project must satisfy all provided Sudoku project requirements and rubric criteria, including:

- Flask Sudoku game
- Easy, Medium and Hard difficulty
- Exactly one solution per generated puzzle
- Locked prefilled cells
- Invalid move feedback
- Check functionality
- Hint functionality
- Timer
- Top 10 leaderboard
- localStorage persistence
- Dark mode
- Responsive design
- Alternating 3x3 box styling
- Testing
- Copilot milestone screenshots
- Maintainable code