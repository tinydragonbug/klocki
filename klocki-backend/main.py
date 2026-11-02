import json
import asyncio
import os
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Hasło dostępu do pokoju gry
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
        # 1. Powrót gracza po istniejącym tokenie sesji
        for p_id, p_token in game_state.get("player_tokens", {}).items():
            if p_token == token:
                self.active_connections[p_id] = websocket
                game_state["player_names"][p_id] = nickname
                return p_id

        # 2. Szukamy slotu HUMAN, w którym nie ma aktywnego połączenia
        for player_id in PLAYERS_ORDER:
            if player_id not in self.active_connections and game_state["player_types"].get(player_id) == "HUMAN":
                self.active_connections[player_id] = websocket
                game_state["player_names"][player_id] = nickname
                game_state["player_tokens"][player_id] = token
                if game_state["host"] is None or game_state["host"] not in self.active_connections:
                    game_state["host"] = player_id
                return player_id

        # 3. KULOODPORNOŚĆ: Jeśli wszystkie sloty zajęły boty, człowiek ZASTĘPUJE pierwszego wolnego bota!
        for player_id in PLAYERS_ORDER:
            if player_id not in self.active_connections and game_state["player_types"].get(player_id) != "HUMAN":
                self.active_connections[player_id] = websocket
                game_state["player_types"][player_id] = "HUMAN"
                game_state["player_names"][player_id] = nickname
                game_state["player_tokens"][player_id] = token
                if game_state["host"] is None or game_state["host"] not in self.active_connections:
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
                    await websocket.send_text(json.dumps({"type": "GAME_FULL", "message": "Pokój jest pełny (4/4 graczy)."}))

            if not assigned_player_id:
                continue

            sender_player = payload.get("player")

            # Przełączanie typu slotu (Dotykowy przełącznik)
            if msg_type == "TOGGLE_SLOT_TYPE":
                target_slot = payload.get("slot")
                if sender_player == game_state["host"] and game_state["status"] == "WAITING" and target_slot in PLAYERS_ORDER:
                    if target_slot not in manager.active_connections:
                        current_t = game_state["player_types"].get(target_slot, "HUMAN")
                        cycle = ["HUMAN", "BOT_EASY", "BOT_NORMAL", "BOT_MASTER"]
                        next_idx = (cycle.index(current_t) + 1) % len(cycle)
                        next_t = cycle[next_idx]
                        
                        game_state["player_types"][target_slot] = next_t
                        names_map = {
                            "HUMAN": "Czeka na gracza...",
                            "BOT_EASY": "Bot (Łatwy)",
                            "BOT_NORMAL": "Bot (Zwyczajny)",
                            "BOT_MASTER": "Bot (Mistrz)"
                        }
                        if next_t != "HUMAN":
                            game_state["player_names"][target_slot] = names_map[next_t]
                        else:
                            game_state["player_names"].pop(target_slot, None)

                        await manager.broadcast({"type": "STATE_UPDATE", "data": game_state})

            elif msg_type == "CLAIM_SLOT":
                target_slot = payload.get("slot")
                if game_state["status"] == "WAITING" and target_slot in PLAYERS_ORDER:
                    # Sprawdzamy czy slot nie jest zajęty przez innego aktywnego człowieka
                    if target_slot not in manager.active_connections:
                        old_slot = assigned_player_id
                        my_nick = game_state["player_names"].get(old_slot, "Gracz")
                        my_token = game_state["player_tokens"].get(old_slot, "")

                        # Zwalniamy stary slot
                        manager.disconnect(old_slot)
                        game_state["player_names"].pop(old_slot, None)
                        game_state["player_tokens"].pop(old_slot, None)
                        game_state["player_types"][old_slot] = "HUMAN"

                        # Zajmujemy nowy slot
                        assigned_player_id = target_slot
                        manager.active_connections[target_slot] = websocket
                        game_state["player_types"][target_slot] = "HUMAN"
                        game_state["player_names"][target_slot] = my_nick
                        game_state["player_tokens"][target_slot] = my_token

                        if game_state["host"] == old_slot:
                            game_state["host"] = target_slot

                        await websocket.send_text(json.dumps({
                            "type": "ASSIGN_PLAYER",
                            "data": {"playerId": target_slot, "nickname": my_nick}
                        }))
                        await manager.broadcast({"type": "STATE_UPDATE", "data": game_state})

            elif msg_type == "FILL_EMPTY_WITH_BOTS":
                if sender_player == game_state["host"] and game_state["status"] == "WAITING":
                    for slot in PLAYERS_ORDER:
                        if slot not in manager.active_connections and game_state["player_types"].get(slot) == "HUMAN":
                            game_state["player_types"][slot] = "BOT_EASY"
                            game_state["player_names"][slot] = "Bot (Łatwy)"
                    await manager.broadcast({"type": "STATE_UPDATE", "data": game_state})
                    await manager.broadcast({"type": "GAME_LOG", "message": "🤖 Puste miejsca zostały uzupełnione botami."})

            elif msg_type == "START_GAME":
                if sender_player == game_state["host"] and game_state["status"] == "WAITING":
                    unfilled_slots = []
                    for slot in PLAYERS_ORDER:
                        slot_type = game_state["player_types"].get(slot, "HUMAN")
                        has_active_human = (slot_type == "HUMAN" and slot in manager.active_connections)
                        is_bot = (slot_type != "HUMAN")
                        if not (has_active_human or is_bot):
                            unfilled_slots.append(slot)

                    if unfilled_slots:
                        await websocket.send_text(json.dumps({
                            "type": "GAME_LOG",
                            "message": f"⚠️ Nie można wystartować! Wolne miejsca: {', '.join(unfilled_slots)}. Uzupełnij je botami lub poczekaj na graczy."
                        }))
                        continue

                    game_state["status"] = "PLAYING"
                    await manager.broadcast({"type": "GAME_LOG", "message": "Host wystartował grę!"})
                    await manager.broadcast({"type": "STATE_UPDATE", "data": game_state})
                    first_p = game_state["current_turn"]
                    if game_state["player_types"].get(first_p, "HUMAN") != "HUMAN":
                        asyncio.create_task(execute_bot_turn(first_p))

            elif msg_type == "RESTART_GAME":
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
                active_ids = list(manager.active_connections.keys())
                new_names = {}
                new_tokens = {}
                new_types = {}

                for slot in PLAYERS_ORDER:
                    if slot in active_ids:
                        new_names[slot] = game_state["player_names"].get(slot, f"Gracz {slot}")
                        new_tokens[slot] = game_state["player_tokens"].get(slot, "")
                        new_types[slot] = "HUMAN"
                    else:
                        new_types[slot] = "HUMAN"

                new_host = game_state["host"] if game_state["host"] in active_ids else (active_ids[0] if active_ids else None)

                game_state.clear()
                game_state.update(get_initial_game_state())

                game_state["player_names"] = new_names
                game_state["player_tokens"] = new_tokens
                game_state["player_types"] = new_types
                game_state["host"] = new_host
                game_state["status"] = "WAITING"

                await manager.broadcast({"type": "GAME_LOG", "message": "👥 Powrót do Poczekalni — wyczyszczono stół."})
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
            if game_state["status"] == "WAITING":
                game_state["player_names"].pop(assigned_player_id, None)
                game_state["player_tokens"].pop(assigned_player_id, None)
                if game_state["host"] == assigned_player_id:
                    remaining = list(manager.active_connections.keys())
                    game_state["host"] = remaining[0] if remaining else None
                await manager.broadcast({"type": "STATE_UPDATE", "data": game_state})
            await manager.broadcast({"type": "GAME_LOG", "message": f"{nick} rozłączył się."})

if os.path.exists("static"):
    if os.path.exists("static/assets"):
        app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

    @app.get("/")
    async def serve_index():
        return FileResponse("static/index.html")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join("static", full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse("static/index.html")