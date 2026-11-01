export interface Coord {
  x: number;
  y: number;
}

/**
 * Normalizuje współrzędne klocka tak, aby lewy górny róg miał współrzędne (0, 0).
 */
export const normalizeSquares = (squares: Coord[]): Coord[] => {
  const minX = Math.min(...squares.map((sq) => sq.x));
  const minY = Math.min(...squares.map((sq) => sq.y));
  return squares
    .map((sq) => ({ x: sq.x - minX, y: sq.y - minY }))
    .sort((a, b) => (a.y === b.y ? a.x - b.x : a.y - b.y));
};

/**
 * Obraca klocek o 90 stopni zgodnie z ruchem wskazówek zegara: (x, y) -> (-y, x).
 */
export const rotateSquares = (squares: Coord[]): Coord[] => {
  const rotated = squares.map((sq) => ({ x: -sq.y, y: sq.x }));
  return normalizeSquares(rotated);
};

/**
 * Odbija klocek lustrzanie w osi poziomej (lewo/prawo): (x, y) -> (-x, y).
 */
export const flipSquares = (squares: Coord[]): Coord[] => {
  const flipped = squares.map((sq) => ({ x: -sq.x, y: sq.y }));
  return normalizeSquares(flipped);
};