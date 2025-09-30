#!/usr/bin/env python3
"""
Restaurant Order Management System - Main Application Entry Point

This is the main entry point for the Restaurant Order Management System,
a comprehensive demonstration of Operating System concepts including:

- Producer-Consumer Pattern
- Thread Synchronization with Semaphores and Mutex Locks
- Bounded Buffer Implementation
- Thread State Management
- Deadlock Prevention
- Race Condition Prevention
- Critical Section Management

The application simulates a restaurant where:
- Chefs (Producers) create orders and place them on a kitchen counter (shared buffer)
- Waiters (Consumers) pick up orders from the counter and deliver them to customers
- The kitchen counter has limited capacity (bounded buffer)
- All operations are thread-safe using proper synchronization primitives

Author: AI Assistant
Date: 2025
License: MIT
"""

import sys
import os
import argparse
import signal
import threading
import time
from typing import Optional

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import application modules
from gui import RestaurantGUI
from utils import setup_logging, validate_config, get_system_info
import config


class RestaurantApplication:
    """
    Main application class for the Restaurant Order Management System.
    
    This class handles application initialization, command-line argument parsing,
    signal handling, and graceful shutdown procedures.
    """
    
    def __init__(self):
        """Initialize the application."""
        self.gui: Optional[RestaurantGUI] = None
        self.logger = None
        self.shutdown_event = threading.Event()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """
        Handle system signals for graceful shutdown.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        if self.logger:
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        
        self.shutdown_event.set()
        
        if self.gui:
            # Schedule GUI shutdown on main thread
            if hasattr(self.gui, 'root'):
                self.gui.root.after(100, self.gui.root.quit)
    
    def parse_arguments(self) -> argparse.Namespace:
        """
        Parse command-line arguments.
        
        Returns:
            argparse.Namespace: Parsed command-line arguments
        """
        parser = argparse.ArgumentParser(
            description="Restaurant Order Management System - OS Concepts Demonstration",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s                          # Start with default settings
  %(prog)s --chefs 5 --waiters 3    # Start with 5 chefs and 3 waiters
  %(prog)s --buffer-size 15         # Start with buffer size of 15
  %(prog)s --speed 2.0              # Start with 2x simulation speed
  %(prog)s --log-level DEBUG        # Enable debug logging
  %(prog)s --demo                   # Start in demo mode
  %(prog)s --headless               # Run without GUI (console only)

OS Concepts Demonstrated:
  - Producer-Consumer Pattern: Chefs produce orders, waiters consume them
  - Thread Synchronization: Semaphores and mutex locks prevent race conditions
  - Bounded Buffer: Kitchen counter with limited capacity
  - Critical Sections: Thread-safe access to shared resources
  - Deadlock Prevention: Timeout mechanisms and proper resource ordering
  - Thread States: Visual representation of RUNNING, WAITING, BLOCKED states
            """
        )
        
        # Simulation parameters
        sim_group = parser.add_argument_group('Simulation Parameters')
        sim_group.add_argument(
            '--chefs', '-c',
            type=int,
            default=config.DEFAULT_NUM_CHEFS,
            metavar='N',
            help=f'Number of chef threads (producers) [{config.MIN_THREADS}-{config.MAX_THREADS}] '
                 f'(default: {config.DEFAULT_NUM_CHEFS})'
        )
        sim_group.add_argument(
            '--waiters', '-w',
            type=int,
            default=config.DEFAULT_NUM_WAITERS,
            metavar='N',
            help=f'Number of waiter threads (consumers) [{config.MIN_THREADS}-{config.MAX_THREADS}] '
                 f'(default: {config.DEFAULT_NUM_WAITERS})'
        )
        sim_group.add_argument(
            '--buffer-size', '-b',
            type=int,
            default=config.DEFAULT_BUFFER_SIZE,
            metavar='N',
            help=f'Shared buffer capacity [{config.MIN_BUFFER_SIZE}-{config.MAX_BUFFER_SIZE}] '
                 f'(default: {config.DEFAULT_BUFFER_SIZE})'
        )
        sim_group.add_argument(
            '--speed', '-s',
            type=float,
            default=config.DEFAULT_SPEED,
            metavar='X',
            help=f'Simulation speed multiplier [{config.MIN_SPEED}-{config.MAX_SPEED}] '
                 f'(default: {config.DEFAULT_SPEED})'
        )
        
        # Application modes
        mode_group = parser.add_argument_group('Application Modes')
        mode_group.add_argument(
            '--demo',
            action='store_true',
            help='Start in demo mode with optimal settings and auto-start'
        )
        mode_group.add_argument(
            '--headless',
            action='store_true',
            help='Run without GUI (console mode only) - for testing/debugging'
        )
        
        # Logging and debugging
        debug_group = parser.add_argument_group('Logging and Debugging')
        debug_group.add_argument(
            '--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default='INFO',
            help='Set logging level (default: INFO)'
        )
        debug_group.add_argument(
            '--log-file',
            type=str,
            metavar='FILE',
            help='Log to file in addition to console'
        )
        debug_group.add_argument(
            '--system-info',
            action='store_true',
            help='Display system information and exit'
        )
        
        # GUI options
        gui_group = parser.add_argument_group('GUI Options')
        gui_group.add_argument(
            '--window-size',
            type=str,
            metavar='WIDTHxHEIGHT',
            help=f'Set window size (default: {config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT})'
        )
        gui_group.add_argument(
            '--fullscreen',
            action='store_true',
            help='Start in fullscreen mode'
        )
        
        return parser.parse_args()
    
    def validate_arguments(self, args: argparse.Namespace) -> dict:
        """
        Validate command-line arguments and return configuration.
        
        Args:
            args: Parsed command-line arguments
            
        Returns:
            dict: Validated configuration dictionary
            
        Raises:
            SystemExit: If arguments are invalid
        """
        try:
            # Create configuration dictionary
            app_config = {
                'num_chefs': args.chefs,
                'num_waiters': args.waiters,
                'buffer_size': args.buffer_size,
                'speed': args.speed,
                'demo_mode': args.demo,
                'headless': args.headless,
                'log_level': args.log_level,
                'log_file': args.log_file,
                'fullscreen': args.fullscreen
            }
            
            # Parse window size if provided
            if args.window_size:
                try:
                    width, height = map(int, args.window_size.split('x'))
                    app_config['window_width'] = width
                    app_config['window_height'] = height
                except ValueError:
                    raise ValueError("Window size must be in format WIDTHxHEIGHT (e.g., 1200x800)")
            else:
                app_config['window_width'] = config.WINDOW_WIDTH
                app_config['window_height'] = config.WINDOW_HEIGHT
            
            # Validate simulation parameters
            sim_config = {
                'num_chefs': app_config['num_chefs'],
                'num_waiters': app_config['num_waiters'],
                'buffer_size': app_config['buffer_size'],
                'speed': app_config['speed']
            }
            
            validated_sim_config = validate_config(sim_config)
            app_config.update(validated_sim_config)
            
            # Demo mode adjustments
            if args.demo:
                app_config.update({
                    'num_chefs': 4,
                    'num_waiters': 3,
                    'buffer_size': 12,
                    'speed': 1.5
                })
            
            return app_config
            
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def setup_application(self, app_config: dict) -> None:
        """
        Setup application components.
        
        Args:
            app_config: Application configuration dictionary
        """
        # Setup logging
        self.logger = setup_logging(
            log_level=app_config['log_level'],
            log_file=app_config.get('log_file')
        )
        
        self.logger.info("Starting Restaurant Order Management System")
        self.logger.info(f"Configuration: {app_config}")
        
        # Log system information
        sys_info = get_system_info()
        self.logger.debug(f"System Info: {sys_info}")
        
        # Initialize GUI if not in headless mode
        if not app_config['headless']:
            self.logger.info("Initializing GUI...")
            self.gui = RestaurantGUI()
            
            # Configure window
            if app_config.get('window_width') and app_config.get('window_height'):
                geometry = f"{app_config['window_width']}x{app_config['window_height']}"
                self.gui.root.geometry(geometry)
            
            if app_config.get('fullscreen'):
                self.gui.root.attributes('-fullscreen', True)
                # Bind Escape key to exit fullscreen
                self.gui.root.bind('<Escape>', lambda e: self.gui.root.attributes('-fullscreen', False))
            
            self.logger.info("GUI initialized successfully")
    
    def run_headless_mode(self, app_config: dict) -> None:
        """
        Run the application in headless mode (console only).
        
        Args:
            app_config: Application configuration dictionary
        """
        self.logger.info("Running in headless mode...")
        
        # Import required modules for headless operation
        from shared_buffer import SharedBuffer
        from producer import ChefThread
        from consumer import WaiterThread
        
        # Create shared buffer
        buffer = SharedBuffer(app_config['buffer_size'])
        
        # Create and start threads
        chefs = []
        waiters = []
        
        # Start chef threads
        for i in range(app_config['num_chefs']):
            chef_name = config.CHEF_NAMES[i % len(config.CHEF_NAMES)]
            chef = ChefThread(i, chef_name, buffer)
            chef.set_speed(app_config['speed'])
            chefs.append(chef)
            chef.start()
            self.logger.info(f"Started {chef_name}")
        
        # Start waiter threads
        for i in range(app_config['num_waiters']):
            waiter_name = config.WAITER_NAMES[i % len(config.WAITER_NAMES)]
            waiter = WaiterThread(i, waiter_name, buffer)
            waiter.set_speed(app_config['speed'])
            waiters.append(waiter)
            waiter.start()
            self.logger.info(f"Started {waiter_name}")
        
        self.logger.info("All threads started. Press Ctrl+C to stop.")
        
        try:
            # Monitor simulation
            start_time = time.time()
            last_report_time = start_time
            
            while not self.shutdown_event.is_set():
                time.sleep(1)
                
                current_time = time.time()
                if current_time - last_report_time >= 10:  # Report every 10 seconds
                    buffer_state = buffer.get_buffer_state()
                    elapsed = current_time - start_time
                    
                    self.logger.info(
                        f"Status: {buffer_state['total_consumed']} orders completed, "
                        f"buffer: {buffer_state['current_size']}/{buffer_state['capacity']}, "
                        f"elapsed: {elapsed:.1f}s"
                    )
                    
                    last_report_time = current_time
        
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        
        finally:
            # Cleanup
            self.logger.info("Stopping threads...")
            
            for chef in chefs:
                chef.stop()
            for waiter in waiters:
                waiter.stop()
            
            # Wait for threads to finish
            for chef in chefs:
                chef.join(timeout=2.0)
            for waiter in waiters:
                waiter.join(timeout=2.0)
            
            buffer.shutdown()
            self.logger.info("Headless mode finished")
    
    def run_gui_mode(self, app_config: dict) -> None:
        """
        Run the application in GUI mode.
        
        Args:
            app_config: Application configuration dictionary
        """
        self.logger.info("Starting GUI mode...")
        
        try:
            # Auto-start demo if requested
            if app_config.get('demo_mode'):
                self.logger.info("Demo mode enabled - will auto-start simulation")
                # Schedule auto-start after GUI is fully loaded
                self.gui.root.after(1000, lambda: self._auto_start_demo(app_config))
            
            # Start GUI main loop
            self.gui.run()
            
        except Exception as e:
            self.logger.error(f"GUI error: {e}", exc_info=True)
            raise
        
        finally:
            self.logger.info("GUI mode finished")
    
    def _auto_start_demo(self, app_config: dict) -> None:
        """
        Auto-start the simulation in demo mode.
        
        Args:
            app_config: Application configuration dictionary
        """
        try:
            # Set configuration values in GUI
            self.gui.control_panel.chef_var.set(app_config['num_chefs'])
            self.gui.control_panel.waiter_var.set(app_config['num_waiters'])
            self.gui.control_panel.buffer_var.set(app_config['buffer_size'])
            self.gui.control_panel.speed_var.set(app_config['speed'])
            
            # Start simulation
            self.gui.control_panel._on_start()
            
            self.logger.info("Demo mode auto-started")
            
        except Exception as e:
            self.logger.error(f"Failed to auto-start demo: {e}")
    
    def run(self) -> int:
        """
        Main application entry point.
        
        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        try:
            # Parse and validate arguments
            args = self.parse_arguments()
            
            # Handle special cases
            if args.system_info:
                self._print_system_info()
                return 0
            
            # Validate configuration
            app_config = self.validate_arguments(args)
            
            # Setup application
            self.setup_application(app_config)
            
            # Run appropriate mode
            if app_config['headless']:
                self.run_headless_mode(app_config)
            else:
                self.run_gui_mode(app_config)
            
            return 0
            
        except KeyboardInterrupt:
            if self.logger:
                self.logger.info("Application interrupted by user")
            return 130  # Standard exit code for Ctrl+C
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Application error: {e}", exc_info=True)
            else:
                print(f"Error: {e}", file=sys.stderr)
            return 1
    
    def _print_system_info(self) -> None:
        """Print system information and exit."""
        sys_info = get_system_info()
        
        print("Restaurant Order Management System - System Information")
        print("=" * 60)
        print(f"Platform: {sys_info['platform']}")
        print(f"Python Version: {sys_info['python_version']}")
        print(f"Architecture: {sys_info['architecture']}")
        print(f"Processor: {sys_info['processor']}")
        print(f"Active Threads: {sys_info['active_threads']}")
        print(f"Main Thread: {sys_info['main_thread']}")
        print()
        
        # Configuration limits
        print("Configuration Limits:")
        print(f"  Threads: {config.MIN_THREADS} - {config.MAX_THREADS}")
        print(f"  Buffer Size: {config.MIN_BUFFER_SIZE} - {config.MAX_BUFFER_SIZE}")
        print(f"  Speed: {config.MIN_SPEED} - {config.MAX_SPEED}")
        print()
        
        # Available dishes and names
        print(f"Available Dishes: {len(config.DISH_NAMES)}")
        print(f"Chef Names: {len(config.CHEF_NAMES)}")
        print(f"Waiter Names: {len(config.WAITER_NAMES)}")


def main() -> int:
    """
    Main function - application entry point.
    
    Returns:
        int: Exit code
    """
    app = RestaurantApplication()
    return app.run()


if __name__ == "__main__":
    # Set up proper exception handling for GUI applications
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)