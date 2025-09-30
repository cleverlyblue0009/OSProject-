"""
Producer Thread Implementation (Chef)

This module implements the producer side of the producer-consumer problem.
Chefs create orders and place them on the kitchen counter (shared buffer).

OS Concepts Demonstrated:
1. Thread creation and lifecycle management
2. Producer in producer-consumer problem
3. Thread states: RUNNING, WAITING, BLOCKED
4. Thread synchronization using semaphores
5. Graceful thread termination
"""

import threading
import time
import random
from typing import Callable, Optional

from order import Order
from shared_buffer import SharedBuffer
import config


class Chef(threading.Thread):
    """
    Producer thread that creates orders and adds them to the shared buffer.
    
    Each chef continuously:
    1. Prepares an order (simulated work)
    2. Attempts to place it on the kitchen counter (buffer)
    3. Blocks if the buffer is full (demonstrates WAITING state)
    4. Repeats until stopped
    
    Attributes:
        chef_id (int): Unique identifier for this chef
        name (str): Human-readable name for this chef
        shared_buffer (SharedBuffer): The shared buffer to produce orders to
        speed_multiplier (float): Controls simulation speed
        stop_event (threading.Event): Signal to stop the thread
        pause_event (threading.Event): Signal to pause the thread
    """
    
    def __init__(
        self,
        chef_id: int,
        name: str,
        shared_buffer: SharedBuffer,
        callback: Optional[Callable] = None,
        speed_multiplier: float = 1.0
    ):
        """
        Initialize a chef thread.
        
        Args:
            chef_id (int): Unique identifier for this chef
            name (str): Human-readable name
            shared_buffer (SharedBuffer): Shared buffer to produce to
            callback (Optional[Callable]): Callback for GUI updates
            speed_multiplier (float): Speed multiplier for simulation
        """
        super().__init__(name=f"Chef-{chef_id}-{name}", daemon=True)
        
        self.chef_id = chef_id
        self.name = name
        self.shared_buffer = shared_buffer
        self.callback = callback
        self.speed_multiplier = speed_multiplier
        
        # Thread control events
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.set()  # Start in non-paused state
        
        # Thread state tracking
        self._state = "IDLE"  # IDLE, RUNNING, WAITING, BLOCKED
        self._state_lock = threading.Lock()
        self._current_action = "Initializing..."
        
        # Statistics
        self._orders_produced = 0
        self._current_order: Optional[Order] = None
        
        # Order ID generator (thread-local)
        self._next_order_id = chef_id * 10000  # Offset by chef_id to avoid conflicts
    
    def run(self) -> None:
        """
        Main thread execution loop.
        
        This is the thread's main function that runs in a separate thread of execution.
        The operating system schedules this thread independently of other threads.
        
        OS Concepts:
        - Thread execution: This method runs concurrently with other threads
        - Thread states: Thread transitions between RUNNING, WAITING, BLOCKED
        - Context switching: OS switches between threads to provide concurrency
        """
        self._set_state("RUNNING")
        self._notify("👨‍🍳 Chef started working")
        
        while not self.stop_event.is_set():
            # Check if paused
            self.pause_event.wait()  # Blocks if pause_event is cleared
            
            if self.stop_event.is_set():
                break
            
            try:
                # Step 1: Prepare the order (simulated work)
                self._prepare_order()
                
                # Step 2: Try to place order on kitchen counter (buffer)
                self._place_order()
                
            except Exception as e:
                self._notify(f"❌ Error: {str(e)}", level="ERROR")
        
        self._set_state("IDLE")
        self._notify("👋 Chef finished shift")
    
    def _prepare_order(self) -> None:
        """
        Prepare a new order (simulate work).
        
        This represents actual work being done by the thread. The sleep
        simulates CPU-bound or I/O-bound work that takes time.
        
        OS Concept: Thread spends time in RUNNING state doing actual work
        """
        self._set_state("RUNNING")
        
        # Create a new order
        self._current_order = Order(
            order_id=self._next_order_id,
            dish_name=random.choice(config.DISH_NAMES),
            chef_id=self.chef_id
        )
        self._next_order_id += 1
        self._current_order.mark_in_preparation()
        
        action = f"Preparing {self._current_order.dish_name}..."
        self._set_action(action)
        self._notify(f"👨‍🍳 {action}")
        
        # Simulate preparation time (actual work)
        prep_time = random.uniform(
            config.MIN_PREPARATION_TIME,
            config.MAX_PREPARATION_TIME
        ) / self.speed_multiplier
        
        time.sleep(prep_time)
    
    def _place_order(self) -> None:
        """
        Place prepared order on the kitchen counter (shared buffer).
        
        This is where the producer interacts with the shared resource.
        If the buffer is full, this thread will block (WAITING state).
        
        OS Concepts:
        - Blocking operation: Thread may wait if buffer is full
        - Synchronization: Semaphore ensures proper coordination
        - State transitions: RUNNING → WAITING (if buffer full) → RUNNING
        """
        if self._current_order is None:
            return
        
        self._set_action("Waiting for counter space...")
        self._set_state("WAITING")
        self._notify(f"⏳ Waiting to place {self._current_order}")
        
        # Try to produce to buffer
        # This may block if buffer is full (demonstrates WAITING state)
        success = self.shared_buffer.produce(
            self._current_order,
            timeout=10.0  # Prevent indefinite blocking (deadlock prevention)
        )
        
        if success:
            self._set_state("RUNNING")
            self._orders_produced += 1
            self._notify(
                f"✅ Placed {self._current_order} on counter "
                f"(Total: {self._orders_produced})"
            )
            self._current_order = None
            self._set_action("Order placed successfully")
        else:
            # Timeout occurred
            self._set_state("BLOCKED")
            self._notify(f"⚠️ Timeout placing order (buffer full too long)", level="WARNING")
            time.sleep(0.5)  # Brief pause before retry
    
    def _set_state(self, state: str) -> None:
        """
        Update thread state (thread-safe).
        
        Args:
            state (str): New state (IDLE, RUNNING, WAITING, BLOCKED)
        """
        with self._state_lock:
            self._state = state
        if self.callback:
            self.callback('state_change', self.chef_id, state)
    
    def _set_action(self, action: str) -> None:
        """Update current action text."""
        self._current_action = action
        if self.callback:
            self.callback('action_change', self.chef_id, action)
    
    def _notify(self, message: str, level: str = "INFO") -> None:
        """
        Send notification to GUI.
        
        Args:
            message (str): Message to log
            level (str): Log level (INFO, WARNING, ERROR)
        """
        if self.callback:
            self.callback('log', self.chef_id, message, level)
    
    def get_state(self) -> str:
        """Get current thread state (thread-safe)."""
        with self._state_lock:
            return self._state
    
    def get_current_action(self) -> str:
        """Get current action description."""
        return self._current_action
    
    def get_orders_produced(self) -> int:
        """Get total number of orders produced."""
        return self._orders_produced
    
    def get_current_order(self) -> Optional[Order]:
        """Get the order currently being worked on."""
        return self._current_order
    
    def pause(self) -> None:
        """
        Pause the thread.
        
        OS Concept: Thread state management - paused threads don't consume CPU
        """
        self.pause_event.clear()
        self._set_state("BLOCKED")
    
    def resume(self) -> None:
        """Resume the thread from paused state."""
        self.pause_event.set()
    
    def stop(self) -> None:
        """
        Signal thread to stop gracefully.
        
        OS Concept: Graceful thread termination using event signaling
        """
        self.stop_event.set()
        self.pause_event.set()  # Unpause if paused
    
    def update_speed(self, speed_multiplier: float) -> None:
        """Update simulation speed multiplier."""
        self.speed_multiplier = speed_multiplier