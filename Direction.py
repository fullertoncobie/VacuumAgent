from enum import Enum
from typing import Tuple, Optional

class Direction(Enum):
    """
    Enum representing cardinal directions with associated movement vectors and angle information.
    Used by the vacuum agent for navigation and orientation in the environment.
    """
    NORTH = (0, (0, 1), 'delta_u')
    EAST = (90, (1, 0), 'delta_r')
    SOUTH = (180, (0, -1), 'delta_d')
    WEST = (270, (-1, 0), 'delta_l')

    def __init__(self, angle: int, movement_vector: Tuple[int, int], delta_key: str):
        """
        Initialize a Direction with its angle, movement vector, and corresponding delta key.
        
        Args:
            angle: The angle in degrees (0=North, 90=East, etc.)
            movement_vector: The (x, y) vector to move in this direction
            delta_key: Key used to access height delta in environment data
        """
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
        """
        Get a direction from an angle in degrees.
        
        Args:
            angle: The angle in degrees
            
        Returns:
            The corresponding Direction enum value
        """
        normalized_angle = angle % 360
        direction_map = {
            0: cls.NORTH,
            90: cls.EAST,
            180: cls.SOUTH,
            270: cls.WEST
        }
        return direction_map[normalized_angle]
    
    def get_relative_position(self, position: str) -> Optional[Tuple[int, int]]:
        """
        Get the movement vector for a relative position.
        
        Args:
            position: One of 'forward', 'left', or 'right'
            
        Returns:
            The movement vector as (x, y) tuple, or None if the position is invalid
        """
        if position == 'forward':
            return self.movement_vector
        elif position == 'left':
            return self.left.movement_vector
        elif position == 'right':
            return self.right.movement_vector
        return None
