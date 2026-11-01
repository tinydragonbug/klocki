// Definiujemy ścisłą listę graczy. 
// Dzięki temu TypeScript zablokuje nas, jeśli spróbujemy przypisać np. "P5".
export type PlayerId = "P1" | "P2" | "P3" | "P4";

// Typ reprezentujący naszą planszę: Klucz (np. "0,0") -> Wartość (np. "P1")
export type BoardGrid = Record<string, PlayerId>;

// Reprezentacja pojedynczego punktu klocka (x, y)
export interface Coordinate {
  x: number;
  y: number;
}

// Reprezentacja definicji klocka
export interface Piece {
  id: string;
  squares: Coordinate[];
}