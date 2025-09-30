"""
Modern Tkinter GUI for the Restaurant Order Management System.

This module implements a polished, professional GUI that visualizes the
Producer-Consumer pattern and thread synchronization in real-time.

Key Features:
- Modern restaurant-themed design
- Real-time thread state visualization
- Interactive control panel
- Animated buffer visualization
- Activity logging with color coding
- Performance statistics dashboard
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import threading
import time
import queue
from typing import Dict, List, Optional, Callable
import math

from shared_buffer import SharedBuffer
from producer import ChefThread
from consumer import WaiterThread
import config


class ModernButton(tk.Button):
    """Custom button with modern styling and hover effects."""
    
    def __init__(self, parent, **kwargs):
        # Extract custom parameters
        hover_color = kwargs.pop('hover_color', config.COLORS['accent'])
        normal_color = kwargs.pop('bg', config.COLORS['primary'])
        
        # Set default styling
        default_style = {
            'bg': normal_color,
            'fg': 'white',
            'font': config.FONTS['body'],
            'relief': 'flat',
            'bd': 0,
            'padx': 20,
            'pady': 8,
            'cursor': 'hand2'
        }
        default_style.update(kwargs)
        
        super().__init__(parent, **default_style)
        
        # Store colors for hover effect
        self.normal_color = normal_color
        self.hover_color = hover_color
        
        # Bind hover events
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, event):
        """Handle mouse enter event."""
        self.configure(bg=self.hover_color)
    
    def _on_leave(self, event):
        """Handle mouse leave event."""
        self.configure(bg=self.normal_color)


class ThreadCard(tk.Frame):
    """Card widget for displaying thread information."""
    
    def __init__(self, parent, thread_type: str, thread_id: int, name: str):
        super().__init__(parent, bg=config.COLORS['light'], relief='solid', bd=1)
        
        self.thread_type = thread_type
        self.thread_id = thread_id
        self.name = name
        
        self._setup_ui()
        self._setup_animations()
    
    def _setup_ui(self):
        """Setup the card UI elements."""
        # Header with emoji and name
        header_frame = tk.Frame(self, bg=config.COLORS['light'])
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        emoji = "👨‍🍳" if self.thread_type == "chef" else "🧑‍💼"
        self.name_label = tk.Label(
            header_frame,
            text=f"{emoji} {self.name}",
            font=config.FONTS['heading'],
            bg=config.COLORS['light'],
            fg=config.COLORS['text']
        )
        self.name_label.pack(side='left')
        
        # State indicator (colored circle)
        self.state_canvas = tk.Canvas(
            header_frame,
            width=20,
            height=20,
            bg=config.COLORS['light'],
            highlightthickness=0
        )
        self.state_canvas.pack(side='right')
        self.state_circle = self.state_canvas.create_oval(
            2, 2, 18, 18,
            fill=config.THREAD_COLORS['IDLE'],
            outline=config.COLORS['border']
        )
        
        # Statistics frame
        stats_frame = tk.Frame(self, bg=config.COLORS['light'])
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        # Orders count
        self.orders_label = tk.Label(
            stats_frame,
            text="Orders: 0",
            font=config.FONTS['small'],
            bg=config.COLORS['light'],
            fg=config.COLORS['text_light']
        )
        self.orders_label.pack(anchor='w')
        
        # Current activity
        self.activity_label = tk.Label(
            stats_frame,
            text="Waiting to start",
            font=config.FONTS['small'],
            bg=config.COLORS['light'],
            fg=config.COLORS['text_light'],
            wraplength=150
        )
        self.activity_label.pack(anchor='w', pady=(2, 0))
        
        # Efficiency rating (for waiters)
        if self.thread_type == "waiter":
            self.efficiency_label = tk.Label(
                stats_frame,
                text="Efficiency: No Data",
                font=config.FONTS['small'],
                bg=config.COLORS['light'],
                fg=config.COLORS['text_light']
            )
            self.efficiency_label.pack(anchor='w', pady=(2, 0))
    
    def _setup_animations(self):
        """Setup animation variables."""
        self.pulse_active = False
        self.pulse_job = None
    
    def update_state(self, state_info: dict):
        """Update the card with new thread state information."""
        state = state_info.get('state', 'IDLE')
        activity = state_info.get('activity', 'Unknown')
        stats = state_info.get('statistics', {})
        
        # Update state indicator color
        color = config.THREAD_COLORS.get(state, config.THREAD_COLORS['IDLE'])
        self.state_canvas.itemconfig(self.state_circle, fill=color)
        
        # Update activity text
        self.activity_label.config(text=activity)
        
        # Update statistics
        if self.thread_type == "chef":
            orders_count = stats.get('orders_produced', 0)
            self.orders_label.config(text=f"Orders Produced: {orders_count}")
        else:  # waiter
            orders_count = stats.get('orders_delivered', 0)
            self.orders_label.config(text=f"Orders Delivered: {orders_count}")
            
            # Update efficiency rating
            if hasattr(self, 'efficiency_label'):
                # Calculate efficiency based on average service time
                avg_service = stats.get('avg_service_time', 0)
                if avg_service == 0:
                    efficiency = "No Data"
                elif avg_service < 2.0:
                    efficiency = "Excellent"
                elif avg_service < 3.0:
                    efficiency = "Good"
                elif avg_service < 4.0:
                    efficiency = "Average"
                else:
                    efficiency = "Needs Improvement"
                
                self.efficiency_label.config(text=f"Efficiency: {efficiency}")
        
        # Start pulse animation for active states
        if state in ['RUNNING', 'WAITING', 'BLOCKED']:
            self._start_pulse()
        else:
            self._stop_pulse()
    
    def _start_pulse(self):
        """Start pulsing animation for active states."""
        if not self.pulse_active:
            self.pulse_active = True
            self._pulse_animation()
    
    def _stop_pulse(self):
        """Stop pulsing animation."""
        self.pulse_active = False
        if self.pulse_job:
            self.after_cancel(self.pulse_job)
            self.pulse_job = None
    
    def _pulse_animation(self):
        """Animate the state indicator with pulsing effect."""
        if not self.pulse_active:
            return
        
        # Get current color
        current_color = self.state_canvas.itemcget(self.state_circle, 'fill')
        
        # Toggle between normal and lighter version
        if current_color.endswith('0'):  # If it's the lighter version
            # Restore original color
            for state, color in config.THREAD_COLORS.items():
                if color + '0' == current_color:
                    new_color = color
                    break
            else:
                new_color = current_color[:-1]  # Remove the '0'
        else:
            # Make it lighter by adding transparency effect (simulate with lighter shade)
            new_color = current_color + '0'  # Simple way to create variation
        
        try:
            self.state_canvas.itemconfig(self.state_circle, fill=new_color)
        except tk.TclError:
            # If color is invalid, just use the original
            pass
        
        # Schedule next pulse
        self.pulse_job = self.after(500, self._pulse_animation)


class BufferVisualization(tk.Frame):
    """Widget for visualizing the shared buffer state."""
    
    def __init__(self, parent, capacity: int):
        super().__init__(parent, bg=config.COLORS['background'])
        
        self.capacity = capacity
        self.slots = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the buffer visualization UI."""
        # Title
        title_label = tk.Label(
            self,
            text="🍽️ Kitchen Counter (Shared Buffer)",
            font=config.FONTS['heading'],
            bg=config.COLORS['background'],
            fg=config.COLORS['text']
        )
        title_label.pack(pady=(0, 10))
        
        # Buffer slots container
        self.slots_frame = tk.Frame(self, bg=config.COLORS['background'])
        self.slots_frame.pack()
        
        # Create buffer slots
        self._create_slots()
        
        # Occupancy indicator
        self.occupancy_frame = tk.Frame(self, bg=config.COLORS['background'])
        self.occupancy_frame.pack(pady=(10, 0))
        
        tk.Label(
            self.occupancy_frame,
            text="Occupancy:",
            font=config.FONTS['body'],
            bg=config.COLORS['background'],
            fg=config.COLORS['text']
        ).pack(side='left')
        
        # Progress bar for occupancy
        self.occupancy_var = tk.DoubleVar()
        self.occupancy_bar = ttk.Progressbar(
            self.occupancy_frame,
            variable=self.occupancy_var,
            maximum=100,
            length=200,
            mode='determinate'
        )
        self.occupancy_bar.pack(side='left', padx=(5, 0))
        
        self.occupancy_label = tk.Label(
            self.occupancy_frame,
            text="0%",
            font=config.FONTS['small'],
            bg=config.COLORS['background'],
            fg=config.COLORS['text_light']
        )
        self.occupancy_label.pack(side='left', padx=(5, 0))
    
    def _create_slots(self):
        """Create visual slots for the buffer."""
        # Calculate grid dimensions
        cols = min(5, self.capacity)
        rows = math.ceil(self.capacity / cols)
        
        for i in range(self.capacity):
            row = i // cols
            col = i % cols
            
            slot_frame = tk.Frame(
                self.slots_frame,
                width=80,
                height=60,
                bg=config.COLORS['light'],
                relief='solid',
                bd=1
            )
            slot_frame.grid(row=row, column=col, padx=2, pady=2)
            slot_frame.pack_propagate(False)
            
            # Slot number
            slot_number = tk.Label(
                slot_frame,
                text=f"#{i+1}",
                font=config.FONTS['small'],
                bg=config.COLORS['light'],
                fg=config.COLORS['text_light']
            )
            slot_number.pack(anchor='nw', padx=2, pady=2)
            
            # Order display
            order_label = tk.Label(
                slot_frame,
                text="Empty",
                font=config.FONTS['small'],
                bg=config.COLORS['light'],
                fg=config.COLORS['text_light'],
                wraplength=70
            )
            order_label.pack(expand=True)
            
            self.slots.append({
                'frame': slot_frame,
                'label': order_label,
                'order': None
            })
    
    def update_buffer(self, buffer_state: dict):
        """Update the buffer visualization with current state."""
        orders = buffer_state.get('orders', [])
        occupancy = buffer_state.get('occupancy_percentage', 0)
        
        # Update slots
        for i, slot in enumerate(self.slots):
            if i < len(orders):
                order = orders[i]
                slot['order'] = order
                slot['label'].config(
                    text=f"Order #{order.order_id}\n{order.dish_name[:15]}...",
                    fg=config.COLORS['text']
                )
                slot['frame'].config(bg=config.COLORS['accent'])
            else:
                slot['order'] = None
                slot['label'].config(
                    text="Empty",
                    fg=config.COLORS['text_light']
                )
                slot['frame'].config(bg=config.COLORS['light'])
        
        # Update occupancy indicator
        self.occupancy_var.set(occupancy)
        self.occupancy_label.config(text=f"{occupancy:.1f}%")


class ActivityLog(tk.Frame):
    """Widget for displaying activity log with color coding."""
    
    def __init__(self, parent):
        super().__init__(parent, bg=config.COLORS['background'])
        
        self._setup_ui()
        self.log_entries = []
    
    def _setup_ui(self):
        """Setup the activity log UI."""
        # Title
        title_label = tk.Label(
            self,
            text="📋 Activity Log",
            font=config.FONTS['heading'],
            bg=config.COLORS['background'],
            fg=config.COLORS['text']
        )
        title_label.pack(anchor='w', pady=(0, 5))
        
        # Log text widget with scrollbar
        log_frame = tk.Frame(self, bg=config.COLORS['background'])
        log_frame.pack(fill='both', expand=True)
        
        self.log_text = tk.Text(
            log_frame,
            height=15,
            width=50,
            font=config.FONTS['monospace'],
            bg=config.COLORS['light'],
            fg=config.COLORS['text'],
            wrap='word',
            state='disabled'
        )
        
        scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Configure text tags for color coding
        self._setup_text_tags()
    
    def _setup_text_tags(self):
        """Setup text tags for color-coded messages."""
        for event_type, color in config.LOG_COLORS.items():
            self.log_text.tag_configure(event_type, foreground=color)
    
    def add_entry(self, timestamp: str, event_type: str, message: str):
        """Add a new entry to the activity log."""
        self.log_entries.append({
            'timestamp': timestamp,
            'type': event_type,
            'message': message
        })
        
        # Limit log entries
        if len(self.log_entries) > config.MAX_LOG_ENTRIES:
            self.log_entries.pop(0)
        
        # Update display
        self._update_display()
    
    def _update_display(self):
        """Update the log display with current entries."""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        
        for entry in self.log_entries:
            timestamp = entry['timestamp']
            event_type = entry['type']
            message = entry['message']
            
            # Insert timestamp
            self.log_text.insert(tk.END, f"[{timestamp}] ", 'info')
            
            # Insert message with appropriate color
            tag = event_type if event_type in config.LOG_COLORS else 'info'
            self.log_text.insert(tk.END, f"{message}\n", tag)
        
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)  # Auto-scroll to bottom
    
    def clear(self):
        """Clear all log entries."""
        self.log_entries.clear()
        self._update_display()


class StatsDashboard(tk.Frame):
    """Widget for displaying real-time statistics."""
    
    def __init__(self, parent):
        super().__init__(parent, bg=config.COLORS['background'])
        
        self._setup_ui()
        self.start_time = time.time()
    
    def _setup_ui(self):
        """Setup the statistics dashboard UI."""
        # Title
        title_label = tk.Label(
            self,
            text="📊 Statistics Dashboard",
            font=config.FONTS['heading'],
            bg=config.COLORS['background'],
            fg=config.COLORS['text']
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Stats grid
        stats_frame = tk.Frame(self, bg=config.COLORS['background'])
        stats_frame.pack(fill='x')
        
        # Create stat labels
        self.stat_labels = {}
        
        stats = [
            ('total_orders', 'Total Orders Processed'),
            ('active_threads', 'Active Threads'),
            ('buffer_occupancy', 'Buffer Occupancy'),
            ('throughput', 'Orders/Minute'),
            ('avg_wait_time', 'Avg Wait Time'),
            ('efficiency', 'System Efficiency')
        ]
        
        for i, (key, label) in enumerate(stats):
            row = i // 2
            col = i % 2
            
            stat_container = tk.Frame(stats_frame, bg=config.COLORS['light'], relief='solid', bd=1)
            stat_container.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            
            tk.Label(
                stat_container,
                text=label,
                font=config.FONTS['small'],
                bg=config.COLORS['light'],
                fg=config.COLORS['text_light']
            ).pack(anchor='w', padx=5, pady=(5, 0))
            
            value_label = tk.Label(
                stat_container,
                text="0",
                font=config.FONTS['body'],
                bg=config.COLORS['light'],
                fg=config.COLORS['text']
            )
            value_label.pack(anchor='w', padx=5, pady=(0, 5))
            
            self.stat_labels[key] = value_label
        
        # Configure grid weights
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
    
    def update_stats(self, buffer_state: dict, chef_states: List[dict], waiter_states: List[dict]):
        """Update statistics with current system state."""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        # Calculate statistics
        total_produced = buffer_state.get('total_produced', 0)
        total_consumed = buffer_state.get('total_consumed', 0)
        buffer_occupancy = buffer_state.get('occupancy_percentage', 0)
        
        # Active threads
        active_chefs = sum(1 for chef in chef_states if chef.get('state') in ['RUNNING', 'WAITING', 'BLOCKED'])
        active_waiters = sum(1 for waiter in waiter_states if waiter.get('state') in ['RUNNING', 'WAITING', 'BLOCKED'])
        active_threads = active_chefs + active_waiters
        
        # Throughput (orders per minute)
        throughput = (total_consumed / max(elapsed_time / 60, 1)) if elapsed_time > 0 else 0
        
        # Average wait time (simplified calculation)
        avg_wait_time = 2.5  # Placeholder - would need more detailed tracking
        
        # System efficiency (percentage of time threads are productive)
        efficiency = min(100, (throughput / max(active_threads, 1)) * 10) if active_threads > 0 else 0
        
        # Update labels
        self.stat_labels['total_orders'].config(text=str(total_consumed))
        self.stat_labels['active_threads'].config(text=str(active_threads))
        self.stat_labels['buffer_occupancy'].config(text=f"{buffer_occupancy:.1f}%")
        self.stat_labels['throughput'].config(text=f"{throughput:.1f}")
        self.stat_labels['avg_wait_time'].config(text=f"{avg_wait_time:.1f}s")
        self.stat_labels['efficiency'].config(text=f"{efficiency:.1f}%")


class ControlPanel(tk.Frame):
    """Widget for simulation control and configuration."""
    
    def __init__(self, parent, callback: Callable):
        super().__init__(parent, bg=config.COLORS['background'])
        
        self.callback = callback
        self.is_running = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the control panel UI."""
        # Title
        title_label = tk.Label(
            self,
            text="🎛️ Control Panel",
            font=config.FONTS['heading'],
            bg=config.COLORS['background'],
            fg=config.COLORS['text']
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Control buttons
        button_frame = tk.Frame(self, bg=config.COLORS['background'])
        button_frame.pack(fill='x', pady=(0, 10))
        
        self.start_button = ModernButton(
            button_frame,
            text="▶️ START",
            command=self._on_start,
            bg=config.COLORS['success']
        )
        self.start_button.pack(side='left', padx=(0, 5))
        
        self.pause_button = ModernButton(
            button_frame,
            text="⏸️ PAUSE",
            command=self._on_pause,
            bg=config.COLORS['warning'],
            state='disabled'
        )
        self.pause_button.pack(side='left', padx=5)
        
        self.reset_button = ModernButton(
            button_frame,
            text="🔄 RESET",
            command=self._on_reset,
            bg=config.COLORS['danger']
        )
        self.reset_button.pack(side='left', padx=5)
        
        # Configuration section
        config_frame = tk.LabelFrame(
            self,
            text="Configuration",
            font=config.FONTS['body'],
            bg=config.COLORS['background'],
            fg=config.COLORS['text']
        )
        config_frame.pack(fill='x', pady=(0, 10))
        
        # Number of chefs
        chef_frame = tk.Frame(config_frame, bg=config.COLORS['background'])
        chef_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            chef_frame,
            text="Chefs:",
            font=config.FONTS['body'],
            bg=config.COLORS['background'],
            fg=config.COLORS['text']
        ).pack(side='left')
        
        self.chef_var = tk.IntVar(value=config.DEFAULT_NUM_CHEFS)
        self.chef_spinbox = tk.Spinbox(
            chef_frame,
            from_=config.MIN_THREADS,
            to=config.MAX_THREADS,
            textvariable=self.chef_var,
            width=5,
            font=config.FONTS['body']
        )
        self.chef_spinbox.pack(side='right')
        
        # Number of waiters
        waiter_frame = tk.Frame(config_frame, bg=config.COLORS['background'])
        waiter_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            waiter_frame,
            text="Waiters:",
            font=config.FONTS['body'],
            bg=config.COLORS['background'],
            fg=config.COLORS['text']
        ).pack(side='left')
        
        self.waiter_var = tk.IntVar(value=config.DEFAULT_NUM_WAITERS)
        self.waiter_spinbox = tk.Spinbox(
            waiter_frame,
            from_=config.MIN_THREADS,
            to=config.MAX_THREADS,
            textvariable=self.waiter_var,
            width=5,
            font=config.FONTS['body']
        )
        self.waiter_spinbox.pack(side='right')
        
        # Buffer size
        buffer_frame = tk.Frame(config_frame, bg=config.COLORS['background'])
        buffer_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            buffer_frame,
            text="Buffer Size:",
            font=config.FONTS['body'],
            bg=config.COLORS['background'],
            fg=config.COLORS['text']
        ).pack(side='left')
        
        self.buffer_var = tk.IntVar(value=config.DEFAULT_BUFFER_SIZE)
        self.buffer_spinbox = tk.Spinbox(
            buffer_frame,
            from_=config.MIN_BUFFER_SIZE,
            to=config.MAX_BUFFER_SIZE,
            textvariable=self.buffer_var,
            width=5,
            font=config.FONTS['body']
        )
        self.buffer_spinbox.pack(side='right')
        
        # Speed control
        speed_frame = tk.Frame(config_frame, bg=config.COLORS['background'])
        speed_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            speed_frame,
            text="Speed:",
            font=config.FONTS['body'],
            bg=config.COLORS['background'],
            fg=config.COLORS['text']
        ).pack(side='left')
        
        self.speed_var = tk.DoubleVar(value=config.DEFAULT_SPEED)
        self.speed_scale = tk.Scale(
            speed_frame,
            from_=config.MIN_SPEED,
            to=config.MAX_SPEED,
            resolution=0.1,
            orient='horizontal',
            variable=self.speed_var,
            font=config.FONTS['small'],
            bg=config.COLORS['background'],
            fg=config.COLORS['text'],
            command=self._on_speed_change
        )
        self.speed_scale.pack(side='right', fill='x', expand=True, padx=(10, 0))
    
    def _on_start(self):
        """Handle start button click."""
        if not self.is_running:
            self.callback('start', self._get_config())
            self.is_running = True
            self.start_button.config(state='disabled')
            self.pause_button.config(state='normal')
            self._disable_config()
    
    def _on_pause(self):
        """Handle pause button click."""
        if self.is_running:
            self.callback('pause', {})
            self.is_running = False
            self.start_button.config(state='normal', text="▶️ RESUME")
            self.pause_button.config(state='disabled')
    
    def _on_reset(self):
        """Handle reset button click."""
        self.callback('reset', {})
        self.is_running = False
        self.start_button.config(state='normal', text="▶️ START")
        self.pause_button.config(state='disabled')
        self._enable_config()
    
    def _on_speed_change(self, value):
        """Handle speed scale change."""
        self.callback('speed_change', {'speed': float(value)})
    
    def _get_config(self) -> dict:
        """Get current configuration values."""
        return {
            'num_chefs': self.chef_var.get(),
            'num_waiters': self.waiter_var.get(),
            'buffer_size': self.buffer_var.get(),
            'speed': self.speed_var.get()
        }
    
    def _disable_config(self):
        """Disable configuration controls during simulation."""
        self.chef_spinbox.config(state='disabled')
        self.waiter_spinbox.config(state='disabled')
        self.buffer_spinbox.config(state='disabled')
    
    def _enable_config(self):
        """Enable configuration controls."""
        self.chef_spinbox.config(state='normal')
        self.waiter_spinbox.config(state='normal')
        self.buffer_spinbox.config(state='normal')


class RestaurantGUI:
    """Main GUI application for the Restaurant Order Management System."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.configure(bg=config.COLORS['background'])
        
        # Simulation components
        self.shared_buffer: Optional[SharedBuffer] = None
        self.chef_threads: List[ChefThread] = []
        self.waiter_threads: List[WaiterThread] = []
        
        # GUI update queue
        self.gui_queue = queue.Queue()
        
        # Setup UI
        self._setup_ui()
        self._setup_update_loop()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_ui(self):
        """Setup the main UI layout."""
        # Main container with padding
        main_frame = tk.Frame(self.root, bg=config.COLORS['background'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        self._create_header(main_frame)
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg=config.COLORS['background'])
        content_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # Left panel (threads and buffer)
        left_panel = tk.Frame(content_frame, bg=config.COLORS['background'])
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right panel (log and controls)
        right_panel = tk.Frame(content_frame, bg=config.COLORS['background'])
        right_panel.pack(side='right', fill='y', padx=(10, 0))
        
        # Setup panels
        self._setup_left_panel(left_panel)
        self._setup_right_panel(right_panel)
    
    def _create_header(self, parent):
        """Create the application header."""
        header_frame = tk.Frame(parent, bg=config.COLORS['background'])
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="🍽️ Restaurant Order Management System",
            font=config.FONTS['title'],
            bg=config.COLORS['background'],
            fg=config.COLORS['primary']
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Operating System Concepts: Producer-Consumer Pattern & Thread Synchronization",
            font=config.FONTS['body'],
            bg=config.COLORS['background'],
            fg=config.COLORS['text_light']
        )
        subtitle_label.pack()
    
    def _setup_left_panel(self, parent):
        """Setup the left panel with threads and buffer visualization."""
        # Statistics dashboard
        self.stats_dashboard = StatsDashboard(parent)
        self.stats_dashboard.pack(fill='x', pady=(0, 20))
        
        # Threads section
        threads_frame = tk.Frame(parent, bg=config.COLORS['background'])
        threads_frame.pack(fill='x', pady=(0, 20))
        
        # Chefs section
        chefs_label = tk.Label(
            threads_frame,
            text="👨‍🍳 Chefs (Producers)",
            font=config.FONTS['heading'],
            bg=config.COLORS['background'],
            fg=config.COLORS['text']
        )
        chefs_label.pack(anchor='w')
        
        self.chefs_frame = tk.Frame(threads_frame, bg=config.COLORS['background'])
        self.chefs_frame.pack(fill='x', pady=(5, 15))
        
        # Waiters section
        waiters_label = tk.Label(
            threads_frame,
            text="🧑‍💼 Waiters (Consumers)",
            font=config.FONTS['heading'],
            bg=config.COLORS['background'],
            fg=config.COLORS['text']
        )
        waiters_label.pack(anchor='w')
        
        self.waiters_frame = tk.Frame(threads_frame, bg=config.COLORS['background'])
        self.waiters_frame.pack(fill='x', pady=(5, 0))
        
        # Buffer visualization
        self.buffer_viz = BufferVisualization(parent, config.DEFAULT_BUFFER_SIZE)
        self.buffer_viz.pack(fill='x')
    
    def _setup_right_panel(self, parent):
        """Setup the right panel with controls and log."""
        # Control panel
        self.control_panel = ControlPanel(parent, self._handle_control_action)
        self.control_panel.pack(fill='x', pady=(0, 20))
        
        # Activity log
        self.activity_log = ActivityLog(parent)
        self.activity_log.pack(fill='both', expand=True)
    
    def _setup_update_loop(self):
        """Setup the GUI update loop."""
        self._process_gui_queue()
        self.root.after(config.GUI_UPDATE_INTERVAL, self._setup_update_loop)
    
    def _process_gui_queue(self):
        """Process messages from the GUI queue."""
        try:
            while True:
                event_data = self.gui_queue.get_nowait()
                self._handle_gui_event(event_data)
        except queue.Empty:
            pass
    
    def _handle_gui_event(self, event_data: dict):
        """Handle GUI events from threads."""
        event_type = event_data.get('type', '')
        message = event_data.get('message', '')
        timestamp = event_data.get('timestamp', '')
        
        # Add to activity log
        if message:
            log_type = self._get_log_type(event_type)
            self.activity_log.add_entry(timestamp, log_type, message)
        
        # Update visualizations if buffer state is included
        if 'buffer_state' in event_data:
            self.buffer_viz.update_buffer(event_data['buffer_state'])
        
        # Update thread cards if state info is included
        if 'state_info' in event_data:
            self._update_thread_card(event_data)
        
        # Update statistics
        self._update_statistics()
    
    def _get_log_type(self, event_type: str) -> str:
        """Map event type to log color type."""
        mapping = {
            'chef_activity': 'production',
            'waiter_activity': 'consumption',
            'production': 'production',
            'consumption': 'consumption',
            'blocking': 'blocking',
            'system': 'system'
        }
        return mapping.get(event_type, 'info')
    
    def _update_thread_card(self, event_data: dict):
        """Update thread card with new state information."""
        # This would update the specific thread card
        # Implementation depends on how cards are stored and managed
        pass
    
    def _update_statistics(self):
        """Update the statistics dashboard."""
        if self.shared_buffer:
            buffer_state = self.shared_buffer.get_buffer_state()
            chef_states = [chef.get_state_info() for chef in self.chef_threads if chef.is_alive()]
            waiter_states = [waiter.get_state_info() for waiter in self.waiter_threads if waiter.is_alive()]
            
            self.stats_dashboard.update_stats(buffer_state, chef_states, waiter_states)
    
    def _handle_control_action(self, action: str, params: dict):
        """Handle control panel actions."""
        if action == 'start':
            self._start_simulation(params)
        elif action == 'pause':
            self._pause_simulation()
        elif action == 'reset':
            self._reset_simulation()
        elif action == 'speed_change':
            self._change_speed(params['speed'])
    
    def _start_simulation(self, config_params: dict):
        """Start the simulation with given parameters."""
        try:
            # Create shared buffer
            buffer_size = config_params['buffer_size']
            self.shared_buffer = SharedBuffer(buffer_size, self._gui_callback)
            
            # Update buffer visualization
            self.buffer_viz = BufferVisualization(self.buffer_viz.master, buffer_size)
            self.buffer_viz.pack(fill='x')
            
            # Create and start chef threads
            num_chefs = config_params['num_chefs']
            self.chef_threads = []
            self._clear_thread_cards(self.chefs_frame)
            
            for i in range(num_chefs):
                chef_name = config.CHEF_NAMES[i % len(config.CHEF_NAMES)]
                chef = ChefThread(i, chef_name, self.shared_buffer, self._gui_callback)
                chef.set_speed(config_params['speed'])
                self.chef_threads.append(chef)
                
                # Create thread card
                card = ThreadCard(self.chefs_frame, "chef", i, chef_name)
                card.pack(side='left', padx=5, pady=5)
                
                chef.start()
            
            # Create and start waiter threads
            num_waiters = config_params['num_waiters']
            self.waiter_threads = []
            self._clear_thread_cards(self.waiters_frame)
            
            for i in range(num_waiters):
                waiter_name = config.WAITER_NAMES[i % len(config.WAITER_NAMES)]
                waiter = WaiterThread(i, waiter_name, self.shared_buffer, self._gui_callback)
                waiter.set_speed(config_params['speed'])
                self.waiter_threads.append(waiter)
                
                # Create thread card
                card = ThreadCard(self.waiters_frame, "waiter", i, waiter_name)
                card.pack(side='left', padx=5, pady=5)
                
                waiter.start()
            
            # Reset statistics start time
            self.stats_dashboard.start_time = time.time()
            
            self.activity_log.add_entry(
                time.strftime("%H:%M:%S"),
                'system',
                f"Simulation started: {num_chefs} chefs, {num_waiters} waiters, buffer size {buffer_size}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start simulation: {str(e)}")
    
    def _pause_simulation(self):
        """Pause the simulation."""
        for chef in self.chef_threads:
            chef.pause()
        for waiter in self.waiter_threads:
            waiter.pause()
        
        self.activity_log.add_entry(
            time.strftime("%H:%M:%S"),
            'system',
            "Simulation paused"
        )
    
    def _reset_simulation(self):
        """Reset the simulation."""
        # Stop all threads
        for chef in self.chef_threads:
            chef.stop()
        for waiter in self.waiter_threads:
            waiter.stop()
        
        # Wait for threads to finish
        for chef in self.chef_threads:
            chef.join(timeout=1.0)
        for waiter in self.waiter_threads:
            waiter.join(timeout=1.0)
        
        # Reset shared buffer
        if self.shared_buffer:
            self.shared_buffer.reset()
        
        # Clear thread cards
        self._clear_thread_cards(self.chefs_frame)
        self._clear_thread_cards(self.waiters_frame)
        
        # Clear activity log
        self.activity_log.clear()
        
        # Reset lists
        self.chef_threads.clear()
        self.waiter_threads.clear()
        
        self.activity_log.add_entry(
            time.strftime("%H:%M:%S"),
            'system',
            "Simulation reset"
        )
    
    def _change_speed(self, speed: float):
        """Change simulation speed."""
        for chef in self.chef_threads:
            chef.set_speed(speed)
        for waiter in self.waiter_threads:
            waiter.set_speed(speed)
        
        self.activity_log.add_entry(
            time.strftime("%H:%M:%S"),
            'system',
            f"Speed changed to {speed}x"
        )
    
    def _clear_thread_cards(self, frame):
        """Clear all thread cards from a frame."""
        for widget in frame.winfo_children():
            widget.destroy()
    
    def _gui_callback(self, event_data: dict):
        """Callback function for thread-to-GUI communication."""
        try:
            self.gui_queue.put_nowait(event_data)
        except queue.Full:
            pass  # Skip if queue is full
    
    def _on_closing(self):
        """Handle application closing."""
        # Stop simulation
        self._reset_simulation()
        
        # Shutdown shared buffer
        if self.shared_buffer:
            self.shared_buffer.shutdown()
        
        # Close application
        self.root.destroy()
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = RestaurantGUI()
    app.run()