"""
Main application GUI for the Mano basic computer simulator.

This module builds a Tkinter GUI that combines the datapath visualisation
from gui.datapath_view with additional panels showing the micro–operation
trace, control signal timeline and register value waveforms.  Buttons allow
the user to step through individual cycles, execute whole instructions or
run the program until it halts.  The GUI automatically updates all views
after each simulator action.

The application is intentionally lightweight and self–contained.  It makes
no assumptions about external frameworks and uses only the standard library.
"""

from __future__ import annotations

import tkinter as tk
from typing import Dict, List, Tuple

from simulator.machine import Machine
from gui.datapath_view import DatapathView


class ControlTimelineView(tk.Frame):
    """Display a digital timeline of control signal values over cycles."""

    def __init__(
        self,
        master: tk.Widget,
        signals: List[str],
        max_cycles: int = 50,
    ) -> None:
        super().__init__(master)
        self.signals = signals
        self.max_cycles = max_cycles
        # Each element in self.data is a dict mapping signal names to 0/1
        self.data: List[Dict[str, int]] = []
        self.row_h = 20
        self.col_w = 10
        self.label_w = 60
        width = self.label_w + self.col_w * self.max_cycles
        height = self.row_h * len(self.signals) + 10
        self.canvas = tk.Canvas(
            self, width=width, height=height, bg="white"
        )
        self.canvas.pack(fill="both", expand=True)
        # Draw the initial blank grid
        self._draw()

    def update_signals(self, cycle_signals: Dict[str, int]) -> None:
        """Append a new cycle's control signals and redraw the timeline."""
        # Normalize unknown signals to 0
        entry = {sig: cycle_signals.get(sig, 0) for sig in self.signals}
        self.data.append(entry)
        if len(self.data) > self.max_cycles:
            self.data.pop(0)
        self._draw()

    def _draw(self) -> None:
        """Render the entire timeline from scratch."""
        self.canvas.delete("all")
        # Draw row backgrounds and labels
        for row, sig in enumerate(self.signals):
            y = row * self.row_h + 5
            # Label text
            self.canvas.create_text(
                5,
                y + self.row_h / 2,
                text=sig,
                anchor="w",
                font=("Helvetica", 8, "bold"),
            )
            # Draw horizontal line separating rows
            self.canvas.create_line(
                0,
                y + self.row_h,
                self.label_w + self.col_w * self.max_cycles,
                y + self.row_h,
                fill="lightgray",
            )
        # Draw vertical lines for each cycle position
        total_width = self.col_w * self.max_cycles
        for i in range(self.max_cycles + 1):
            x = self.label_w + i * self.col_w
            self.canvas.create_line(
                x,
                5,
                x,
                5 + self.row_h * len(self.signals),
                fill="lightgray",
            )
        # Draw high/low rectangles for each recorded cycle
        for row, sig in enumerate(self.signals):
            y = row * self.row_h + 5
            for i, entry in enumerate(self.data):
                x = self.label_w + i * self.col_w
                val = entry.get(sig, 0)
                fill = "green" if val else "white"
                # Surround with a border for readability
                self.canvas.create_rectangle(
                    x,
                    y,
                    x + self.col_w,
                    y + self.row_h,
                    fill=fill,
                    outline="gray",
                )


class WaveformView(tk.Frame):
    """Plot numeric register values over time as simple waveforms."""

    def __init__(
        self,
        master: tk.Widget,
        regs: List[str],
        max_cycles: int = 50,
    ) -> None:
        super().__init__(master)
        self.regs = regs
        self.max_cycles = max_cycles
        # Data for each register: list of integers
        self.data: Dict[str, List[int]] = {r: [] for r in regs}
        self.row_h = 50
        self.col_w = 10
        self.label_w = 60
        width = self.label_w + self.col_w * self.max_cycles
        height = self.row_h * len(self.regs)
        self.canvas = tk.Canvas(
            self, width=width, height=height, bg="white"
        )
        self.canvas.pack(fill="both", expand=True)
        # Predefine colours for registers
        self.colours: Dict[str, str] = {
            "AC": "#d62728",  # reddish
            "DR": "#2ca02c",  # green
            "AR": "#1f77b4",  # blue
            "PC": "#ff7f0e",  # orange
            "IR": "#9467bd",  # purple
            "TR": "#8c564b",  # brown
        }
        self._draw()

    def update_values(self, values: Dict[str, int]) -> None:
        """Append a new sample of register values and redraw the waveforms."""
        for reg in self.regs:
            self.data[reg].append(values.get(reg, 0))
            if len(self.data[reg]) > self.max_cycles:
                self.data[reg].pop(0)
        self._draw()

    def _draw(self) -> None:
        """Render the waveforms from scratch."""
        self.canvas.delete("all")
        for row, reg in enumerate(self.regs):
            y_base = row * self.row_h
            # Label
            self.canvas.create_text(
                5,
                y_base + 10,
                text=reg,
                anchor="nw",
                font=("Helvetica", 8, "bold"),
            )
            # Draw horizontal midline for zero reference
            mid_y = y_base + self.row_h - 10
            self.canvas.create_line(
                self.label_w,
                mid_y,
                self.label_w + self.col_w * self.max_cycles,
                mid_y,
                fill="lightgray",
                dash=(2, 4),
            )
            values = self.data.get(reg, [])
            if not values:
                continue
            # Determine scaling based on bit width: 16-bit regs up to 0xFFFF, 12-bit up to 0xFFF.
            max_val = 0xFFFF if reg in ["AC", "DR", "IR", "TR"] else 0xFFF
            # vertical range for waveform (upper margin 15px, lower margin 10px)
            wave_h = self.row_h - 25
            # Draw a step line: for each segment, draw horizontal then vertical lines.
            for i, val in enumerate(values):
                # Normalise value to [0,1]
                norm = val / max_val if max_val else 0
                # y coordinate: invert so higher values appear near top of row
                y_val = y_base + 5 + wave_h * (1 - norm)
                x_val = self.label_w + i * self.col_w + self.col_w / 2
                # For the first point just store coordinates
                if i == 0:
                    prev_x, prev_y = x_val, y_val
                    continue
                # Draw horizontal line from previous x to current x at previous y
                self.canvas.create_line(
                    prev_x,
                    prev_y,
                    x_val,
                    prev_y,
                    fill=self.colours.get(reg, "black"),
                    width=2,
                )
                # Draw vertical jump to new value
                self.canvas.create_line(
                    x_val,
                    prev_y,
                    x_val,
                    y_val,
                    fill=self.colours.get(reg, "black"),
                    width=2,
                )
                prev_x, prev_y = x_val, y_val


class MainApp:
    """Encapsulates the entire GUI and simulator control logic."""

    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.title("Mano Basic Computer Simulator")

        # Instantiate the machine and load the default program and data
        self.machine = Machine()
        try:
            # Try loading program and data from the default relative path
            self.machine.load_program_and_data(
                prog_file="data/program.txt", data_file="data/data.txt"
            )
        except Exception:
            # Fallback to absolute path if executed outside repository root
            self.machine.load_program_and_data(
                prog_file="/home/oai/share/Mano_Simulator-hisham/data/program.txt",
                data_file="/home/oai/share/Mano_Simulator-hisham/data/data.txt",
            )

        # Keep track of the cycle number for timeline indexing
        self.cycle_counter = 0

        # Layout frames: left side for datapath, right side for controls and info
        self.left_frame = tk.Frame(self.master)
        self.left_frame.pack(side="left", fill="both", expand=False)
        self.right_frame = tk.Frame(self.master)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Datapath view
        self.datapath_view = DatapathView(self.left_frame, self.machine)
        self.datapath_view.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        # Control and info panels stacked vertically on the right
        self.controls_frame = tk.Frame(self.right_frame)
        self.controls_frame.pack(side="top", fill="x", pady=5)
        self.timeline_frame = tk.Frame(self.right_frame)
        self.timeline_frame.pack(side="top", fill="x", pady=5)
        self.waveform_frame = tk.Frame(self.right_frame)
        self.waveform_frame.pack(side="top", fill="x", pady=5)
        self.trace_frame = tk.Frame(self.right_frame)
        self.trace_frame.pack(side="top", fill="both", expand=True, pady=5)

        # Buttons for stepping and running
        btn_next_cycle = tk.Button(
            self.controls_frame,
            text="Next Cycle",
            command=self._on_next_cycle,
            width=12,
        )
        btn_next_inst = tk.Button(
            self.controls_frame,
            text="Next Instruction",
            command=self._on_next_instruction,
            width=15,
        )
        btn_run = tk.Button(
            self.controls_frame,
            text="Run Until Halt",
            command=self._on_run_until_halt,
            width=15,
        )
        btn_reset = tk.Button(
            self.controls_frame,
            text="Reset",
            command=self._on_reset,
            width=8,
        )
        btn_next_cycle.grid(row=0, column=0, padx=2)
        btn_next_inst.grid(row=0, column=1, padx=2)
        btn_run.grid(row=0, column=2, padx=2)
        btn_reset.grid(row=0, column=3, padx=2)

        # Define the list of control signals we track for the timeline
        self.signals = ["IR_load", "PC_inc", "READ", "WRITE", "ALU_op"]
        self.timeline_view = ControlTimelineView(self.timeline_frame, self.signals)
        self.timeline_view.pack(side="top", fill="x", expand=True)

        # Define which registers to show in the waveform
        self.regs = ["AC", "DR", "AR", "PC", "IR", "TR"]
        self.waveform_view = WaveformView(self.waveform_frame, self.regs)
        self.waveform_view.pack(side="top", fill="x", expand=True)

        # Micro-op trace list
        self.trace_list = tk.Listbox(
            self.trace_frame,
            height=15,
            width=50,
            font=("Helvetica", 9),
        )
        self.trace_list.pack(side="left", fill="both", expand=True)
        self.trace_scroll = tk.Scrollbar(self.trace_frame, orient="vertical")
        self.trace_scroll.pack(side="right", fill="y")
        self.trace_list.config(yscrollcommand=self.trace_scroll.set)
        self.trace_scroll.config(command=self.trace_list.yview)
        self.trace_list.bind("<<ListboxSelect>>", self._on_trace_select)

        # Initial sample for waveform and timeline (before any cycles)
        self._record_cycle(
            micro_op="Initial state",
            changed=[],
            cycle_signals={sig: 0 for sig in self.signals},
        )

    # ------------------------------------------------------------------
    # Simulation step handlers
    # ------------------------------------------------------------------
    def _record_cycle(
        self,
        micro_op: str,
        changed: List[str],
        cycle_signals: Dict[str, int],
    ) -> None:
        """Record a cycle: update the datapath view, timeline, waveform and trace."""
        # Append micro-operation to trace
        self.trace_list.insert(tk.END, f"{self.cycle_counter:03d}: {micro_op}")
        # Scroll the list to show the latest entry
        self.trace_list.yview_moveto(1.0)
        # Highlight changed components
        self.datapath_view.highlight_components(changed)
        # Highlight the path implied by the micro-op
        self.datapath_view.highlight_by_micro_op(micro_op)
        # Update control timeline
        self.timeline_view.update_signals(cycle_signals)
        # Update waveform values
        reg_values = {reg: getattr(self.machine, reg).value for reg in self.regs}
        self.waveform_view.update_values(reg_values)
        self.cycle_counter += 1

    def _compute_signals(self, micro: str, changed: List[str]) -> Dict[str, int]:
        """Derive which control signals are active based on the micro-op text."""
        signals = {sig: 0 for sig in self.signals}
        # Extract descriptor after colon
        if ":" in micro:
            _, desc = micro.split(":", 1)
        else:
            desc = micro
        desc = desc.strip()
        if not desc or "←" not in desc:
            return signals
        # Consider only first comma-separated operation
        op = desc.split(",")[0].strip()
        left, right = op.split("←", 1)
        dest = left.strip()
        expr = right.strip()
        # Memory read
        if "M[" in expr and not dest.startswith("M["):
            signals["READ"] = 1
        # Memory write
        if dest.startswith("M["):
            signals["WRITE"] = 1
        # IR load
        if dest.startswith("IR"):
            signals["IR_load"] = 1
        # PC increment
        if dest.startswith("PC") and "+" in expr:
            signals["PC_inc"] = 1
        # ALU operation: detect logical or arithmetic ops
        if any(op_symbol in expr for op_symbol in ["∧", "+", "-", "∨"]):
            signals["ALU_op"] = 1
        return signals

    def _on_next_cycle(self) -> None:
        """Handle the 'Next Cycle' button click."""
        # Step one cycle
        micro_op, changed = self.machine.step_cycle()
        # Determine which of the changed items correspond to visual components
        vis_changed = [c for c in changed if c in self.datapath_view.components]
        # Compute the control signals for this micro-op
        cycle_signals = self._compute_signals(micro_op, vis_changed)
        # Record the cycle in all views
        self._record_cycle(micro_op, vis_changed, cycle_signals)

    def _on_next_instruction(self) -> None:
        """Handle the 'Next Instruction' button click."""
        # If halted, do nothing
        if self.machine.S.value == 0:
            return
        # Continue stepping cycles until an instruction finishes
        while True:
            micro_op, changed = self.machine.step_cycle()
            vis_changed = [c for c in changed if c in self.datapath_view.components]
            cycle_signals = self._compute_signals(micro_op, vis_changed)
            self._record_cycle(micro_op, vis_changed, cycle_signals)
            # Break if machine halted or sequence counter reset (new instruction)
            if self.machine.S.value == 0 or self.machine.SC.value == 0:
                break
            # Update the GUI to remain responsive during long instructions
            self.master.update_idletasks()

    def _on_run_until_halt(self) -> None:
        """Handle the 'Run Until Halt' button click."""
        # Run repeatedly until halt; update UI after each cycle
        while self.machine.S.value != 0:
            micro_op, changed = self.machine.step_cycle()
            vis_changed = [c for c in changed if c in self.datapath_view.components]
            cycle_signals = self._compute_signals(micro_op, vis_changed)
            self._record_cycle(micro_op, vis_changed, cycle_signals)
            # Break if halted within step_cycle (HLT sets S=0)
            if self.machine.S.value == 0:
                break
            # Break the loop every 500 cycles to give Tk event loop a chance to
            # process user events (avoids freezing UI on long runs)
            if (self.cycle_counter % 500) == 0:
                self.master.update_idletasks()

    def _on_reset(self) -> None:
        """Handle the 'Reset' button click."""
        # Reload the program and data, reset profiler counters
        self.machine.load_program_and_data(
            prog_file="data/program.txt", data_file="data/data.txt"
        )
        self.cycle_counter = 0
        # Clear views
        self.trace_list.delete(0, tk.END)
        self.timeline_view.data.clear()
        self.timeline_view._draw()
        self.waveform_view.data = {reg: [] for reg in self.regs}
        self.waveform_view._draw()
        # Reset write counts in datapath view
        for comp in self.datapath_view.components.values():
            comp["writes"] = 0
            self.datapath_view.canvas.itemconfigure(comp["count_id"], text="0")
            # Also reset colours
            self.datapath_view.canvas.itemconfigure(comp["rect_id"], fill="lightgray")
        # Insert initial state into trace
        self._record_cycle(
            micro_op="Reset state",
            changed=[],
            cycle_signals={sig: 0 for sig in self.signals},
        )

    def _on_trace_select(self, event: tk.Event) -> None:
        """When the user selects a micro-op in the trace, highlight its path."""
        selection = self.trace_list.curselection()
        if not selection:
            return
        index = selection[0]
        item_text = self.trace_list.get(index)
        # Extract micro-op part after the cycle number
        try:
            _, micro_op = item_text.split(":", 1)
        except ValueError:
            micro_op = item_text
        micro_op = micro_op.strip()
        # Highlight the corresponding path
        self.datapath_view.highlight_by_micro_op(micro_op)


def run_gui() -> None:
    """Entry point to launch the GUI application."""
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()