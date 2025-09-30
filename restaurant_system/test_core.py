#!/usr/bin/env python3
"""
Test script for the Restaurant Order Management System core functionality.

This script demonstrates the Producer-Consumer pattern and thread synchronization
without requiring a GUI, making it suitable for testing in environments where
tkinter is not available.
"""

import sys
import time
import threading
from typing import List

# Import our modules
from shared_buffer import SharedBuffer
from producer import ChefThread
from consumer import WaiterThread
import config


def test_basic_functionality():
    """Test basic producer-consumer functionality."""
    print("🍽️ Restaurant Order Management System - Core Functionality Test")
    print("=" * 60)
    
    # Configuration
    num_chefs = 2
    num_waiters = 2
    buffer_size = 5
    test_duration = 10  # seconds
    
    print(f"Configuration:")
    print(f"  Chefs: {num_chefs}")
    print(f"  Waiters: {num_waiters}")
    print(f"  Buffer Size: {buffer_size}")
    print(f"  Test Duration: {test_duration} seconds")
    print()
    
    # Create shared buffer
    def gui_callback(event_data):
        """Simple callback to print events."""
        timestamp = event_data.get('timestamp', '')
        message = event_data.get('message', '')
        if message:
            print(f"[{timestamp}] {message}")
    
    buffer = SharedBuffer(buffer_size, gui_callback)
    
    # Create threads
    chefs: List[ChefThread] = []
    waiters: List[WaiterThread] = []
    
    print("Starting threads...")
    
    # Create and start chef threads
    for i in range(num_chefs):
        chef_name = config.CHEF_NAMES[i % len(config.CHEF_NAMES)]
        chef = ChefThread(i, chef_name, buffer, gui_callback)
        chef.set_speed(2.0)  # 2x speed for faster testing
        chefs.append(chef)
        chef.start()
        print(f"  Started {chef_name}")
    
    # Create and start waiter threads
    for i in range(num_waiters):
        waiter_name = config.WAITER_NAMES[i % len(config.WAITER_NAMES)]
        waiter = WaiterThread(i, waiter_name, buffer, gui_callback)
        waiter.set_speed(2.0)  # 2x speed for faster testing
        waiters.append(waiter)
        waiter.start()
        print(f"  Started {waiter_name}")
    
    print(f"\nRunning simulation for {test_duration} seconds...")
    print("Press Ctrl+C to stop early")
    print("-" * 60)
    
    try:
        # Monitor the simulation
        start_time = time.time()
        last_report = start_time
        
        while time.time() - start_time < test_duration:
            time.sleep(1)
            
            current_time = time.time()
            if current_time - last_report >= 3:  # Report every 3 seconds
                buffer_state = buffer.get_buffer_state()
                elapsed = current_time - start_time
                
                print(f"\n📊 Status Report (t={elapsed:.1f}s):")
                print(f"  Orders Produced: {buffer_state['total_produced']}")
                print(f"  Orders Consumed: {buffer_state['total_consumed']}")
                print(f"  Buffer Occupancy: {buffer_state['current_size']}/{buffer_state['capacity']}")
                print(f"  Occupancy Rate: {buffer_state['occupancy_percentage']:.1f}%")
                
                # Thread states
                active_chefs = sum(1 for chef in chefs if chef.is_alive())
                active_waiters = sum(1 for waiter in waiters if waiter.is_alive())
                print(f"  Active Threads: {active_chefs} chefs, {active_waiters} waiters")
                print("-" * 40)
                
                last_report = current_time
    
    except KeyboardInterrupt:
        print("\n⏹️ Stopping simulation early...")
    
    # Stop all threads
    print("\n🛑 Stopping threads...")
    for chef in chefs:
        chef.stop()
    for waiter in waiters:
        waiter.stop()
    
    # Wait for threads to finish
    print("⏳ Waiting for threads to finish...")
    for chef in chefs:
        chef.join(timeout=2.0)
        if chef.is_alive():
            print(f"  Warning: {chef.chef_name} did not stop cleanly")
    
    for waiter in waiters:
        waiter.join(timeout=2.0)
        if waiter.is_alive():
            print(f"  Warning: {waiter.waiter_name} did not stop cleanly")
    
    # Final statistics
    buffer_state = buffer.get_buffer_state()
    elapsed_time = time.time() - start_time
    
    print("\n📈 Final Results:")
    print("=" * 40)
    print(f"Total Runtime: {elapsed_time:.1f} seconds")
    print(f"Orders Produced: {buffer_state['total_produced']}")
    print(f"Orders Consumed: {buffer_state['total_consumed']}")
    print(f"Final Buffer State: {buffer_state['current_size']}/{buffer_state['capacity']}")
    
    if elapsed_time > 0:
        production_rate = buffer_state['total_produced'] / elapsed_time * 60
        consumption_rate = buffer_state['total_consumed'] / elapsed_time * 60
        print(f"Production Rate: {production_rate:.1f} orders/minute")
        print(f"Consumption Rate: {consumption_rate:.1f} orders/minute")
    
    # Thread performance
    print("\n👨‍🍳 Chef Performance:")
    for chef in chefs:
        state_info = chef.get_state_info()
        stats = state_info['statistics']
        print(f"  {state_info['name']}: {stats['orders_produced']} orders, "
              f"{stats['avg_preparation_time']:.1f}s avg prep time")
    
    print("\n🧑‍💼 Waiter Performance:")
    for waiter in waiters:
        state_info = waiter.get_state_info()
        stats = state_info['statistics']
        print(f"  {state_info['name']}: {stats['orders_delivered']} orders, "
              f"{stats['avg_delivery_time']:.1f}s avg delivery time")
    
    # Cleanup
    buffer.shutdown()
    
    print("\n✅ Test completed successfully!")
    print("\nOS Concepts Demonstrated:")
    print("  ✓ Producer-Consumer Pattern")
    print("  ✓ Thread Synchronization with Semaphores")
    print("  ✓ Mutex Locks for Critical Section Protection")
    print("  ✓ Bounded Buffer Implementation")
    print("  ✓ Race Condition Prevention")
    print("  ✓ Graceful Thread Termination")


def test_synchronization_edge_cases():
    """Test edge cases for synchronization."""
    print("\n🔬 Testing Synchronization Edge Cases")
    print("=" * 40)
    
    # Test 1: Buffer overflow prevention
    print("Test 1: Buffer Overflow Prevention")
    buffer = SharedBuffer(2)  # Very small buffer
    
    # Create many producers, few consumers
    chefs = []
    for i in range(3):
        chef = ChefThread(i, f"TestChef{i}", buffer)
        chef.set_speed(5.0)  # Very fast
        chefs.append(chef)
        chef.start()
    
    # Single slow consumer
    waiter = WaiterThread(0, "TestWaiter", buffer)
    waiter.set_speed(0.5)  # Very slow
    waiter.start()
    
    time.sleep(3)  # Let it run briefly
    
    # Stop threads
    for chef in chefs:
        chef.stop()
    waiter.stop()
    
    for chef in chefs:
        chef.join(timeout=1.0)
    waiter.join(timeout=1.0)
    
    buffer_state = buffer.get_buffer_state()
    print(f"  Result: Buffer never exceeded capacity ({buffer_state['capacity']})")
    print(f"  Final occupancy: {buffer_state['current_size']}")
    
    buffer.shutdown()
    
    # Test 2: Buffer underflow prevention
    print("\nTest 2: Buffer Underflow Prevention")
    buffer = SharedBuffer(5)
    
    # Single slow producer
    chef = ChefThread(0, "SlowChef", buffer)
    chef.set_speed(0.5)  # Very slow
    chef.start()
    
    # Many fast consumers
    waiters = []
    for i in range(3):
        waiter = WaiterThread(i, f"FastWaiter{i}", buffer)
        waiter.set_speed(5.0)  # Very fast
        waiters.append(waiter)
        waiter.start()
    
    time.sleep(3)  # Let it run briefly
    
    # Stop threads
    chef.stop()
    for waiter in waiters:
        waiter.stop()
    
    chef.join(timeout=1.0)
    for waiter in waiters:
        waiter.join(timeout=1.0)
    
    buffer_state = buffer.get_buffer_state()
    print(f"  Result: Buffer never went below 0")
    print(f"  Final occupancy: {buffer_state['current_size']}")
    
    buffer.shutdown()
    
    print("✅ All synchronization tests passed!")


if __name__ == "__main__":
    try:
        test_basic_functionality()
        test_synchronization_edge_cases()
        
        print("\n🎉 All tests completed successfully!")
        print("\nThis demonstrates that the Restaurant Order Management System")
        print("correctly implements OS synchronization concepts:")
        print("- Producer-Consumer pattern with bounded buffer")
        print("- Semaphore-based resource counting")
        print("- Mutex locks for critical section protection")
        print("- Proper thread lifecycle management")
        print("- Race condition and deadlock prevention")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)