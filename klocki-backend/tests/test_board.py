from app.game.board import Board
from app.game.piece import Piece

def test_board_initialization():
    board = Board()
    assert board.size == 20
    assert len(board.grid) == 0

def test_place_piece_successfully():
    board = Board()
    piece = Piece("LINE3", [(0, 0), (1, 0), (2, 0)])
    assert board.place_piece(piece, 0, 0, "player_1") is True

def test_place_piece_out_of_bounds():
    board = Board()
    piece = Piece("LINE3", [(0, 0), (1, 0), (2, 0)])
    assert board.place_piece(piece, 19, 0, "player_1") is False

def test_place_piece_on_occupied_squares():
    board = Board()
    piece1 = Piece("DOT", [(0, 0)])
    piece2 = Piece("LINE3", [(0, 0), (1, 0), (2, 0)])
    
    board.place_piece(piece1, 5, 5, "player_1")
    assert board.place_piece(piece2, 4, 5, "player_2") is False

def test_contact_rule_fails_if_touching_own_edge():
    board = Board()
    piece1 = Piece("DOT", [(0, 0)])
    piece2 = Piece("DOT", [(0, 0)])
    
    board.place_piece(piece1, 5, 5, "player_1")
    assert board.place_piece(piece2, 6, 5, "player_1") is False

def test_contact_rule_succeeds_if_touching_own_corner():
    board = Board()
    piece1 = Piece("DOT", [(0, 0)])
    piece2 = Piece("DOT", [(0, 0)])
    
    board.place_piece(piece1, 5, 5, "player_1")
    assert board.place_piece(piece2, 6, 6, "player_1") is True

def test_different_players_can_touch_edges():
    board = Board()
    piece1 = Piece("DOT", [(0, 0)])
    piece2 = Piece("DOT", [(0, 0)])
    
    board.place_piece(piece1, 5, 5, "player_1")
    assert board.place_piece(piece2, 6, 5, "player_2") is True

# --- NOWE TESTY REGULY PIERWSZEGO RUCHU ---

def test_first_move_must_cover_start_position():
    # Definiujemy narożniki dla dwóch graczy
    starts = {"P1": (0, 0), "P2": (19, 19)}
    board = Board(size=20, start_positions=starts)
    
    piece = Piece("LINE3", [(0, 0), (1, 0), (2, 0)])
    
    # Próba 1: Gracz 1 kładzie klocek gdzieś na środku (błąd)
    assert board.place_piece(piece, 5, 5, "P1") is False
    
    # Próba 2: Gracz 1 kładzie klocek tak, że przykrywa pole (0,0) - (sukces)
    assert board.place_piece(piece, 0, 0, "P1") is True

def test_first_move_start_position_for_another_player():
    starts = {"P1": (0, 0), "P2": (19, 19)}
    board = Board(size=20, start_positions=starts)
    
    # Dla ułatwienia testu używamy klocka jednopunktowego
    piece = Piece("DOT", [(0, 0)])
    
    # Gracz 2 musi zająć pole (19, 19)
    assert board.place_piece(piece, 19, 19, "P2") is True