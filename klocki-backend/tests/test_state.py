from app.game.state import GameState

def test_add_players_and_start_game():
    game = GameState()
    assert game.status == "WAITING"
    
    assert game.add_player("P1") is True
    assert game.add_player("P2") is True
    assert len(game.players) == 2
    
    assert game.start_game() is True
    assert game.status == "PLAYING"
    
    # Nie można dodawać graczy w trakcie gry
    assert game.add_player("P3") is False

def test_turn_order_and_passing():
    game = GameState()
    game.add_player("P1")
    game.add_player("P2")
    game.add_player("P3")
    game.start_game()
    
    # Pierwsza tura: P1
    assert game.get_current_player().player_id == "P1"
    
    # P1 pasuje, tura przechodzi na P2
    assert game.pass_turn("P1") is True
    assert game.get_current_player().player_id == "P2"
    
    # P2 próbuje spasować nie w swojej turze (błąd, bo podajemy P1)
    assert game.pass_turn("P1") is False 
    
    # P2 pasuje
    game.pass_turn("P2")
    assert game.get_current_player().player_id == "P3"
    
    # P3 pasuje - WSZYSCY SPASOWALI
    game.pass_turn("P3")
    assert game.status == "FINISHED"
    assert game.get_current_player() is None