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
  onFillBots: () => void;
}

export const LobbyModal: React.FC<LobbyModalProps> = ({
  myPlayerId,
  hostPlayer,
  playersList,
  playerNames,
  playerTypes,
  onSetSlotType,
  onStartGame,
  onFillBots,
}) => {
  const isHost = myPlayerId === hostPlayer;

  const isSlotReady = (slot: string) => {
    const type = playerTypes[slot] || 'HUMAN';
    if (type !== 'HUMAN') return true;
    return !!playerNames[slot];
  };

  const allSlotsReady = playersList.every(isSlotReady);
  const hasEmptyHumanSlots = playersList.some((s) => (playerTypes[s] === 'HUMAN' && !playerNames[s]));

  return (
    <div className="game-over-overlay">
      <div className="game-over-modal" style={{ maxWidth: '520px', width: '92%' }}>
        <h2>Poczekalnia</h2>
        <p style={{ color: '#6c757d', fontSize: '14px', margin: '-5px 0 16px 0' }}>
          Oczekujemy na graczy i gotowość Hosta (wymagane 4 miejsca)...
        </p>

        <table className="score-table" style={{ margin: '10px 0 20px 0' }}>
          <thead>
            <tr>
              <th style={{ width: '25%' }}>Miejsce</th>
              <th style={{ width: '45%' }}>Gracz</th>
              <th style={{ width: '30%' }}>Typ Slotu</th>
            </tr>
          </thead>
          <tbody>
            {playersList.map((slot) => {
              const isOccupiedByHuman = playerTypes[slot] === 'HUMAN' && !!playerNames[slot];
              const isBot = playerTypes[slot] !== 'HUMAN';
              const isMe = myPlayerId === slot;
              const isSlotHost = hostPlayer === slot;

              return (
                <tr key={slot} className={isMe ? 'my-score-row' : ''}>
                  <td style={{ fontWeight: 'bold' }}>
                    {slot} {isSlotHost && '👑 (Host)'}
                  </td>
                  <td>
                    {isOccupiedByHuman && (
                      <span style={{ color: '#2ecc71', fontWeight: 'bold' }}>
                        {playerNames[slot]} {isMe && '(Ty)'}
                      </span>
                    )}
                    {isBot && (
                      <span style={{ color: '#3498db', fontWeight: 'bold' }}>
                        🤖 {playerNames[slot] || 'Bot'}
                      </span>
                    )}
                    {!isOccupiedByHuman && !isBot && (
                      <span style={{ color: '#95a5a6', fontStyle: 'italic' }}>
                        ⚪ Wolne miejsce...
                      </span>
                    )}
                  </td>
                  <td>
                    {isHost && !isOccupiedByHuman ? (
                      <select
                        value={playerTypes[slot] || 'HUMAN'}
                        onChange={(e) => onSetSlotType(slot, e.target.value)}
                        style={{
                          padding: '6px',
                          borderRadius: '4px',
                          border: '1px solid #ced4da',
                          fontSize: '13px',
                          background: '#fff',
                          cursor: 'pointer',
                        }}
                      >
                        <option value="HUMAN">Czekaj na gracza</option>
                        <option value="BOT_EASY">Bot (Łatwy)</option>
                        <option value="BOT_NORMAL">Bot (Zwyczajny)</option>
                        <option value="BOT_MASTER">Bot (Mistrz)</option>
                      </select>
                    ) : (
                      <span style={{ fontSize: '13px', color: '#495057' }}>
                        {playerTypes[slot] === 'HUMAN' ? 'Gracz (Człowiek)' : 'Sztuczna Inteligencja'}
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {isHost ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {hasEmptyHumanSlots && (
              <button
                type="button"
                onClick={onFillBots}
                style={{
                  padding: '10px',
                  backgroundColor: '#3498db',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontWeight: 'bold',
                  fontSize: '14px',
                  cursor: 'pointer',
                }}
              >
                🤖 Uzupełnij puste miejsca Botami
              </button>
            )}

            <button
              className="restart-button"
              onClick={onStartGame}
              disabled={!allSlotsReady}
              style={{
                backgroundColor: allSlotsReady ? '#2ecc71' : '#bdc3c7',
                cursor: allSlotsReady ? 'pointer' : 'not-allowed',
                boxShadow: allSlotsReady ? '0 4px 10px rgba(46, 204, 113, 0.35)' : 'none',
              }}
            >
              {allSlotsReady ? '🚀 Wystartuj Grę!' : '⏳ Czekam na obsadzenie 4 miejsc...'}
            </button>
          </div>
        ) : (
          <p style={{ color: '#f39c12', fontWeight: 'bold', margin: '14px 0 0 0' }}>
            👑 Tylko Host może zarządzać botami i wystartować grę.
          </p>
        )}
      </div>
    </div>
  );
};