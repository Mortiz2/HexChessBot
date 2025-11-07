import math
import collections

# Representation of a single hex cell in cube coordinates (q, r, s)
_Hex = collections.namedtuple("Hex", ["q", "r", "s"])

def Hex(q, r, s):
    # In cube coordinates, q + r + s must always be 0
    assert round(q + r + s) == 0, "q + r + s must be 0"
    return _Hex(q, r, s)


# --- Basic operations on hexes ---

def hex_add(a, b):
    """Add two hex coordinates."""
    return Hex(a.q + b.q, a.r + b.r, a.s + b.s)

def hex_subtract(a, b):
    """Subtract one hex coordinate from another."""
    return Hex(a.q - b.q, a.r - b.r, a.s - b.s)


# --- Directions and neighbors ---

# The six possible directions from any hex (clockwise)
hex_directions = [
    Hex(1, 0, -1), Hex(1, -1, 0), Hex(0, -1, 1),
    Hex(-1, 0, 1), Hex(-1, 1, 0), Hex(0, 1, -1)
]

def hex_direction(direction):
    """Get the direction vector (0–5)."""
    return hex_directions[direction]

def hex_neighbor(hex, direction):
    """Return the neighboring hex in the given direction (0–5)."""
    return hex_add(hex, hex_direction(direction))


# --- Distance between two hexes ---

def hex_distance(a, b):
    """Compute hex distance (number of steps between two hexes)."""
    return (abs(a.q - b.q) + abs(a.r - b.r) + abs(a.s - b.s)) // 2


# --- Example usage ---

if __name__ == "__main__":
    center = Hex(0, 0, 0)

    # List all neighbors around the center
    neighbors = [hex_neighbor(center, d) for d in range(6)]
    print("Neighbors:", neighbors)

    # Compute distance between two hexes
    a = Hex(0, 0, 0)
    b = Hex(2, -1, -1)
    print("Distance:", hex_distance(a, b))
