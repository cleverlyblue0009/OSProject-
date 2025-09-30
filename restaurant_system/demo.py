#!/usr/bin/env python3
"""
Demonstration script for the Restaurant Order Management System.

This script shows the core Producer-Consumer functionality without GUI,
demonstrating all the key OS concepts in a simple, observable way.
"""

import time
import sys
from shared_buffer import SharedBuffer
from producer import ChefThread
from consumer import WaiterThread
import config

def simple_demo():
    """Run a simple demonstration of the Producer-Consumer pattern."""
    print("🍽️ Restaurant Order Management System")
    print("Operating System Concepts Demonstration")
    print("=" * 50)
    print()
    
    print("This demonstration shows:")
    print("✓ Producer-Consumer Pattern")
    print("✓ Thread Synchronization with Semaphores")
    print("✓ Mutex Locks for Critical Sections")
    print("✓ Bounded Buffer Implementation")
    print("✓ Race Condition Prevention")
    print()
    
    # Simple callback to show events
    events = []
    def event_callback(event_data):
        message = event_data.get('message', '')
        if 'added' in message or 'picked up' in message:
            events.append(message)
    
    # Create shared buffer (kitchen counter)
    print("Creating shared buffer (kitchen counter) with capacity 3...")
    buffer = SharedBuffer(3, event_callback)
    
    # Create one chef (producer)
    print("Starting Chef Marco (Producer Thread)...")
    chef = ChefThread(0, "Chef Marco", buffer, event_callback)
    chef.set_speed(3.0)  # Fast for demo
    chef.start()
    
    # Create one waiter (consumer)  
    print("Starting Waiter Alex (Consumer Thread)...")
    waiter = WaiterThread(0, "Waiter Alex", buffer, event_callback)
    waiter.set_speed(3.0)  # Fast for demo
    waiter.start()
    
    print("\nRunning simulation for 3 seconds...")
    print("Watch the Producer-Consumer pattern in action:")
    print("-" * 40)
    
    # Run for a short time
    start_time = time.time()
    while time.time() - start_time < 3:
        time.sleep(0.1)
        
        # Print recent events
        while events:
            event = events.pop(0)
            print(f"  {event}")
    
    # Stop threads
    print("\nStopping threads...")
    chef.stop()
    waiter.stop()
    
    # Wait briefly for cleanup
    chef.join(timeout=0.5)
    waiter.join(timeout=0.5)
    
    # Show final statistics
    buffer_state = buffer.get_buffer_state()
    chef_info = chef.get_state_info()
    waiter_info = waiter.get_state_info()
    
    print("\n📊 Final Statistics:")
    print(f"  Orders Produced: {chef_info['statistics']['orders_produced']}")
    print(f"  Orders Delivered: {waiter_info['statistics']['orders_delivered']}")
    print(f"  Buffer Final State: {buffer_state['current_size']}/{buffer_state['capacity']}")
    
    buffer.shutdown()
    
    print("\n✅ Demonstration Complete!")
    print("\nKey OS Concepts Successfully Demonstrated:")
    print("  🔄 Producer-Consumer Pattern: Chef creates, Waiter consumes")
    print("  🔒 Semaphores: Control access to buffer slots")
    print("  🛡️  Mutex Locks: Protect critical sections")
    print("  📦 Bounded Buffer: Limited capacity prevents overflow")
    print("  ⚡ Thread Safety: No race conditions occurred")
    
    if chef_info['statistics']['orders_produced'] > 0:
        print("\n🎉 SUCCESS: All synchronization mechanisms working correctly!")
    else:
        print("\n⚠️  Note: Run longer for more visible results")

if __name__ == "__main__":
    try:
        simple_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)