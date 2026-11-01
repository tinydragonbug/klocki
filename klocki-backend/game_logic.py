BOARD_SIZE = 20

def is_move_valid_blokus(grid: dict, squares: list, player_id: str) -> tuple[bool, str]:
    # 1. Sprawdzenie granic planszy i kolizji
    for sq in squares:
        if sq['x'] < 0 or sq['x'] >= 20 or sq['y'] < 0 or sq['y'] >= 20:
            return False, "Klocek wychodzi poza planszę."
        
        target_key = f"{sq['x']},{sq['y']}"
        if target_key in grid:
            return False, "Pole jest już zajęte."

    # Sprawdzamy, czy to pierwszy ruch gracza na planszy
    has_pieces = any(val == player_id for val in grid.values())

    if not has_pieces:
        # ZASADA 1. RUCHU: Musi precyzyjnie dotykać odpowiedniego narożnika
        starting_corners = {
            "P1": "0,0",
            "P2": "19,0",
            "P3": "19,19",
            "P4": "0,19"
        }
        
        my_corner = starting_corners.get(player_id)
        if not my_corner:
            return False, "Nieznany identyfikator gracza."
            
        touches_corner = any(f"{sq['x']},{sq['y']}" == my_corner for sq in squares)
        
        if not touches_corner:
            return False, f"Pierwszy ruch musi dotykać rogu startowego: {my_corner}."
            
        return True, "Poprawny pierwszy ruch."

    # Kolejne ruchy - standardowe zasady Blokusa
    directions_edge = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    directions_corner = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    
    touches_my_corner = False

    for sq in squares:
        # Sprawdzanie styku krawędzi (Niedozwolone)
        for dx, dy in directions_edge:
            neighbor = f"{sq['x'] + dx},{sq['y'] + dy}"
            if grid.get(neighbor) == player_id:
                return False, "Klocek nie może stykać się bokiem z Twoim klockiem."
                
        # Sprawdzanie styku rogów (Wymagane minimum jedno)
        for dx, dy in directions_corner:
            corner = f"{sq['x'] + dx},{sq['y'] + dy}"
            if grid.get(corner) == player_id:
                touches_my_corner = True

    if not touches_my_corner:
        return False, "Klocek musi stykać się rogiem z Twoim innym klockiem."

    return True, "Poprawny ruch."

# Słownik kształtów do szybkiej weryfikacji dostępności ruchów
PIECE_SHAPES_EVAL = {
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

def generate_orientations_eval(squares: list[dict]) -> list[list[dict]]:
    orientations = []
    current = squares
    for _ in range(2):
        for _ in range(4):
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

CACHED_ORIENTATIONS_EVAL = {
    p_id: generate_orientations_eval(sqs) for p_id, sqs in PIECE_SHAPES_EVAL.items()
}

def get_player_available_corners(grid: dict, player_id: str) -> list[tuple[int, int]]:
    has_pieces = any(v == player_id for v in grid.values())
    if not has_pieces:
        start_corners = {"P1": (0, 0), "P2": (19, 0), "P3": (19, 19), "P4": (0, 19)}
        return [start_corners[player_id]]

    potential = set()
    dirs_corner = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    dirs_edge = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    for key, owner in grid.items():
        if owner == player_id:
            x, y = map(int, key.split(","))
            for dx, dy in dirs_corner:
                cx, cy = x + dx, y + dy
                if 0 <= cx < 20 and 0 <= cy < 20 and f"{cx},{cy}" not in grid:
                    touches_edge = False
                    for ex, ey in dirs_edge:
                        if grid.get(f"{cx + ex},{cy + ey}") == player_id:
                            touches_edge = True
                            break
                    if not touches_edge:
                        potential.add((cx, cy))
    return list(potential)

def player_has_any_valid_move(grid: dict, inventory: list[str], player_id: str) -> bool:
    """
    Sprawdza, czy gracz może wykonać choć jeden legalny ruch na planszy.
    Zwraca True przy pierwszym napotkanym poprawnym ruchu (early exit).
    """
    if not inventory:
        return False

    corners = get_player_available_corners(grid, player_id)
    if not corners:
        return False

    for piece_id in inventory:
        variants = CACHED_ORIENTATIONS_EVAL.get(piece_id, [])
        for variant in variants:
            for ax, ay in corners:
                for sq in variant:
                    ox = ax - sq["x"]
                    oy = ay - sq["y"]
                    target = [{"x": ox + s["x"], "y": oy + s["y"]} for s in variant]
                    valid, _ = is_move_valid_blokus(grid, target, player_id)
                    if valid:
                        return True
    return False