from typing import List, Optional, Dict
from app.game.board import Board
from app.game.catalog import get_full_set  # <--- NOWY IMPORT

class PlayerState:
    def __init__(self, player_id: str):
        self.player_id = player_id
        self.has_passed = False
        self.available_pieces = get_full_set()  # <--- KAŻDY GRACZ DOSTAJE 21 KLOCKÓW
        self.score = 0

class GameState:
    def __init__(self):
        # Konfiguracja 4 narożników dla maksymalnie 4 graczy
        self.start_positions = {
            "P1": (0, 0), "P2": (19, 0),
            "P3": (19, 19), "P4": (0, 19)
        }
        self.board = Board(size=20, start_positions=self.start_positions)
        self.players: List[PlayerState] = []
        self.current_turn_index = 0
        self.status = "WAITING" # WAITING, PLAYING, FINISHED

    def add_player(self, player_id: str) -> bool:
        """Dodaje gracza do lobby. Zwraca True jeśli się udało."""
        if self.status != "WAITING" or len(self.players) >= 4:
            return False
        
        # Zapobieganie dodaniu tego samego gracza dwukrotnie
        if any(p.player_id == player_id for p in self.players):
            return False

        self.players.append(PlayerState(player_id))
        return True

    def start_game(self) -> bool:
        """Uruchamia rozgrywkę, o ile jest choć jeden gracz."""
        if len(self.players) < 1:
            return False
        self.status = "PLAYING"
        self.current_turn_index = 0
        return True

    def get_current_player(self) -> Optional[PlayerState]:
        """Zwraca gracza, którego aktualnie jest tura."""
        if self.status != "PLAYING":
            return None
        return self.players[self.current_turn_index]

    def pass_turn(self, player_id: str) -> bool:
        """
        Gracz pasuje. Jeśli wszyscy spasują, gra się kończy.
        Zwraca True, jeśli pasowanie zostało przyjęte.
        """
        current_player = self.get_current_player()
        if not current_player or current_player.player_id != player_id:
            return False # Nie można spasować nie w swojej turze

        current_player.has_passed = True
        self._advance_turn()
        return True

    def _advance_turn(self):
        """Mechanika przełączania tury na następnego aktywnego gracza."""
        start_index = self.current_turn_index
        
        for _ in range(len(self.players)):
            self.current_turn_index = (self.current_turn_index + 1) % len(self.players)
            if not self.players[self.current_turn_index].has_passed:
                return # Znaleziono gracza, gra toczy się dalej

        # Jeśli pętla się zakończyła i nie znalazła nikogo aktywnego
        self.status = "FINISHED"