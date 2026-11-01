import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import type { BoardGrid } from '../types';
import './Board.css';

interface BoardProps {
  grid: BoardGrid;
  projectedSquares?: string[];
  activePlayer?: string;
  isValidHover?: boolean;
}

const BoardCell = ({ x, y, occupant, isProjected, activePlayer, isValidHover }: any) => {
  const { setNodeRef } = useDroppable({ id: `cell-${x}-${y}`, data: { x, y } });

  let className = "board-cell";

  // Jeśli pole jest zajęte - nakładamy pełny kolor gracza
  if (occupant) {
    className += ` player-${occupant}`;
  } 
  // Jeśli gracz najechał cieniem - nakładamy walidację
  else if (isProjected && activePlayer) {
    className += isValidHover ? ` projected-valid player-${activePlayer}` : ` projected-invalid player-${activePlayer}`;
  }

  return <div ref={setNodeRef} className={className}></div>;
};

export const Board: React.FC<BoardProps> = ({ grid, projectedSquares = [], activePlayer, isValidHover }) => {
  const cells = [];
  for (let y = 0; y < 20; y++) {
    for (let x = 0; x < 20; x++) {
      const key = `${x},${y}`;
      cells.push(
        <BoardCell 
          key={key} x={x} y={y} 
          occupant={grid[key]} 
          isProjected={projectedSquares.includes(key)} 
          activePlayer={activePlayer}
          isValidHover={isValidHover} 
        />
      );
    }
  }
  
  return (
    // NOWE: Dedykowany kontener oddzielający siatkę od pozycjonowania znaczników
    <div className="board-container">
      {/* Kolorowe kątowniki nałożone na rogi planszy */}
      <div className="frame-marker marker-p1" title="Start P1"></div>
      <div className="frame-marker marker-p2" title="Start P2"></div>
      <div className="frame-marker marker-p3" title="Start P3"></div>
      <div className="frame-marker marker-p4" title="Start P4"></div>
      
      <div className="board">
        {cells}
      </div>
    </div>
  );
};