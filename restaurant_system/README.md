# 🍽️ Restaurant Order Management System

## Operating System Concepts Demonstration

A comprehensive Python application that demonstrates fundamental Operating System concepts through a restaurant simulation with a modern, polished GUI. This project showcases the Producer-Consumer pattern, thread synchronization, and concurrent programming principles in an intuitive and visually appealing way.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![GUI](https://img.shields.io/badge/GUI-Tkinter-orange.svg)
![Threading](https://img.shields.io/badge/Threading-Synchronization-red.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [OS Concepts Demonstrated](#os-concepts-demonstrated)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Screenshots](#screenshots)
- [Configuration](#configuration)
- [Testing Scenarios](#testing-scenarios)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The Restaurant Order Management System simulates a restaurant kitchen where:

- **👨‍🍳 Chefs (Producers)** create orders and place them on a kitchen counter
- **🧑‍💼 Waiters (Consumers)** pick up orders from the counter and deliver them to customers
- **🍽️ Kitchen Counter (Shared Buffer)** has limited capacity, requiring proper synchronization
- **🔄 Thread Synchronization** prevents race conditions and ensures data consistency

This simulation provides a real-world context for understanding complex OS concepts, making them accessible and engaging for students and educators.

## 🖥️ OS Concepts Demonstrated

### 1. **Producer-Consumer Pattern**
- **Producers (Chefs):** Generate orders and place them in the shared buffer
- **Consumers (Waiters):** Remove orders from the shared buffer and process them
- **Bounded Buffer:** Kitchen counter with fixed capacity (5-20 orders)

### 2. **Thread Synchronization**
- **Semaphores:** 
  - `empty_slots`: Counts available buffer spaces (producers wait on this)
  - `full_slots`: Counts occupied buffer spaces (consumers wait on this)
- **Mutex Locks:** Protect critical sections during buffer access
- **Critical Sections:** Buffer modification operations are atomic

### 3. **Concurrency Management**
- **Multiple Threads:** 1-8 chef and waiter threads running concurrently
- **Thread States:** Visual representation of RUNNING, WAITING, BLOCKED, PAUSED states
- **Race Condition Prevention:** Proper locking mechanisms ensure data integrity

### 4. **Deadlock Prevention**
- **Timeout Mechanisms:** Threads don't wait indefinitely for resources
- **Resource Ordering:** Consistent acquisition order prevents circular dependencies
- **Deadlock Detection:** System monitors for potential deadlock conditions

### 5. **Thread Lifecycle Management**
- **Thread Creation:** Dynamic thread spawning based on configuration
- **Thread Termination:** Graceful shutdown with proper cleanup
- **Thread Monitoring:** Real-time state tracking and performance metrics

## ✨ Features

### 🎨 Modern GUI Design
- **Restaurant Theme:** Warm color palette with professional styling
- **Real-time Visualization:** Live updates of thread states and buffer occupancy
- **Interactive Controls:** Start/pause/reset simulation with configurable parameters
- **Activity Logging:** Color-coded event log with timestamps
- **Performance Dashboard:** Real-time statistics and efficiency metrics

### 🔧 Advanced Functionality
- **Configurable Parameters:** Adjust number of threads, buffer size, and simulation speed
- **Animation Effects:** Smooth transitions and pulsing indicators for active threads
- **Demo Mode:** Pre-configured optimal settings for demonstrations
- **Headless Mode:** Console-only operation for testing and automation
- **Export Capabilities:** Save simulation logs and performance reports

### 🛡️ Robust Implementation
- **Thread Safety:** All operations are properly synchronized
- **Error Handling:** Comprehensive exception handling and graceful degradation
- **Resource Management:** Proper cleanup and memory management
- **Cross-platform:** Works on Windows, macOS, and Linux

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- tkinter (usually included with Python)
- No additional dependencies required for basic functionality

### Quick Start

1. **Clone or Download** the project files to your local machine

2. **Navigate** to the project directory:
   ```bash
   cd restaurant_system
   ```

3. **Run** the application:
   ```bash
   python main.py
   ```

### Optional Dependencies

For enhanced system monitoring (optional):
```bash
pip install psutil
```

## 🚀 Usage

### Basic Usage

Start the application with default settings:
```bash
python main.py
```

### Command Line Options

```bash
# Custom configuration
python main.py --chefs 5 --waiters 3 --buffer-size 15

# Demo mode with optimal settings
python main.py --demo

# Headless mode for testing
python main.py --headless --chefs 4 --waiters 2

# Debug mode with detailed logging
python main.py --log-level DEBUG --log-file simulation.log

# Custom window size
python main.py --window-size 1400x900

# Fullscreen mode
python main.py --fullscreen
```

### GUI Controls

1. **Start Simulation:** Click "▶️ START" to begin with current settings
2. **Pause/Resume:** Use "⏸️ PAUSE" to temporarily halt the simulation
3. **Reset:** Click "🔄 RESET" to stop and clear the simulation
4. **Speed Control:** Adjust the speed slider (0.1x to 5.0x normal speed)
5. **Configuration:** Modify thread counts and buffer size before starting

### Keyboard Shortcuts

- **Escape:** Exit fullscreen mode
- **Ctrl+C:** Graceful shutdown (console mode)

## 🏗️ Architecture

### Project Structure

```
restaurant_system/
├── main.py              # Application entry point
├── config.py            # Configuration constants and settings
├── order.py             # Order data class and status management
├── shared_buffer.py     # Thread-safe bounded buffer implementation
├── producer.py          # Chef (Producer) thread class
├── consumer.py          # Waiter (Consumer) thread class
├── gui.py              # Modern Tkinter GUI implementation
├── utils.py            # Utility functions and helpers
└── README.md           # This documentation file
```

### Class Hierarchy

```
RestaurantApplication (main.py)
├── RestaurantGUI (gui.py)
│   ├── ThreadCard
│   ├── BufferVisualization
│   ├── ActivityLog
│   ├── StatsDashboard
│   └── ControlPanel
├── SharedBuffer (shared_buffer.py)
├── ChefThread (producer.py)
├── WaiterThread (consumer.py)
└── Order (order.py)
```

### Thread Communication

```mermaid
graph TD
    A[Chef Threads] -->|produce()| B[Shared Buffer]
    B -->|consume()| C[Waiter Threads]
    B -->|GUI Events| D[GUI Queue]
    D --> E[Main GUI Thread]
    F[Control Panel] -->|Commands| G[Thread Manager]
```

### Synchronization Mechanism

```python
# Producer Algorithm (Chef)
empty_slots.acquire()      # Wait for empty slot
mutex.acquire()            # Enter critical section
buffer.append(order)       # Add order to buffer
mutex.release()            # Exit critical section
full_slots.release()       # Signal new item available

# Consumer Algorithm (Waiter)
full_slots.acquire()       # Wait for full slot
mutex.acquire()            # Enter critical section
order = buffer.pop()       # Remove order from buffer
mutex.release()            # Exit critical section
empty_slots.release()      # Signal slot now empty
```

## 📸 Screenshots

*Note: Screenshots would be placed here in a real deployment*

### Main Interface
- Modern restaurant-themed GUI with thread cards
- Real-time buffer visualization
- Activity log with color-coded events

### Thread State Visualization
- Color-coded thread state indicators
- Performance statistics for each thread
- Animated status indicators

### Control Panel
- Intuitive configuration controls
- Real-time speed adjustment
- Start/pause/reset functionality

## ⚙️ Configuration

### Default Settings

| Parameter | Default Value | Range | Description |
|-----------|---------------|-------|-------------|
| Chefs | 3 | 1-8 | Number of producer threads |
| Waiters | 3 | 1-8 | Number of consumer threads |
| Buffer Size | 10 | 5-20 | Kitchen counter capacity |
| Speed | 1.0x | 0.1x-5.0x | Simulation speed multiplier |

### Timing Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Preparation Time | 1-3 seconds | Time for chefs to prepare orders |
| Delivery Time | 1-2 seconds | Time for waiters to deliver orders |
| GUI Update Rate | 50ms | Refresh rate for visual updates |

### Color Scheme

The application uses a professional restaurant theme:

- **Background:** Warm cream (#F5F5DC)
- **Primary:** Deep red (#8B0000)
- **Accent:** Gold (#DAA520)
- **Success:** Forest green (#228B22)
- **Warning:** Dark orange (#FF8C00)
- **Danger:** Crimson (#DC143C)

## 🧪 Testing Scenarios

### 1. Normal Operation
- Start with default settings (3 chefs, 3 waiters, buffer size 10)
- Observe steady order flow and balanced thread utilization
- Verify no deadlocks or race conditions occur

### 2. Buffer Overflow Prevention
- Set 1 waiter and 5 chefs with small buffer (size 5)
- Observe chefs blocking when buffer is full
- Verify proper synchronization prevents overflow

### 3. Buffer Underflow Prevention
- Set 5 waiters and 1 chef with any buffer size
- Observe waiters blocking when buffer is empty
- Verify proper synchronization prevents underflow

### 4. Deadlock Prevention
- Test various thread combinations and buffer sizes
- Monitor for deadlock detection warnings
- Verify timeout mechanisms prevent indefinite blocking

### 5. Performance Testing
- Run with maximum threads (8 chefs, 8 waiters)
- Monitor system resource usage
- Test simulation at various speeds (0.1x to 5.0x)

### 6. Stress Testing
- Run simulation for extended periods (30+ minutes)
- Monitor memory usage and thread stability
- Test pause/resume functionality under load

## 🔧 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check Python version
python --version  # Should be 3.8+

# Check tkinter availability
python -c "import tkinter; print('tkinter available')"

# Run with debug logging
python main.py --log-level DEBUG
```

#### GUI Performance Issues
- Reduce number of threads (try 2-3 each)
- Decrease simulation speed
- Close other applications to free memory
- Check system requirements

#### Thread Synchronization Errors
- These should not occur in normal operation
- If they do, please report as a bug with log files
- Try resetting the simulation

#### Memory Usage
- The application typically uses 50-100MB of RAM
- Memory usage increases with thread count and simulation duration
- Reset simulation periodically for long-running tests

### Debug Mode

Enable detailed logging for troubleshooting:
```bash
python main.py --log-level DEBUG --log-file debug.log
```

### System Requirements

- **Minimum:** Python 3.8, 512MB RAM, 50MB disk space
- **Recommended:** Python 3.9+, 1GB RAM, modern CPU
- **Display:** 1024x768 minimum resolution (1200x800 recommended)

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all classes and methods
- Include unit tests for new features

### Areas for Contribution

- Additional synchronization primitives (barriers, condition variables)
- Performance optimizations
- New visualization features
- Additional OS concepts (scheduling algorithms, memory management)
- Cross-platform improvements
- Documentation enhancements

## 📚 Educational Use

This project is designed for educational purposes and can be used in:

### Operating Systems Courses
- Demonstrate Producer-Consumer pattern
- Teach thread synchronization concepts
- Show practical applications of semaphores and mutexes
- Illustrate deadlock prevention techniques

### Programming Courses
- Multi-threaded programming examples
- GUI development with Tkinter
- Object-oriented design patterns
- Error handling and resource management

### Suggested Exercises

1. **Modify Buffer Implementation:** Change from FIFO to priority queue
2. **Add New Thread Types:** Implement dishwashers or managers
3. **Implement Scheduling:** Add different chef/waiter priorities
4. **Performance Analysis:** Measure and optimize throughput
5. **Add Persistence:** Save/load simulation state

## 📄 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2025 Restaurant Order Management System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Acknowledgments

- Inspired by classic Operating Systems textbooks and courses
- GUI design influenced by modern restaurant management systems
- Threading concepts based on established computer science principles
- Community feedback and suggestions for improvements

## 📞 Support

For questions, issues, or suggestions:

1. Check the troubleshooting section above
2. Review existing issues in the project repository
3. Create a new issue with detailed information
4. Include log files and system information when reporting bugs

---

**Happy Learning! 🎓**

*This project demonstrates that complex OS concepts can be made accessible and engaging through thoughtful design and implementation.*