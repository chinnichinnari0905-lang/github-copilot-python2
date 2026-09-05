const SIZE = 9;
const LEADERBOARD_KEY = 'sudokuLeaderboard';
const COMPLETED_GAMES_KEY = 'sudokuCompletedGames';
const THEME_KEY = 'sudoku-theme';

const state = {
  difficulty: 'medium',
  puzzle: [],
  lockedCells: [],
  hintsUsed: 0,
  elapsedSeconds: 0,
  startedAt: null,
  timerId: null,
  completed: false,
  scoreSaved: false,
  gameId: null,
};

function element(id) {
  return document.getElementById(id);
}

function createGameId() {
  if (window.crypto && typeof window.crypto.randomUUID === 'function') {
    return window.crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function setMessage(message, kind = '') {
  const messageElement = element('message');
  messageElement.textContent = message;
  messageElement.dataset.kind = kind;
}

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
  const remainder = (seconds % 60).toString().padStart(2, '0');
  return `${minutes}:${remainder}`;
}

function updateTimer() {
  element('timer').textContent = formatTime(state.elapsedSeconds);
}

function stopTimer() {
  if (state.timerId !== null) {
    updateElapsedTime();
    window.clearInterval(state.timerId);
    state.timerId = null;
  }
  state.startedAt = null;
}

function updateElapsedTime() {
  if (state.startedAt === null) return;
  state.elapsedSeconds = Math.floor((Date.now() - state.startedAt) / 1000);
  updateTimer();
}

function startTimer() {
  stopTimer();
  state.startedAt = Date.now();
  updateElapsedTime();
  state.timerId = window.setInterval(updateElapsedTime, 250);
}

function readBoard() {
  return Array.from({ length: SIZE }, (_, row) =>
    Array.from({ length: SIZE }, (_, col) => {
      const input = document.querySelector(
        `.sudoku-cell[data-row="${row}"][data-col="${col}"]`,
      );
      return input.value ? Number(input.value) : 0;
    }),
  );
}

function getConflictMessage(input, board, value) {
  const row = Number(input.dataset.row);
  const col = Number(input.dataset.col);
  const boxRow = Math.floor(row / 3) * 3;
  const boxCol = Math.floor(col / 3) * 3;
  const boxValues = [];
  for (let boxRowIndex = boxRow; boxRowIndex < boxRow + 3; boxRowIndex += 1) {
    for (let boxColIndex = boxCol; boxColIndex < boxCol + 3; boxColIndex += 1) {
      boxValues.push(board[boxRowIndex][boxColIndex]);
    }
  }

  if (board[row].filter((cell) => cell === value).length > 1) {
    return 'This number conflicts with another number in the row.';
  }
  if (board.some((line, index) => index !== row && line[col] === value)) {
    return 'This number conflicts with another number in the column.';
  }
  if (boxValues.filter((cell) => cell === value).length > 1) {
    return 'This number conflicts with another number in the 3x3 box.';
  }
  return '';
}

function validateCellInput(input) {
  const rawValue = input.value;
  input.classList.remove('incorrect');
  input.removeAttribute('aria-invalid');

  if (rawValue === '') {
    setMessage('');
    return true;
  }
  if (!/^[1-9]$/.test(rawValue)) {
    input.value = '';
    input.classList.add('incorrect');
    input.setAttribute('aria-invalid', 'true');
    return false;
  }

  const message = getConflictMessage(input, readBoard(), Number(rawValue));
  if (message) {
    input.classList.add('incorrect');
    input.setAttribute('aria-invalid', 'true');
    setMessage(message, 'error');
    return false;
  }

  setMessage('Entry is valid.', 'success');
  return true;
}

function createBoard() {
  const board = element('sudoku-board');
  board.replaceChildren();
  for (let row = 0; row < SIZE; row += 1) {
    const rowElement = document.createElement('div');
    rowElement.className = 'sudoku-row';
    for (let col = 0; col < SIZE; col += 1) {
      const input = document.createElement('input');
      input.className = 'sudoku-cell';
      input.type = 'text';
      input.inputMode = 'numeric';
      input.maxLength = 1;
      input.dataset.row = row;
      input.dataset.col = col;
      input.setAttribute('aria-label', `Row ${row + 1}, column ${col + 1}`);
      input.addEventListener('input', () => {
        if (input.value.length > 1) {
          input.value = input.value.slice(-1);
        }
        if (!/^[1-9]$/.test(input.value) && input.value !== '') {
          input.value = '';
          input.classList.add('incorrect');
          input.setAttribute('aria-invalid', 'true');
          setMessage('Enter a number from 1 to 9.', 'error');
          return;
        }
        validateCellInput(input);
      });
      rowElement.appendChild(input);
    }
    board.appendChild(rowElement);
  }
}

function renderPuzzle() {
  createBoard();
  for (let row = 0; row < SIZE; row += 1) {
    for (let col = 0; col < SIZE; col += 1) {
      const input = document.querySelector(
        `.sudoku-cell[data-row="${row}"][data-col="${col}"]`,
      );
      if (state.lockedCells[row][col]) {
        input.value = state.puzzle[row][col];
        input.disabled = true;
        input.classList.add('prefilled');
      }
    }
  }
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Request failed.');
  }
  return data;
}

async function startNewGame() {
  stopTimer();
  state.difficulty = element('difficulty').value;
  try {
    const data = await requestJson(
      `/new?difficulty=${encodeURIComponent(state.difficulty)}`,
    );
    state.puzzle = data.puzzle;
    state.lockedCells = data.locked_cells;
    state.hintsUsed = 0;
    state.elapsedSeconds = 0;
    state.completed = false;
    state.scoreSaved = false;
    state.gameId = createGameId();
    element('hint-count').textContent = '0';
    updateTimer();
    renderPuzzle();
    setMessage('');
    startTimer();
  } catch (error) {
    setMessage(error.message, 'error');
  }
}

async function checkPuzzle() {
  if (state.completed) return;
  try {
    const data = await requestJson('/check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ board: readBoard() }),
    });
    document.querySelectorAll('.sudoku-cell').forEach((input) => {
      if (!input.disabled) {
        input.classList.remove('incorrect');
        input.removeAttribute('aria-invalid');
      }
    });
    data.incorrect.forEach(([row, col]) => {
      const input = document.querySelector(
        `.sudoku-cell[data-row="${row}"][data-col="${col}"]`,
      );
      input.classList.add('incorrect');
      input.setAttribute('aria-invalid', 'true');
    });
    if (data.complete) {
      completeGame();
    } else {
      const incorrectCount = data.incorrect.length;
      setMessage(
        `${incorrectCount} cell${incorrectCount === 1 ? '' : 's'} incorrect or incomplete.`,
        'error',
      );
    }
  } catch (error) {
    setMessage(error.message, 'error');
  }
}

function completeGame() {
  if (state.completed || state.scoreSaved) return;
  stopTimer();
  const saved = saveLeaderboardEntry();
  if (saved) {
    state.scoreSaved = true;
    state.completed = true;
    setMessage(
      `Congratulations! You solved it in ${formatTime(state.elapsedSeconds)}.`,
      'success',
    );
    renderLeaderboard();
  } else {
    setMessage(
      'Puzzle solved, but a player name is required to save your score.',
      'error',
    );
  }
}

async function useHint() {
  if (state.completed) return;
  try {
    const data = await requestJson('/hint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ board: readBoard() }),
    });
    const input = document.querySelector(
      `.sudoku-cell[data-row="${data.row}"][data-col="${data.col}"]`,
    );
    input.value = data.value;
    input.disabled = true;
    input.classList.add('prefilled', 'hinted');
    state.lockedCells[data.row][data.col] = true;
    state.puzzle[data.row][data.col] = data.value;
    state.hintsUsed = data.hints_used;
    element('hint-count').textContent = state.hintsUsed;
    setMessage('A hint was added and the cell is now locked.', 'success');
  } catch (error) {
    setMessage(error.message, 'error');
  }
}

function loadLeaderboard() {
  let storedEntries;
  try {
    storedEntries = JSON.parse(localStorage.getItem(LEADERBOARD_KEY) || '[]');
  } catch {
    return [];
  }
  if (!Array.isArray(storedEntries)) return [];
  const entries = storedEntries
    .map(normalizeLeaderboardEntry)
    .filter((entry) => entry !== null)
    .sort(compareLeaderboardEntries)
    .slice(0, 10);
  return entries;
}

function normalizeLeaderboardEntry(entry) {
  if (!entry || typeof entry !== 'object') return null;
  const time = Number(entry.time);
  const hints = Number(entry.hints);
  const name = typeof entry.name === 'string' ? entry.name.trim() : '';
  const difficulty = typeof entry.difficulty === 'string'
    ? entry.difficulty.trim().toLowerCase()
    : '';
  const gameId = typeof entry.gameId === 'string' ? entry.gameId.trim() : '';
  if (
    !name ||
    !gameId ||
    !Number.isFinite(time) ||
    time < 0 ||
    !Number.isInteger(hints) ||
    hints < 0 ||
    !['easy', 'medium', 'hard'].includes(difficulty)
  ) {
    return null;
  }
  return { name, time, difficulty, hints, gameId };
}

function compareLeaderboardEntries(left, right) {
  return left.time - right.time || left.name.localeCompare(right.name);
}

function saveLeaderboard(entries) {
  try {
    localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(entries.slice(0, 10)));
    return true;
  } catch {
    return false;
  }
}

function loadCompletedGameIds() {
  try {
    const storedIds = JSON.parse(localStorage.getItem(COMPLETED_GAMES_KEY) || '[]');
    return Array.isArray(storedIds)
      ? storedIds.filter((id) => typeof id === 'string' && id.trim())
      : [];
  } catch {
    return [];
  }
}

function saveCompletedGameId(gameId) {
  try {
    const completedIds = loadCompletedGameIds();
    if (!completedIds.includes(gameId)) completedIds.push(gameId);
    localStorage.setItem(COMPLETED_GAMES_KEY, JSON.stringify(completedIds));
    return true;
  } catch {
    return false;
  }
}

function isDuplicateCompletion(entries, entry) {
  return entries.some((storedEntry) => storedEntry.gameId === entry.gameId)
    || loadCompletedGameIds().includes(entry.gameId);
}

function addLeaderboardEntry(entry) {
  const entries = loadLeaderboard();
  if (isDuplicateCompletion(entries, entry)) return entries;
  entries.push(entry);
  entries.sort(compareLeaderboardEntries);
  return saveLeaderboard(entries) ? entries.slice(0, 10) : null;
}

function saveLeaderboardEntry() {
  if (state.scoreSaved) return true;
  const nameInput = element('playerName');
  const normalizedName = nameInput.value.trim();
  if (!normalizedName) {
    nameInput.setAttribute('aria-invalid', 'true');
    setMessage('Enter a player name before saving your score.', 'error');
    nameInput.focus();
    return false;
  }
  nameInput.value = normalizedName;
  nameInput.removeAttribute('aria-invalid');
  const entry = normalizeLeaderboardEntry({
    name: normalizedName,
    time: state.elapsedSeconds,
    difficulty: state.difficulty,
    hints: state.hintsUsed,
    gameId: state.gameId,
  });
  if (entry === null) return false;
  const entries = addLeaderboardEntry(entry);
  if (entries === null) return false;
  return saveCompletedGameId(entry.gameId);
}

function renderLeaderboard() {
  const body = element('leaderboard').querySelector('tbody');
  body.replaceChildren();
  const entries = loadLeaderboard();
  if (entries.length === 0) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 5;
    cell.textContent = 'No scores yet.';
    row.appendChild(cell);
    body.appendChild(row);
    return;
  }
  entries.forEach((entry, index) => {
    const row = document.createElement('tr');
    [index + 1, entry.name, formatTime(entry.time), entry.difficulty, entry.hints]
      .forEach((value) => {
        const cell = document.createElement('td');
        cell.textContent = value;
        row.appendChild(cell);
      });
    body.appendChild(row);
  });
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  element('toggle-theme').textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
  localStorage.setItem(THEME_KEY, theme);
}

function toggleTheme() {
  applyTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
}

window.addEventListener('load', () => {
  element('new-game').addEventListener('click', startNewGame);
  element('check-puzzle').addEventListener('click', checkPuzzle);
  element('hint').addEventListener('click', useHint);
  element('toggle-theme').addEventListener('click', toggleTheme);
  applyTheme(localStorage.getItem(THEME_KEY) || 'light');
  renderLeaderboard();
  startNewGame();
});
