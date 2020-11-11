export function getSocketUrl(gameId) {
    gameId = gameId ? gameId : "";
    return `ws://127.0.0.1:8000/ws/${gameId}`;
}

