import random
import math
from game_logic import is_move_valid_blokus

# Pełny katalog klocków (współrzędne lokalne znormalizowane do 0,0)
PIECE_SHAPES = {
    "1": [{"x": 0, "y": 0}],
    "2": [{"x": 0, "y": 0}, {"x": 1, "y": 0}],
    "3": [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0}],
    "4": [{"x": 0, "y": 0}, {"x": 0, "y": 1}, {"x": 1, "y": 1}],
    "5": [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0}, {"x": 3, "y": 0}],
    "6": [{"x": 0, "y": 0}, {"x": 0, "y": 1}, {"x": 0, "y": 2}, {"x": 1, "y": 2}],
    "7": [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0}, {"x": 1, "y": 1}],
    "8": [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 0, "y": 1}, {"x": 1, "y": 1}],
    "9": [{"x": 1, "y": 0}, {"x": 2, "y": 0}, {"x": 0, "y": 1}, {"x": 1, "y": 1}],
    "10": [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0}, {"x": 3, "y": 0}, {"x": 4, "y": 0}],
    "11": [{"x": 0, "y": 0}, {"x": 0, "y": 1}, {"x": 0, "y": 2}, {"x": 0, "y": 3}, {"x": 1, "y": 3}],
    "12": [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 1, "y": 1}, {"x": 1, "y": 2}, {"x": 1, "y": 3}],
    "13": [{"x": 0, "y": 0}, {"x": 0, "y": 1}, {"x": 0, "y": 2}, {"x": 1, "y": 1}, {"x": 2, "y": 1}],
    "14": [{"x": 0, "y": 0}, {"x": 0, "y": 1}, {"x": 1, "y": 1}, {"x": 1, "y": 2}, {"x": 2, "y": 2}],
    "15": [{"x": 0, "y": 0}, {"x": 0, "y": 1}, {"x": 0, "y": 2}, {"x": 1, "y": 0}, {"x": 1, "y": 2}],
    "16": [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0}, {"x": 2, "y": 1}, {"x": 2, "y": 2}],
    "17": [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0}, {"x": 0, "y": 1}, {"x": 0, "y": 2}],
    "18": [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 1, "y": 1}, {"x": 1, "y": 2}, {"x": 2, "y": 2}],
    "19": [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 1, "y": 1}, {"x": 2, "y": 1}, {"x": 2, "y": 2}],
    "20": [{"x": 1, "y": 0}, {"x": 0, "y": 1}, {"x": 1, "y": 1}, {"x": 2, "y": 1}, {"x": 1, "y": 2}],
    "21": [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0}, {"x": 1, "y": 1}, {"x": 1, "y": 2}],
}

# Pre-kalkulacja unikalnych orientacji geometrycznych dla wydajności
CACHED_ORIENTATIONS: dict[str, list[list[dict]]] = {}

def get_possible_orientations(squares: list[dict]) -> list[list[dict]]:
    orientations = []
    current = squares
    for _ in range(2):  # oryginał i lustrzane odbicie
        for _ in range(4):  # 4 obroty co 90 stopni
            min_x = min(sq["x"] for sq in current)
            min_y = min(sq["y"] for sq in current)
            normalized = sorted(
                [{"x": sq["x"] - min_x, "y": sq["y"] - min_y} for sq in current],
                key=lambda s: (s["x"], s["y"])
            )
            if normalized not in orientations:
                orientations.append(normalized)
            current = [{"x": -sq["y"], "y": sq["x"]} for sq in current]
        current = [{"x": -sq["x"], "y": sq["y"]} for sq in current]
    return orientations

for p_id, p_squares in PIECE_SHAPES.items():
    CACHED_ORIENTATIONS[p_id] = get_possible_orientations(p_squares)


def get_player_corners(grid: dict, player_id: str) -> list[tuple[int, int]]:
    """Zwraca listę wolnych pól na planszy, które stykają się rogiem z klockami gracza i nie dotykają bokiem."""
    has_pieces = any(v == player_id for v in grid.values())
    if not has_pieces:
        # Pierwszy ruch — róg startowy
        start_corners = {"P1": (0, 0), "P2": (19, 0), "P3": (19, 19), "P4": (0, 19)}
        return [start_corners[player_id]]

    potential_corners = set()
    directions_corner = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    directions_edge = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    for key, owner in grid.items():
        if owner == player_id:
            x, y = map(int, key.split(","))
            for dx, dy in directions_corner:
                cx, cy = x + dx, y + dy
                if 0 <= cx < 20 and 0 <= cy < 20 and f"{cx},{cy}" not in grid:
                    # Sprawdź, czy nie styka się bokiem z własnym kolorem
                    touches_own_edge = False
                    for ex, ey in directions_edge:
                        if grid.get(f"{cx + ex},{cy + ey}") == player_id:
                            touches_own_edge = True
                            break
                    if not touches_own_edge:
                        potential_corners.add((cx, cy))

    return list(potential_corners)


def evaluate_move_normal(squares: list[dict]) -> float:
    """Heurystyka dla Bota Zwyczajnego: preferuj duże klocki i ruch ku środkowi planszy."""
    piece_size = len(squares)
    score = piece_size * 20.0

    # Środek planszy 20x20 to punkt (9.5, 9.5)
    center_dist = sum(math.hypot(sq["x"] - 9.5, sq["y"] - 9.5) for sq in squares) / piece_size
    # Im bliżej środka, tym mniejszy dystans, czyli wyższy bonus
    score += (15.0 - center_dist) * 2.0
    return score


def evaluate_move_master(grid: dict, squares: list[dict], player_id: str) -> float:
    """
    Heurystyka dla Bota Mistrza:
    1. Duże klocki (zwłaszcza trudne pentomina o nieregularnym kształcie).
    2. Zdobywanie nowych narożników (mobilność na przyszłość).
    3. Przesuwanie się w głąb planszy i blokowanie narożników przeciwników.
    """
    piece_size = len(squares)
    score = piece_size * 35.0

    # Symulacja tymczasowego położenia klocka
    simulated_grid = grid.copy()
    for sq in squares:
        simulated_grid[f"{sq['x']},{sq['y']}"] = player_id

    # 1. Mobilność: Ile nowych rogów zyskujemy po tym ruchu?
    new_corners = len(get_player_corners(simulated_grid, player_id))
    score += new_corners * 8.0

    # 2. Dystans do środka planszy
    center_dist = sum(math.hypot(sq["x"] - 9.5, sq["y"] - 9.5) for sq in squares) / piece_size
    score += (15.0 - center_dist) * 4.0

    # 3. Blokowanie: Czy ten ruch dotyka krawędzią potencjalnych rogów przeciwników?
    directions_edge = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    blocked_opponent_potential = 0
    for sq in squares:
        for dx, dy in directions_edge:
            nx, ny = sq["x"] + dx, sq["y"] + dy
            neighbor_key = f"{nx},{ny}"
            if neighbor_key in grid and grid[neighbor_key] != player_id:
                blocked_opponent_potential += 1
    score += blocked_opponent_potential * 6.0

    return score


def find_bot_move(grid: dict, inventory: list[str], player_id: str, difficulty: str):
    """
    Główna funkcja wyboru ruchu bota z uwzględnieniem 3 poziomów trudności.
    Zwraca (piece_id, target_squares) lub (None, None).
    """
    if not inventory:
        return None, None

    # Zoptymalizowane szukanie punktów zaczepienia (narożniki)
    target_anchors = get_player_corners(grid, player_id)
    if not target_anchors:
        return None, None

    # Sortowanie inwentarza w zależności od poziomu trudności
    sorted_inventory = inventory.copy()
    if difficulty == "BOT_EASY":
        random.shuffle(sorted_inventory)
    else:
        # Zwyczajny i Mistrz zaczynają od klocków największych (5-polowych)
        sorted_inventory.sort(
            key=lambda pid: len(PIECE_SHAPES.get(pid, [])),
            reverse=True
        )

    legal_moves: list[tuple[str, list[dict], float]] = []

    for piece_id in sorted_inventory:
        variants = CACHED_ORIENTATIONS.get(piece_id, [])

        for variant in variants:
            # Każdy kwadrat klocka próbujemy przyłożyć do każdego wolnego narożnika gracza
            for anchor_x, anchor_y in target_anchors:
                for sq in variant:
                    origin_x = anchor_x - sq["x"]
                    origin_y = anchor_y - sq["y"]

                    target_squares = [
                        {"x": origin_x + s["x"], "y": origin_y + s["y"]}
                        for s in variant
                    ]

                    is_valid, _ = is_move_valid_blokus(grid, target_squares, player_id)
                    if is_valid:
                        if difficulty == "BOT_EASY":
                            # Łatwy: zwraca natychmiast pierwszy poprawny ruch
                            return piece_id, target_squares

                        # Oblicz ocenę heurystyczną
                        if difficulty == "BOT_NORMAL":
                            move_score = evaluate_move_normal(target_squares)
                        else:  # BOT_MASTER
                            move_score = evaluate_move_master(grid, target_squares, player_id)

                        legal_moves.append((piece_id, target_squares, move_score))

                        # Ograniczenie próbkowania dla zachowania czasu <150ms
                        limit = 35 if difficulty == "BOT_NORMAL" else 60
                        if len(legal_moves) >= limit:
                            break
                if legal_moves and len(legal_moves) >= (35 if difficulty == "BOT_NORMAL" else 60):
                    break
            if legal_moves and len(legal_moves) >= (35 if difficulty == "BOT_NORMAL" else 60):
                break

        # Jeśli dla trudniejszych botów znaleźliśmy już legalne ruchy dużymi klockami, wybierz najlepszy
        if legal_moves and difficulty in ("BOT_NORMAL", "BOT_MASTER"):
            # Sortuj malejąco po ocenie punktowej
            legal_moves.sort(key=lambda m: m[2], reverse=True)
            # Normalny dodaje odrobinę losowości z 3 najlepszych; Mistrz zawsze bierze absolutnie najlepszy
            if difficulty == "BOT_NORMAL":
                chosen = random.choice(legal_moves[:min(3, len(legal_moves))])
            else:
                chosen = legal_moves[0]
            return chosen[0], chosen[1]

    if legal_moves:
        legal_moves.sort(key=lambda m: m[2], reverse=True)
        return legal_moves[0][0], legal_moves[0][1]

    return None, None