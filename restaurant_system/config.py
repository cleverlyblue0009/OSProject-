"""
Configuration Constants for Restaurant Order Management System

This module contains all configuration constants used throughout the application.
These constants define the behavior of the OS simulation including timing,
threading parameters, and UI styling.
"""

# ==============================================================================
# THREADING CONFIGURATION
# ==============================================================================

# Default number of producer threads (chefs)
DEFAULT_NUM_CHEFS = 3

# Default number of consumer threads (waiters)
DEFAULT_NUM_WAITERS = 3

# Default buffer size (kitchen counter capacity)
DEFAULT_BUFFER_SIZE = 10

# Minimum and maximum values for configuration
MIN_THREADS = 1
MAX_THREADS = 10
MIN_BUFFER_SIZE = 5
MAX_BUFFER_SIZE = 20

# ==============================================================================
# TIMING CONFIGURATION (in seconds)
# ==============================================================================

# Time range for order preparation (chef work time)
MIN_PREPARATION_TIME = 0.5
MAX_PREPARATION_TIME = 2.0

# Time range for order delivery (waiter work time)
MIN_DELIVERY_TIME = 0.3
MAX_DELIVERY_TIME = 1.5

# GUI update interval (milliseconds) - for smooth 60fps updates
GUI_UPDATE_INTERVAL = 16  # ~60 FPS

# Thread state check interval (seconds)
THREAD_CHECK_INTERVAL = 0.1

# ==============================================================================
# SIMULATION SPEED CONFIGURATION
# ==============================================================================

DEFAULT_SPEED_MULTIPLIER = 1.0
MIN_SPEED_MULTIPLIER = 0.1
MAX_SPEED_MULTIPLIER = 5.0

# ==============================================================================
# GUI CONFIGURATION
# ==============================================================================

# Window dimensions
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
WINDOW_TITLE = "🍽️ Restaurant Order Management System - OS Simulation"

# Color scheme - Professional restaurant theme
COLOR_BACKGROUND = "#F5F5DC"  # Beige/Cream
COLOR_PRIMARY = "#8B0000"     # Dark Red
COLOR_ACCENT = "#DAA520"      # Goldenrod
COLOR_PANEL = "#FFFFFF"       # White
COLOR_TEXT = "#2C3E50"        # Dark Gray
COLOR_TEXT_LIGHT = "#7F8C8D"  # Light Gray

# Thread state colors
COLOR_RUNNING = "#27AE60"     # Green
COLOR_WAITING = "#F39C12"     # Orange/Yellow
COLOR_BLOCKED = "#E74C3C"     # Red
COLOR_IDLE = "#95A5A6"        # Gray

# Log message colors
COLOR_LOG_PRODUCTION = "#3498DB"   # Blue
COLOR_LOG_CONSUMPTION = "#27AE60"  # Green
COLOR_LOG_BLOCKING = "#E74C3C"     # Red
COLOR_LOG_INFO = "#7F8C8D"         # Gray

# Font configuration
FONT_HEADER = ("Arial", 20, "bold")
FONT_TITLE = ("Arial", 14, "bold")
FONT_BODY = ("Arial", 11)
FONT_SMALL = ("Arial", 9)
FONT_LOG = ("Courier", 9)

# Spacing and padding
PADDING_LARGE = 20
PADDING_MEDIUM = 10
PADDING_SMALL = 5

# ==============================================================================
# ORDER CONFIGURATION
# ==============================================================================

# Available dish types
DISH_NAMES = [
    "🍕 Margherita Pizza",
    "🍝 Carbonara Pasta",
    "🥗 Caesar Salad",
    "🥩 Grilled Steak",
    "🍤 Shrimp Scampi",
    "🍔 Classic Burger",
    "🍜 Ramen Bowl",
    "🌮 Fish Tacos",
    "🍱 Sushi Platter",
    "🥘 Paella",
    "🍗 Fried Chicken",
    "🥙 Gyro Wrap",
]

# Chef names
CHEF_NAMES = [
    "Chef Mario",
    "Chef Pierre",
    "Chef Akira",
    "Chef Rosa",
    "Chef Chen",
    "Chef Isabella",
    "Chef Dimitri",
    "Chef Mei",
    "Chef Antonio",
    "Chef Yuki",
]

# Waiter names
WAITER_NAMES = [
    "Alex",
    "Sam",
    "Jordan",
    "Casey",
    "Morgan",
    "Riley",
    "Taylor",
    "Jamie",
    "Quinn",
    "Drew",
]

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================

# Maximum number of log entries to keep in memory
MAX_LOG_ENTRIES = 100

# Log format
LOG_TIMESTAMP_FORMAT = "%H:%M:%S"

# ==============================================================================
# ANIMATION CONFIGURATION
# ==============================================================================

# Animation durations (milliseconds)
ANIMATION_DURATION = 300

# Pulse animation for active threads
PULSE_ANIMATION_SPEED = 1000  # milliseconds per pulse cycle