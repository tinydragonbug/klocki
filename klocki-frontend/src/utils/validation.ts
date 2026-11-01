import type { BoardGrid, PlayerId } from '../types';

export const isMoveValidClient = (grid: BoardGrid, projectedSquares: {x: number, y: number}[], player: PlayerId): boolean => {
  // 1. Sprawdzenie granic planszy i nakładania się klocków
  for (const sq of projectedSquares) {
    if (sq.x < 0 || sq.x >= 20 || sq.y < 0 || sq.y >= 20) return false;
    if (grid[`${sq.x},${sq.y}`]) return false;
  }

  // Sprawdzamy, czy gracz ma już jakieś klocki na planszy
  const hasPiecesOnBoard = Object.values(grid).includes(player);
  

  if (!hasPiecesOnBoard) {
    // 2. Pierwszy ruch MUSI dotykać wyznaczonego rogu startowego
    const startingCorners: Record<string, string> = {
      "P1": "0,0", "P2": "19,0", "P3": "19,19", "P4": "0,19"
    };
    const myCorner = startingCorners[player];
    return projectedSquares.some(sq => `${sq.x},${sq.y}` === myCorner);
  }

  // 3. Kolejne ruchy: Nie może stykać się bokiem, musi stykać się rogiem
  let touchesCorner = false;
  const directionsEdge = [[0, -1], [0, 1], [-1, 0], [1, 0]];
  const directionsCorner = [[-1, -1], [1, -1], [-1, 1], [1, 1]];

  for (const sq of projectedSquares) {
    // Sprawdzanie boków (Niedozwolone)
    for (const [dx, dy] of directionsEdge) {
      const neighbor = `${sq.x + dx},${sq.y + dy}`;
      if (grid[neighbor] === player) return false;
    }
    // Sprawdzanie rogów (Wymagane minimum jedno)
    for (const [dx, dy] of directionsCorner) {
      const corner = `${sq.x + dx},${sq.y + dy}`;
      if (grid[corner] === player) touchesCorner = true;
    }
  }

  return touchesCorner;
};