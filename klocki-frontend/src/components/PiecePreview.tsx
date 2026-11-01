import React, { useState } from 'react';
import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import type { Piece, PlayerId, Coordinate } from '../types';
import './PiecePreview.css';

interface PiecePreviewProps {
  piece: Piece;
  player: PlayerId;
}

const rotateSquares = (squares: Coordinate[]): Coordinate[] => {
  const rotated = squares.map(sq => ({ x: -sq.y, y: sq.x }));
  const minX = Math.min(...rotated.map(sq => sq.x));
  const minY = Math.min(...rotated.map(sq => sq.y));
  return rotated.map(sq => ({ x: sq.x - minX, y: sq.y - minY }));
};

export const PiecePreview: React.FC<PiecePreviewProps> = ({ piece, player }) => {
  const [currentSquares, setCurrentSquares] = useState<Coordinate[]>(piece.squares);
  
  // NOWE: Stan przechowujący relatywny punkt chwytu (za którą kratkę trzymamy)
  const [grabOffset, setGrabOffset] = useState<Coordinate>({ x: 0, y: 0 });

  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: `piece-${piece.id}`,
    data: { 
      piece: { ...piece, squares: currentSquares }, 
      player,
      grabOffset // NOWE: Przekazujemy punkt chwytu wyżej do App.tsx
    },
  });

  const style = {
    transform: CSS.Translate.toString(transform),
    // Klocek staje się blady (40% widoczności), gdy jest w powietrzu
    opacity: isDragging ? 0.4 : 1,
    cursor: isDragging ? 'grabbing' : 'grab',
    zIndex: isDragging ? 1000 : 1,
  };

  const handleClick = () => {
    if (!isDragging) {
      setCurrentSquares(prev => rotateSquares(prev));
    }
  };

  const GRID_SIZE = 5;
  const cells = Array.from({ length: GRID_SIZE * GRID_SIZE }, (_, i) => i);

  return (
    <div 
      ref={setNodeRef} 
      style={style} 
      {...listeners} 
      {...attributes} 
      onClick={handleClick}
      className="piece-preview"
    >
      {cells.map((index) => {
        const x = index % GRID_SIZE;
        const y = Math.floor(index / GRID_SIZE);
        
        const isFilled = currentSquares.some(sq => sq.x === x && sq.y === y);
        const cellClass = isFilled ? `preview-cell player-${player}` : "preview-cell empty";

        return (
          <div 
            key={`${x},${y}`} 
            className={cellClass}
            // NOWE: Zapisujemy współrzędne wewnątrz pudełka 5x5 w momencie kliknięcia
            onPointerDown={isFilled ? () => setGrabOffset({ x, y }) : undefined}
          ></div>
        );
      })}
    </div>
  );
};