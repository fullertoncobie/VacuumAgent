"""
Direction module for vacuum agent navigation.
Represents cardinal directions with movement vectors and angle information.
"""
from enum import Enum
from typing import Tuple, Optional

class Direction(Enum):
    """Cardinal directions with movement vectors and angle information."""
    NORTH = (0, (0, 1), 'delta_u')
    EAST = (90, (1, 0), 'delta_r')
    SOUTH = (180, (0, -1), 'delta_d')
    WEST = (270, (-1, 0), 'delta_l')

    def __init__(self, angle: int, movement_vector: Tuple[int, int], delta_key: str):
        """Initialize direction with angle, movement vector, and delta key."""
        self.angle = angle
        self.movement_vector = movement_vector
        self.delta_key = delta_key
    
    @property
    def left(self) -> 'Direction':
        """Return the direction 90 degrees to the left."""
        return Direction.from_angle(self.angle - 90)
    
    @property
    def right(self) -> 'Direction':
        """Return the direction 90 degrees to the right."""
        return Direction.from_angle(self.angle + 90)
    
    @classmethod
    def from_angle(cls, angle: int) -> 'Direction':
        """Get a direction from an angle in degrees."""
        normalized_angle = angle % 360
        direction_map = {
            0: cls.NORTH,
            90: cls.EAST,
            180: cls.SOUTH,
            270: cls.WEST
        }
        return direction_map[normalized_angle]
    
    def get_relative_position(self, position: str) -> Optional[Tuple[int, int]]:
        """Get movement vector for a relative position (forward, left, right)."""
        if position == 'forward':
            return self.movement_vector
        elif position == 'left':
            return self.left.movement_vector
        elif position == 'right':
            return self.right.movement_vector
        return None
