from typing import List, Tuple
from app.game.piece import Piece

# Katalog definiuje kształty we współrzędnych (x, y).
# System automatycznie je "znormalizuje" w klasie Piece.
PIECES_DEFINITIONS = {
    # 1-polowe (Monomino) - 1 sztuka
    "I1": [(0, 0)],
    
    # 2-polowe (Domino) - 1 sztuka
    "I2": [(0, 0), (1, 0)],
    
    # 3-polowe (Tromina) - 2 sztuki
    "I3": [(0, 0), (1, 0), (2, 0)],
    "V3": [(0, 0), (0, 1), (1, 1)],
    
    # 4-polowe (Tetromina) - 5 sztuk
    "I4": [(0, 0), (1, 0), (2, 0), (3, 0)],
    "O4": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "T4": [(0, 0), (1, 0), (2, 0), (1, 1)],
    "L4": [(0, 0), (0, 1), (0, 2), (1, 2)],
    "Z4": [(0, 0), (1, 0), (1, 1), (2, 1)],
    
    # 5-polowe (Pentomina) - 12 sztuk
    "F5": [(1, 0), (2, 0), (0, 1), (1, 1), (1, 2)],
    "I5": [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
    "L5": [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3)],
    "N5": [(1, 0), (1, 1), (0, 2), (1, 2), (0, 3)],
    "P5": [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)],
    "T5": [(0, 0), (1, 0), (2, 0), (1, 1), (1, 2)],
    "U5": [(0, 0), (2, 0), (0, 1), (1, 1), (2, 1)],
    "V5": [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)],
    "W5": [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)],
    "X5": [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)],
    "Y5": [(1, 0), (0, 1), (1, 1), (1, 2), (1, 3)],
    "Z5": [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2)]
}

def get_full_set() -> List[Piece]:
    """
    Zwraca nową listę zawierającą pełny zestaw 21 klocków.
    Każdy gracz musi otrzymać wywołanie tej funkcji.
    """
    return [Piece(piece_id, squares) for piece_id, squares in PIECES_DEFINITIONS.items()]