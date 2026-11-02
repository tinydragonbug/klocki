import React, { useState, useEffect } from 'react';
import type { DragStartEvent, DragOverEvent, DragEndEvent } from '@dnd-kit/core';
import { DndContext, useSensor, useSensors, PointerSensor, TouchSensor } from '@dnd-kit/core';
import type { BoardGrid, Piece, PlayerId } from './types';
import { Board } from './components/Board';
import { PlayerHand } from './components/PlayerHand';
import { LobbyModal } from './components/modals/LobbyModal';
import { GameOverModal } from './components/modals/GameOverModal';
import { FULL_CATALOG } from './utils/catalog';
import { isMoveValidClient } from './utils/validation';
import './App.css';

const PLAYERS_LIST: PlayerId[] = ['P1', 'P2', 'P3', 'P4'];

const getOrCreateSessionId = (): string => {
  let sid = localStorage.getItem('blokus_session_id');
  if (!sid) {
    sid = Math.random().toString(36).substring(2, 15);
    localStorage.setItem('blokus_session_id', sid);
  }
  return sid;
};

function App() {
  const [grid, setGrid] = useState<BoardGrid>({});
  const [inventories, setInventories] = useState<Record<string, string[]>>({
    P1: [],
    P2: [],
    P3: [],
    P4: [],
  });
  const [playerNames, setPlayerNames] = useState<Record<string, string>>({});
  const [playerTypes, setPlayerTypes] = useState<Record<string, string>>({
    P1: 'HUMAN',
    P2: 'HUMAN',
    P3: 'HUMAN',
    P4: 'HUMAN',
  });
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [logs, setLogs] = useState<string[]>([]);

  const [myPlayerId, setMyPlayerId] = useState<string | null>(null);
  const [currentTurn, setCurrentTurn] = useState<string>('P1');
  const [gameStatus, setGameStatus] = useState<string>('WAITING');
  const [hostPlayer, setHostPlayer] = useState<string | null>(null);
  const [isGameFull, setIsGameFull] = useState<boolean>(false);

  const [sessionId] = useState<string>(getOrCreateSessionId);
  const [nicknameInput, setNicknameInput] = useState<string>(
    localStorage.getItem('blokus_nickname') || ''
  );
  const [passwordInput, setPasswordInput] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [isChatEnabled, setIsChatEnabled] = useState<boolean>(false);
  const [chatInput, setChatInput] = useState<string>('');

  const [activeDrag, setActiveDrag] = useState<{
    piece: Piece;
    player: PlayerId;
    grabOffset: { x: number; y: number };
  } | null>(null);
  const [activeTarget, setActiveTarget] = useState<{ x: number; y: number } | null>(null);

  useEffect(() => {
    const isHttps = window.location.protocol === 'https:';
    const wsProtocol = isHttps ? 'wss:' : 'ws:';
    
    const wsUrl = window.location.port === '5173'
      ? 'ws://localhost:8000/ws'
      : `${wsProtocol}//${window.location.host}/ws`;

    const ws = new WebSocket(wsUrl);
    ws.onopen = () => setIsConnected(true);

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.type === 'ASSIGN_PLAYER') {
        setMyPlayerId(message.data.playerId);
        setErrorMessage(null);
      } else if (message.type === 'ERROR_MESSAGE') {
        setErrorMessage(message.message);
      } else if (message.type === 'GAME_FULL') {
        setIsGameFull(true);
      } else if (message.type === 'STATE_UPDATE') {
        setGrid(message.data.grid);
        setInventories(message.data.inventories);
        setCurrentTurn(message.data.current_turn);
        setPlayerNames(message.data.player_names || {});
        setGameStatus(message.data.status || 'WAITING');
        setHostPlayer(message.data.host || null);
        if (message.data.player_types) {
          setPlayerTypes(message.data.player_types);
        }
      } else if (message.type === 'GAME_LOG') {
        setLogs((prevLogs) => [...prevLogs, message.message].slice(-7));
      }
    };

    ws.onclose = () => setIsConnected(false);
    setSocket(ws);
    return () => ws.close();
  }, []);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5,
      },
    }),
    useSensor(TouchSensor, {
      activationConstraint: {
        delay: 120,
        tolerance: 5,
      },
    })
  );

  const handleJoinLobby = (e: React.FormEvent) => {
    e.preventDefault();
    const name = nicknameInput.trim();
    if (socket && isConnected && name) {
      localStorage.setItem('blokus_nickname', name);
      socket.send(
        JSON.stringify({
          type: 'JOIN_LOBBY',
          data: { nickname: name, token: sessionId, password: passwordInput.trim() },
        })
      );
    }
  };

  const handleStartGame = () => {
    if (socket && isConnected && myPlayerId === hostPlayer) {
      socket.send(
        JSON.stringify({
          type: 'START_GAME',
          data: { player: myPlayerId },
        })
      );
    }
  };

  const handleSetSlotType = (slot: string, slotType: string) => {
    if (socket && isConnected && myPlayerId === hostPlayer) {
      socket.send(
        JSON.stringify({
          type: 'SET_SLOT_TYPE',
          data: {
            player: myPlayerId,
            slot: slot,
            slotType: slotType,
          },
        })
      );
    }
  };

  const handleFillBots = () => {
    if (socket && isConnected && myPlayerId === hostPlayer) {
      socket.send(
        JSON.stringify({
          type: 'FILL_EMPTY_WITH_BOTS',
          data: { player: myPlayerId },
        })
      );
    }
  };

  const handleRestartGame = () => {
    if (socket && isConnected) {
      socket.send(JSON.stringify({ type: 'RESTART_GAME' }));
    }
  };

  const handleReturnToLobby = () => {
    if (socket && isConnected) {
      socket.send(JSON.stringify({ type: 'RETURN_TO_LOBBY' }));
    }
  };

  const handleSendChat = (e: React.FormEvent) => {
    e.preventDefault();
    if (socket && isConnected && myPlayerId && chatInput.trim()) {
      socket.send(
        JSON.stringify({
          type: 'CHAT_MESSAGE',
          data: { player: myPlayerId, text: chatInput.trim() },
        })
      );
      setChatInput('');
    }
  };

  const handleDragStart = (event: DragStartEvent) => {
    if (
      myPlayerId !== currentTurn ||
      currentTurn === 'KONIEC' ||
      gameStatus !== 'PLAYING'
    ) {
      return;
    }
    setActiveDrag(event.active.data.current as any);
  };

  const handleDragOver = (event: DragOverEvent) => {
    if (event.over) {
      setActiveTarget(event.over.data.current as { x: number; y: number });
    } else {
      setActiveTarget(null);
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
    setActiveDrag(null);
    setActiveTarget(null);

    const { active, over } = event;
    if (over && active && socket && isConnected && myPlayerId) {
      const target = over.data.current as { x: number; y: number };
      const dragged = active.data.current as {
        piece: Piece;
        player: PlayerId;
        grabOffset: { x: number; y: number };
      };

      const originX = target.x - (dragged.grabOffset?.x || 0);
      const originY = target.y - (dragged.grabOffset?.y || 0);
      const targetSquares = dragged.piece.squares.map((sq) => ({
        x: originX + sq.x,
        y: originY + sq.y,
      }));

      socket.send(
        JSON.stringify({
          type: 'PLACE_PIECE',
          data: {
            player: myPlayerId,
            pieceId: dragged.piece.id,
            squares: targetSquares,
          },
        })
      );
    }
  };

  const handlePassTurn = () => {
    if (socket && isConnected && myPlayerId) {
      socket.send(
        JSON.stringify({
          type: 'PASS_TURN',
          data: { player: myPlayerId },
        })
      );
    }
  };

  let projectedSquares: { x: number; y: number }[] = [];
  let projectedKeys: string[] = [];
  let isValidHover = false;

  if (activeDrag && activeTarget && myPlayerId) {
    const originX = activeDrag.grabOffset
      ? activeTarget.x - activeDrag.grabOffset.x
      : activeTarget.x;
    const originY = activeDrag.grabOffset
      ? activeTarget.y - activeDrag.grabOffset.y
      : activeTarget.y;

    projectedSquares = activeDrag.piece.squares.map((sq) => ({
      x: originX + sq.x,
      y: originY + sq.y,
    }));
    projectedKeys = projectedSquares.map((sq) => `${sq.x},${sq.y}`);

    isValidHover = isMoveValidClient(
      grid,
      projectedSquares,
      myPlayerId as PlayerId
    );
  }

  if (isGameFull) {
    return (
      <div className="full-screen-message">
        Przepraszamy, pokój gry jest już pełny (4/4 graczy).
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="full-screen-message">
        Łączenie z serwerem Klocków...
      </div>
    );
  }

  if (!myPlayerId) {
    return (
      <div className="lobby-container">
        <div className="lobby-box">
          <h1>Witaj w Klockach!</h1>
          <form onSubmit={handleJoinLobby}>
            <input
              type="text"
              placeholder="Wpisz swój nick..."
              value={nicknameInput}
              onChange={(e) => setNicknameInput(e.target.value)}
              maxLength={15}
              required
              autoFocus
              style={{ marginBottom: '10px' }}
            />
            <input
              type="password"
              placeholder="Hasło pokoju..."
              value={passwordInput}
              onChange={(e) => {
                setPasswordInput(e.target.value);
                setErrorMessage(null);
              }}
              required
              style={{ marginBottom: '12px' }}
            />
            {errorMessage && (
              <p style={{ color: '#e74c3c', fontSize: '13px', margin: '0 0 12px 0', fontWeight: 'bold' }}>
                ⚠️ {errorMessage}
              </p>
            )}
            <button type="submit">Dołącz do Gry</button>
          </form>
        </div>
      </div>
    );
  }

  const myInventory = inventories?.[myPlayerId] || [];
  const myAvailablePieces = FULL_CATALOG.filter((piece) =>
    myInventory.includes(String(piece.id))
  );

  const isMyTurn = myPlayerId === currentTurn;
  const isGameOver = currentTurn === 'KONIEC';

  const myName = playerNames[myPlayerId] || myPlayerId;
  const currentTurnName = playerNames[currentTurn] || currentTurn;

  const calculateScore = (playerId: string): number => {
    const remainingPieceIds = inventories?.[playerId] || [];
    if (remainingPieceIds.length === 0) return 15;
    let penaltyPoints = 0;
    remainingPieceIds.forEach((pieceId) => {
      const pieceDef = FULL_CATALOG.find((p) => p.id === pieceId);
      if (pieceDef) penaltyPoints += pieceDef.squares.length;
    });
    return -penaltyPoints;
  };

  let statusBg = '#f8d7da';
  if (isGameOver) {
    statusBg = '#f1c40f';
  } else if (isMyTurn && gameStatus === 'PLAYING') {
    statusBg = '#d4edda';
  }

  let statusText = `🔴 Czekaj, teraz gra: ${currentTurnName}`;
  if (isGameOver) {
    statusText = 'KONIEC GRY!';
  } else if (gameStatus === 'WAITING') {
    statusText = 'Oczekiwanie na start...';
  } else if (isMyTurn) {
    statusText = '🟢 TWOJA TURA!';
  }

  return (
    <div className="app-container">
      <div className="status-bar" style={{ background: statusBg }}>
        <b>
          Grasz jako: {myName} ({myPlayerId})
        </b>
        <span style={{ marginLeft: '20px' }}>{statusText}</span>
      </div>

      <h1>Klocki</h1>

      {gameStatus === 'WAITING' && (
        <LobbyModal
          myPlayerId={myPlayerId}
          hostPlayer={hostPlayer}
          playersList={PLAYERS_LIST}
          playerNames={playerNames}
          playerTypes={playerTypes}
          onSetSlotType={handleSetSlotType}
          onStartGame={handleStartGame}
          onFillBots={handleFillBots}
        />
      )}

      {isGameOver && (
        <GameOverModal
          myPlayerId={myPlayerId}
          playersList={PLAYERS_LIST}
          playerNames={playerNames}
          inventories={inventories}
          calculateScore={calculateScore}
          onRestartGame={handleRestartGame}
          onReturnToLobby={handleReturnToLobby}
        />
      )}

      <DndContext
        sensors={sensors}
        onDragStart={handleDragStart}
        onDragOver={handleDragOver}
        onDragEnd={handleDragEnd}
      >
        <div className="game-layout">
          <Board
            grid={grid}
            projectedSquares={projectedKeys}
            activePlayer={activeDrag?.player}
            isValidHover={isValidHover}
          />

          <div className="side-panel">
            <PlayerHand
              playerId={myPlayerId as PlayerId}
              pieces={myAvailablePieces}
            />

            <button
              onClick={handlePassTurn}
              disabled={!isMyTurn || isGameOver || gameStatus !== 'PLAYING'}
              className="pass-button"
              style={{
                backgroundColor:
                  isMyTurn && !isGameOver && gameStatus === 'PLAYING'
                    ? '#e74c3c'
                    : '#95a5a6',
                marginBottom: '15px',
              }}
            >
              Zablokowany? Spasuj
            </button>

            <div
              style={{
                backgroundColor: '#ecf0f1',
                padding: '10px',
                borderRadius: '5px',
                marginBottom: '10px',
              }}
            >
              <label
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  fontSize: '14px',
                }}
              >
                <input
                  type="checkbox"
                  checked={isChatEnabled}
                  onChange={(e) => setIsChatEnabled(e.target.checked)}
                  style={{ marginRight: '10px' }}
                />
                Włącz czat w grze
              </label>

              {isChatEnabled && (
                <form
                  onSubmit={handleSendChat}
                  style={{ display: 'flex', marginTop: '10px' }}
                >
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    maxLength={60}
                    placeholder="Napisz wiadomość..."
                    style={{
                      flex: 1,
                      padding: '8px',
                      borderRadius: '4px',
                      border: '1px solid #ccc',
                      marginRight: '5px',
                    }}
                  />
                  <button
                    type="submit"
                    style={{
                      padding: '8px 12px',
                      backgroundColor: '#3498db',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontWeight: 'bold',
                    }}
                  >
                    Wyślij
                  </button>
                </form>
              )}
            </div>

            <div className="game-console">
              {logs.map((log, index) => {
                const logColor = log.startsWith('[') ? '#f1c40f' : '#2ecc71';
                return (
                  <div key={index} style={{ color: logColor }}>
                    {'>'} {log}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </DndContext>
    </div>
  );
}

export default App;