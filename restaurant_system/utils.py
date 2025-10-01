"""
Utility Functions and Helper Classes

This module contains utility functions and helper classes used throughout
the restaurant order management system.
"""

from datetime import datetime
from typing import Tuple
import config


def format_timestamp(dt: datetime = None) -> str:
    """
    Format a datetime object as a timestamp string.
    
    Args:
        dt (datetime): Datetime to format (defaults to now)
        
    Returns:
        str: Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(config.LOG_TIMESTAMP_FORMAT)


def get_state_color(state: str) -> str:
    """
    Get the color code for a thread state.
    
    Args:
        state (str): Thread state (RUNNING, WAITING, BLOCKED, IDLE)
        
    Returns:
        str: Hex color code
    """
    state_colors = {
        'RUNNING': config.COLOR_RUNNING,
        'WAITING': config.COLOR_WAITING,
        'BLOCKED': config.COLOR_BLOCKED,
        'IDLE': config.COLOR_IDLE,
    }
    return state_colors.get(state, config.COLOR_IDLE)


def get_log_color(level: str) -> str:
    """
    Get the color code for a log level.
    
    Args:
        level (str): Log level (INFO, WARNING, ERROR)
        
    Returns:
        str: Hex color code
    """
    level_colors = {
        'INFO': config.COLOR_LOG_INFO,
        'WARNING': config.COLOR_LOG_BLOCKING,
        'ERROR': config.COLOR_LOG_BLOCKING,
    }
    return level_colors.get(level, config.COLOR_LOG_INFO)


def lighten_color(hex_color: str, factor: float = 0.3) -> str:
    """
    Lighten a hex color by a given factor.
    
    Args:
        hex_color (str): Hex color code (e.g., "#FF0000")
        factor (float): Lightening factor (0.0 to 1.0)
        
    Returns:
        str: Lightened hex color code
    """
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')
    
    # Convert to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # Lighten
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    
    # Clamp values
    r = min(255, max(0, r))
    g = min(255, max(0, g))
    b = min(255, max(0, b))
    
    # Convert back to hex
    return f"#{r:02x}{g:02x}{b:02x}"


def darken_color(hex_color: str, factor: float = 0.3) -> str:
    """
    Darken a hex color by a given factor.
    
    Args:
        hex_color (str): Hex color code (e.g., "#FF0000")
        factor (float): Darkening factor (0.0 to 1.0)
        
    Returns:
        str: Darkened hex color code
    """
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')
    
    # Convert to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # Darken
    r = int(r * (1 - factor))
    g = int(g * (1 - factor))
    b = int(b * (1 - factor))
    
    # Clamp values
    r = min(255, max(0, r))
    g = min(255, max(0, g))
    b = min(255, max(0, b))
    
    # Convert back to hex
    return f"#{r:02x}{g:02x}{b:02x}"


def validate_config_value(value: int, min_val: int, max_val: int, default: int) -> int:
    """
    Validate and clamp a configuration value.
    
    Args:
        value (int): Value to validate
        min_val (int): Minimum allowed value
        max_val (int): Maximum allowed value
        default (int): Default value if invalid
        
    Returns:
        int: Validated value
    """
    try:
        value = int(value)
        if min_val <= value <= max_val:
            return value
        return default
    except (ValueError, TypeError):
        return default


class RateLimiter:
    """
    Simple rate limiter to prevent excessive GUI updates.
    
    This helps maintain smooth performance by limiting how frequently
    certain operations can occur.
    """
    
    def __init__(self, max_rate: float):
        """
        Initialize rate limiter.
        
        Args:
            max_rate (float): Maximum operations per second
        """
        self.min_interval = 1.0 / max_rate
        self.last_time = 0.0
    
    def can_proceed(self) -> bool:
        """
        Check if enough time has passed since last operation.
        
        Returns:
            bool: True if operation can proceed
        """
        current_time = datetime.now().timestamp()
        if current_time - self.last_time >= self.min_interval:
            self.last_time = current_time
            return True
        return False
    
    def reset(self) -> None:
        """Reset the rate limiter."""
        self.last_time = 0.0


class CircularBuffer:
    """
    Simple circular buffer for storing limited number of items.
    Useful for keeping recent log entries.
    """
    
    def __init__(self, capacity: int):
        """
        Initialize circular buffer.
        
        Args:
            capacity (int): Maximum number of items to store
        """
        self.capacity = capacity
        self.buffer = []
    
    def append(self, item) -> None:
        """Add item to buffer, removing oldest if full."""
        self.buffer.append(item)
        if len(self.buffer) > self.capacity:
            self.buffer.pop(0)
    
    def get_all(self) -> list:
        """Get all items in buffer."""
        return self.buffer.copy()
    
    def clear(self) -> None:
        """Clear all items from buffer."""
        self.buffer.clear()
    
    def __len__(self) -> int:
        """Get current number of items in buffer."""
        return len(self.buffer)


def create_tooltip_text(component: str) -> str:
    """
    Create helpful tooltip text for UI components.
    
    Args:
        component (str): Component identifier
        
    Returns:
        str: Tooltip text explaining the component
    """
    tooltips = {
        'chef_state': 'Thread State:\n🟢 RUNNING - Actively working\n🟡 WAITING - Waiting for buffer space\n🔴 BLOCKED - Paused or blocked',
        'waiter_state': 'Thread State:\n🟢 RUNNING - Actively working\n🟡 WAITING - Waiting for orders\n🔴 BLOCKED - Paused or blocked',
        'buffer': 'Kitchen Counter (Shared Buffer):\nFixed-size buffer protected by semaphores.\nChefs add orders, waiters remove them.',
        'statistics': 'Real-time Statistics:\nTracks total orders produced and consumed,\ncurrent buffer occupancy.',
        'speed': 'Simulation Speed:\nControls how fast threads work.\nHigher = faster simulation.',
        'control': 'Simulation Controls:\nStart/Pause/Reset the simulation.\nReconfigure thread counts and buffer size.',
    }
    return tooltips.get(component, 'No description available')


def format_number(num: int) -> str:
    """
    Format a number with thousands separators.
    
    Args:
        num (int): Number to format
        
    Returns:
        str: Formatted number string
    """
    return f"{num:,}"