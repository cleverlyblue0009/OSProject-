"""
Consumer (Waiter) thread implementation for the Restaurant Order Management System.

This module implements the consumer threads that represent waiters in the restaurant.
Each waiter picks up orders from the shared buffer (kitchen counter) and delivers them.

Key OS Concepts Demonstrated:
- Consumer thread in Producer-Consumer pattern
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


class WaiterThread(threading.Thread):
    """
    Consumer thread representing a waiter in the restaurant.
    
    This class implements a consumer thread that continuously picks up orders
    from the shared buffer and delivers them to customers. It demonstrates proper
    thread synchronization and state management.
    
    OS Concepts Implemented:
    - Thread creation and lifecycle management
    - Consumer role in Producer-Consumer pattern
    - Thread state transitions and monitoring
    - Proper resource cleanup and shutdown
    - Thread-safe state reporting
    """
    
    def __init__(self, waiter_id: int, name: str, shared_buffer: SharedBuffer, 
                 gui_callback: Optional[Callable] = None):
        """
        Initialize the waiter thread.
        
        Args:
            waiter_id (int): Unique identifier for this waiter
            name (str): Display name for the waiter
            shared_buffer (SharedBuffer): Shared buffer to pick up orders from
            gui_callback (Optional[Callable]): Callback for GUI updates
        """
        super().__init__(name=f"Waiter-{waiter_id}", daemon=True)
        
        self.waiter_id = waiter_id
        self.waiter_name = name
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
        self.orders_delivered = 0
        self.orders_blocked = 0
        self.total_delivery_time = 0.0
        self.total_service_time = 0.0  # Time from pickup to delivery
        self.stats_lock = threading.Lock()
        
        # Current activity
        self.current_activity = "Waiting to start"
        self.current_order: Optional[Order] = None
        
        # Speed multiplier for simulation control
        self.speed_multiplier = 1.0
    
    def run(self) -> None:
        """
        Main thread execution method.
        
        This method implements the consumer algorithm:
        1. Wait for an order in the shared buffer
        2. Pick up the order (remove from buffer)
        3. Deliver the order (simulate delivery time)
        4. Repeat until stopped
        """
        self._set_state(ThreadState.RUNNING)
        self._update_activity("Started serving")
        
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
                
                # Attempt to pick up an order from buffer
                self._set_state(ThreadState.WAITING)
                self._update_activity("Waiting for orders")
                
                order = self._pickup_order()
                
                if order is not None:
                    self.current_order = order
                    self._set_state(ThreadState.RUNNING)
                    
                    # Deliver the order
                    self._deliver_order(order)
                    
                    with self.stats_lock:
                        self.orders_delivered += 1
                    
                    self._update_activity(f"Delivered Order #{order.order_id}")
                    self.current_order = None
                    
                    # Brief pause between deliveries (scaled by speed)
                    self._sleep_scaled(random.uniform(0.3, 1.0))
                else:
                    with self.stats_lock:
                        self.orders_blocked += 1
                    self._update_activity("No orders available")
                    
                    # Brief pause when no orders available
                    self._sleep_scaled(0.5)
                
        except Exception as e:
            self._update_activity(f"Error: {str(e)}")
        finally:
            self._set_state(ThreadState.TERMINATED)
            self._update_activity("Finished shift")
    
    def _pickup_order(self) -> Optional[Order]:
        """
        Attempt to pick up an order from the shared buffer.
        
        Returns:
            Optional[Order]: Order picked up, or None if no orders available
        """
        try:
            # Set state to blocked while waiting for orders
            self._set_state(ThreadState.BLOCKED)
            
            # Attempt to consume with timeout to prevent indefinite blocking
            order = self.shared_buffer.consume(self.waiter_id, timeout=2.0)
            
            if order:
                self._notify_gui(f"Waiter {self.waiter_name} picked up Order #{order.order_id}")
            else:
                self._notify_gui(f"Waiter {self.waiter_name} found no orders available")
            
            return order
            
        except Exception as e:
            self._notify_gui(f"Waiter {self.waiter_name} error picking up order: {str(e)}")
            return None
    
    def _deliver_order(self, order: Order) -> None:
        """
        Simulate order delivery with realistic timing.
        
        Args:
            order (Order): Order to deliver
        """
        pickup_time = time.time()
        
        # Calculate delivery time
        delivery_time = random.uniform(
            config.MIN_DELIVERY_TIME,
            config.MAX_DELIVERY_TIME
        )
        
        self._update_activity(f"Delivering {order.dish_name} (Order #{order.order_id})")
        
        # Simulate delivery with interruptible sleep
        self._sleep_scaled(delivery_time)
        
        if not self.stop_event.is_set():
            # Complete the delivery
            order.complete_delivery()
            delivery_end_time = time.time()
            
            # Update statistics
            with self.stats_lock:
                self.total_delivery_time += delivery_time
                service_time = delivery_end_time - pickup_time
                self.total_service_time += service_time
            
            self._notify_gui(f"Waiter {self.waiter_name} delivered Order #{order.order_id} to customer")
    
    def pause(self) -> None:
        """Pause the waiter thread execution."""
        self.pause_event.clear()
        self._notify_gui(f"Waiter {self.waiter_name} paused")
    
    def resume(self) -> None:
        """Resume the waiter thread execution."""
        self.pause_event.set()
        self._notify_gui(f"Waiter {self.waiter_name} resumed")
    
    def stop(self) -> None:
        """Stop the waiter thread gracefully."""
        self.stop_event.set()
        self.pause_event.set()  # Ensure thread isn't blocked on pause
        self._notify_gui(f"Waiter {self.waiter_name} stopping")
    
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
                'orders_delivered': self.orders_delivered,
                'orders_blocked': self.orders_blocked,
                'total_delivery_time': self.total_delivery_time,
                'total_service_time': self.total_service_time,
                'avg_delivery_time': (
                    self.total_delivery_time / max(1, self.orders_delivered)
                ),
                'avg_service_time': (
                    self.total_service_time / max(1, self.orders_delivered)
                )
            }
        
        return {
            'waiter_id': self.waiter_id,
            'name': self.waiter_name,
            'state': current_state.value,
            'activity': current_activity,
            'current_order': self.current_order,
            'is_alive': self.is_alive(),
            'statistics': stats
        }
    
    def get_efficiency_rating(self) -> str:
        """
        Calculate waiter efficiency rating based on performance.
        
        Returns:
            str: Efficiency rating (Excellent, Good, Average, Poor)
        """
        with self.stats_lock:
            if self.orders_delivered == 0:
                return "No Data"
            
            avg_service_time = self.total_service_time / self.orders_delivered
            
            if avg_service_time < 2.0:
                return "Excellent"
            elif avg_service_time < 3.0:
                return "Good"
            elif avg_service_time < 4.0:
                return "Average"
            else:
                return "Needs Improvement"
    
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
            self._notify_gui(f"Waiter {self.waiter_name} state: {old_state.value} → {new_state.value}")
    
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
                    'type': 'waiter_activity',
                    'waiter_id': self.waiter_id,
                    'message': message,
                    'timestamp': timestamp,
                    'state_info': self.get_state_info()
                }
                self.gui_callback(event_data)
            except Exception:
                # Silently handle GUI callback errors
                pass