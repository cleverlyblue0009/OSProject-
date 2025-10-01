"""
Consumer Thread Implementation (Waiter)

This module implements the consumer side of the producer-consumer problem.
Waiters pick up orders from the kitchen counter (shared buffer) and deliver them.

OS Concepts Demonstrated:
1. Thread creation and lifecycle management
2. Consumer in producer-consumer problem
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


class Waiter(threading.Thread):
    """
    Consumer thread that picks up orders from the shared buffer and delivers them.
    
    Each waiter continuously:
    1. Attempts to pick up an order from the kitchen counter (buffer)
    2. Blocks if the buffer is empty (demonstrates WAITING state)
    3. Delivers the order (simulated work)
    4. Repeats until stopped
    
    Attributes:
        waiter_id (int): Unique identifier for this waiter
        name (str): Human-readable name for this waiter
        shared_buffer (SharedBuffer): The shared buffer to consume orders from
        speed_multiplier (float): Controls simulation speed
        stop_event (threading.Event): Signal to stop the thread
        pause_event (threading.Event): Signal to pause the thread
    """
    
    def __init__(
        self,
        waiter_id: int,
        name: str,
        shared_buffer: SharedBuffer,
        callback: Optional[Callable] = None,
        speed_multiplier: float = 1.0
    ):
        """
        Initialize a waiter thread.
        
        Args:
            waiter_id (int): Unique identifier for this waiter
            name (str): Human-readable name
            shared_buffer (SharedBuffer): Shared buffer to consume from
            callback (Optional[Callable]): Callback for GUI updates
            speed_multiplier (float): Speed multiplier for simulation
        """
        super().__init__(name=f"Waiter-{waiter_id}-{name}", daemon=True)
        
        self.waiter_id = waiter_id
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
        self._orders_delivered = 0
        self._current_order: Optional[Order] = None
    
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
        self._notify("🧑‍💼 Waiter started shift")
        
        while not self.stop_event.is_set():
            # Check if paused
            self.pause_event.wait()  # Blocks if pause_event is cleared
            
            if self.stop_event.is_set():
                break
            
            try:
                # Step 1: Try to pick up order from kitchen counter (buffer)
                self._pickup_order()
                
                # Step 2: Deliver the order (simulated work)
                if self._current_order:
                    self._deliver_order()
                
            except Exception as e:
                self._notify(f"❌ Error: {str(e)}", level="ERROR")
        
        self._set_state("IDLE")
        self._notify("👋 Waiter finished shift")
    
    def _pickup_order(self) -> None:
        """
        Pick up an order from the kitchen counter (shared buffer).
        
        This is where the consumer interacts with the shared resource.
        If the buffer is empty, this thread will block (WAITING state).
        
        OS Concepts:
        - Blocking operation: Thread may wait if buffer is empty
        - Synchronization: Semaphore ensures proper coordination
        - State transitions: RUNNING → WAITING (if buffer empty) → RUNNING
        """
        self._set_action("Checking for orders...")
        self._set_state("WAITING")
        self._notify("⏳ Waiting for order to pickup")
        
        # Try to consume from buffer
        # This may block if buffer is empty (demonstrates WAITING state)
        order = self.shared_buffer.consume(
            timeout=10.0  # Prevent indefinite blocking (deadlock prevention)
        )
        
        if order:
            self._set_state("RUNNING")
            self._current_order = order
            self._current_order.mark_in_delivery(self.waiter_id)
            self._notify(f"📦 Picked up {order}")
            self._set_action(f"Picked up {order.dish_name}")
        else:
            # Timeout occurred
            self._set_state("BLOCKED")
            self._notify("⚠️ Timeout waiting for order (buffer empty too long)", level="WARNING")
            time.sleep(0.5)  # Brief pause before retry
    
    def _deliver_order(self) -> None:
        """
        Deliver the picked up order (simulate work).
        
        This represents actual work being done by the thread. The sleep
        simulates CPU-bound or I/O-bound work that takes time.
        
        OS Concept: Thread spends time in RUNNING state doing actual work
        """
        if self._current_order is None:
            return
        
        self._set_state("RUNNING")
        action = f"Delivering {self._current_order.dish_name}..."
        self._set_action(action)
        self._notify(f"🚶 {action}")
        
        # Simulate delivery time (actual work)
        delivery_time = random.uniform(
            config.MIN_DELIVERY_TIME,
            config.MAX_DELIVERY_TIME
        ) / self.speed_multiplier
        
        time.sleep(delivery_time)
        
        # Complete the order
        self._current_order.mark_completed()
        self._orders_delivered += 1
        
        processing_time = self._current_order.get_processing_time()
        self._notify(
            f"✅ Delivered {self._current_order} "
            f"(Total: {self._orders_delivered}, Time: {processing_time:.2f}s)"
        )
        
        self._current_order = None
        self._set_action("Order delivered successfully")
    
    def _set_state(self, state: str) -> None:
        """
        Update thread state (thread-safe).
        
        Args:
            state (str): New state (IDLE, RUNNING, WAITING, BLOCKED)
        """
        with self._state_lock:
            self._state = state
        if self.callback:
            self.callback('state_change', self.waiter_id, state)
    
    def _set_action(self, action: str) -> None:
        """Update current action text."""
        self._current_action = action
        if self.callback:
            self.callback('action_change', self.waiter_id, action)
    
    def _notify(self, message: str, level: str = "INFO") -> None:
        """
        Send notification to GUI.
        
        Args:
            message (str): Message to log
            level (str): Log level (INFO, WARNING, ERROR)
        """
        if self.callback:
            self.callback('log', self.waiter_id, message, level)
    
    def get_state(self) -> str:
        """Get current thread state (thread-safe)."""
        with self._state_lock:
            return self._state
    
    def get_current_action(self) -> str:
        """Get current action description."""
        return self._current_action
    
    def get_orders_delivered(self) -> int:
        """Get total number of orders delivered."""
        return self._orders_delivered
    
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