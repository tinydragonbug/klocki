import React, { useState, useEffect } from 'react';
import { useDraggable } from '@dnd-kit/core';
import type { Piece, PlayerId } from '../types';
import { rotateSquares, flipSquares } from '../utils/transforms';
import './PlayerHand.css';

interface HandProps {
  playerId: PlayerId;
  pieces: Piece[];
}

interface DraggablePieceProps {
  piece: Piece;
  player: PlayerId;
  isSelected: boolean;
  onSelect: () => void;
}

const DraggablePiece: React.FC<DraggablePieceProps> = ({
  piece,
  player,
  isSelected,
  onSelect,
}) => {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: `hand-piece-${piece.id}`,
    data: {
      piece,
      player,
      grabOffset: { x: 0, y: 0 },
    },
  });

  const maxX = Math.max(...piece.squares.map((s) => s.x)) + 1;
  const maxY = Math.max(...piece.squares.map((s) => s.y)) + 1;

  const style: React.CSSProperties = {
    transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined,
    opacity: isDragging ? 0.3 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      {...listeners}
      {...attributes}
      onClick={onSelect}
      style={style}
      className={`piece-compact-item ${isSelected ? 'selected' : ''}`}
      title="Kliknij, aby zaznaczyć do obrotu | Przeciągnij na planszę"
    >
      <div
        className="piece-grid-raw"
        style={{
          gridTemplateColumns: `repeat(${maxX}, 14px)`,
          gridTemplateRows: `repeat(${maxY}, 14px)`,
        }}
      >
        {piece.squares.map((sq, i) => (
          <div
            key={i}
            className={`hand-square player-${player}`}
            style={{
              gridColumnStart: sq.x + 1,
              gridRowStart: sq.y + 1,
            }}
          />
        ))}
      </div>
    </div>
  );
};

export const PlayerHand: React.FC<HandProps> = ({ playerId, pieces }) => {
  // Przechowujemy orientacje klocków w słowniku: { [pieceId]: Coord[] }
  const [orientations, setOrientations] = useState<Record<string, { x: number; y: number }[]>>({});
  const [selectedPieceId, setSelectedPieceId] = useState<string | null>(null);

  // Ustawiamy zaznaczenie na pierwszy klocek, jeśli obecny zniknął (został postawiony)
  useEffect(() => {
    if (pieces.length > 0) {
      if (!selectedPieceId || !pieces.some((p) => String(p.id) === selectedPieceId)) {
        setSelectedPieceId(String(pieces[0].id));
      }
    } else {
      setSelectedPieceId(null);
    }
  }, [pieces, selectedPieceId]);

  const handleRotateSelected = () => {
    if (!selectedPieceId) return;
    const currentPiece = pieces.find((p) => String(p.id) === selectedPieceId);
    if (!currentPiece) return;

    const baseSquares = orientations[selectedPieceId] || currentPiece.squares;
    const rotated = rotateSquares(baseSquares);
    setOrientations((prev) => ({ ...prev, [selectedPieceId]: rotated }));
  };

  const handleFlipSelected = () => {
    if (!selectedPieceId) return;
    const currentPiece = pieces.find((p) => String(p.id) === selectedPieceId);
    if (!currentPiece) return;

    const baseSquares = orientations[selectedPieceId] || currentPiece.squares;
    const flipped = flipSquares(baseSquares);
    setOrientations((prev) => ({ ...prev, [selectedPieceId]: flipped }));
  };

  // Obsługa skrótów klawiszowych: R (obrót), F (lustro)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignorujemy, gdy gracz pisze na czacie
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }
      if (e.key === 'r' || e.key === 'R') {
        handleRotateSelected();
      } else if (e.key === 'f' || e.key === 'F') {
        handleFlipSelected();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  });

  return (
    <div className="player-hand-container">
      <div className="hand-header">
        <h3>Klocki Gracza: {playerId} ({pieces.length})</h3>

        {/* Wspólny pasek narzędzi transformacji na samej górze */}
        <div className="global-transform-bar">
          <button
            type="button"
            className="transform-action-btn"
            onClick={handleRotateSelected}
            disabled={!selectedPieceId}
            title="Obróć zaznaczony klocek o 90° (Klawisz R)"
          >
            🔄 Obróć [R]
          </button>
          <button
            type="button"
            className="transform-action-btn"
            onClick={handleFlipSelected}
            disabled={!selectedPieceId}
            title="Odbij lustrzanie w poziomie (Klawisz F)"
          >
            🪞 Lustro [F]
          </button>
        </div>
      </div>

      {/* Czysta lista klocków bez zbędnych ramek i przycisków */}
      <div className="player-hand-grid-view">
        {pieces.map((piece) => {
          const pieceIdStr = String(piece.id);
          const currentSquares = orientations[pieceIdStr] || piece.squares;
          const dynamicPiece: Piece = {
            ...piece,
            squares: currentSquares,
          };

          return (
            <DraggablePiece
              key={piece.id}
              piece={dynamicPiece}
              player={playerId}
              isSelected={selectedPieceId === pieceIdStr}
              onSelect={() => setSelectedPieceId(pieceIdStr)}
            />
          );
        })}
      </div>
    </div>
  );
};