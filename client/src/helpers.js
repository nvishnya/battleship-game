export function getSocketUrl(gameId) {
    gameId = gameId ? gameId : "";
    return `ws://127.0.0.1:8000/ws/${gameId}`;
}

export function getShipsUrl(rows, cols) {
    return `random-board/?rows=${rows}&cols=${cols}`;
}

export function zeros(m, n) {
    return [...Array(m)].map(() => Array(n).fill(-1));
}

export function getShipClassName(length, orientation) {
    return `ship-${orientation}-${length}`
}

export function isPlacementPossible() {
    console.log();
}