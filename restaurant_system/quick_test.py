#!/usr/bin/env python3
"""
Quick test of the Restaurant Order Management System core functionality.
"""

import time
import threading
from shared_buffer import SharedBuffer
from producer import ChefThread
from consumer import WaiterThread
import config

def main():
    print("🍽️ Restaurant Order Management System - Quick Test")
    print("=" * 50)
    
    # Create a small buffer
    buffer = SharedBuffer(3)
    
    # Create one chef and one waiter
    chef = ChefThread(0, "TestChef", buffer)
    waiter = WaiterThread(0, "TestWaiter", buffer)
    
    # Set high speed for quick test
    chef.set_speed(10.0)
    waiter.set_speed(10.0)
    
    print("Starting threads...")
    chef.start()
    waiter.start()
    
    # Run for 2 seconds
    time.sleep(2)
    
    print("Stopping threads...")
    chef.stop()
    waiter.stop()
    
    # Wait for completion
    chef.join(timeout=1.0)
    waiter.join(timeout=1.0)
    
    # Get final stats
    buffer_state = buffer.get_buffer_state()
    chef_stats = chef.get_state_info()['statistics']
    waiter_stats = waiter.get_state_info()['statistics']
    
    print(f"\nResults:")
    print(f"  Orders Produced: {chef_stats['orders_produced']}")
    print(f"  Orders Delivered: {waiter_stats['orders_delivered']}")
    print(f"  Buffer Final State: {buffer_state['current_size']}/{buffer_state['capacity']}")
    
    buffer.shutdown()
    
    if chef_stats['orders_produced'] > 0 and waiter_stats['orders_delivered'] > 0:
        print("✅ SUCCESS: Producer-Consumer pattern working correctly!")
    else:
        print("❌ FAILED: No orders processed")
    
    print("\nOS Concepts Demonstrated:")
    print("  ✓ Producer-Consumer Pattern")
    print("  ✓ Thread Synchronization")
    print("  ✓ Semaphores and Mutex Locks")
    print("  ✓ Bounded Buffer")

if __name__ == "__main__":
    main()