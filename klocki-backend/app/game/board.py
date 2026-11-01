from typing import Dict, Tuple, List, Optional
from app.game.piece import Piece

class Board:
    def __init__(self, size: int = 20, start_positions: Optional[Dict[str, Tuple[int, int]]] = None):
        self.size = size
        self.grid: Dict[Tuple[int, int], str] = {}
        # Słownik: player_id -> (x, y) pola startowego
        self.start_positions = start_positions or {}

    def is_within_bounds(self, squares: List[Tuple[int, int]]) -> bool:
        for x, y in squares:
            if x < 0 or x >= self.size or y < 0 or y >= self.size:
                return False
        return True

    def are_squares_free(self, squares: List[Tuple[int, int]]) -> bool:
        for sq in squares:
            if sq in self.grid:
                return False
        return True

    def validate_contact_rules(self, squares: List[Tuple[int, int]], player_id: str) -> bool:
        # Sprawdzamy, czy gracz kładzie swój pierwszy klocek
        if player_id not in self.grid.values():
            # REGULA PIERWSZEGO RUCHU
            expected_start = self.start_positions.get(player_id)
            if expected_start:
                if expected_start not in squares:
                    return False # Błąd: Pierwszy klocek nie leży na polu startowym
            return True # Jeśli nie przypisano pola startowego, pozwalamy kłaść gdziekolwiek

        touches_own_corner = False

        for x, y in squares:
            # 1. Sprawdzanie boków (zakaz)
            edges = [(x, y-1), (x, y+1), (x-1, y), (x+1, y)]
            for ex, ey in edges:
                if self.grid.get((ex, ey)) == player_id:
                    return False

            # 2. Sprawdzanie narożników (wymóg)
            corners = [(x-1, y-1), (x+1, y-1), (x-1, y+1), (x+1, y+1)]
            for cx, cy in corners:
                if self.grid.get((cx, cy)) == player_id:
                    touches_own_corner = True

        return touches_own_corner

    def place_piece(self, piece: Piece, board_x: int, board_y: int, player_id: str) -> bool:
        target_squares = piece.get_squares_at(board_x, board_y)

        if not self.is_within_bounds(target_squares):
            return False
        if not self.are_squares_free(target_squares):
            return False
        if not self.validate_contact_rules(target_squares, player_id):
            return False

        for sq in target_squares:
            self.grid[sq] = player_id
            
        return True