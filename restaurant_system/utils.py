"""
Utility functions for the Restaurant Order Management System.

This module contains helper functions and utilities used throughout
the application for logging, validation, and system monitoring.
"""

import logging
import time
import threading
from typing import Dict, List, Any, Optional
import sys
import os


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup logging configuration for the application.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (Optional[str]): Path to log file, if None logs to console only
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("RestaurantSystem")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create file handler: {e}")
    
    return logger


def validate_config(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize configuration parameters.
    
    Args:
        config_dict (Dict[str, Any]): Configuration dictionary to validate
        
    Returns:
        Dict[str, Any]: Validated and sanitized configuration
        
    Raises:
        ValueError: If configuration parameters are invalid
    """
    import config
    
    validated = {}
    
    # Validate number of chefs
    num_chefs = config_dict.get('num_chefs', config.DEFAULT_NUM_CHEFS)
    if not isinstance(num_chefs, int) or not (config.MIN_THREADS <= num_chefs <= config.MAX_THREADS):
        raise ValueError(f"Number of chefs must be between {config.MIN_THREADS} and {config.MAX_THREADS}")
    validated['num_chefs'] = num_chefs
    
    # Validate number of waiters
    num_waiters = config_dict.get('num_waiters', config.DEFAULT_NUM_WAITERS)
    if not isinstance(num_waiters, int) or not (config.MIN_THREADS <= num_waiters <= config.MAX_THREADS):
        raise ValueError(f"Number of waiters must be between {config.MIN_THREADS} and {config.MAX_THREADS}")
    validated['num_waiters'] = num_waiters
    
    # Validate buffer size
    buffer_size = config_dict.get('buffer_size', config.DEFAULT_BUFFER_SIZE)
    if not isinstance(buffer_size, int) or not (config.MIN_BUFFER_SIZE <= buffer_size <= config.MAX_BUFFER_SIZE):
        raise ValueError(f"Buffer size must be between {config.MIN_BUFFER_SIZE} and {config.MAX_BUFFER_SIZE}")
    validated['buffer_size'] = buffer_size
    
    # Validate speed
    speed = config_dict.get('speed', config.DEFAULT_SPEED)
    if not isinstance(speed, (int, float)) or not (config.MIN_SPEED <= speed <= config.MAX_SPEED):
        raise ValueError(f"Speed must be between {config.MIN_SPEED} and {config.MAX_SPEED}")
    validated['speed'] = float(speed)
    
    return validated


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds to a human-readable string.
    
    Args:
        seconds (float): Duration in seconds
        
    Returns:
        str: Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        return f"{hours}h {remaining_minutes}m"


def format_timestamp(timestamp: float) -> str:
    """
    Format a timestamp to a readable string.
    
    Args:
        timestamp (float): Unix timestamp
        
    Returns:
        str: Formatted timestamp string
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


def calculate_statistics(orders: List[Any]) -> Dict[str, float]:
    """
    Calculate statistics from a list of completed orders.
    
    Args:
        orders (List[Any]): List of Order objects
        
    Returns:
        Dict[str, float]: Dictionary containing calculated statistics
    """
    if not orders:
        return {
            'total_orders': 0,
            'avg_preparation_time': 0.0,
            'avg_delivery_time': 0.0,
            'avg_total_time': 0.0,
            'min_total_time': 0.0,
            'max_total_time': 0.0,
            'throughput_per_hour': 0.0
        }
    
    # Filter completed orders
    completed_orders = [order for order in orders if order.delivery_end_time is not None]
    
    if not completed_orders:
        return {
            'total_orders': len(orders),
            'avg_preparation_time': 0.0,
            'avg_delivery_time': 0.0,
            'avg_total_time': 0.0,
            'min_total_time': 0.0,
            'max_total_time': 0.0,
            'throughput_per_hour': 0.0
        }
    
    # Calculate preparation times
    prep_times = [order.preparation_duration for order in completed_orders 
                  if order.preparation_duration is not None]
    avg_prep_time = sum(prep_times) / len(prep_times) if prep_times else 0.0
    
    # Calculate delivery times
    delivery_times = [order.delivery_duration for order in completed_orders 
                      if order.delivery_duration is not None]
    avg_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else 0.0
    
    # Calculate total times
    total_times = [order.total_duration for order in completed_orders 
                   if order.total_duration is not None]
    avg_total_time = sum(total_times) / len(total_times) if total_times else 0.0
    min_total_time = min(total_times) if total_times else 0.0
    max_total_time = max(total_times) if total_times else 0.0
    
    # Calculate throughput
    if completed_orders:
        time_span = completed_orders[-1].delivery_end_time - completed_orders[0].created_time
        throughput_per_hour = (len(completed_orders) / max(time_span / 3600, 1/3600))
    else:
        throughput_per_hour = 0.0
    
    return {
        'total_orders': len(completed_orders),
        'avg_preparation_time': avg_prep_time,
        'avg_delivery_time': avg_delivery_time,
        'avg_total_time': avg_total_time,
        'min_total_time': min_total_time,
        'max_total_time': max_total_time,
        'throughput_per_hour': throughput_per_hour
    }


def monitor_system_resources() -> Dict[str, Any]:
    """
    Monitor system resources (CPU, memory, threads).
    
    Returns:
        Dict[str, Any]: Dictionary containing system resource information
    """
    try:
        import psutil
        
        # Get current process
        process = psutil.Process()
        
        # CPU usage
        cpu_percent = process.cpu_percent()
        
        # Memory usage
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        # Thread count
        thread_count = process.num_threads()
        
        # System-wide info
        system_cpu = psutil.cpu_percent()
        system_memory = psutil.virtual_memory()
        
        return {
            'process_cpu_percent': cpu_percent,
            'process_memory_mb': memory_mb,
            'process_thread_count': thread_count,
            'system_cpu_percent': system_cpu,
            'system_memory_percent': system_memory.percent,
            'system_memory_available_gb': system_memory.available / 1024 / 1024 / 1024
        }
        
    except ImportError:
        # psutil not available, return basic info
        return {
            'process_cpu_percent': 0.0,
            'process_memory_mb': 0.0,
            'process_thread_count': threading.active_count(),
            'system_cpu_percent': 0.0,
            'system_memory_percent': 0.0,
            'system_memory_available_gb': 0.0
        }
    except Exception:
        # Error getting system info
        return {
            'process_cpu_percent': 0.0,
            'process_memory_mb': 0.0,
            'process_thread_count': threading.active_count(),
            'system_cpu_percent': 0.0,
            'system_memory_percent': 0.0,
            'system_memory_available_gb': 0.0
        }


def export_simulation_log(log_entries: List[Dict[str, Any]], filename: str) -> bool:
    """
    Export simulation log entries to a file.
    
    Args:
        log_entries (List[Dict[str, Any]]): List of log entry dictionaries
        filename (str): Output filename
        
    Returns:
        bool: True if export successful, False otherwise
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Restaurant Order Management System - Simulation Log\n")
            f.write("=" * 60 + "\n\n")
            
            for entry in log_entries:
                timestamp = entry.get('timestamp', 'Unknown')
                event_type = entry.get('type', 'Unknown')
                message = entry.get('message', '')
                
                f.write(f"[{timestamp}] {event_type.upper()}: {message}\n")
        
        return True
        
    except Exception as e:
        print(f"Error exporting log: {e}")
        return False


def check_deadlock_conditions(chef_states: List[Dict], waiter_states: List[Dict], 
                             buffer_state: Dict) -> Optional[str]:
    """
    Check for potential deadlock conditions in the system.
    
    Args:
        chef_states (List[Dict]): List of chef state dictionaries
        waiter_states (List[Dict]): List of waiter state dictionaries
        buffer_state (Dict): Current buffer state
        
    Returns:
        Optional[str]: Warning message if deadlock detected, None otherwise
    """
    # Check if all chefs are blocked and buffer is full
    blocked_chefs = sum(1 for chef in chef_states if chef.get('state') == 'BLOCKED')
    total_chefs = len(chef_states)
    buffer_full = buffer_state.get('current_size', 0) >= buffer_state.get('capacity', 1)
    
    if blocked_chefs == total_chefs and total_chefs > 0 and buffer_full:
        return "Potential deadlock: All chefs blocked and buffer full"
    
    # Check if all waiters are blocked and buffer is empty
    blocked_waiters = sum(1 for waiter in waiter_states if waiter.get('state') == 'BLOCKED')
    total_waiters = len(waiter_states)
    buffer_empty = buffer_state.get('current_size', 0) == 0
    
    if blocked_waiters == total_waiters and total_waiters > 0 and buffer_empty:
        return "Potential deadlock: All waiters blocked and buffer empty"
    
    return None


def create_performance_report(chef_states: List[Dict], waiter_states: List[Dict], 
                            buffer_state: Dict, elapsed_time: float) -> str:
    """
    Create a performance report for the simulation.
    
    Args:
        chef_states (List[Dict]): List of chef state dictionaries
        waiter_states (List[Dict]): List of waiter state dictionaries
        buffer_state (Dict): Current buffer state
        elapsed_time (float): Total simulation time in seconds
        
    Returns:
        str: Formatted performance report
    """
    report = []
    report.append("Restaurant Order Management System - Performance Report")
    report.append("=" * 60)
    report.append(f"Simulation Duration: {format_duration(elapsed_time)}")
    report.append("")
    
    # Buffer statistics
    report.append("Buffer Statistics:")
    report.append(f"  Capacity: {buffer_state.get('capacity', 0)}")
    report.append(f"  Current Occupancy: {buffer_state.get('current_size', 0)}")
    report.append(f"  Occupancy Rate: {buffer_state.get('occupancy_percentage', 0):.1f}%")
    report.append(f"  Total Produced: {buffer_state.get('total_produced', 0)}")
    report.append(f"  Total Consumed: {buffer_state.get('total_consumed', 0)}")
    report.append("")
    
    # Chef statistics
    report.append("Chef Performance:")
    total_produced = 0
    total_blocked = 0
    for i, chef in enumerate(chef_states):
        stats = chef.get('statistics', {})
        produced = stats.get('orders_produced', 0)
        blocked = stats.get('orders_blocked', 0)
        avg_prep = stats.get('avg_preparation_time', 0)
        
        total_produced += produced
        total_blocked += blocked
        
        report.append(f"  {chef.get('name', f'Chef {i}')}: {produced} orders, "
                     f"{blocked} blocked, {avg_prep:.1f}s avg prep time")
    
    report.append(f"  Total: {total_produced} orders produced, {total_blocked} blocked")
    report.append("")
    
    # Waiter statistics
    report.append("Waiter Performance:")
    total_delivered = 0
    total_waiter_blocked = 0
    for i, waiter in enumerate(waiter_states):
        stats = waiter.get('statistics', {})
        delivered = stats.get('orders_delivered', 0)
        blocked = stats.get('orders_blocked', 0)
        avg_delivery = stats.get('avg_delivery_time', 0)
        avg_service = stats.get('avg_service_time', 0)
        
        total_delivered += delivered
        total_waiter_blocked += blocked
        
        report.append(f"  {waiter.get('name', f'Waiter {i}')}: {delivered} orders, "
                     f"{blocked} blocked, {avg_delivery:.1f}s avg delivery, "
                     f"{avg_service:.1f}s avg service time")
    
    report.append(f"  Total: {total_delivered} orders delivered, {total_waiter_blocked} blocked")
    report.append("")
    
    # System efficiency
    if elapsed_time > 0:
        throughput = total_delivered / (elapsed_time / 60)  # orders per minute
        report.append("System Efficiency:")
        report.append(f"  Throughput: {throughput:.2f} orders/minute")
        report.append(f"  Production Rate: {total_produced / (elapsed_time / 60):.2f} orders/minute")
        report.append(f"  Buffer Utilization: {buffer_state.get('occupancy_percentage', 0):.1f}%")
    
    return "\n".join(report)


def get_system_info() -> Dict[str, Any]:
    """
    Get system information for debugging and monitoring.
    
    Returns:
        Dict[str, Any]: System information dictionary
    """
    import platform
    
    return {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'architecture': platform.architecture(),
        'processor': platform.processor(),
        'active_threads': threading.active_count(),
        'main_thread': threading.main_thread().name,
        'current_thread': threading.current_thread().name
    }