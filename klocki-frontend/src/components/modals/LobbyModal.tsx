import React from 'react';
import type { PlayerId } from '../../types';

interface LobbyModalProps {
  myPlayerId: string | null;
  hostPlayer: string | null;
  playersList: PlayerId[];
  playerNames: Record<string, string>;
  playerTypes: Record<string, string>;
  onSetSlotType: (slot: string, slotType: string) => void;
  onStartGame: () => void;
}

export const LobbyModal: React.FC<LobbyModalProps> = ({
  myPlayerId,
  hostPlayer,
  playersList,
  playerNames,
  playerTypes,
  onSetSlotType,
  onStartGame,
}) => {
  return (
    <div className="game-over-overlay">
      <div className="game-over-modal" style={{ width: '420px' }}>
        <h2>Poczekalnia</h2>
        <p>Oczekujemy na graczy i gotowość Hosta...</p>

        <table className="score-table" style={{ marginTop: '20px', marginBottom: '20px' }}>
          <thead>
            <tr>
              <th>Miejsce</th>
              <th>Status / Typ gracza</th>
            </tr>
          </thead>
          <tbody>
            {playersList.map((p) => {
              const isHost = hostPlayer === p;
              const pNick = playerNames[p];
              const currentType = playerTypes[p] || 'HUMAN';
              const isOccupiedByHuman = Boolean(pNick && currentType === 'HUMAN');

              return (
                <tr key={p}>
                  <td>
                    <b>{p}</b> {isHost ? '👑 (Host)' : ''}
                  </td>
                  <td>
                    {myPlayerId === hostPlayer && !isHost && !isOccupiedByHuman ? (
                      <select
                        value={currentType}
                        onChange={(e) => onSetSlotType(p, e.target.value)}
                        style={{
                          padding: '6px',
                          borderRadius: '4px',
                          border: '1px solid #ccc',
                        }}
                      >
                        <option value="HUMAN">Czeka na gracza (Człowiek)</option>
                        <option value="BOT_EASY">🤖 Bot (Łatwy)</option>
                        <option value="BOT_NORMAL">🤖 Bot (Zwyczajny)</option>
                        <option value="BOT_MASTER">🤖 Bot (Mistrz)</option>
                      </select>
                    ) : (
                      <span>
                        {pNick ? (
                          <span style={{ color: '#2ecc71', fontWeight: 'bold' }}>{pNick}</span>
                        ) : (
                          <span style={{ color: '#95a5a6' }}>Puste miejsce</span>
                        )}
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {myPlayerId === hostPlayer ? (
          <button
            className="restart-button"
            style={{
              backgroundColor: '#2ecc71',
              width: '100%',
              fontSize: '20px',
              padding: '15px',
            }}
            onClick={onStartGame}
          >
            Rozpocznij Grę
          </button>
        ) : (
          <p style={{ color: '#f1c40f', fontWeight: 'bold' }}>
            Tylko Host (👑) może wystartować grę.
          </p>
        )}
      </div>
    </div>
  );
};