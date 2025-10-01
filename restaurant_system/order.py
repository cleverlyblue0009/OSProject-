"""
Order Data Class

This module defines the Order class which represents a food order in the restaurant
system. Each order is created by a chef (producer) and delivered by a waiter (consumer).

OS Concept Demonstrated:
- Data structures shared between concurrent threads
- Immutable data objects to prevent race conditions on order details
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Order:
    """
    Represents a food order in the restaurant system.
    
    This class encapsulates all information about a single order. Using a dataclass
    with frozen=True would make it immutable, but we keep it mutable for status updates.
    Thread safety is ensured by proper synchronization at the buffer level.
    
    Attributes:
        order_id (int): Unique identifier for the order
        dish_name (str): Name of the dish being ordered
        chef_id (int): ID of the chef who prepared the order
        waiter_id (Optional[int]): ID of the waiter who delivered the order
        created_at (datetime): Timestamp when order was created
        completed_at (Optional[datetime]): Timestamp when order was delivered
        status (str): Current status of the order
    """
    
    order_id: int
    dish_name: str
    chef_id: int
    waiter_id: Optional[int] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    status: str = "pending"
    
    def __post_init__(self):
        """Initialize created_at timestamp if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def mark_in_preparation(self) -> None:
        """Mark order as being prepared by a chef."""
        self.status = "preparing"
    
    def mark_ready(self) -> None:
        """Mark order as ready for pickup (in buffer)."""
        self.status = "ready"
    
    def mark_in_delivery(self, waiter_id: int) -> None:
        """
        Mark order as being delivered by a waiter.
        
        Args:
            waiter_id (int): ID of the waiter delivering the order
        """
        self.status = "delivering"
        self.waiter_id = waiter_id
    
    def mark_completed(self) -> None:
        """Mark order as completed/delivered."""
        self.status = "completed"
        self.completed_at = datetime.now()
    
    def get_processing_time(self) -> Optional[float]:
        """
        Calculate total processing time from creation to completion.
        
        Returns:
            Optional[float]: Processing time in seconds, or None if not completed
        """
        if self.completed_at is None:
            return None
        return (self.completed_at - self.created_at).total_seconds()
    
    def __str__(self) -> str:
        """String representation of the order."""
        return f"Order #{self.order_id}: {self.dish_name}"
    
    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (f"Order(id={self.order_id}, dish={self.dish_name}, "
                f"chef={self.chef_id}, waiter={self.waiter_id}, "
                f"status={self.status})")