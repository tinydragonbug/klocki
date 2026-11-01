from typing import List, Tuple

class Piece:
    def __init__(self, piece_id: str, squares: List[Tuple[int, int]]):
        self.id = piece_id
        self.squares = self._normalize(squares)

    def _normalize(self, squares: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if not squares:
            return []
        
        min_x = min(sq[0] for sq in squares)
        min_y = min(sq[1] for sq in squares)
        
        normalized = [((sq[0] - min_x), (sq[1] - min_y)) for sq in squares]
        return sorted(normalized)

    def rotate_90(self) -> 'Piece':
        rotated_squares = [(-y, x) for x, y in self.squares]
        return Piece(self.id, rotated_squares)

    def flip_horizontal(self) -> 'Piece':
        flipped_squares = [(-x, y) for x, y in self.squares]
        return Piece(self.id, flipped_squares)

    def get_squares_at(self, board_x: int, board_y: int) -> List[Tuple[int, int]]:
        return [(x + board_x, y + board_y) for x, y in self.squares]