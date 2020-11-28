export function getSocketUrl(url, gameId) {
  gameId = gameId ? gameId : "";
  return `${url}${gameId}`;
}

export function getShipsUrl(rows, cols) {
  return `random-board/?rows=${rows}&cols=${cols}`;
}

export function zeros(m, n, a) {
  return [...Array(m)].map(() => Array(n).fill(a));
}

export function getShipClassName(length, orientation) {
  return `ship-${orientation}-${length}`;
}

export function isPlacementPossible(board, ship, maxX, maxY) {
  if (isShipInRange(ship, maxX, maxY)) {
    for (let i = ship.x - 1; i < ship.x + ship.rows + 1; i++) {
      for (let j = ship.y - 1; j < ship.y + ship.cols + 1; j++) {
        if (!isXYinRange(i, j, maxY, maxY)) {
          continue
        }
        if (board[i][j] != 0) {
          return false
        }
      }
    }
    return true
  }
  return false
}
export function placeShips(rows, cols, ships) {
  let board = zeros(rows, cols, 0);
  ships.forEach(ship => {
    for (let i = ship.x; i < ship.x + ship.rows; i++) {
      for (let j = ship.y; j < ship.y + ship.cols; j++) {
        board[i][j] = ship.length
      }
    }
  });
  return board
}

function isXYinRange(x, y, maxX, maxY) {
  return (x >= 0 && y >= 0 && x < maxX && y < maxY)
}

function isShipInRange(ship, maxX, maxY) {
  for (let i = 0; i < ship.rows; i++) {
    for (let j = 0; j < ship.cols; j++) {
      if (!isXYinRange(ship.x + i, ship.y + j, maxX, maxY))
        return false
    }
  }
  return true
}