"""
Configuration constants for the Restaurant Order Management System.

This module contains all configuration parameters for the simulation,
including GUI settings, threading parameters, and visual styling.
"""

# Threading Configuration
DEFAULT_NUM_CHEFS = 3
DEFAULT_NUM_WAITERS = 3
DEFAULT_BUFFER_SIZE = 10
MIN_THREADS = 1
MAX_THREADS = 8
MIN_BUFFER_SIZE = 5
MAX_BUFFER_SIZE = 20

# Timing Configuration (in seconds)
MIN_PREPARATION_TIME = 1.0
MAX_PREPARATION_TIME = 3.0
MIN_DELIVERY_TIME = 1.0
MAX_DELIVERY_TIME = 2.0
GUI_UPDATE_INTERVAL = 50  # milliseconds

# Simulation Speed
DEFAULT_SPEED = 1.0
MIN_SPEED = 0.1
MAX_SPEED = 5.0

# GUI Configuration
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Restaurant Order Management System - OS Simulation"

# Color Scheme - Professional Restaurant Theme
COLORS = {
    'background': '#F5F5DC',        # Warm cream/beige
    'primary': '#8B0000',           # Deep red
    'accent': '#DAA520',            # Gold
    'success': '#228B22',           # Forest green
    'warning': '#FF8C00',           # Dark orange
    'danger': '#DC143C',            # Crimson
    'info': '#4682B4',              # Steel blue
    'light': '#F8F8FF',             # Ghost white
    'dark': '#2F4F4F',              # Dark slate gray
    'border': '#D3D3D3',            # Light gray
    'text': '#2F2F2F',              # Dark gray
    'text_light': '#696969',        # Dim gray
}

# Thread State Colors
THREAD_COLORS = {
    'RUNNING': '#00FF00',           # Bright green
    'WAITING': '#FFD700',           # Gold
    'BLOCKED': '#FF0000',           # Red
    'IDLE': '#808080',              # Gray
}

# Font Configuration
FONTS = {
    'title': ('Arial', 16, 'bold'),
    'heading': ('Arial', 12, 'bold'),
    'body': ('Arial', 10),
    'small': ('Arial', 8),
    'monospace': ('Courier New', 9),
}

# Dish Names for Order Generation
DISH_NAMES = [
    "Margherita Pizza", "Chicken Alfredo", "Caesar Salad", "Ribeye Steak",
    "Fish and Chips", "Pad Thai", "Chicken Tikka Masala", "Beef Burger",
    "Vegetable Stir Fry", "Lobster Bisque", "Grilled Salmon", "Mushroom Risotto",
    "BBQ Ribs", "Chicken Wings", "Greek Salad", "Beef Tacos", "Shrimp Scampi",
    "Pork Chops", "Vegetable Curry", "Clam Chowder", "Turkey Sandwich",
    "Chicken Parmesan", "Beef Stroganoff", "Fish Tacos", "Lamb Chops"
]

# Chef Names
CHEF_NAMES = [
    "Chef Marco", "Chef Isabella", "Chef Giovanni", "Chef Sofia", "Chef Antonio",
    "Chef Elena", "Chef Francesco", "Chef Giulia"
]

# Waiter Names
WAITER_NAMES = [
    "Alex", "Jordan", "Casey", "Taylor", "Morgan", "Riley", "Avery", "Quinn"
]

# Activity Log Configuration
MAX_LOG_ENTRIES = 100
LOG_COLORS = {
    'production': '#4682B4',        # Steel blue
    'consumption': '#228B22',       # Forest green
    'blocking': '#DC143C',          # Crimson
    'system': '#FF8C00',            # Dark orange
    'info': '#2F4F4F',              # Dark slate gray
}

# Animation Configuration
ANIMATION_DURATION = 300  # milliseconds
PULSE_INTERVAL = 1000     # milliseconds for status indicators