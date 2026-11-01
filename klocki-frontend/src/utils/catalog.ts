import type { Piece } from '../types';

// Oficjalny zestaw 21 klocków do Blokusa
export const FULL_CATALOG: Piece[] = [
  // 1-kratkowe
  { id: "1", squares: [{ x: 0, y: 0 }] },
  // 2-kratkowe
  { id: "2", squares: [{ x: 0, y: 0 }, { x: 1, y: 0 }] },
  // 3-kratkowe
  { id: "3", squares: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }] }, // I3
  { id: "4", squares: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 0, y: 1 }] }, // V3
  // 4-kratkowe
  { id: "5", squares: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }, { x: 3, y: 0 }] }, // I4
  { id: "6", squares: [{ x: 0, y: 1 }, { x: 1, y: 1 }, { x: 2, y: 1 }, { x: 2, y: 0 }] }, // L4
  { id: "7", squares: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }, { x: 1, y: 1 }] }, // T4
  { id: "8", squares: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 1 }] }, // O4 (Kwadrat)
  { id: "9", squares: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 1, y: 1 }, { x: 2, y: 1 }] }, // Z4
  // 5-kratkowe
  { id: "10", squares: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }, { x: 3, y: 0 }, { x: 4, y: 0 }] }, // I5
  { id: "11", squares: [{ x: 0, y: 1 }, { x: 1, y: 1 }, { x: 2, y: 1 }, { x: 3, y: 1 }, { x: 0, y: 0 }] }, // L5
  { id: "12", squares: [{ x: 0, y: 1 }, { x: 1, y: 1 }, { x: 2, y: 1 }, { x: 3, y: 1 }, { x: 1, y: 0 }] }, // Y
  { id: "13", squares: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }, { x: 0, y: 1 }, { x: 0, y: 2 }] }, // V5
  { id: "14", squares: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }, { x: 1, y: 1 }, { x: 1, y: 2 }] }, // T5
  { id: "15", squares: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 1 }] }, // P (Gruby L)
  { id: "16", squares: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 1, y: 1 }, { x: 2, y: 1 }, { x: 3, y: 1 }] }, // N
  { id: "17", squares: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 1, y: 1 }, { x: 2, y: 1 }, { x: 2, y: 2 }] }, // W
  { id: "18", squares: [{ x: 0, y: 1 }, { x: 1, y: 1 }, { x: 1, y: 0 }, { x: 2, y: 1 }, { x: 2, y: 2 }] }, // F
  { id: "19", squares: [{ x: 0, y: 1 }, { x: 1, y: 1 }, { x: 2, y: 1 }, { x: 1, y: 0 }, { x: 1, y: 2 }] }, // X (Krzyżyk)
  { id: "20", squares: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }, { x: 0, y: 1 }, { x: 2, y: 1 }] }, // U
  { id: "21", squares: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 1, y: 1 }, { x: 1, y: 2 }, { x: 2, y: 2 }] }  // Z5
];