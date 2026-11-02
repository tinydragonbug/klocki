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
  onLeaveLobby: () => void;
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
  onLeaveLobby,
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
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <h2 style={{ margin: 0, fontSize: '24px' }}>Poczekalnia</h2>
          <button
            type="button"
            onClick={onLeaveLobby}
            style={{
              padding: '6px 12px',
              fontSize: '12px',
              backgroundColor: '#e74c3c',
              color: '#ffffff',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              fontWeight: 'bold',
              touchAction: 'manipulation',
            }}
          >
            🚪 Wyjdź z gry
          </button>
        </div>

        <p style={{ color: '#6c757d', fontSize: '13px', margin: '0 0 16px 0', textAlign: 'left' }}>
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
                    <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                      {/* Jeśli slot jest wolny lub zajęty przez bota, gracz może usiąść */}
                      {!isMe && !isOccupiedByHuman && (
                        <button
                          type="button"
                          onClick={() => onClaimSlot(slot)}
                          style={{
                            padding: '8px 12px',
                            fontSize: '12px',
                            backgroundColor: '#2ecc71',
                            color: '#fff',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontWeight: 'bold',
                            touchAction: 'manipulation',
                          }}
                        >
                          Usiądź
                        </button>
                      )}

                      {/* Przycisk zmiany typu slotu (tylko dla Hosta) */}
                      {isHost && !isOccupiedByHuman && (
                        <button
                          type="button"
                          onClick={() => onToggleSlotType(slot)}
                          style={{
                            padding: '8px 10px',
                            fontSize: '12px',
                            backgroundColor: isBot ? '#e8f4fd' : '#f8f9fa',
                            color: '#2c3e50',
                            border: '1px solid #ced4da',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontWeight: '600',
                            touchAction: 'manipulation',
                          }}
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
                    </div>
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