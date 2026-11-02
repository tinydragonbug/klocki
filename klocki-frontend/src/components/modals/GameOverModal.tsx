import React from 'react';
import type { PlayerId } from '../../types';

interface GameOverModalProps {
  myPlayerId: string | null;
  playersList: PlayerId[];
  playerNames: Record<string, string>;
  inventories: Record<string, string[]>;
  calculateScore: (playerId: string) => number;
  onRestartGame: () => void;
  onReturnToLobby: () => void;
}

export const GameOverModal: React.FC<GameOverModalProps> = ({
  myPlayerId,
  playersList,
  playerNames,
  inventories,
  calculateScore,
  onRestartGame,
  onReturnToLobby,
}) => {
  const rankedPlayers = playersList.map((p) => {
    const score = calculateScore(p);
    const piecesLeft = inventories?.[p]?.length || 0;
    const pName = playerNames[p] || p;
    const isMe = myPlayerId === p;
    return { id: p, name: pName, score, piecesLeft, isMe };
  });

  rankedPlayers.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    return a.piecesLeft - b.piecesLeft;
  });

  const medals = ['🥇 1.', '🥈 2.', '🥉 3.', '4.'];
  const winner = rankedPlayers[0];

  return (
    <div className="game-over-overlay">
      <div className="game-over-modal" style={{ width: '480px' }}>
        <h2>Koniec Gry!</h2>
        {winner && (
          <p style={{ color: '#f1c40f', fontSize: '18px', fontWeight: 'bold', margin: '10px 0' }}>
            Wygrywa: {winner.name} ({winner.score > 0 ? `+${winner.score}` : winner.score} pkt)!
          </p>
        )}

        <table className="score-table">
          <thead>
            <tr>
              <th>Miejsce</th>
              <th>Gracz</th>
              <th>Pozostałe klocki</th>
              <th>Wynik Końcowy</th>
            </tr>
          </thead>
          <tbody>
            {rankedPlayers.map((player, index) => {
              const scoreColor = player.score > 0 ? '#2ecc71' : (player.score === 0 ? '#f1c40f' : '#e74c3c');
              const scoreFormatted = player.score > 0 ? `+${player.score}` : `${player.score}`;

              return (
                <tr key={player.id} className={player.isMe ? 'my-score-row' : ''}>
                  <td style={{ fontWeight: 'bold' }}>{medals[index] || `${index + 1}.`}</td>
                  <td style={{ fontWeight: 'bold' }}>
                    {player.name} {player.isMe ? '(Ty)' : ''}
                  </td>
                  <td>{player.piecesLeft} szt.</td>
                  <td style={{ color: scoreColor, fontWeight: 'bold' }}>
                    {scoreFormatted} pkt
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        <p className="winner-announcement">
          Ranking ułożony wg najwyższego wyniku (najbliżej zera lub na plusie).
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '16px' }}>
          <button className="restart-button" onClick={onRestartGame}>
            🔄 Zagraj jeszcze raz (ten sam skład)
          </button>

          <button
            onClick={onReturnToLobby}
            style={{
              padding: '12px 20px',
              fontSize: '15px',
              fontWeight: '600',
              color: '#495057',
              backgroundColor: '#e9ecef',
              border: '1px solid #ced4da',
              borderRadius: '8px',
              cursor: 'pointer',
              width: '80%',
              maxWidth: '320px',
              margin: '0 auto',
              touchAction: 'manipulation',
            }}
          >
            👥 Wróć do Poczekalni (zmień graczy/boty)
          </button>
        </div>
      </div>
    </div>
  );
};