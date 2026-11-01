from app.game.piece import Piece

def test_piece_initialization_and_normalization():
    raw_squares = [(2, 2), (3, 2), (4, 2)]
    piece = Piece("LINE3", raw_squares)
    assert piece.squares == [(0, 0), (1, 0), (2, 0)]

def test_piece_rotation_90_degrees():
    raw_squares = [(0, 0), (0, 1), (0, 2), (1, 2)]
    piece = Piece("L4", raw_squares)
    rotated = piece.rotate_90()
    expected_squares = [(0, 0), (0, 1), (1, 0), (2, 0)]
    assert rotated.squares == sorted(expected_squares)

def test_get_squares_at_board_position():
    piece = Piece("DOT", [(0, 0)])
    board_positions = piece.get_squares_at(5, 10)
    assert board_positions == [(5, 10)]