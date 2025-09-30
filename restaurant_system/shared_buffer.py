"""
Thread-safe shared buffer implementation for the Restaurant Order Management System.

This module implements the classic Producer-Consumer problem solution using
semaphores and mutex locks. The SharedBuffer class represents the kitchen counter
where chefs place prepared orders and waiters pick them up for delivery.

Key OS Concepts Demonstrated:
- Semaphores for resource counting (empty/full slots)
- Mutex locks for critical section protection
- Bounded buffer implementation
- Race condition prevention
- Deadlock prevention through proper resource ordering
"""

import threading
import time
from typing import List, Optional, Callable
from collections import deque
import queue

from order import Order


class SharedBuffer:
    """
    Thread-safe bounded buffer implementing the Producer-Consumer pattern.
    
    This class represents the kitchen counter where orders are placed by chefs
    (producers) and picked up by waiters (consumers). It uses semaphores and
    mutex locks to ensure thread safety and prevent race conditions.
    
    OS Concepts Implemented:
    - Bounded Buffer: Fixed capacity prevents unlimited resource consumption
    - Semaphores: Count available empty and full slots
    - Mutex Lock: Protects critical section during buffer access
    - Critical Section: Buffer modification operations are atomic
    """
    
    def __init__(self, capacity: int, gui_callback: Optional[Callable] = None):
        """
        Initialize the shared buffer with specified capacity.
        
        Args:
            capacity (int): Maximum number of orders the buffer can hold
            gui_callback (Optional[Callable]): Callback function for GUI updates
        """
        self.capacity = capacity
        self.buffer: deque[Order] = deque()
        self.gui_callback = gui_callback
        
        # Semaphores for Producer-Consumer synchronization
        # empty: Counts available empty slots (initially all slots are empty)
        # full: Counts occupied slots (initially no slots are occupied)
        self.empty_slots = threading.Semaphore(capacity)  # Producer waits on this
        self.full_slots = threading.Semaphore(0)          # Consumer waits on this
        
        # Mutex lock for critical section protection
        # Ensures only one thread can modify the buffer at a time
        self.mutex = threading.Lock()
        
        # Statistics tracking
        self.total_produced = 0
        self.total_consumed = 0
        self.stats_lock = threading.Lock()
        
        # Event for graceful shutdown
        self.shutdown_event = threading.Event()
        
        # Queue for thread-safe GUI communication
        self.gui_queue = queue.Queue()
    
    def produce(self, order: Order, producer_id: int, timeout: float = 5.0) -> bool:
        """
        Add an order to the buffer (Producer operation).
        
        This method implements the producer side of the Producer-Consumer pattern.
        It follows the standard algorithm:
        1. Wait for an empty slot (P(empty))
        2. Acquire mutex lock for critical section
        3. Add item to buffer
        4. Release mutex lock
        5. Signal that a slot is now full (V(full))
        
        Args:
            order (Order): The order to add to the buffer
            producer_id (int): ID of the producing chef
            timeout (float): Maximum time to wait for buffer space
            
        Returns:
            bool: True if order was successfully added, False if timeout occurred
        """
        if self.shutdown_event.is_set():
            return False
        
        try:
            # Step 1: Wait for an empty slot (with timeout for deadlock prevention)
            if not self.empty_slots.acquire(timeout=timeout):
                self._notify_gui('blocking', f"Chef {producer_id} blocked - buffer full")
                return False
            
            # Check shutdown again after acquiring semaphore
            if self.shutdown_event.is_set():
                self.empty_slots.release()  # Release the acquired semaphore
                return False
            
            # Step 2: Enter critical section
            with self.mutex:
                # Step 3: Add order to buffer (critical section)
                self.buffer.append(order)
                order.complete_preparation()
                
                # Update statistics
                with self.stats_lock:
                    self.total_produced += 1
                
                # Notify GUI of buffer state change
                self._notify_gui('production', 
                               f"Chef {producer_id} added Order #{order.order_id} "
                               f"({order.dish_name}) to buffer")
                
                # Log buffer state for debugging
                buffer_state = f"Buffer: {len(self.buffer)}/{self.capacity} orders"
                self._notify_gui('info', buffer_state)
            
            # Step 4: Signal that a slot is now full
            self.full_slots.release()
            
            return True
            
        except Exception as e:
            self._notify_gui('system', f"Error in produce: {str(e)}")
            return False
    
    def consume(self, consumer_id: int, timeout: float = 5.0) -> Optional[Order]:
        """
        Remove an order from the buffer (Consumer operation).
        
        This method implements the consumer side of the Producer-Consumer pattern.
        It follows the standard algorithm:
        1. Wait for a full slot (P(full))
        2. Acquire mutex lock for critical section
        3. Remove item from buffer
        4. Release mutex lock
        5. Signal that a slot is now empty (V(empty))
        
        Args:
            consumer_id (int): ID of the consuming waiter
            timeout (float): Maximum time to wait for an order
            
        Returns:
            Optional[Order]: The consumed order, or None if timeout occurred
        """
        if self.shutdown_event.is_set():
            return None
        
        try:
            # Step 1: Wait for a full slot (with timeout for deadlock prevention)
            if not self.full_slots.acquire(timeout=timeout):
                self._notify_gui('blocking', f"Waiter {consumer_id} blocked - buffer empty")
                return None
            
            # Check shutdown again after acquiring semaphore
            if self.shutdown_event.is_set():
                self.full_slots.release()  # Release the acquired semaphore
                return None
            
            # Step 2: Enter critical section
            with self.mutex:
                # Step 3: Remove order from buffer (critical section)
                if not self.buffer:  # Double-check buffer is not empty
                    self.full_slots.release()
                    return None
                
                order = self.buffer.popleft()
                order.start_delivery(consumer_id)
                
                # Update statistics
                with self.stats_lock:
                    self.total_consumed += 1
                
                # Notify GUI of buffer state change
                self._notify_gui('consumption', 
                               f"Waiter {consumer_id} picked up Order #{order.order_id} "
                               f"({order.dish_name}) from buffer")
                
                # Log buffer state for debugging
                buffer_state = f"Buffer: {len(self.buffer)}/{self.capacity} orders"
                self._notify_gui('info', buffer_state)
            
            # Step 4: Signal that a slot is now empty
            self.empty_slots.release()
            
            return order
            
        except Exception as e:
            self._notify_gui('system', f"Error in consume: {str(e)}")
            return None
    
    def get_buffer_state(self) -> dict:
        """
        Get current buffer state in a thread-safe manner.
        
        Returns:
            dict: Dictionary containing buffer statistics and state
        """
        with self.mutex:
            buffer_orders = list(self.buffer)
        
        with self.stats_lock:
            return {
                'orders': buffer_orders,
                'current_size': len(buffer_orders),
                'capacity': self.capacity,
                'occupancy_percentage': (len(buffer_orders) / self.capacity) * 100,
                'total_produced': self.total_produced,
                'total_consumed': self.total_consumed,
                'empty_slots_available': self.capacity - len(buffer_orders),
                'full_slots_available': len(buffer_orders)
            }
    
    def reset(self) -> None:
        """
        Reset the buffer to initial state.
        
        This method clears all orders and resets statistics while maintaining
        thread safety. Used when restarting the simulation.
        """
        # Signal shutdown to prevent new operations
        self.shutdown_event.set()
        
        # Wait a brief moment for ongoing operations to complete
        time.sleep(0.1)
        
        # Reset semaphores and buffer
        with self.mutex:
            self.buffer.clear()
            
            # Reset semaphores to initial state
            # Drain any existing permits
            while self.empty_slots.acquire(blocking=False):
                pass
            while self.full_slots.acquire(blocking=False):
                pass
            
            # Set semaphores to initial values
            for _ in range(self.capacity):
                self.empty_slots.release()
        
        # Reset statistics
        with self.stats_lock:
            self.total_produced = 0
            self.total_consumed = 0
        
        # Clear shutdown event
        self.shutdown_event.clear()
        
        self._notify_gui('system', "Buffer reset completed")
    
    def shutdown(self) -> None:
        """
        Gracefully shutdown the buffer.
        
        This method signals all waiting threads to stop and prevents
        new operations from starting.
        """
        self.shutdown_event.set()
        
        # Release all waiting threads
        # This prevents deadlock during shutdown
        for _ in range(10):  # Release enough permits to wake up waiting threads
            self.empty_slots.release()
            self.full_slots.release()
        
        self._notify_gui('system', "Buffer shutdown initiated")
    
    def is_shutdown(self) -> bool:
        """Check if the buffer is in shutdown state."""
        return self.shutdown_event.is_set()
    
    def _notify_gui(self, event_type: str, message: str) -> None:
        """
        Send a message to the GUI through the thread-safe queue.
        
        Args:
            event_type (str): Type of event (production, consumption, blocking, etc.)
            message (str): Message to display in the GUI
        """
        try:
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            event_data = {
                'type': event_type,
                'message': message,
                'timestamp': timestamp,
                'buffer_state': self.get_buffer_state()
            }
            
            # Use non-blocking put to prevent GUI queue from blocking threads
            self.gui_queue.put_nowait(event_data)
            
            # Also call the callback if provided
            if self.gui_callback:
                self.gui_callback(event_data)
                
        except queue.Full:
            # If GUI queue is full, just skip this update
            pass
        except Exception:
            # Silently handle any GUI communication errors
            pass