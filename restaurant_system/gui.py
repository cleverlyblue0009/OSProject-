"""
Modern Tkinter GUI for Restaurant Order Management System

This module implements a polished, professional graphical user interface
that visualizes the producer-consumer problem in real-time.

Key Features:
- Real-time thread state visualization
- Animated buffer updates
- Color-coded status indicators
- Activity logging
- Simulation controls
- Performance metrics
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import queue
import threading
from typing import Dict, List, Optional
from datetime import datetime

import config
import utils
from shared_buffer import SharedBuffer
from producer import Chef
from consumer import Waiter


class RestaurantGUI:
    """
    Main GUI class for the restaurant order management system.
    
    This class creates and manages all GUI elements, handles user interactions,
    and updates displays based on thread activity.
    """
    
    def __init__(self, root: tk.Tk):
        """Initialize the GUI."""
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.configure(bg=config.COLOR_BACKGROUND)
        
        # Simulation components
        self.shared_buffer: Optional[SharedBuffer] = None
        self.chefs: List[Chef] = []
        self.waiters: List[Waiter] = []
        self.is_running = False
        self.is_paused = False
        self.speed_multiplier = config.DEFAULT_SPEED_MULTIPLIER
        
        # Thread-safe communication queue
        # OS Concept: Queue for thread-safe communication between worker threads and GUI thread
        self.update_queue = queue.Queue()
        
        # GUI element references
        self.chef_cards: Dict[int, Dict] = {}
        self.waiter_cards: Dict[int, Dict] = {}
        self.buffer_slots: List[tk.Label] = []
        
        # Build the GUI
        self._create_gui()
        
        # Start GUI update loop
        self._schedule_gui_update()
    
    def _create_gui(self) -> None:
        """Create all GUI elements."""
        # Main container with padding
        main_frame = tk.Frame(self.root, bg=config.COLOR_BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=config.PADDING_LARGE, pady=config.PADDING_LARGE)
        
        # Header
        self._create_header(main_frame)
        
        # Content area (scrollable)
        canvas = tk.Canvas(main_frame, bg=config.COLOR_BACKGROUND, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=config.COLOR_BACKGROUND)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Content sections
        self._create_statistics_panel(scrollable_frame)
        self._create_chef_section(scrollable_frame)
        self._create_buffer_section(scrollable_frame)
        self._create_waiter_section(scrollable_frame)
        self._create_log_section(scrollable_frame)
        self._create_control_panel(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_header(self, parent: tk.Frame) -> None:
        """Create the header section."""
        header_frame = tk.Frame(parent, bg=config.COLOR_PRIMARY, relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, config.PADDING_LARGE))
        
        title_label = tk.Label(
            header_frame,
            text="🍽️ Restaurant Order Management System",
            font=config.FONT_HEADER,
            bg=config.COLOR_PRIMARY,
            fg="white",
            pady=config.PADDING_MEDIUM
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Operating System Concepts: Producer-Consumer Problem with Semaphores",
            font=config.FONT_SMALL,
            bg=config.COLOR_PRIMARY,
            fg="white",
            pady=(0, config.PADDING_SMALL)
        )
        subtitle_label.pack()
    
    def _create_statistics_panel(self, parent: tk.Frame) -> None:
        """Create the statistics dashboard."""
        stats_frame = tk.Frame(parent, bg=config.COLOR_PANEL, relief=tk.RAISED, bd=2)
        stats_frame.pack(fill=tk.X, pady=(0, config.PADDING_MEDIUM))
        
        tk.Label(
            stats_frame,
            text="📊 Real-Time Statistics",
            font=config.FONT_TITLE,
            bg=config.COLOR_PANEL,
            fg=config.COLOR_PRIMARY
        ).pack(pady=config.PADDING_SMALL)
        
        # Stats container
        stats_container = tk.Frame(stats_frame, bg=config.COLOR_PANEL)
        stats_container.pack(fill=tk.X, padx=config.PADDING_MEDIUM, pady=config.PADDING_SMALL)
        
        # Orders produced
        self.stats_produced_label = self._create_stat_box(
            stats_container, "Orders Produced", "0", 0
        )
        
        # Orders consumed
        self.stats_consumed_label = self._create_stat_box(
            stats_container, "Orders Delivered", "0", 1
        )
        
        # Buffer occupancy
        self.stats_buffer_label = self._create_stat_box(
            stats_container, "Buffer Occupancy", "0/0", 2
        )
        
        # Active threads
        self.stats_threads_label = self._create_stat_box(
            stats_container, "Active Threads", "0", 3
        )
        
        # Buffer occupancy progress bar
        self.buffer_progress = ttk.Progressbar(
            stats_frame,
            mode='determinate',
            length=400
        )
        self.buffer_progress.pack(pady=config.PADDING_SMALL)
    
    def _create_stat_box(self, parent: tk.Frame, label: str, value: str, column: int) -> tk.Label:
        """Create a statistics box."""
        box = tk.Frame(parent, bg=utils.lighten_color(config.COLOR_ACCENT, 0.5), relief=tk.RAISED, bd=2)
        box.grid(row=0, column=column, padx=config.PADDING_SMALL, sticky="ew")
        parent.columnconfigure(column, weight=1)
        
        tk.Label(
            box,
            text=label,
            font=config.FONT_SMALL,
            bg=utils.lighten_color(config.COLOR_ACCENT, 0.5),
            fg=config.COLOR_TEXT
        ).pack(pady=(config.PADDING_SMALL, 0))
        
        value_label = tk.Label(
            box,
            text=value,
            font=config.FONT_TITLE,
            bg=utils.lighten_color(config.COLOR_ACCENT, 0.5),
            fg=config.COLOR_PRIMARY
        )
        value_label.pack(pady=(0, config.PADDING_SMALL))
        
        return value_label
    
    def _create_chef_section(self, parent: tk.Frame) -> None:
        """Create the chef section."""
        chef_frame = tk.Frame(parent, bg=config.COLOR_PANEL, relief=tk.RAISED, bd=2)
        chef_frame.pack(fill=tk.X, pady=(0, config.PADDING_MEDIUM))
        
        tk.Label(
            chef_frame,
            text="👨‍🍳 Chefs (Producers)",
            font=config.FONT_TITLE,
            bg=config.COLOR_PANEL,
            fg=config.COLOR_PRIMARY
        ).pack(pady=config.PADDING_SMALL)
        
        self.chef_container = tk.Frame(chef_frame, bg=config.COLOR_PANEL)
        self.chef_container.pack(fill=tk.X, padx=config.PADDING_MEDIUM, pady=config.PADDING_SMALL)
    
    def _create_waiter_section(self, parent: tk.Frame) -> None:
        """Create the waiter section."""
        waiter_frame = tk.Frame(parent, bg=config.COLOR_PANEL, relief=tk.RAISED, bd=2)
        waiter_frame.pack(fill=tk.X, pady=(0, config.PADDING_MEDIUM))
        
        tk.Label(
            waiter_frame,
            text="🧑‍💼 Waiters (Consumers)",
            font=config.FONT_TITLE,
            bg=config.COLOR_PANEL,
            fg=config.COLOR_PRIMARY
        ).pack(pady=config.PADDING_SMALL)
        
        self.waiter_container = tk.Frame(waiter_frame, bg=config.COLOR_PANEL)
        self.waiter_container.pack(fill=tk.X, padx=config.PADDING_MEDIUM, pady=config.PADDING_SMALL)
    
    def _create_buffer_section(self, parent: tk.Frame) -> None:
        """Create the buffer visualization section."""
        buffer_frame = tk.Frame(parent, bg=config.COLOR_PANEL, relief=tk.RAISED, bd=2)
        buffer_frame.pack(fill=tk.X, pady=(0, config.PADDING_MEDIUM))
        
        tk.Label(
            buffer_frame,
            text="🍽️ Kitchen Counter (Shared Buffer)",
            font=config.FONT_TITLE,
            bg=config.COLOR_PANEL,
            fg=config.COLOR_PRIMARY
        ).pack(pady=config.PADDING_SMALL)
        
        self.buffer_container = tk.Frame(buffer_frame, bg=config.COLOR_PANEL)
        self.buffer_container.pack(fill=tk.X, padx=config.PADDING_MEDIUM, pady=config.PADDING_MEDIUM)
    
    def _create_log_section(self, parent: tk.Frame) -> None:
        """Create the activity log section."""
        log_frame = tk.Frame(parent, bg=config.COLOR_PANEL, relief=tk.RAISED, bd=2)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, config.PADDING_MEDIUM))
        
        tk.Label(
            log_frame,
            text="📋 Activity Log",
            font=config.FONT_TITLE,
            bg=config.COLOR_PANEL,
            fg=config.COLOR_PRIMARY
        ).pack(pady=config.PADDING_SMALL)
        
        # Create scrolled text widget for logs
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            width=100,
            font=config.FONT_LOG,
            bg="#F8F9FA",
            fg=config.COLOR_TEXT,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(padx=config.PADDING_MEDIUM, pady=config.PADDING_SMALL, fill=tk.BOTH, expand=True)
        
        # Configure tags for colored text
        self.log_text.tag_config("INFO", foreground=config.COLOR_LOG_INFO)
        self.log_text.tag_config("WARNING", foreground=config.COLOR_LOG_BLOCKING)
        self.log_text.tag_config("ERROR", foreground=config.COLOR_LOG_BLOCKING, font=config.FONT_LOG + ("bold",))
        self.log_text.tag_config("PRODUCTION", foreground=config.COLOR_LOG_PRODUCTION)
        self.log_text.tag_config("CONSUMPTION", foreground=config.COLOR_LOG_CONSUMPTION)
    
    def _create_control_panel(self, parent: tk.Frame) -> None:
        """Create the control panel."""
        control_frame = tk.Frame(parent, bg=config.COLOR_PANEL, relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X)
        
        tk.Label(
            control_frame,
            text="🎮 Simulation Controls",
            font=config.FONT_TITLE,
            bg=config.COLOR_PANEL,
            fg=config.COLOR_PRIMARY
        ).pack(pady=config.PADDING_SMALL)
        
        # Button container
        button_frame = tk.Frame(control_frame, bg=config.COLOR_PANEL)
        button_frame.pack(pady=config.PADDING_SMALL)
        
        # Start/Pause button
        self.start_button = tk.Button(
            button_frame,
            text="▶️ START",
            command=self._toggle_simulation,
            bg=config.COLOR_RUNNING,
            fg="white",
            font=config.FONT_BODY,
            padx=20,
            pady=10,
            relief=tk.RAISED,
            bd=3
        )
        self.start_button.pack(side=tk.LEFT, padx=config.PADDING_SMALL)
        
        # Reset button
        reset_button = tk.Button(
            button_frame,
            text="🔄 RESET",
            command=self._reset_simulation,
            bg=config.COLOR_BLOCKED,
            fg="white",
            font=config.FONT_BODY,
            padx=20,
            pady=10,
            relief=tk.RAISED,
            bd=3
        )
        reset_button.pack(side=tk.LEFT, padx=config.PADDING_SMALL)
        
        # Configuration frame
        config_frame = tk.Frame(control_frame, bg=config.COLOR_PANEL)
        config_frame.pack(pady=config.PADDING_MEDIUM, padx=config.PADDING_LARGE, fill=tk.X)
        
        # Number of chefs
        self._create_spinbox(config_frame, "Number of Chefs:", 0, 1, config.MAX_THREADS, config.DEFAULT_NUM_CHEFS, "num_chefs")
        
        # Number of waiters
        self._create_spinbox(config_frame, "Number of Waiters:", 1, 1, config.MAX_THREADS, config.DEFAULT_NUM_WAITERS, "num_waiters")
        
        # Buffer size
        self._create_spinbox(config_frame, "Buffer Size:", 2, config.MIN_BUFFER_SIZE, config.MAX_BUFFER_SIZE, config.DEFAULT_BUFFER_SIZE, "buffer_size")
        
        # Speed slider
        speed_frame = tk.Frame(config_frame, bg=config.COLOR_PANEL)
        speed_frame.grid(row=3, column=0, columnspan=2, pady=config.PADDING_SMALL, sticky="ew")
        
        tk.Label(
            speed_frame,
            text="Simulation Speed:",
            font=config.FONT_BODY,
            bg=config.COLOR_PANEL,
            fg=config.COLOR_TEXT
        ).pack(side=tk.LEFT, padx=config.PADDING_SMALL)
        
        self.speed_var = tk.DoubleVar(value=config.DEFAULT_SPEED_MULTIPLIER)
        self.speed_slider = tk.Scale(
            speed_frame,
            from_=config.MIN_SPEED_MULTIPLIER,
            to=config.MAX_SPEED_MULTIPLIER,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            command=self._update_speed,
            bg=config.COLOR_PANEL,
            font=config.FONT_SMALL,
            length=200
        )
        self.speed_slider.pack(side=tk.LEFT, padx=config.PADDING_SMALL)
        
        self.speed_label = tk.Label(
            speed_frame,
            text=f"{config.DEFAULT_SPEED_MULTIPLIER:.1f}x",
            font=config.FONT_BODY,
            bg=config.COLOR_PANEL,
            fg=config.COLOR_TEXT,
            width=5
        )
        self.speed_label.pack(side=tk.LEFT)
    
    def _create_spinbox(self, parent: tk.Frame, label: str, row: int, from_: int, to: int, default: int, attr_name: str) -> None:
        """Create a labeled spinbox."""
        tk.Label(
            parent,
            text=label,
            font=config.FONT_BODY,
            bg=config.COLOR_PANEL,
            fg=config.COLOR_TEXT
        ).grid(row=row, column=0, sticky="e", padx=config.PADDING_SMALL, pady=config.PADDING_SMALL)
        
        spinbox = tk.Spinbox(
            parent,
            from_=from_,
            to=to,
            font=config.FONT_BODY,
            width=10
        )
        spinbox.delete(0, tk.END)
        spinbox.insert(0, default)
        spinbox.grid(row=row, column=1, sticky="w", padx=config.PADDING_SMALL, pady=config.PADDING_SMALL)
        
        setattr(self, attr_name + "_spinbox", spinbox)
    
    def _create_thread_card(self, parent: tk.Frame, thread_id: int, name: str, thread_type: str, column: int) -> Dict:
        """Create a visual card for a thread."""
        card = tk.Frame(
            parent,
            bg=utils.lighten_color(config.COLOR_ACCENT, 0.6),
            relief=tk.RAISED,
            bd=3,
            padx=config.PADDING_MEDIUM,
            pady=config.PADDING_MEDIUM
        )
        card.grid(row=0, column=column, padx=config.PADDING_SMALL, pady=config.PADDING_SMALL, sticky="nsew")
        parent.columnconfigure(column, weight=1)
        
        # Name
        name_label = tk.Label(
            card,
            text=name,
            font=config.FONT_TITLE,
            bg=utils.lighten_color(config.COLOR_ACCENT, 0.6),
            fg=config.COLOR_TEXT
        )
        name_label.pack()
        
        # State indicator (colored circle)
        state_canvas = tk.Canvas(card, width=30, height=30, bg=utils.lighten_color(config.COLOR_ACCENT, 0.6), highlightthickness=0)
        state_canvas.pack(pady=config.PADDING_SMALL)
        state_indicator = state_canvas.create_oval(5, 5, 25, 25, fill=config.COLOR_IDLE, outline="")
        
        # State text
        state_label = tk.Label(
            card,
            text="IDLE",
            font=config.FONT_SMALL,
            bg=utils.lighten_color(config.COLOR_ACCENT, 0.6),
            fg=config.COLOR_TEXT
        )
        state_label.pack()
        
        # Count
        count_label = tk.Label(
            card,
            text="0 orders",
            font=config.FONT_BODY,
            bg=utils.lighten_color(config.COLOR_ACCENT, 0.6),
            fg=config.COLOR_TEXT
        )
        count_label.pack(pady=config.PADDING_SMALL)
        
        # Action
        action_label = tk.Label(
            card,
            text="Idle",
            font=config.FONT_SMALL,
            bg=utils.lighten_color(config.COLOR_ACCENT, 0.6),
            fg=config.COLOR_TEXT_LIGHT,
            wraplength=150
        )
        action_label.pack()
        
        return {
            'card': card,
            'state_canvas': state_canvas,
            'state_indicator': state_indicator,
            'state_label': state_label,
            'count_label': count_label,
            'action_label': action_label
        }
    
    def _create_buffer_slot(self, parent: tk.Frame, index: int) -> tk.Label:
        """Create a visual slot for the buffer."""
        slot = tk.Label(
            parent,
            text="Empty",
            font=config.FONT_SMALL,
            bg="white",
            fg=config.COLOR_TEXT_LIGHT,
            relief=tk.SUNKEN,
            bd=2,
            width=12,
            height=3
        )
        slot.grid(row=index // 5, column=index % 5, padx=config.PADDING_SMALL, pady=config.PADDING_SMALL)
        return slot
    
    def _toggle_simulation(self) -> None:
        """Start or pause the simulation."""
        if not self.is_running:
            self._start_simulation()
        else:
            self._pause_resume_simulation()
    
    def _start_simulation(self) -> None:
        """Start the simulation."""
        # Get configuration values
        num_chefs = int(self.num_chefs_spinbox.get())
        num_waiters = int(self.num_waiters_spinbox.get())
        buffer_size = int(self.buffer_size_spinbox.get())
        
        # Validate
        num_chefs = utils.validate_config_value(num_chefs, config.MIN_THREADS, config.MAX_THREADS, config.DEFAULT_NUM_CHEFS)
        num_waiters = utils.validate_config_value(num_waiters, config.MIN_THREADS, config.MAX_THREADS, config.DEFAULT_NUM_WAITERS)
        buffer_size = utils.validate_config_value(buffer_size, config.MIN_BUFFER_SIZE, config.MAX_BUFFER_SIZE, config.DEFAULT_BUFFER_SIZE)
        
        # Create shared buffer
        self.shared_buffer = SharedBuffer(buffer_size)
        
        # Clear existing cards
        for widget in self.chef_container.winfo_children():
            widget.destroy()
        for widget in self.waiter_container.winfo_children():
            widget.destroy()
        for widget in self.buffer_container.winfo_children():
            widget.destroy()
        
        self.chef_cards.clear()
        self.waiter_cards.clear()
        self.buffer_slots.clear()
        
        # Create chef threads and cards
        for i in range(num_chefs):
            name = config.CHEF_NAMES[i % len(config.CHEF_NAMES)]
            chef = Chef(i, name, self.shared_buffer, self._thread_callback, self.speed_multiplier)
            self.chefs.append(chef)
            card = self._create_thread_card(self.chef_container, i, name, "chef", i)
            self.chef_cards[i] = card
        
        # Create waiter threads and cards
        for i in range(num_waiters):
            name = config.WAITER_NAMES[i % len(config.WAITER_NAMES)]
            waiter = Waiter(i, name, self.shared_buffer, self._thread_callback, self.speed_multiplier)
            self.waiters.append(waiter)
            card = self._create_thread_card(self.waiter_container, i, name, "waiter", i)
            self.waiter_cards[i] = card
        
        # Create buffer slots
        for i in range(buffer_size):
            slot = self._create_buffer_slot(self.buffer_container, i)
            self.buffer_slots.append(slot)
        
        # Start all threads
        for chef in self.chefs:
            chef.start()
        for waiter in self.waiters:
            waiter.start()
        
        self.is_running = True
        self.is_paused = False
        self.start_button.config(text="⏸️ PAUSE", bg=config.COLOR_WAITING)
        
        self._log_message("🎬 Simulation started!", "INFO")
    
    def _pause_resume_simulation(self) -> None:
        """Pause or resume the simulation."""
        if self.is_paused:
            # Resume
            for chef in self.chefs:
                chef.resume()
            for waiter in self.waiters:
                waiter.resume()
            self.is_paused = False
            self.start_button.config(text="⏸️ PAUSE", bg=config.COLOR_WAITING)
            self._log_message("▶️ Simulation resumed", "INFO")
        else:
            # Pause
            for chef in self.chefs:
                chef.pause()
            for waiter in self.waiters:
                waiter.pause()
            self.is_paused = True
            self.start_button.config(text="▶️ RESUME", bg=config.COLOR_RUNNING)
            self._log_message("⏸️ Simulation paused", "INFO")
    
    def _reset_simulation(self) -> None:
        """Reset the simulation."""
        # Stop all threads
        for chef in self.chefs:
            chef.stop()
        for waiter in self.waiters:
            waiter.stop()
        
        # Wait for threads to finish
        for chef in self.chefs:
            chef.join(timeout=2.0)
        for waiter in self.waiters:
            waiter.join(timeout=2.0)
        
        self.chefs.clear()
        self.waiters.clear()
        self.shared_buffer = None
        self.is_running = False
        self.is_paused = False
        
        # Clear UI
        for widget in self.chef_container.winfo_children():
            widget.destroy()
        for widget in self.waiter_container.winfo_children():
            widget.destroy()
        for widget in self.buffer_container.winfo_children():
            widget.destroy()
        
        self.chef_cards.clear()
        self.waiter_cards.clear()
        self.buffer_slots.clear()
        
        # Reset button
        self.start_button.config(text="▶️ START", bg=config.COLOR_RUNNING)
        
        # Clear log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Reset statistics
        self._update_statistics(0, 0, 0, 0, 0)
        
        self._log_message("🔄 Simulation reset", "INFO")
    
    def _update_speed(self, value: str) -> None:
        """Update simulation speed."""
        self.speed_multiplier = float(value)
        self.speed_label.config(text=f"{self.speed_multiplier:.1f}x")
        
        # Update all threads
        for chef in self.chefs:
            chef.update_speed(self.speed_multiplier)
        for waiter in self.waiters:
            waiter.update_speed(self.speed_multiplier)
    
    def _thread_callback(self, event_type: str, thread_id: int, *args) -> None:
        """
        Callback for thread events (called from worker threads).
        
        OS Concept: Thread-safe communication using queue.
        Worker threads cannot directly update GUI (Tkinter is not thread-safe).
        Instead, they put events in a queue that the GUI thread processes.
        """
        self.update_queue.put((event_type, thread_id, args))
    
    def _schedule_gui_update(self) -> None:
        """Schedule periodic GUI updates."""
        self._process_update_queue()
        self._update_display()
        self.root.after(config.GUI_UPDATE_INTERVAL, self._schedule_gui_update)
    
    def _process_update_queue(self) -> None:
        """Process all pending updates from worker threads."""
        try:
            while True:
                event_type, thread_id, args = self.update_queue.get_nowait()
                
                if event_type == 'log':
                    message = args[0]
                    level = args[1] if len(args) > 1 else "INFO"
                    self._log_message(message, level)
                
                elif event_type == 'state_change':
                    state = args[0]
                    self._update_thread_state(thread_id, state)
                
                elif event_type == 'action_change':
                    action = args[0]
                    self._update_thread_action(thread_id, action)
        
        except queue.Empty:
            pass
    
    def _update_display(self) -> None:
        """Update all visual elements."""
        if not self.shared_buffer:
            return
        
        # Update buffer visualization
        orders = self.shared_buffer.get_orders_snapshot()
        for i, slot in enumerate(self.buffer_slots):
            if i < len(orders):
                order = orders[i]
                slot.config(
                    text=f"#{order.order_id}\n{order.dish_name[:10]}...",
                    bg=utils.lighten_color(config.COLOR_ACCENT, 0.4),
                    fg=config.COLOR_TEXT
                )
            else:
                slot.config(text="Empty", bg="white", fg=config.COLOR_TEXT_LIGHT)
        
        # Update statistics
        stats = self.shared_buffer.get_statistics()
        active_threads = sum(1 for chef in self.chefs if chef.get_state() == "RUNNING") + \
                        sum(1 for waiter in self.waiters if waiter.get_state() == "RUNNING")
        
        self._update_statistics(
            stats['total_produced'],
            stats['total_consumed'],
            stats['current_size'],
            stats['capacity'],
            active_threads
        )
        
        # Update thread cards
        for i, chef in enumerate(self.chefs):
            if i in self.chef_cards:
                card = self.chef_cards[i]
                card['count_label'].config(text=f"{chef.get_orders_produced()} orders")
                card['action_label'].config(text=chef.get_current_action())
        
        for i, waiter in enumerate(self.waiters):
            if i in self.waiter_cards:
                card = self.waiter_cards[i]
                card['count_label'].config(text=f"{waiter.get_orders_delivered()} orders")
                card['action_label'].config(text=waiter.get_current_action())
    
    def _update_statistics(self, produced: int, consumed: int, buffer_size: int, capacity: int, active_threads: int) -> None:
        """Update statistics display."""
        self.stats_produced_label.config(text=utils.format_number(produced))
        self.stats_consumed_label.config(text=utils.format_number(consumed))
        self.stats_buffer_label.config(text=f"{buffer_size}/{capacity}")
        self.stats_threads_label.config(text=str(active_threads))
        
        # Update progress bar
        if capacity > 0:
            self.buffer_progress['maximum'] = capacity
            self.buffer_progress['value'] = buffer_size
    
    def _update_thread_state(self, thread_id: int, state: str) -> None:
        """Update thread state visualization."""
        color = utils.get_state_color(state)
        
        # Check if it's a chef or waiter
        if thread_id in self.chef_cards:
            card = self.chef_cards[thread_id]
            card['state_canvas'].itemconfig(card['state_indicator'], fill=color)
            card['state_label'].config(text=state)
        elif thread_id in self.waiter_cards:
            card = self.waiter_cards[thread_id]
            card['state_canvas'].itemconfig(card['state_indicator'], fill=color)
            card['state_label'].config(text=state)
    
    def _update_thread_action(self, thread_id: int, action: str) -> None:
        """Update thread action text."""
        if thread_id in self.chef_cards:
            card = self.chef_cards[thread_id]
            card['action_label'].config(text=action)
        elif thread_id in self.waiter_cards:
            card = self.waiter_cards[thread_id]
            card['action_label'].config(text=action)
    
    def _log_message(self, message: str, level: str = "INFO") -> None:
        """Add a message to the activity log."""
        timestamp = utils.format_timestamp()
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, formatted_message, level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Limit log size
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > config.MAX_LOG_ENTRIES:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, f"{lines - config.MAX_LOG_ENTRIES}.0")
            self.log_text.config(state=tk.DISABLED)


def run_gui() -> None:
    """Create and run the GUI."""
    root = tk.Tk()
    app = RestaurantGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()