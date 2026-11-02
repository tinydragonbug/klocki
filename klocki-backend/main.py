import json
import asyncio
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from game_logic import is_move_valid_blokus, player_has_any_valid_move
from bot_ai import find_bot_move

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PLAYERS_ORDER = ["P1", "P2", "P3", "P4"]
ALL_PIECES = [str(i) for i in range(1, 22)]

# Hasło dostępu do pokoju dla znajomych
ROOM_PASSWORD = "kloc"

def get_initial_game_state():
    return {
        "status": "WAITING",
        "host": None,
        "grid": {},
        "inventories": {
            "P1": ALL_PIECES.copy(),
            "P2": ALL_PIECES.copy(),
            "P3": ALL_PIECES.copy(),
            "P4": ALL_PIECES.copy()
        },
        "current_turn": "P1",
        "passed_players": [],
        "player_names": {},
        "player_tokens": {},
        "player_types": {
            "P1": "HUMAN",
            "P2": "HUMAN",
            "P3": "HUMAN",
            "P4": "HUMAN"
        }
    }

game_state = get_initial_game_state()

@app.get("/api/health")
def health_check():
    """Punkt kontrolny potwierdzający działanie silnika gry."""
    return {
        "status": "online",
        "service": "Blokus Game Engine",
        "version": "1.0.0",
        "active_players": len(game_state.get("player_names", {}))
    }

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

    async def join_lobby(self, websocket: WebSocket, nickname: str, token: str) -> str | None:
        # Powrót rozłączonego gracza po tokenie sesji
        for p_id, p_token in game_state.get("player_tokens", {}).items():
            if p_token == token:
                self.active_connections[p_id] = websocket
                game_state["player_names"][p_id] = nickname
                return p_id

        # Przydział nowego wolnego slotu przeznaczonego dla człowieka
        for player_id in PLAYERS_ORDER:
            if player_id not in game_state.get("player_tokens", {}) and game_state["player_types"].get(player_id) == "HUMAN":
                self.active_connections[player_id] = websocket
                game_state["player_names"][player_id] = nickname
                game_state["player_tokens"][player_id] = token
                if game_state["host"] is None:
                    game_state["host"] = player_id
                return player_id
        return None

    def disconnect(self, player_id: str):
        if player_id in self.active_connections:
            del self.active_connections[player_id]

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections.values()):
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                pass

manager = ConnectionManager()

def get_next_turn(current_player: str, passed_list: list) -> str | None:
    if len(passed_list) >= len(PLAYERS_ORDER):
        return None
    current_index = PLAYERS_ORDER.index(current_player)
    for i in range(1, len(PLAYERS_ORDER) + 1):
        next_index = (current_index + i) % len(PLAYERS_ORDER)
        candidate = PLAYERS_ORDER[next_index]
        if candidate not in passed_list:
            return candidate
    return None

async def advance_turn_or_end(current_p: str, action_log: str):
    await manager.broadcast({"type": "GAME_LOG", "message": action_log})

    while True:
        next_p = get_next_turn(current_p, game_state["passed_players"])
        
        if not next_p:
            game_state["current_turn"] = "KONIEC"
            game_state["status"] = "FINISHED"
            await manager.broadcast({"type": "GAME_LOG", "message": "🏁 KONIEC GRY! Brak dalszych ruchów."})
            break

        p_inv = game_state["inventories"].get(next_p, [])
        p_name = game_state["player_names"].get(next_p, next_p)
        has_move = player_has_any_valid_move(game_state["grid"], p_inv, next_p)

        if has_move:
            game_state["current_turn"] = next_p
            await manager.broadcast({"type": "GAME_LOG", "message": f"Tura: {p_name}."})
            break
        else:
            if next_p not in game_state["passed_players"]:
                game_state["passed_players"].append(next_p)
            await manager.broadcast({
                "type": "GAME_LOG", 
                "message": f"⚠️ {p_name} nie ma żadnego legalnego ruchu — automatyczny PAS."
            })
            current_p = next_p

    await manager.broadcast({"type": "STATE_UPDATE", "data": game_state})

    if game_state["status"] == "PLAYING" and game_state["current_turn"] != "KONIEC":
        curr = game_state["current_turn"]
        if game_state["player_types"].get(curr, "HUMAN") != "HUMAN":
            asyncio.create_task(execute_bot_turn(curr))

async def execute_bot_turn(bot_id: str):
    await asyncio.sleep(0.6)
    if game_state["status"] != "PLAYING" or game_state["current_turn"] != bot_id:
        return

    diff = game_state["player_types"].get(bot_id, "BOT_EASY")
    bot_name = game_state["player_names"].get(bot_id, bot_id)
    inv = game_state["inventories"].get(bot_id, [])

    piece_id, squares = await asyncio.to_thread(
        find_bot_move,
        game_state["grid"],
        inv,
        bot_id,
        diff
    )

    if piece_id and squares:
        for sq in squares:
            game_state["grid"][f"{sq['x']},{sq['y']}"] = bot_id
        game_state["inventories"][bot_id].remove(piece_id)
        await advance_turn_or_end(bot_id, f"🤖 {bot_name} zagrał klocek {piece_id}.")
    else:
        if bot_id not in game_state["passed_players"]:
            game_state["passed_players"].append(bot_id)
        await advance_turn_or_end(bot_id, f"🤖 {bot_name} nie ma ruchu i PASUJE.")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    assigned_player_id = None

    try:
        while True:
            raw_data = await websocket.receive_text()
            message = json.loads(raw_data)
            msg_type = message.get("type")
            payload = message.get("data", {})

            if msg_type == "JOIN_LOBBY":
                password_given = payload.get("password", "")
                if password_given != ROOM_PASSWORD:
                    await websocket.send_text(json.dumps({
                        "type": "ERROR_MESSAGE",
                        "message": "Niepoprawne hasło pokoju!"
                    }))
                    continue

                nickname = payload.get("nickname", "Anonim")
                token = payload.get("token", "")
                assigned_player_id = await manager.join_lobby(websocket, nickname, token)

                if assigned_player_id:
                    await websocket.send_text(json.dumps({
                        "type": "ASSIGN_PLAYER",
                        "data": {"playerId": assigned_player_id, "nickname": nickname}
                    }))
                    await manager.broadcast({"type": "STATE_UPDATE", "data": game_state})
                else:
                    await websocket.send_text(json.dumps({"type": "GAME_FULL", "message": "Pokój jest pełny."}))

            if not assigned_player_id:
                continue

            sender_player = payload.get("player")

            if msg_type == "SET_SLOT_TYPE":
                target_slot = payload.get("slot")
                slot_type = payload.get("slotType")
                if sender_player == game_state["host"] and game_state["status"] == "WAITING" and target_slot in PLAYERS_ORDER:
                    game_state["player_types"][target_slot] = slot_type
                    if slot_type != "HUMAN":
                        names_map = {
                            "BOT_EASY": "Bot (Łatwy)",
                            "BOT_NORMAL": "Bot (Zwyczajny)",
                            "BOT_MASTER": "Bot (Mistrz)"
                        }
                        game_state["player_names"][target_slot] = names_map.get(slot_type, "Bot")
                    else:
                        if target_slot not in game_state.get("player_tokens", {}):
                            game_state["player_names"].pop(target_slot, None)
                    await manager.broadcast({"type": "STATE_UPDATE", "data": game_state})

            elif msg_type == "START_GAME":
                if sender_player == game_state["host"] and game_state["status"] == "WAITING":
                    game_state["status"] = "PLAYING"
                    await manager.broadcast({"type": "GAME_LOG", "message": "Host wystartował grę!"})
                    await manager.broadcast({"type": "STATE_UPDATE", "data": game_state})
                    first_p = game_state["current_turn"]
                    if game_state["player_types"].get(first_p, "HUMAN") != "HUMAN":
                        asyncio.create_task(execute_bot_turn(first_p))

            elif msg_type == "RESTART_GAME":
                # Restart partii w tym samym składzie graczy i botów
                current_names = game_state["player_names"].copy()
                current_tokens = game_state.get("player_tokens", {}).copy()
                current_types = game_state.get("player_types", {}).copy()
                current_host = game_state["host"]

                game_state.clear()
                game_state.update(get_initial_game_state())

                game_state["player_names"] = current_names
                game_state["player_tokens"] = current_tokens
                game_state["player_types"] = current_types
                game_state["host"] = current_host
                game_state["status"] = "PLAYING"

                await manager.broadcast({"type": "GAME_LOG", "message": "🔄 Rozpoczęto nową partię w tym samym składzie!"})
                await manager.broadcast({"type": "STATE_UPDATE", "data": game_state})
                
                first_p = game_state["current_turn"]
                if game_state["player_types"].get(first_p, "HUMAN") != "HUMAN":
                    asyncio.create_task(execute_bot_turn(first_p))

            elif msg_type == "RETURN_TO_LOBBY":
                # Powrót do poczekalni z zachowaniem obecnych graczy
                current_names = game_state["player_names"].copy()
                current_tokens = game_state.get("player_tokens", {}).copy()
                current_types = game_state.get("player_types", {}).copy()
                current_host = game_state["host"]

                game_state.clear()
                game_state.update(get_initial_game_state())

                game_state["player_names"] = current_names
                game_state["player_tokens"] = current_tokens
                game_state["player_types"] = current_types
                game_state["host"] = current_host
                game_state["status"] = "WAITING"

                await manager.broadcast({"type": "GAME_LOG", "message": "👥 Powrót do Poczekalni — gotowi na zmiany składu."})
                await manager.broadcast({"type": "STATE_UPDATE", "data": game_state})

            elif msg_type == "PLACE_PIECE":
                if sender_player != assigned_player_id or game_state["status"] != "PLAYING":
                    continue
                piece_id = payload["pieceId"]
                squares = payload["squares"]

                if sender_player != game_state["current_turn"]:
                    continue
                if piece_id not in game_state["inventories"].get(sender_player, []):
                    continue

                is_valid, reason = is_move_valid_blokus(game_state["grid"], squares, sender_player)
                if is_valid:
                    for sq in squares:
                        game_state["grid"][f"{sq['x']},{sq['y']}"] = sender_player
                    game_state["inventories"][sender_player].remove(piece_id)
                    nick = game_state["player_names"].get(sender_player, sender_player)
                    await advance_turn_or_end(sender_player, f"{nick} ułożył klocek {piece_id}.")
                else:
                    await websocket.send_text(json.dumps({"type": "GAME_LOG", "message": f"Odrzucono: {reason}"}))

            elif msg_type == "PASS_TURN":
                if sender_player != assigned_player_id or game_state["status"] != "PLAYING":
                    continue
                if sender_player != game_state["current_turn"]:
                    continue
                if sender_player not in game_state["passed_players"]:
                    game_state["passed_players"].append(sender_player)
                nick = game_state["player_names"].get(sender_player, sender_player)
                await advance_turn_or_end(sender_player, f"{nick} PASUJE.")

            elif msg_type == "CHAT_MESSAGE":
                text = payload.get("text", "").strip()
                if text:
                    nick = game_state["player_names"].get(sender_player, sender_player)
                    await manager.broadcast({"type": "GAME_LOG", "message": f"[{nick}]: {text}"})

    except WebSocketDisconnect:
        manager.disconnect(assigned_player_id)
        if assigned_player_id:
            nick = game_state["player_names"].get(assigned_player_id, assigned_player_id)
            await manager.broadcast({"type": "GAME_LOG", "message": f"{nick} rozłączył się."})

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Sprawdzamy obecność katalogu static (zbudowanego w kontenerze produkcyjnym)
if os.path.exists("static"):
    # 1. Montujemy zasoby statyczne (pliki JS, CSS, obrazki z Vite)
    if os.path.exists("static/assets"):
        app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

    # 2. Główny punkt wejścia do gry
    @app.get("/")
    async def serve_index():
        return FileResponse("static/index.html")

    # 3. Obsługa pozostałych ścieżek SPA (Single Page Application)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join("static", full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse("static/index.html")          