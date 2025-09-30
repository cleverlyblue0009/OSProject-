"""
Order data class for the Restaurant Order Management System.

This module defines the Order class that represents individual food orders
in the restaurant simulation. Each order contains metadata and status information.
"""

import time
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class OrderStatus(Enum):
    """Enumeration of possible order statuses."""
    CREATED = "Created"
    IN_PREPARATION = "In Preparation"
    READY = "Ready"
    BEING_DELIVERED = "Being Delivered"
    DELIVERED = "Delivered"


@dataclass
class Order:
    """
    Represents a restaurant order with all necessary metadata.
    
    This class encapsulates all information about a food order, including
    timing information, status tracking, and identification details.
    
    Attributes:
        order_id (int): Unique identifier for the order
        dish_name (str): Name of the dish being ordered
        created_time (float): Timestamp when order was created
        chef_id (Optional[int]): ID of chef who prepared the order
        waiter_id (Optional[int]): ID of waiter who will deliver the order
        status (OrderStatus): Current status of the order
        preparation_start_time (Optional[float]): When preparation started
        preparation_end_time (Optional[float]): When preparation completed
        delivery_start_time (Optional[float]): When delivery started
        delivery_end_time (Optional[float]): When delivery completed
    """
    
    order_id: int
    dish_name: str
    created_time: float
    chef_id: Optional[int] = None
    waiter_id: Optional[int] = None
    status: OrderStatus = OrderStatus.CREATED
    preparation_start_time: Optional[float] = None
    preparation_end_time: Optional[float] = None
    delivery_start_time: Optional[float] = None
    delivery_end_time: Optional[float] = None
    
    def __post_init__(self):
        """Initialize the order with creation timestamp if not provided."""
        if self.created_time is None:
            self.created_time = time.time()
    
    def start_preparation(self, chef_id: int) -> None:
        """
        Mark the order as starting preparation.
        
        Args:
            chef_id (int): ID of the chef starting preparation
        """
        self.chef_id = chef_id
        self.status = OrderStatus.IN_PREPARATION
        self.preparation_start_time = time.time()
    
    def complete_preparation(self) -> None:
        """Mark the order as ready for delivery."""
        self.status = OrderStatus.READY
        self.preparation_end_time = time.time()
    
    def start_delivery(self, waiter_id: int) -> None:
        """
        Mark the order as starting delivery.
        
        Args:
            waiter_id (int): ID of the waiter starting delivery
        """
        self.waiter_id = waiter_id
        self.status = OrderStatus.BEING_DELIVERED
        self.delivery_start_time = time.time()
    
    def complete_delivery(self) -> None:
        """Mark the order as delivered."""
        self.status = OrderStatus.DELIVERED
        self.delivery_end_time = time.time()
    
    @property
    def preparation_duration(self) -> Optional[float]:
        """
        Calculate the preparation duration in seconds.
        
        Returns:
            Optional[float]: Duration in seconds, or None if not completed
        """
        if self.preparation_start_time and self.preparation_end_time:
            return self.preparation_end_time - self.preparation_start_time
        return None
    
    @property
    def delivery_duration(self) -> Optional[float]:
        """
        Calculate the delivery duration in seconds.
        
        Returns:
            Optional[float]: Duration in seconds, or None if not completed
        """
        if self.delivery_start_time and self.delivery_end_time:
            return self.delivery_end_time - self.delivery_start_time
        return None
    
    @property
    def total_duration(self) -> Optional[float]:
        """
        Calculate the total order duration from creation to delivery.
        
        Returns:
            Optional[float]: Duration in seconds, or None if not delivered
        """
        if self.delivery_end_time:
            return self.delivery_end_time - self.created_time
        return None
    
    def get_formatted_time(self) -> str:
        """
        Get a formatted string representation of the creation time.
        
        Returns:
            str: Formatted timestamp string
        """
        return time.strftime("%H:%M:%S", time.localtime(self.created_time))
    
    def __str__(self) -> str:
        """String representation of the order."""
        return f"Order #{self.order_id}: {self.dish_name} ({self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (f"Order(id={self.order_id}, dish='{self.dish_name}', "
                f"status={self.status.value}, chef_id={self.chef_id}, "
                f"waiter_id={self.waiter_id})")