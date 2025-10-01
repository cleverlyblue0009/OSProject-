# 🚀 Quick Start Guide

## Get Running in 30 Seconds!

### Step 1: Navigate to Directory
```bash
cd restaurant_system
```

### Step 2: Run the Application
```bash
python3 main.py
```

### Step 3: Use the GUI

1. **Click "START"** button
2. Watch the magic happen! ✨

That's it! The simulation will start with default settings:
- 3 Chefs (producers)
- 3 Waiters (consumers)
- Buffer size of 10

## 🎮 Controls

| Button | Action |
|--------|--------|
| ▶️ START | Begin simulation |
| ⏸️ PAUSE | Pause all threads |
| 🔄 RESET | Stop and reset everything |

## 🎚️ Adjusting Parameters

Before clicking START, you can change:

- **Number of Chefs**: 1-10 (default: 3)
- **Number of Waiters**: 1-10 (default: 3)
- **Buffer Size**: 5-20 (default: 10)
- **Speed**: 0.1x to 5.0x (default: 1.0x)

## 🔍 What to Watch

### Thread States (Colored Circles)
- 🟢 **Green (RUNNING)**: Thread is working
- 🟡 **Yellow (WAITING)**: Thread is blocked waiting for resource
- 🔴 **Red (BLOCKED)**: Thread is paused

### Buffer Visualization
- Watch orders appear and disappear in real-time
- See when buffer gets full (chefs wait)
- See when buffer gets empty (waiters wait)

### Activity Log
- Scroll down to see all events
- Color-coded messages
- Timestamps for everything

## 🧪 Try These Experiments!

### Experiment 1: Buffer Overflow
```
Chefs: 5
Waiters: 1
Buffer: 5
```
**Result**: Chefs will frequently block (yellow) waiting for space

### Experiment 2: Buffer Underflow
```
Chefs: 1
Waiters: 5
Buffer: 5
```
**Result**: Waiters will frequently block (yellow) waiting for orders

### Experiment 3: Balanced System
```
Chefs: 3
Waiters: 3
Buffer: 10
Speed: 2.0x
```
**Result**: Smooth operation with minimal blocking

### Experiment 4: High Contention
```
Chefs: 8
Waiters: 8
Buffer: 5
Speed: 3.0x
```
**Result**: Lots of action! Watch threads compete for buffer access

## 📊 Understanding Statistics

| Metric | Meaning |
|--------|---------|
| **Orders Produced** | Total orders created by all chefs |
| **Orders Delivered** | Total orders delivered by all waiters |
| **Buffer Occupancy** | Current orders in buffer / Max capacity |
| **Active Threads** | Threads currently in RUNNING state |

## ❓ Common Questions

**Q: Why are threads yellow (WAITING)?**
A: They're blocked by semaphores:
- Chefs wait when buffer is FULL
- Waiters wait when buffer is EMPTY

**Q: What's the progress bar?**
A: Shows buffer occupancy percentage (how full the kitchen counter is)

**Q: Can I change settings while running?**
A: Speed can be adjusted anytime. For other settings, click RESET first.

**Q: What if it crashes?**
A: Check that Python 3.8+ is installed and tkinter is available:
```bash
python3 --version
python3 -c "import tkinter"
```

## 🎓 OS Concepts Quick Reference

| What You See | OS Concept |
|--------------|------------|
| Chefs | Producer Threads |
| Waiters | Consumer Threads |
| Kitchen Counter | Bounded Buffer |
| Yellow State | Semaphore Blocking |
| Buffer Slots | Shared Resource |
| Activity Log | Thread Events |

## 💡 Pro Tips

1. **Start Slow**: Use 0.5x speed to clearly see what's happening
2. **Watch States**: Focus on color changes to understand blocking
3. **Read Logs**: Activity log shows exactly what each thread is doing
4. **Pause Anytime**: Use PAUSE to freeze and examine the state
5. **Try Extremes**: Test with 1 chef & 10 waiters to see starvation

## 🆘 Need Help?

1. Read the full [README.md](README.md)
2. Check console output for error messages
3. Ensure all files are in the same directory
4. Verify Python version: `python3 --version`

## 🎉 Have Fun!

This is a learning tool - experiment, break things, and learn from it!

**Pro Challenge**: Try to achieve 100% buffer utilization with zero blocking. Is it possible? Why or why not?

---

**Need more info?** Check [README.md](README.md) for complete documentation.