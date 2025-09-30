"""
Thread-Safe Shared Buffer Implementation

This module implements the bounded buffer (kitchen counter) shared between
producer and consumer threads.

OS Concepts Demonstrated:
1. Producer-Consumer Problem: Classic synchronization problem
2. Bounded Buffer: Fixed-size shared resource
3. Semaphores: For counting empty/full slots
4. Mutex Lock: For mutual exclusion in critical sections
5. Critical Section: Protecting shared data structure access
6. Deadlock Prevention: Proper resource ordering

The buffer uses three synchronization primitives:
- empty_slots: Semaphore counting available slots (producers wait on this)
- full_slots: Semaphore counting filled slots (consumers wait on this)
- mutex: Lock ensuring only one thread accesses buffer at a time
"""

import threading
from typing import Optional, List
from collections import deque
import time

from order import Order


class SharedBuffer:
    """
    Thread-safe bounded buffer implementing the producer-consumer pattern.
    
    This class represents the kitchen counter where chefs place orders and
    waiters pick them up. It uses semaphores and mutex locks to ensure
    thread-safe access and prevent race conditions.
    
    Attributes:
        capacity (int): Maximum number of orders the buffer can hold
        buffer (deque): The actual data structure holding orders
        empty_slots (Semaphore): Counts available empty slots
        full_slots (Semaphore): Counts filled slots with orders
        mutex (Lock): Ensures mutual exclusion for buffer access
    """
    
    def __init__(self, capacity: int):
        """
        Initialize the shared buffer with given capacity.
        
        Args:
            capacity (int): Maximum number of orders the buffer can hold
            
        OS Concept: Initialize synchronization primitives for thread coordination
        """
        self.capacity = capacity
        self.buffer: deque[Order] = deque()
        
        # Semaphore: Counts empty slots (initially all slots are empty)
        # Producers (chefs) wait on this before adding orders
        self.empty_slots = threading.Semaphore(capacity)
        
        # Semaphore: Counts full slots (initially no slots are filled)
        # Consumers (waiters) wait on this before removing orders
        self.full_slots = threading.Semaphore(0)
        
        # Mutex: Ensures only one thread accesses the buffer at a time
        # This protects the critical section where buffer is modified
        self.mutex = threading.Lock()
        
        # Statistics tracking
        self._total_produced = 0
        self._total_consumed = 0
        self._stats_lock = threading.Lock()  # Separate lock for stats
    
    def produce(self, order: Order, timeout: Optional[float] = None) -> bool:
        """
        Add an order to the buffer (called by chef/producer threads).
        
        This method implements the producer side of the producer-consumer problem:
        1. Wait for an empty slot (P operation on empty_slots semaphore)
        2. Acquire mutex lock (enter critical section)
        3. Add order to buffer
        4. Release mutex lock (exit critical section)
        5. Signal that a slot is now full (V operation on full_slots semaphore)
        
        Args:
            order (Order): The order to add to the buffer
            timeout (Optional[float]): Maximum time to wait for empty slot
            
        Returns:
            bool: True if order was added, False if timeout occurred
            
        OS Concepts:
        - Critical Section: The buffer modification is protected by mutex
        - Semaphore Operations: P(empty_slots) and V(full_slots)
        - Blocking: Thread blocks if buffer is full
        """
        # P(empty_slots): Wait for an empty slot
        # If buffer is full, this will block the thread (WAITING state)
        acquired = self.empty_slots.acquire(blocking=True, timeout=timeout)
        
        if not acquired:
            # Timeout occurred - buffer was full for too long
            return False
        
        try:
            # Enter critical section - acquire mutex lock
            # This ensures no other thread can modify buffer simultaneously
            self.mutex.acquire()
            
            # ===== CRITICAL SECTION START =====
            # Modify shared resource (buffer)
            order.mark_ready()
            self.buffer.append(order)
            # ===== CRITICAL SECTION END =====
            
        finally:
            # Always release the mutex, even if an exception occurs
            # This prevents deadlock from unreleased locks
            self.mutex.release()
        
        # V(full_slots): Signal that a slot is now full
        # This will wake up a waiting consumer (if any)
        self.full_slots.release()
        
        # Update statistics (using separate lock to avoid holding main mutex)
        with self._stats_lock:
            self._total_produced += 1
        
        return True
    
    def consume(self, timeout: Optional[float] = None) -> Optional[Order]:
        """
        Remove and return an order from the buffer (called by waiter/consumer threads).
        
        This method implements the consumer side of the producer-consumer problem:
        1. Wait for a full slot (P operation on full_slots semaphore)
        2. Acquire mutex lock (enter critical section)
        3. Remove order from buffer
        4. Release mutex lock (exit critical section)
        5. Signal that a slot is now empty (V operation on empty_slots semaphore)
        
        Args:
            timeout (Optional[float]): Maximum time to wait for full slot
            
        Returns:
            Optional[Order]: The order removed from buffer, or None if timeout
            
        OS Concepts:
        - Critical Section: The buffer modification is protected by mutex
        - Semaphore Operations: P(full_slots) and V(empty_slots)
        - Blocking: Thread blocks if buffer is empty
        """
        # P(full_slots): Wait for a filled slot
        # If buffer is empty, this will block the thread (WAITING state)
        acquired = self.full_slots.acquire(blocking=True, timeout=timeout)
        
        if not acquired:
            # Timeout occurred - buffer was empty for too long
            return None
        
        order = None
        try:
            # Enter critical section - acquire mutex lock
            self.mutex.acquire()
            
            # ===== CRITICAL SECTION START =====
            # Modify shared resource (buffer)
            if self.buffer:  # Double-check (defensive programming)
                order = self.buffer.popleft()
            # ===== CRITICAL SECTION END =====
            
        finally:
            # Always release the mutex
            self.mutex.release()
        
        # V(empty_slots): Signal that a slot is now empty
        # This will wake up a waiting producer (if any)
        self.empty_slots.release()
        
        # Update statistics
        if order:
            with self._stats_lock:
                self._total_consumed += 1
        
        return order
    
    def get_size(self) -> int:
        """
        Get current number of orders in buffer (thread-safe).
        
        Returns:
            int: Number of orders currently in buffer
        """
        with self.mutex:
            return len(self.buffer)
    
    def get_orders_snapshot(self) -> List[Order]:
        """
        Get a snapshot of current orders in buffer (thread-safe).
        
        Returns:
            List[Order]: Copy of current orders in buffer
            
        Note: This returns a snapshot at a specific moment. The actual buffer
        may change immediately after this call due to concurrent access.
        """
        with self.mutex:
            return list(self.buffer)
    
    def get_statistics(self) -> dict:
        """
        Get buffer statistics (thread-safe).
        
        Returns:
            dict: Statistics including total produced/consumed, current size
        """
        with self._stats_lock:
            total_produced = self._total_produced
            total_consumed = self._total_consumed
        
        with self.mutex:
            current_size = len(self.buffer)
        
        return {
            'total_produced': total_produced,
            'total_consumed': total_consumed,
            'current_size': current_size,
            'capacity': self.capacity,
            'occupancy_percent': (current_size / self.capacity * 100) if self.capacity > 0 else 0
        }
    
    def is_empty(self) -> bool:
        """Check if buffer is empty (thread-safe)."""
        with self.mutex:
            return len(self.buffer) == 0
    
    def is_full(self) -> bool:
        """Check if buffer is full (thread-safe)."""
        with self.mutex:
            return len(self.buffer) >= self.capacity
    
    def reset_statistics(self) -> None:
        """Reset statistics counters (thread-safe)."""
        with self._stats_lock:
            self._total_produced = 0
            self._total_consumed = 0