import pytest
from game_logic import is_move_valid_blokus, player_has_any_valid_move

# ============================================================================
# 1. TESTY GRANIC PLANSZY I KOLIZJI
# ============================================================================

def test_move_out_of_bounds():
    """Ruch wychodzący poza planszę 20x20 musi zostać odrzucony."""
    grid = {}
    # Klocek wystający poza prawą krawędź planszy
    invalid_squares = [{"x": 19, "y": 0}, {"x": 20, "y": 0}]
    is_valid, reason = is_move_valid_blokus(grid, invalid_squares, "P1")
    assert is_valid is False
    assert "poza planszę" in reason

    # Klocek ze współrzędną ujemną
    invalid_squares_neg = [{"x": -1, "y": 0}, {"x": 0, "y": 0}]
    is_valid, reason = is_move_valid_blokus(grid, invalid_squares_neg, "P1")
    assert is_valid is False
    assert "poza planszę" in reason


def test_move_collision_with_existing_piece():
    """Ruch na pole już zajęte musi zostać odrzucony."""
    grid = {"5,5": "P2"}
    # Próba położenia klocka na zajętym polu (5,5)
    move_squares = [{"x": 5, "y": 5}, {"x": 5, "y": 6}]
    is_valid, reason = is_move_valid_blokus(grid, move_squares, "P1")
    assert is_valid is False
    assert "Pole jest już zajęte" in reason


# ============================================================================
# 2. TESTY ZASADY PIERWSZEGO RUCHU (DEDYKOWANE NAROŻNIKI)
# ============================================================================

@pytest.mark.parametrize("player_id, corner_x, corner_y", [
    ("P1", 0, 0),      # Lewy Górny
    ("P2", 19, 0),     # Prawy Górny
    ("P3", 19, 19),    # Prawy Dolny
    ("P4", 0, 19),     # Lewy Dolny
])
def test_first_move_valid_corners(player_id, corner_x, corner_y):
    """Każdy z 4 graczy musi mieć możliwość poprawnego rozpoczęcia gry w swoim rogu."""
    grid = {}
    move_squares = [{"x": corner_x, "y": corner_y}]
    is_valid, reason = is_move_valid_blokus(grid, move_squares, player_id)
    assert is_valid is True
    assert "Poprawny pierwszy ruch" in reason


@pytest.mark.parametrize("player_id, wrong_corner_x, wrong_corner_y", [
    ("P1", 19, 0),     # P1 w rogu P2
    ("P2", 0, 0),      # P2 w rogu P1
    ("P3", 0, 19),     # P3 w rogu P4
    ("P4", 19, 19),    # P4 w rogu P3
    ("P1", 5, 5),      # Dowolne pole w środku
])
def test_first_move_invalid_starting_position(player_id, wrong_corner_x, wrong_corner_y):
    """Próba wykonania 1. ruchu w cudzym rogu lub na środku planszy musi zostać odrzucona."""
    grid = {}
    move_squares = [{"x": wrong_corner_x, "y": wrong_corner_y}]
    is_valid, reason = is_move_valid_blokus(grid, move_squares, player_id)
    assert is_valid is False
    assert "Pierwszy ruch musi dotykać rogu startowego" in reason


# ============================================================================
# 3. TESTY STYKU KRAWĘDZIAMI I ROGAMI (STANDARDOWE REGUŁY BLOKUSA)
# ============================================================================

def test_edge_contact_with_own_piece_forbidden():
    """Klocek NIE MOŻE stykać się bokiem (krawędzią) z innym klockiem tego samego gracza."""
    # P1 ma już klocek w rogu (0,0)
    grid = {"0,0": "P1"}
    
    # Próba położenia klocka bezpośrednio pod nim (0,1) — styk krawędzią
    move_squares = [{"x": 0, "y": 1}]
    is_valid, reason = is_move_valid_blokus(grid, move_squares, "P1")
    assert is_valid is False
    assert "nie może stykać się bokiem" in reason


def test_corner_contact_with_own_piece_required():
    """Klocek MUSI stykać się co najmniej jednym rogiem z własnym klockiem."""
    # P1 ma klocek w rogu (0,0)
    grid = {"0,0": "P1"}

    # Ruch po przekątnej na pole (1,1) — idealny styk narożnikiem
    valid_squares = [{"x": 1, "y": 1}]
    is_valid, reason = is_move_valid_blokus(grid, valid_squares, "P1")
    assert is_valid is True
    assert "Poprawny ruch" in reason

    # Ruch oddalony (2,2) bez żadnego styku z P1
    isolated_squares = [{"x": 2, "y": 2}]
    is_valid, reason = is_move_valid_blokus(grid, isolated_squares, "P1")
    assert is_valid is False
    assert "musi stykać się rogiem" in reason


def test_edge_contact_with_opponent_allowed():
    """Klocek MOŻE (i często taktycznie powinien) stykać się bokiem z klockiem PRZECIWNIKA."""
    # P1 ma klocek w (1,1), a przeciwnik P2 stoi w (1,2)
    grid = {
        "0,0": "P1",
        "1,2": "P2"
    }
    # P1 kładzie klocek na (1,1) — styka się rogiem z własnym (0,0) ORAZ bokiem z wrogim P2 (1,2)
    move_squares = [{"x": 1, "y": 1}]
    is_valid, reason = is_move_valid_blokus(grid, move_squares, "P1")
    assert is_valid is True
    assert "Poprawny ruch" in reason


# ============================================================================
# 4. TEST DETEKCJI BRAKU RUCHÓW (AUTO-PASS)
# ============================================================================

def test_player_has_no_valid_moves_when_completely_blocked():
    """Gdy gracz nie ma żadnego dostępnego narożnika, funkcja musi zwrócić False."""
    # P1 w rogu (0,0) zostaje szczelnie otoczony przez klocki przeciwnika P2 na (0,1) i (1,0)
    # oraz pole przekątne (1,1) jest zajęte
    grid = {
        "0,0": "P1",
        "0,1": "P2",
        "1,0": "P2",
        "1,1": "P2"
    }
    # Inwentarz P1 zawiera najmniejszy klocek 1-polowy
    inventory = ["1"]
    has_move = player_has_any_valid_move(grid, inventory, "P1")
    assert has_move is False


def test_player_has_moves_available():
    """Na pustej planszy gracz z niepustym inwentarzem zawsze ma co najmniej jeden legalny ruch."""
    grid = {}
    inventory = ["1", "2", "3"]
    assert player_has_any_valid_move(grid, inventory, "P1") is True