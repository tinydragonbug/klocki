import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import type { BoardGrid, PlayerId } from '../types';
import './Board.css';

// Pełne kolory graczy
const PLAYER_COLORS: Record<string, string> = {
  P1: '#e74c3c', // Czerwony
  P2: '#3498db', // Niebieski
  P3: '#f1c40f', // Żółty
  P4: '#2ecc71', // Zielony
};

// Wyblakłe (półprzezroczyste) kolory graczy dla nielegalnych ruchów
const PLAYER_GHOST_INVALID_COLORS: Record<string, string> = {
  P1: 'rgba(231, 76, 60, 0.35)',
  P2: 'rgba(52, 152, 219, 0.35)',
  P3: 'rgba(241, 196, 15, 0.35)',
  P4: 'rgba(46, 204, 113, 0.35)',
};

interface BoardProps {
  grid: BoardGrid;
  projectedSquares?: string[];
  activePlayer?: PlayerId;
  isValidHover?: boolean;
}

interface CellProps {
  x: number;
  y: number;
  owner?: string;
  isProjected: boolean;
  isValidHover: boolean;
  activePlayer?: PlayerId;
}

const DroppableCell: React.FC<CellProps> = ({
  x,
  y,
  owner,
  isProjected,
  isValidHover,
  activePlayer,
}) => {
  const { setNodeRef } = useDroppable({
    id: `cell-${x}-${y}`,
    data: { x, y },
  });

  let cellClass = 'board-cell';
  let backgroundColor: string | undefined = undefined;

  // 1. Jeśli pole jest już zajęte na stałe:
  if (owner) {
    backgroundColor = PLAYER_COLORS[owner] || '#34495e';
  } 
  // 2. Jeśli pole jest pod przeciąganym klockiem (cień):
  else if (isProjected && activePlayer) {
    if (isValidHover) {
      // Normalny, pełny kolor gracza
      backgroundColor = PLAYER_COLORS[activePlayer];
      cellClass += ' hover-valid';
    } else {
      // Wyblakły kolor gracza
      backgroundColor = PLAYER_GHOST_INVALID_COLORS[activePlayer] || 'rgba(0, 0, 0, 0.15)';
      cellClass += ' hover-invalid';
    }
  }

  return (
    <div
      ref={setNodeRef}
      className={cellClass}
      style={{
        backgroundColor,
      }}
    />
  );
};

export const Board: React.FC<BoardProps> = ({
  grid = {},
  projectedSquares = [],
  activePlayer,
  isValidHover = false,
}) => {
  const cells = [];

  for (let y = 0; y < 20; y++) {
    for (let x = 0; x < 20; x++) {
      const key = `${x},${y}`;
      const owner = grid[key];
      const isProjected = projectedSquares.includes(key);

      cells.push(
        <DroppableCell
          key={key}
          x={x}
          y={y}
          owner={owner}
          isProjected={isProjected}
          isValidHover={isValidHover}
          activePlayer={activePlayer}
        />
      );
    }
  }

  return (
    <div className="board-container">
      {/* 4 kolorowe punkty narożników startowych */}
      <div className="frame-marker marker-p1" title="Start P1 (Czerwony)" />
      <div className="frame-marker marker-p2" title="Start P2 (Niebieski)" />
      <div className="frame-marker marker-p3" title="Start P3 (Żółty)" />
      <div className="frame-marker marker-p4" title="Start P4 (Zielony)" />

      {/* Siatka 20x20 */}
      <div className="board">
        {cells}
      </div>
    </div>
  );
};