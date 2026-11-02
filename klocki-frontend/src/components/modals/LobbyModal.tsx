import React from 'react';
import type { PlayerId } from '../../types';

interface LobbyModalProps {
  myPlayerId: string | null;
  hostPlayer: string | null;
  playersList: PlayerId[];
  playerNames: Record<string, string>;
  playerTypes: Record<string, string>;
  onToggleSlotType: (slot: string) => void;
  onClaimSlot: (slot: string) => void;
  onStartGame: () => void;
  onFillBots: () => void;
}

export const LobbyModal: React.FC<LobbyModalProps> = ({
  myPlayerId,
  hostPlayer,
  playersList,
  playerNames,
  playerTypes,
  onToggleSlotType,
  onClaimSlot,
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
  const hasEmptyHumanSlots = playersList.some((s) => playerTypes[s] === 'HUMAN' && !playerNames[s]);

  const getSlotTypeLabel = (type: string) => {
    switch (type) {
      case 'BOT_EASY': return '🤖 Bot (Łatwy)';
      case 'BOT_NORMAL': return '🤖 Bot (Zwyczajny)';
      case 'BOT_MASTER': return '🤖 Bot (Mistrz)';
      default: return '👤 Czeka na gracza';
    }
  };

  return (
    <div className="game-over-overlay">
      <div className="game-over-modal" style={{ maxWidth: '520px', width: '94%', padding: '20px' }}>
        <h2 style={{ margin: '0 0 6px 0', fontSize: '24px' }}>Poczekalnia</h2>
        <p style={{ color: '#6c757d', fontSize: '13px', margin: '0 0 16px 0' }}>
          Do gry wymagane są 4 obsadzone miejsca (gracze lub boty).
        </p>

        <table className="score-table" style={{ margin: '0 0 16px 0', fontSize: '14px' }}>
          <thead>
            <tr>
              <th style={{ width: '22%' }}>Miejsce</th>
              <th style={{ width: '40%' }}>Gracz</th>
              <th style={{ width: '38%' }}>Zarządzanie</th>
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
                    {slot} {isSlotHost && '👑'}
                  </td>
                  <td>
                    {isOccupiedByHuman && (
                      <span style={{ color: '#27ae60', fontWeight: 'bold' }}>
                        {playerNames[slot]} {isMe && '(Ty)'}
                      </span>
                    )}
                    {isBot && (
                      <span style={{ color: '#2980b9', fontWeight: 'bold' }}>
                        {playerNames[slot] || 'Bot'}
                      </span>
                    )}
                    {!isOccupiedByHuman && !isBot && (
                      <span style={{ color: '#95a5a6', fontStyle: 'italic' }}>
                        ⚪ Wolne
                      </span>
                    )}
                  </td>
                  <td>
                    {/* Jeśli slot jest wolny lub jest botem, gracz może w niego usiąść */}
                    {!isMe && !isOccupiedByHuman && (
                      <button
                        type="button"
                        onClick={() => onClaimSlot(slot)}
                        style={{
                          padding: '6px 10px',
                          fontSize: '12px',
                          backgroundColor: '#2ecc71',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontWeight: 'bold',
                          marginRight: '6px',
                          touchAction: 'manipulation',
                        }}
                      >
                        Usiądź
                      </button>
                    )}

                    {/* Host ma dotykowy przycisk do cyklicznej zmiany typu slotu */}
                    {isHost && !isOccupiedByHuman && (
                      <button
                        type="button"
                        onClick={() => onToggleSlotType(slot)}
                        style={{
                          padding: '6px 10px',
                          fontSize: '12px',
                          backgroundColor: isBot ? '#e8f4fd' : '#f8f9fa',
                          color: '#2c3e50',
                          border: '1px solid #ced4da',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontWeight: '600',
                          touchAction: 'manipulation',
                        }}
                        title="Kliknij, aby zmienić typ"
                      >
                        {getSlotTypeLabel(playerTypes[slot] || 'HUMAN')} 🔄
                      </button>
                    )}

                    {!isHost && isOccupiedByHuman && !isMe && (
                      <span style={{ fontSize: '12px', color: '#7f8c8d' }}>Zajęte</span>
                    )}
                    {isMe && (
                      <span style={{ fontSize: '12px', color: '#27ae60', fontWeight: 'bold' }}>Twoje miejsce</span>
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
                  padding: '12px',
                  backgroundColor: '#3498db',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontWeight: 'bold',
                  fontSize: '14px',
                  cursor: 'pointer',
                  touchAction: 'manipulation',
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
                width: '100%',
                maxWidth: '100%',
                padding: '14px',
                touchAction: 'manipulation',
              }}
            >
              {allSlotsReady ? '🚀 Wystartuj Grę!' : '⏳ Czekam na obsadzenie 4 miejsc...'}
            </button>
          </div>
        ) : (
          <p style={{ color: '#d35400', fontWeight: 'bold', fontSize: '14px', margin: '10px 0 0 0' }}>
            👑 Oczekuj na gotowość Hosta do startu gry.
          </p>
        )}
      </div>
    </div>
  );
};