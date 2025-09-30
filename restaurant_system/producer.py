"""
Producer (Chef) thread implementation for the Restaurant Order Management System.

This module implements the producer threads that represent chefs in the restaurant.
Each chef creates orders and places them in the shared buffer (kitchen counter).

Key OS Concepts Demonstrated:
- Producer thread in Producer-Consumer pattern
- Thread lifecycle management (start, pause, resume, stop)
- Thread state tracking and reporting
- Proper synchronization with shared resources
- Random timing simulation for realistic behavior
"""

import threading
import time
import random
from typing import Optional, Callable
from enum import Enum

from order import Order, OrderStatus
from shared_buffer import SharedBuffer
import config


class ThreadState(Enum):
    """Enumeration of possible thread states for OS demonstration."""
    IDLE = "IDLE"           # Thread created but not started
    RUNNING = "RUNNING"     # Thread actively executing
    WAITING = "WAITING"     # Thread waiting for resources
    BLOCKED = "BLOCKED"     # Thread blocked on synchronization
    PAUSED = "PAUSED"       # Thread paused by user
    TERMINATED = "TERMINATED"  # Thread finished execution


class ChefThread(threading.Thread):
    """
    Producer thread representing a chef in the restaurant.
    
    This class implements a producer thread that continuously creates orders
    and attempts to place them in the shared buffer. It demonstrates proper
    thread synchronization and state management.
    
    OS Concepts Implemented:
    - Thread creation and lifecycle management
    - Producer role in Producer-Consumer pattern
    - Thread state transitions and monitoring
    - Proper resource cleanup and shutdown
    - Thread-safe state reporting
    """
    
    def __init__(self, chef_id: int, name: str, shared_buffer: SharedBuffer, 
                 gui_callback: Optional[Callable] = None):
        """
        Initialize the chef thread.
        
        Args:
            chef_id (int): Unique identifier for this chef
            name (str): Display name for the chef
            shared_buffer (SharedBuffer): Shared buffer to place orders in
            gui_callback (Optional[Callable]): Callback for GUI updates
        """
        super().__init__(name=f"Chef-{chef_id}", daemon=True)
        
        self.chef_id = chef_id
        self.chef_name = name
        self.shared_buffer = shared_buffer
        self.gui_callback = gui_callback
        
        # Thread control events
        self.pause_event = threading.Event()
        self.stop_event = threading.Event()
        self.pause_event.set()  # Start in running state
        
        # Thread state tracking
        self.current_state = ThreadState.IDLE
        self.state_lock = threading.Lock()
        
        # Statistics
        self.orders_produced = 0
        self.orders_blocked = 0
        self.total_preparation_time = 0.0
        self.stats_lock = threading.Lock()
        
        # Current activity
        self.current_activity = "Waiting to start"
        self.current_order: Optional[Order] = None
        
        # Order ID counter (class variable to ensure uniqueness)
        if not hasattr(ChefThread, '_order_counter'):
            ChefThread._order_counter = 0
            ChefThread._counter_lock = threading.Lock()
        
        # Speed multiplier for simulation control
        self.speed_multiplier = 1.0
    
    def run(self) -> None:
        """
        Main thread execution method.
        
        This method implements the producer algorithm:
        1. Create an order (simulate preparation)
        2. Attempt to place order in shared buffer
        3. Handle blocking/waiting scenarios
        4. Repeat until stopped
        """
        self._set_state(ThreadState.RUNNING)
        self._update_activity("Started cooking")
        
        try:
            while not self.stop_event.is_set():
                # Check if paused
                if not self.pause_event.is_set():
                    self._set_state(ThreadState.PAUSED)
                    self._update_activity("Paused")
                    self.pause_event.wait()  # Block until resumed
                    if self.stop_event.is_set():
                        break
                    self._set_state(ThreadState.RUNNING)
                
                # Create a new order
                order = self._create_order()
                self.current_order = order
                
                # Simulate order preparation
                self._prepare_order(order)
                
                # Attempt to place order in buffer
                self._set_state(ThreadState.WAITING)
                self._update_activity(f"Waiting to place Order #{order.order_id}")
                
                success = self._place_order(order)
                
                if success:
                    with self.stats_lock:
                        self.orders_produced += 1
                    self._update_activity(f"Placed Order #{order.order_id}")
                    self._set_state(ThreadState.RUNNING)
                else:
                    with self.stats_lock:
                        self.orders_blocked += 1
                    self._update_activity("Failed to place order - buffer full")
                
                self.current_order = None
                
                # Brief pause between orders (scaled by speed)
                self._sleep_scaled(random.uniform(0.5, 1.5))
                
        except Exception as e:
            self._update_activity(f"Error: {str(e)}")
        finally:
            self._set_state(ThreadState.TERMINATED)
            self._update_activity("Finished shift")
    
    def _create_order(self) -> Order:
        """
        Create a new order with unique ID and random dish.
        
        Returns:
            Order: Newly created order object
        """
        # Generate unique order ID
        with ChefThread._counter_lock:
            ChefThread._order_counter += 1
            order_id = ChefThread._order_counter
        
        # Select random dish
        dish_name = random.choice(config.DISH_NAMES)
        
        # Create order
        order = Order(
            order_id=order_id,
            dish_name=dish_name,
            created_time=time.time()
        )
        
        self._notify_gui(f"Chef {self.chef_name} started preparing Order #{order_id}: {dish_name}")
        return order
    
    def _prepare_order(self, order: Order) -> None:
        """
        Simulate order preparation with realistic timing.
        
        Args:
            order (Order): Order to prepare
        """
        order.start_preparation(self.chef_id)
        
        # Calculate preparation time
        prep_time = random.uniform(
            config.MIN_PREPARATION_TIME,
            config.MAX_PREPARATION_TIME
        )
        
        with self.stats_lock:
            self.total_preparation_time += prep_time
        
        self._set_state(ThreadState.RUNNING)
        self._update_activity(f"Preparing {order.dish_name} (Order #{order.order_id})")
        
        # Simulate preparation with interruptible sleep
        self._sleep_scaled(prep_time)
        
        if not self.stop_event.is_set():
            self._notify_gui(f"Chef {self.chef_name} finished preparing Order #{order.order_id}")
    
    def _place_order(self, order: Order) -> bool:
        """
        Attempt to place order in shared buffer.
        
        Args:
            order (Order): Order to place in buffer
            
        Returns:
            bool: True if successfully placed, False if blocked
        """
        try:
            # Set state to blocked while waiting for buffer space
            self._set_state(ThreadState.BLOCKED)
            
            # Attempt to produce with timeout to prevent indefinite blocking
            success = self.shared_buffer.produce(order, self.chef_id, timeout=2.0)
            
            if success:
                self._notify_gui(f"Chef {self.chef_name} placed Order #{order.order_id} on counter")
            else:
                self._notify_gui(f"Chef {self.chef_name} couldn't place Order #{order.order_id} - counter full")
            
            return success
            
        except Exception as e:
            self._notify_gui(f"Chef {self.chef_name} error placing order: {str(e)}")
            return False
    
    def pause(self) -> None:
        """Pause the chef thread execution."""
        self.pause_event.clear()
        self._notify_gui(f"Chef {self.chef_name} paused")
    
    def resume(self) -> None:
        """Resume the chef thread execution."""
        self.pause_event.set()
        self._notify_gui(f"Chef {self.chef_name} resumed")
    
    def stop(self) -> None:
        """Stop the chef thread gracefully."""
        self.stop_event.set()
        self.pause_event.set()  # Ensure thread isn't blocked on pause
        self._notify_gui(f"Chef {self.chef_name} stopping")
    
    def set_speed(self, speed_multiplier: float) -> None:
        """
        Set the simulation speed multiplier.
        
        Args:
            speed_multiplier (float): Speed multiplier (1.0 = normal, 2.0 = 2x speed)
        """
        self.speed_multiplier = max(0.1, min(5.0, speed_multiplier))
    
    def get_state_info(self) -> dict:
        """
        Get current thread state information.
        
        Returns:
            dict: Dictionary containing thread state and statistics
        """
        with self.state_lock:
            current_state = self.current_state
            current_activity = self.current_activity
        
        with self.stats_lock:
            stats = {
                'orders_produced': self.orders_produced,
                'orders_blocked': self.orders_blocked,
                'total_preparation_time': self.total_preparation_time,
                'avg_preparation_time': (
                    self.total_preparation_time / max(1, self.orders_produced)
                )
            }
        
        return {
            'chef_id': self.chef_id,
            'name': self.chef_name,
            'state': current_state.value,
            'activity': current_activity,
            'current_order': self.current_order,
            'is_alive': self.is_alive(),
            'statistics': stats
        }
    
    def _set_state(self, new_state: ThreadState) -> None:
        """
        Update thread state in a thread-safe manner.
        
        Args:
            new_state (ThreadState): New state to set
        """
        with self.state_lock:
            old_state = self.current_state
            self.current_state = new_state
            
        # Notify GUI of state change
        if old_state != new_state:
            self._notify_gui(f"Chef {self.chef_name} state: {old_state.value} → {new_state.value}")
    
    def _update_activity(self, activity: str) -> None:
        """
        Update current activity description.
        
        Args:
            activity (str): Description of current activity
        """
        with self.state_lock:
            self.current_activity = activity
    
    def _sleep_scaled(self, duration: float) -> None:
        """
        Sleep for a duration scaled by the speed multiplier.
        
        This method allows for interruptible sleep that respects the
        stop event and speed settings.
        
        Args:
            duration (float): Base duration in seconds
        """
        scaled_duration = duration / self.speed_multiplier
        end_time = time.time() + scaled_duration
        
        while time.time() < end_time and not self.stop_event.is_set():
            # Sleep in small increments to allow for interruption
            remaining = end_time - time.time()
            sleep_time = min(0.1, remaining)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def _notify_gui(self, message: str) -> None:
        """
        Send a message to the GUI callback.
        
        Args:
            message (str): Message to send to GUI
        """
        if self.gui_callback:
            try:
                timestamp = time.strftime("%H:%M:%S", time.localtime())
                event_data = {
                    'type': 'chef_activity',
                    'chef_id': self.chef_id,
                    'message': message,
                    'timestamp': timestamp,
                    'state_info': self.get_state_info()
                }
                self.gui_callback(event_data)
            except Exception:
                # Silently handle GUI callback errors
                pass