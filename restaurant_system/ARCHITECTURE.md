# 🏗️ System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MAIN APPLICATION                            │
│                          (main.py)                                  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                    GUI THREAD (Tkinter)                      │ │
│  │                        (gui.py)                              │ │
│  │                                                              │ │
│  │  • Renders UI components                                    │ │
│  │  • Handles user input                                       │ │
│  │  • Updates displays (60 FPS)                                │ │
│  │  • Thread-safe queue consumer                               │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              ↓↑                                     │
│                     update_queue.Queue()                            │
│                    (Thread-safe communication)                      │
│                              ↓↑                                     │
└─────────────────────────────────────────────────────────────────────┘
                                ↓↑
┌─────────────────────────────────────────────────────────────────────┐
│                      SHARED BUFFER LAYER                            │
│                    (shared_buffer.py)                               │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              SharedBuffer (Bounded Buffer)                  │   │
│  │                                                             │   │
│  │  Components:                                                │   │
│  │  • buffer: deque()           [Orders stored here]          │   │
│  │  • empty_slots: Semaphore()  [Counts empty slots]         │   │
│  │  • full_slots: Semaphore()   [Counts filled slots]        │   │
│  │  • mutex: Lock()             [Protects critical section]   │   │
│  │                                                             │   │
│  │  Operations:                                                │   │
│  │  • produce(order)   - Add order to buffer                  │   │
│  │  • consume()        - Remove order from buffer             │   │
│  │  • get_statistics() - Thread-safe stats                    │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              ↑↓                                     │
└─────────────────────────────────────────────────────────────────────┘
                                ↑↓
                ┌───────────────┴───────────────┐
                ↑                               ↓
┌───────────────────────────┐       ┌───────────────────────────┐
│   PRODUCER THREADS        │       │   CONSUMER THREADS        │
│   (producer.py)           │       │   (consumer.py)           │
│                           │       │                           │
│ ┌─────────────────────┐   │       │   ┌─────────────────────┐ │
│ │   Chef Thread 1     │   │       │   │   Waiter Thread 1   │ │
│ │   • Create orders   │   │       │   │   • Pick up orders  │ │
│ │   • Wait for space  │   │       │   │   • Wait for orders │ │
│ │   • Add to buffer   │   │       │   │   • Remove from buf │ │
│ └─────────────────────┘   │       │   └─────────────────────┘ │
│                           │       │                           │
│ ┌─────────────────────┐   │       │   ┌─────────────────────┐ │
│ │   Chef Thread 2     │   │       │   │   Waiter Thread 2   │ │
│ └─────────────────────┘   │       │   └─────────────────────┘ │
│                           │       │                           │
│ ┌─────────────────────┐   │       │   ┌─────────────────────┐ │
│ │   Chef Thread 3     │   │       │   │   Waiter Thread 3   │ │
│ └─────────────────────┘   │       │   └─────────────────────┘ │
│                           │       │                           │
│         (1-10 threads)    │       │         (1-10 threads)    │
└───────────────────────────┘       └───────────────────────────┘
```

---

## Component Interaction Flow

### Producer (Chef) Flow

```
┌─────────────┐
│  Chef Thread│
│  (RUNNING)  │
└──────┬──────┘
       │
       ↓
┌──────────────────────────┐
│ 1. Prepare Order         │
│    (Simulate work)       │
│    sleep(random time)    │
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│ 2. P(empty_slots)        │◄────── May block if buffer full
│    (Wait for space)      │        (Thread → WAITING state)
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│ 3. mutex.acquire()       │◄────── Enter critical section
│    (Lock buffer)         │
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│ 4. buffer.append(order)  │
│    (Modify shared data)  │
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│ 5. mutex.release()       │◄────── Exit critical section
│    (Unlock buffer)       │
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│ 6. V(full_slots)         │◄────── Wake up waiting consumer
│    (Signal order ready)  │
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│ 7. Notify GUI            │
│    via update_queue      │
└──────┬───────────────────┘
       │
       ↓ (loop back to step 1)
```

### Consumer (Waiter) Flow

```
┌─────────────┐
│Waiter Thread│
│  (RUNNING)  │
└──────┬──────┘
       │
       ↓
┌──────────────────────────┐
│ 1. P(full_slots)         │◄────── May block if buffer empty
│    (Wait for order)      │        (Thread → WAITING state)
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│ 2. mutex.acquire()       │◄────── Enter critical section
│    (Lock buffer)         │
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│ 3. order=buffer.pop()    │
│    (Modify shared data)  │
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│ 4. mutex.release()       │◄────── Exit critical section
│    (Unlock buffer)       │
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│ 5. V(empty_slots)        │◄────── Wake up waiting producer
│    (Signal space avail)  │
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│ 6. Deliver Order         │
│    (Simulate work)       │
│    sleep(random time)    │
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│ 7. Notify GUI            │
│    via update_queue      │
└──────┬───────────────────┘
       │
       ↓ (loop back to step 1)
```

---

## Synchronization Mechanism

### Semaphore State Diagram

```
Initial State (capacity=10):
┌──────────────────────────┐
│ empty_slots = 10         │ (All slots available)
│ full_slots = 0           │ (No orders ready)
│ buffer = []              │ (Empty buffer)
└──────────────────────────┘

After Chef adds 1 order:
┌──────────────────────────┐
│ empty_slots = 9          │ ↓ decreased
│ full_slots = 1           │ ↑ increased
│ buffer = [Order#1]       │
└──────────────────────────┘

After Waiter picks up 1 order:
┌──────────────────────────┐
│ empty_slots = 10         │ ↑ increased
│ full_slots = 0           │ ↓ decreased
│ buffer = []              │
└──────────────────────────┘

Invariant (always true):
empty_slots + full_slots + threads_in_critical_section = capacity
```

### Critical Section Protection

```
Time →

Thread A (Chef):
    │
    ├─► P(empty_slots) ────────┐
    │                          │ Wait if buffer full
    ├─► mutex.acquire() ───────┘
    │
    ├─► ╔═══════════════════╗
    │   ║ CRITICAL SECTION  ║  ← Only ONE thread here
    │   ║ buffer.append()   ║
    │   ╚═══════════════════╝
    │
    ├─► mutex.release()
    │
    ├─► V(full_slots)
    │
    ↓


Thread B (Waiter):
    │                          (blocked waiting for mutex)
    ├─► P(full_slots)          │
    │                          │
    ├─► mutex.acquire() ───────┘
    │                          (enters after A releases)
    ├─► ╔═══════════════════╗
    │   ║ CRITICAL SECTION  ║
    │   ║ buffer.pop()      ║
    │   ╚═══════════════════╝
    │
    ├─► mutex.release()
    │
    ├─► V(empty_slots)
    │
    ↓
```

---

## Thread State Transitions

```
                    start()
    ┌─────────────────────────────────┐
    │                                 │
    │         NEW (Created)           │
    │                                 │
    └─────────────┬───────────────────┘
                  │
                  ↓
    ┌─────────────────────────────────┐
    │                                 │
    │     RUNNING (Doing work)        │
    │                                 │
    └─────┬───────────────────┬───────┘
          │                   │
          │ P(semaphore)      │ pause()
          │ blocks            │
          ↓                   ↓
    ┌─────────────┐     ┌─────────────┐
    │   WAITING   │     │   BLOCKED   │
    │ (Semaphore) │     │  (Paused)   │
    └──────┬──────┘     └──────┬──────┘
           │                   │
           │ V(semaphore)      │ resume()
           │ signals           │
           ↓                   ↓
    ┌─────────────────────────────────┐
    │                                 │
    │     RUNNING (Doing work)        │
    │                                 │
    └─────────────┬───────────────────┘
                  │
                  │ stop()
                  ↓
    ┌─────────────────────────────────┐
    │                                 │
    │    IDLE (Terminated)            │
    │                                 │
    └─────────────────────────────────┘
```

---

## Data Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                         User Input                             │
│                                                                │
│   [START] [PAUSE] [RESET] [Speed Slider] [Configuration]      │
└────────────┬───────────────────────────────────────────────────┘
             │
             ↓
┌────────────────────────────────────────────────────────────────┐
│                      GUI Layer (gui.py)                        │
│                                                                │
│  • Captures user actions                                      │
│  • Creates/controls threads                                   │
│  • Processes update queue                                     │
│  • Renders visual elements                                    │
└────────────┬───────────────────────────────────────────────────┘
             │
             ↓
┌────────────────────────────────────────────────────────────────┐
│                   Thread Control Layer                         │
│                                                                │
│  start() → Create and start threads                           │
│  pause() → Set pause events                                   │
│  resume() → Clear pause events                                │
│  stop() → Set stop events                                     │
└───┬────────────────────────────────────────────────────────┬───┘
    │                                                        │
    ↓                                                        ↓
┌───────────────────┐                            ┌───────────────────┐
│ Producer Threads  │                            │ Consumer Threads  │
│                   │                            │                   │
│ • Create orders   │                            │ • Pickup orders   │
│ • Check events    │                            │ • Check events    │
│ • Produce to buf  │                            │ • Consume from buf│
│ • Send callbacks  │                            │ • Send callbacks  │
└─────────┬─────────┘                            └─────────┬─────────┘
          │                                                │
          │            ┌──────────────────┐              │
          └───────────►│  Shared Buffer   │◄─────────────┘
                       │                  │
                       │ • Semaphores     │
                       │ • Mutex lock     │
                       │ • Deque buffer   │
                       └────────┬─────────┘
                                │
                                ↓
                       ┌──────────────────┐
                       │ Order Objects    │
                       │  (order.py)      │
                       │                  │
                       │ • ID             │
                       │ • Dish name      │
                       │ • Timestamps     │
                       │ • Status         │
                       └────────┬─────────┘
                                │
                                ↓
                       ┌──────────────────┐
                       │  Statistics &    │
                       │  Logging         │
                       └──────────────────┘
                                │
                                ↓
                       ┌──────────────────┐
                       │  Update Queue    │
                       │ (Thread→GUI)     │
                       └────────┬─────────┘
                                │
                                ↓
                       ┌──────────────────┐
                       │   GUI Display    │
                       │  Update (60fps)  │
                       └──────────────────┘
```

---

## Module Dependencies

```
main.py
  │
  ├─► gui.py
  │    │
  │    ├─► config.py
  │    ├─► utils.py
  │    ├─► shared_buffer.py
  │    │     │
  │    │     └─► order.py
  │    │
  │    ├─► producer.py
  │    │     │
  │    │     ├─► shared_buffer.py
  │    │     ├─► order.py
  │    │     └─► config.py
  │    │
  │    └─► consumer.py
  │          │
  │          ├─► shared_buffer.py
  │          ├─► order.py
  │          └─► config.py
  │
  └─► tkinter (GUI framework)

Dependency Graph:
┌──────────┐
│ main.py  │
└────┬─────┘
     │
     ↓
┌──────────┐     ┌─────────────┐
│  gui.py  │────►│  config.py  │
└────┬─────┘     └─────────────┘
     │           ┌─────────────┐
     ├──────────►│  utils.py   │
     │           └─────────────┘
     │           ┌──────────────────┐
     ├──────────►│ shared_buffer.py │
     │           └────────┬─────────┘
     │                    │
     │                    ↓
     │           ┌─────────────┐
     │           │  order.py   │
     │           └─────────────┘
     │                    ↑
     │           ┌────────┴─────────┐
     │           │                  │
     │    ┌──────┴──────┐    ┌──────┴──────┐
     ├───►│ producer.py │    │ consumer.py │◄──┐
     │    └─────────────┘    └─────────────┘   │
     └──────────────────────────────────────────┘
```

---

## File Responsibilities

| File | Primary Responsibility | Key Classes/Functions |
|------|----------------------|----------------------|
| `main.py` | Entry point, initialization | `main()`, `check_python_version()` |
| `gui.py` | User interface, visualization | `RestaurantGUI` class |
| `shared_buffer.py` | Synchronized buffer | `SharedBuffer` class |
| `producer.py` | Producer threads | `Chef` class |
| `consumer.py` | Consumer threads | `Waiter` class |
| `order.py` | Data model | `Order` class |
| `config.py` | Configuration constants | Global constants |
| `utils.py` | Helper functions | Utility functions |

---

## Communication Patterns

### 1. Thread → GUI Communication

```
Worker Thread                      Main GUI Thread
     │                                    │
     ├─► callback('log', ...)             │
     │        │                           │
     │        ↓                           │
     │   update_queue.put()               │
     │                                    │
     │                          ┌─────────┴────────┐
     │                          │ GUI update loop  │
     │                          │ (every 16ms)     │
     │                          └─────────┬────────┘
     │                                    │
     │                          update_queue.get()
     │                                    │
     │                                    ↓
     │                          Update GUI elements
```

### 2. Thread → Buffer Communication

```
Chef Thread                        Shared Buffer
     │                                    │
     ├─► shared_buffer.produce(order)     │
     │                                    │
     │                          ┌─────────┴────────┐
     │                          │ 1. P(empty_slots)│
     │                          │ 2. acquire(mutex)│
     │                          │ 3. append(order) │
     │                          │ 4. release(mutex)│
     │                          │ 5. V(full_slots) │
     │                          └─────────┬────────┘
     │                                    │
     │◄───────── return True ─────────────┤
```

### 3. GUI → Thread Communication

```
GUI                                Worker Threads
     │                                    │
     ├─► thread.pause()                   │
     │                                    │
     │                          ┌─────────┴────────┐
     │                          │ pause_event.clear()
     │                          │                  │
     │                          │ Thread checks:   │
     │                          │ pause_event.wait()
     │                          │ (blocks here)    │
     │                          └──────────────────┘
     │
     ├─► thread.resume()
     │                          ┌──────────────────┐
     │                          │ pause_event.set()│
     │                          │                  │
     │                          │ Thread continues │
     │                          └──────────────────┘
```

---

## Memory Model

```
┌─────────────────────────────────────────────────────────────┐
│                     PROCESS MEMORY SPACE                    │
│                    (Shared by all threads)                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │            SHARED DATA (Heap)                      │    │
│  │                                                    │    │
│  │  • SharedBuffer instance                          │    │
│  │    - buffer (deque)                               │    │
│  │    - empty_slots (Semaphore)                      │    │
│  │    - full_slots (Semaphore)                       │    │
│  │    - mutex (Lock)                                 │    │
│  │                                                    │    │
│  │  • Order objects                                  │    │
│  │  • Configuration data                             │    │
│  │  • GUI objects                                    │    │
│  │  • update_queue                                   │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐            │
│  │Chef Thread │ │Chef Thread │ │Chef Thread │  ...        │
│  │   Stack 1  │ │   Stack 2  │ │   Stack 3  │            │
│  │            │ │            │ │            │            │
│  │ • Local    │ │ • Local    │ │ • Local    │            │
│  │   vars     │ │   vars     │ │   vars     │            │
│  │ • Function │ │ • Function │ │ • Function │            │
│  │   calls    │ │   calls    │ │   calls    │            │
│  └────────────┘ └────────────┘ └────────────┘            │
│                                                             │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐            │
│  │Wait Thread │ │Wait Thread │ │Wait Thread │  ...        │
│  │   Stack 1  │ │   Stack 2  │ │   Stack 3  │            │
│  └────────────┘ └────────────┘ └────────────┘            │
│                                                             │
│  ┌────────────┐                                            │
│  │ GUI Thread │                                            │
│  │   Stack    │                                            │
│  └────────────┘                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Key Point: All threads share the same heap (SharedBuffer),
but each has its own stack (local variables).
```

---

## Timing Diagram Example

```
Time →

Chef-1:  │──Prep──│─Wait─│Acq│Add│Rel│────Prep────│...
                   ↓      ↓   ↓   ↓
Semaphore:         P(empty)   V(full)

Buffer:  []              [Order#1]              []

Semaphore:                    P(full)   V(empty)
                              ↓   ↓   ↓      ↓
Waiter-1: │─Wait─────────────│Acq│Rem│Rel│──Deliver──│...
                                  ↓
Chef-2:   │───Prep───│─Wait─│....│Acq│Add│Rel│...
                             (blocked by Chef-1's mutex)

Legend:
Prep    = Preparing order
Wait    = Waiting on semaphore (WAITING state)
Acq     = Acquire mutex (enter critical section)
Add/Rem = Add/Remove from buffer
Rel     = Release mutex (exit critical section)
Deliver = Delivering order
```

---

## Scalability Model

```
System Load vs Buffer Size:

Chefs=3, Waiters=3, Buffer=5:
┌────────┐
│████████│ 80% Buffer Utilization
│████████│ Low blocking
│████████│ Balanced
└────────┘

Chefs=10, Waiters=3, Buffer=5:
┌────────┐
│████████│ 95% Buffer Utilization
│████████│ Chefs frequently blocked
│████████│ Unbalanced (overproduction)
└────────┘

Chefs=3, Waiters=10, Buffer=5:
┌────────┐
│██░░░░░░│ 20% Buffer Utilization
│        │ Waiters frequently blocked
│        │ Unbalanced (underconsumption)
└────────┘

Chefs=5, Waiters=5, Buffer=20:
┌────────────────────┐
│███░░░░░░░░░░░░░░░░░│ 30% Buffer Utilization
│                    │ Low blocking
│                    │ Oversized buffer
└────────────────────┘
```

---

## Error Handling Flow

```
┌─────────────────────────────┐
│   Operation Attempted       │
└──────────┬──────────────────┘
           │
           ↓
    ┌──────────────┐
    │ Try block    │
    └──────┬───────┘
           │
    ┌──────▼────────┐
    │ Success?      │
    └──┬────────┬───┘
       │        │
     Yes        No
       │        │
       │        ↓
       │   ┌────────────────┐
       │   │ Except block   │
       │   └────────┬───────┘
       │            │
       │            ↓
       │   ┌────────────────┐
       │   │ Log error      │
       │   │ Notify GUI     │
       │   │ Graceful handle│
       │   └────────┬───────┘
       │            │
       └────────────┤
                    │
                    ↓
           ┌────────────────┐
           │ Finally block  │
           │ (cleanup)      │
           └────────────────┘
                    │
                    ↓
           ┌────────────────┐
           │ Continue       │
           └────────────────┘
```

---

## Summary

This architecture implements a **classic producer-consumer system** with:

✅ **Clear separation of concerns** - Each module has single responsibility
✅ **Thread-safe operations** - Proper synchronization throughout
✅ **Scalable design** - Configurable thread counts and buffer size
✅ **Robust error handling** - Graceful degradation
✅ **Clean communication** - Well-defined interfaces between components
✅ **Educational value** - Clear demonstration of OS concepts

The system effectively demonstrates Operating System concepts while maintaining
production-quality code standards and user experience.