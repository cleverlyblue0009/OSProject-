#!/usr/bin/env python3
"""
Restaurant Order Management System - Main Entry Point

This is a complete Operating System concepts demonstration through a
multi-threaded restaurant simulation with a modern GUI.

OS Concepts Demonstrated:
1. Concurrency: Multiple threads (chefs and waiters) running simultaneously
2. Producer-Consumer Problem: Classic synchronization problem
3. Semaphores: For counting empty/full buffer slots
4. Mutex Locks: For protecting critical sections
5. Thread States: Visual representation of RUNNING, WAITING, BLOCKED states
6. Deadlock Prevention: Timeout mechanisms and proper resource ordering
7. Bounded Buffer: Fixed-size shared resource
8. Thread-safe Communication: Queue-based GUI updates

Architecture:
- SharedBuffer: Thread-safe bounded buffer with semaphore synchronization
- Chef (Producer): Creates orders and places them in buffer
- Waiter (Consumer): Picks up orders from buffer and delivers them
- GUI: Real-time visualization of all thread activities

Author: Generated for OS Concepts Course
Date: 2025
Python Version: 3.8+
"""

import sys
import tkinter as tk
from tkinter import messagebox

# Import GUI module
from gui import RestaurantGUI


def check_python_version() -> bool:
    """
    Check if Python version meets requirements.
    
    Returns:
        bool: True if version is adequate
    """
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]}+ required.")
        print(f"Current version: {current_version[0]}.{current_version[1]}")
        return False
    
    return True


def show_welcome_dialog(root: tk.Tk) -> None:
    """Show welcome message with OS concepts explanation."""
    welcome_msg = """
🍽️ Restaurant Order Management System
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Welcome to the Operating System Concepts Demonstration!

This application simulates a restaurant using multiple threads:

👨‍🍳 CHEFS (Producers):
   - Create orders and place them on the kitchen counter
   - Demonstrate PRODUCER behavior
   - Block when counter is FULL (WAITING state)

🍽️ KITCHEN COUNTER (Shared Buffer):
   - Fixed-size bounded buffer (capacity: 10)
   - Protected by SEMAPHORES and MUTEX locks
   - Demonstrates CRITICAL SECTION management

🧑‍💼 WAITERS (Consumers):
   - Pick up orders from counter and deliver them
   - Demonstrate CONSUMER behavior
   - Block when counter is EMPTY (WAITING state)

🔑 KEY OS CONCEPTS:
   ✓ Producer-Consumer Problem
   ✓ Semaphore Synchronization
   ✓ Mutex Locks (Critical Sections)
   ✓ Thread States (RUNNING/WAITING/BLOCKED)
   ✓ Deadlock Prevention
   ✓ Concurrent Thread Execution

📊 FEATURES:
   • Real-time thread state visualization
   • Color-coded status indicators
   • Activity logging
   • Configurable parameters
   • Simulation speed control

Click START to begin the simulation!
    """
    
    messagebox.showinfo("Welcome - OS Concepts Demo", welcome_msg)


def main() -> None:
    """
    Main entry point for the application.
    
    This function:
    1. Checks Python version
    2. Creates the Tkinter root window
    3. Initializes the GUI
    4. Starts the event loop
    """
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    try:
        # Create root window
        root = tk.Tk()
        
        # Set window icon (if available)
        # root.iconbitmap('icon.ico')  # Uncomment if you have an icon file
        
        # Show welcome dialog
        root.after(500, lambda: show_welcome_dialog(root))
        
        # Create GUI
        app = RestaurantGUI(root)
        
        # Handle window close event
        def on_closing():
            """Handle window close event gracefully."""
            if app.is_running:
                if messagebox.askokcancel("Quit", "Simulation is running. Stop and quit?"):
                    app._reset_simulation()
                    root.destroy()
            else:
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Center window on screen
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Start the GUI event loop
        print("=" * 60)
        print("🍽️  Restaurant Order Management System - OS Simulation")
        print("=" * 60)
        print("\nGUI started successfully!")
        print("Press START in the GUI to begin the simulation.")
        print("\nOS Concepts Demonstrated:")
        print("  • Producer-Consumer Problem")
        print("  • Semaphore Synchronization")
        print("  • Mutex Locks and Critical Sections")
        print("  • Thread States and Transitions")
        print("  • Deadlock Prevention")
        print("  • Bounded Buffer Management")
        print("\nClose the window or press Ctrl+C to exit.")
        print("=" * 60)
        
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\n\nShutdown requested by user (Ctrl+C)")
        print("Cleaning up...")
        sys.exit(0)
    
    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()