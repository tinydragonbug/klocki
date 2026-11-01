from app.game.catalog import get_full_set
from app.game.state import GameState

def test_catalog_has_correct_amount_of_pieces_and_squares():
    full_set = get_full_set()
    
    # Warunek 1: Dokładnie 21 klocków
    assert len(full_set) == 21
    
    # Warunek 2: Dokładnie 89 pól
    total_squares = sum(len(piece.squares) for piece in full_set)
    assert total_squares == 89

def test_player_receives_full_set_on_join():
    game = GameState()
    game.add_player("P1")
    
    player = game.players[0]
    
    assert len(player.available_pieces) == 21
    
    # Upewniamy się, że wśród klocków jest "X5" (pentomino) i "I1" (monomino)
    piece_ids = [p.id for p in player.available_pieces]
    assert "X5" in piece_ids
    assert "I1" in piece_ids