"""Camera type definitions for thermal imaging."""

from enum import Enum, auto


class CameraType(Enum):
    """Enumeration of supported thermal camera types."""
    MOBOTIX = auto()
    FLIR = auto()
    
    @classmethod
    def from_string(cls, name):
        """Convert string to camera type enum."""
        name = name.upper()
        if name == 'MOBOTIX':
            return cls.MOBOTIX
        elif name == 'FLIR':
            return cls.FLIR
        else:
            raise ValueError(f"Unknown camera type: {name}")
    
    def __str__(self):
        """Return the string representation of the camera type."""
        return self.name.capitalize()