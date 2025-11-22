"""
Datapath view for the Mano basic computer simulator.

This module defines a Tkinter based visualization of Mano's Basic Computer
datapath.  A canvas is used to draw the various registers, the common bus,
the memory block, and the ALU.  Registers flash when they are written to
and track a running count of writes.  Hovering the mouse over a register
shows a tooltip displaying its current value in both hexadecimal and signed
decimal form.  When the simulator executes a micro–operation that moves
data between components the wires involved briefly highlight and an arrow is
drawn indicating the direction of transfer.

The view does not drive the simulator itself; instead a Machine instance
should be provided and external code should call the `highlight_components`
and `highlight_by_micro_op` methods when appropriate.  See gui/app.py for
integration details.
"""

from __future__ import annotations

import tkinter as tk
from typing import Dict, List, Optional, Tuple

# Import the Machine type for type hints; the simulator is only used by
# clients of this view.  Import inside type checking guard to avoid
# circular imports at runtime.
try:
    from simulator.machine import Machine
except Exception:
    Machine = object  # type: ignore


class DatapathView(tk.Frame):
    """A graphical representation of Mano's Basic Computer datapath.

    Parameters
    ----------
    master : tk.Widget
        Parent widget.
    machine : Machine
        Simulator machine instance providing register values.
    width : int, optional
        Width of the canvas in pixels.
    height : int, optional
        Height of the canvas in pixels.
    bus_y : int, optional
        Y coordinate of the common bus within the canvas.
    """

    def __init__(
        self,
        master: tk.Widget,
        machine: Machine,
        *,
        width: int = 700,
        height: int = 350,
        bus_y: int = 250,
    ) -> None:
        super().__init__(master)
        self.machine = machine
        self.canvas = tk.Canvas(self, width=width, height=height, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.bus_y = bus_y
        # Dictionary storing widget info per component.  Each entry maps
        # component name (e.g. "AC") to a dictionary with keys:
        #   rect_id: canvas rectangle id
        #   label_id: canvas text id for the component name
        #   count_id: canvas text id for the write count
        #   pos: (x, y, w, h) bounding box
        #   writes: integer count of writes
        self.components: Dict[str, Dict[str, object]] = {}

        # Keep track of an optional tooltip item id so it can be removed.
        self._tooltip: Optional[int] = None

        # Bus line id so it can be recoloured for highlights.
        self.bus_id: Optional[int] = None

        # Id of the temporary arrow drawn during path highlighting.
        self._arrow_id: Optional[int] = None

        # Draw the static datapath diagram.
        self._draw_static_elements()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def _draw_static_elements(self) -> None:
        """Create the register boxes, bus, memory and ALU shapes."""
        # Define register positions (x, y) and dimensions.
        # All registers have uniform size.
        reg_w, reg_h = 90, 40
        coords: Dict[str, Tuple[int, int]] = {
            "AR": (50, 50),
            "PC": (50, 120),
            "IR": (170, 50),
            "TR": (170, 120),
            "DR": (290, 50),
            "AC": (290, 120),
        }

        # Draw bus line first so it appears beneath other elements.
        self.bus_id = self.canvas.create_line(
            40, self.bus_y, 640, self.bus_y, fill="gray", width=4
        )

        # Create each register box, label, and vertical connection to the bus.
        for name, (x, y) in coords.items():
            rect = self.canvas.create_rectangle(
                x,
                y,
                x + reg_w,
                y + reg_h,
                fill="lightgray",
                outline="black",
            )
            label = self.canvas.create_text(
                x + reg_w / 2,
                y + reg_h / 2,
                text=name,
                font=("Helvetica", 11, "bold"),
            )
            # Write count displayed in the top right of each register box.
            count_id = self.canvas.create_text(
                x + reg_w - 3,
                y + 3,
                text="0",
                font=("Helvetica", 8),
                fill="blue",
                anchor="ne",
            )
            # Draw a vertical line from the bottom centre of the register
            # down to the bus.
            cx = x + reg_w / 2
            cy = y + reg_h
            self.canvas.create_line(
                cx,
                cy,
                cx,
                self.bus_y,
                fill="gray",
                width=2,
            )
            # Store component metadata.
            self.components[name] = {
                "rect_id": rect,
                "label_id": label,
                "count_id": count_id,
                "pos": (x, y, reg_w, reg_h),
                "writes": 0,
            }
            # Bind tooltip events on the rectangle and its label.
            self.canvas.tag_bind(
                rect,
                "<Enter>",
                lambda e, n=name: self._show_tooltip(e, n),
            )
            self.canvas.tag_bind(
                rect,
                "<Leave>",
                lambda e: self._hide_tooltip(),
            )
            self.canvas.tag_bind(
                label,
                "<Enter>",
                lambda e, n=name: self._show_tooltip(e, n),
            )
            self.canvas.tag_bind(
                label,
                "<Leave>",
                lambda e: self._hide_tooltip(),
            )

        # Draw Memory block.  Its size is larger than registers to suggest a
        # bank of words.
        mem_x, mem_y, mem_w, mem_h = 420, 80, 140, 160
        mem_rect = self.canvas.create_rectangle(
            mem_x,
            mem_y,
            mem_x + mem_w,
            mem_y + mem_h,
            fill="lightgray",
            outline="black",
        )
        mem_label = self.canvas.create_text(
            mem_x + mem_w / 2,
            mem_y + 15,
            text="MEM",
            font=("Helvetica", 11, "bold"),
        )
        mem_count_id = self.canvas.create_text(
            mem_x + mem_w - 3,
            mem_y + 3,
            text="0",
            font=("Helvetica", 8),
            fill="blue",
            anchor="ne",
        )
        # Connect memory to the bus via a vertical and horizontal line.
        # The horizontal bus line already reaches near memory.  Draw a
        # vertical line from bus up to the centre of memory.
        mem_cx = mem_x  # attach from left side of memory
        mem_cy = mem_y + mem_h / 2
        # vertical line to bus
        self.canvas.create_line(
            mem_cx,
            mem_cy,
            mem_cx,
            self.bus_y,
            fill="gray",
            width=2,
        )
        # horizontal small stub from bus to align with memory side
        self.canvas.create_line(
            mem_cx,
            self.bus_y,
            640,
            self.bus_y,
            fill="gray",
            width=4,
        )
        # Store memory metadata under key 'MEM'
        self.components["MEM"] = {
            "rect_id": mem_rect,
            "label_id": mem_label,
            "count_id": mem_count_id,
            "pos": (mem_x, mem_y, mem_w, mem_h),
            "writes": 0,
        }
        self.canvas.tag_bind(
            mem_rect,
            "<Enter>",
            lambda e, n="MEM": self._show_tooltip(e, n),
        )
        self.canvas.tag_bind(
            mem_rect,
            "<Leave>",
            lambda e: self._hide_tooltip(),
        )

        # Draw the ALU.  The ALU sits between the AC and DR registers.
        alu_w, alu_h = 60, 40
        alu_x, alu_y = 290 + reg_w + 10, 120  # right of AC
        alu_rect = self.canvas.create_rectangle(
            alu_x,
            alu_y,
            alu_x + alu_w,
            alu_y + alu_h,
            fill="lightgray",
            outline="black",
        )
        alu_label = self.canvas.create_text(
            alu_x + alu_w / 2,
            alu_y + alu_h / 2,
            text="ALU",
            font=("Helvetica", 11, "bold"),
        )
        alu_count_id = self.canvas.create_text(
            alu_x + alu_w - 3,
            alu_y + 3,
            text="0",
            font=("Helvetica", 8),
            fill="blue",
            anchor="ne",
        )
        self.components["ALU"] = {
            "rect_id": alu_rect,
            "label_id": alu_label,
            "count_id": alu_count_id,
            "pos": (alu_x, alu_y, alu_w, alu_h),
            "writes": 0,
        }
        self.canvas.tag_bind(
            alu_rect,
            "<Enter>",
            lambda e, n="ALU": self._show_tooltip(e, n),
        )
        self.canvas.tag_bind(
            alu_rect,
            "<Leave>",
            lambda e: self._hide_tooltip(),
        )

    # ------------------------------------------------------------------
    # Tooltip handling
    # ------------------------------------------------------------------
    def _show_tooltip(self, event: tk.Event, name: str) -> None:
        """Display a tooltip near the mouse pointer with register contents."""
        # Destroy any existing tooltip
        self._hide_tooltip()
        # Only registers have meaningful values; memory shows number of accesses
        if name == "MEM":
            value_hex = "--"
            value_signed = "--"
        elif name == "ALU":
            # The ALU doesn't hold state; show description instead.
            value_hex = "ALU"
            value_signed = ""
        else:
            # Fetch register value from the machine.
            val: int = getattr(self.machine, name).value  # type: ignore
            # Determine bit width: AC, DR, IR, TR are 16-bit; AR, PC are 12-bit.
            bits = 16 if name in ["AC", "DR", "IR", "TR"] else 12
            max_val = 1 << (bits - 1)
            # Signed conversion using two's complement
            if val >= max_val:
                signed_val = val - (1 << bits)
            else:
                signed_val = val
            value_hex = f"0x{val:0{bits // 4}X}"
            value_signed = str(signed_val)
        text = f"{name}: {value_hex}\nSigned: {value_signed}"
        # Create a small label on the canvas near the pointer.  Use a
        # rectangle with text for better visibility.
        x = event.x + 10
        y = event.y + 10
        padding = 4
        # measure text lines
        font = ("Helvetica", 9)
        # Create the text item off-screen to measure its bbox.
        temp_id = self.canvas.create_text(x, y, text=text, font=font, anchor="nw")
        bbox = self.canvas.bbox(temp_id)
        if bbox is None:
            width = 60
            height = 30
        else:
            x0, y0, x1, y1 = bbox
            width = x1 - x0
            height = y1 - y0
        # Remove the temporary text
        self.canvas.delete(temp_id)
        # Draw the background rectangle for tooltip
        rect_id = self.canvas.create_rectangle(
            x - padding,
            y - padding,
            x + width + padding,
            y + height + padding,
            fill="lightyellow",
            outline="black",
            tags=("tooltip",),
        )
        text_id = self.canvas.create_text(
            x,
            y,
            text=text,
            font=font,
            anchor="nw",
            tags=("tooltip",),
        )
        # Store the tooltip ids so they can be removed later
        self._tooltip = rect_id  # we will delete by tag

    def _hide_tooltip(self) -> None:
        """Remove any existing tooltip from the canvas."""
        # Delete both background and text by tag
        self.canvas.delete("tooltip")
        self._tooltip = None

    # ------------------------------------------------------------------
    # Highlighting
    # ------------------------------------------------------------------
    def highlight_components(self, changed: List[str]) -> None:
        """Flash registers and memory blocks that were written this cycle.

        Parameters
        ----------
        changed : list of str
            A list of component names that were updated on the last cycle.
        """
        for name in changed:
            if name not in self.components:
                # Skip flags or memory indices like M[123]
                continue
            comp = self.components[name]
            rect_id = comp["rect_id"]
            # Increment write count
            comp["writes"] += 1
            # Update the count text
            self.canvas.itemconfigure(comp["count_id"], text=str(comp["writes"]))
            # Change fill colour temporarily
            self.canvas.itemconfigure(rect_id, fill="yellow")
            # Schedule revert to default colour after 350ms
            def revert_color(rid=rect_id):
                # Revert to lightgray only if still highlighted
                self.canvas.itemconfigure(rid, fill="lightgray")
            self.canvas.after(350, revert_color)

    def _clear_previous_arrow(self) -> None:
        """Remove any previously drawn arrow and restore bus colour."""
        if self._arrow_id is not None:
            self.canvas.delete(self._arrow_id)
            self._arrow_id = None
        # Restore bus colour
        if self.bus_id is not None:
            self.canvas.itemconfigure(self.bus_id, fill="gray")

    def _draw_arrow(self, src: str, dest: str) -> None:
        """Draw a red arrow from the centre of the source to the centre of dest.

        Parameters
        ----------
        src : str
            Name of the source component.
        dest : str
            Name of the destination component.
        """
        # Compute centre coordinates for source and destination
        def centre_of(name: str) -> Tuple[float, float]:
            comp = self.components.get(name)
            if not comp:
                return 0.0, 0.0
            x, y, w, h = comp["pos"]
            return x + w / 2, y + h / 2

        x1, y1 = centre_of(src)
        x2, y2 = centre_of(dest)
        # Draw arrow
        self._arrow_id = self.canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            fill="red",
            width=3,
            arrow=tk.LAST,
            smooth=True,
        )
        # Highlight bus
        if self.bus_id is not None:
            self.canvas.itemconfigure(self.bus_id, fill="red")
        # Remove arrow after a short duration
        def remove_arrow():
            if self._arrow_id is not None:
                self.canvas.delete(self._arrow_id)
                self._arrow_id = None
            if self.bus_id is not None:
                self.canvas.itemconfigure(self.bus_id, fill="gray")
        self.canvas.after(350, remove_arrow)

    def highlight_by_micro_op(self, micro: str) -> None:
        """Parse a micro–operation string and highlight the corresponding path.

        The micro–operation is expected to be in the format returned by
        `Machine.step_cycle()` or `Machine.step_instruction()`, e.g.
        ``"T1: IR ← M[AR], PC ← PC + 1"`` or ``"T4: DR ← M[AR]"``.

        Only simple transfers between a single source and destination are
        visualised.  Memory read and write operations are mapped to the
        component "MEM".  Arithmetic operations involving the ALU cause
        the ALU block to flash but no arrow is drawn since internal
        datapath details are complex.

        Parameters
        ----------
        micro : str
            The micro–operation text to parse.
        """
        # Clear any prior arrow
        self._clear_previous_arrow()
        # Attempt to extract the RHS of the micro op, ignoring the timing tag.
        if ":" in micro:
            _, desc = micro.split(":", 1)
        else:
            desc = micro
        # Consider only the first transfer if multiple are separated by commas.
        # E.g. "IR ← M[AR], PC ← PC + 1" – highlight the register load.
        parts = desc.split(",")
        if not parts:
            return
        # Trim whitespace on the selected micro op
        op = parts[0].strip()
        if "←" not in op:
            return
        left, right = op.split("←", 1)
        dest = left.strip()
        expr = right.strip()
        # Remove any comments after semicolon
        if ";" in expr:
            expr = expr.split(";")[0].strip()
        # Determine destination component name
        dest_name = dest
        if dest_name.startswith("M["):
            dest_name = "MEM"
        # Determine source component(s) involved.  Only handle the
        # straightforward cases used in the basic computer.
        sources: List[str] = []
        # Memory read: RHS contains "M[".
        if "M[" in expr:
            sources.append("MEM")
        # Check for register names in the expression.  We scan for
        # component names rather than rely on complicated parsing.
        for name in ["AR", "PC", "DR", "AC", "IR", "TR"]:
            if name in expr:
                sources.append(name)
        # Remove duplicates while preserving order
        seen = set()
        unique_sources: List[str] = []
        for s in sources:
            if s not in seen:
                seen.add(s)
                unique_sources.append(s)
        # If the operation is an ALU operation (contains ∧ or + or - or ∨),
        # flash the ALU block but don't draw an arrow.
        if any(op in expr for op in ["∧", "+", "-", "∨"]):
            self._flash_alu()
            return
        # Draw arrows from each source to the destination
        for src in unique_sources:
            if src == dest_name:
                continue
            if src not in self.components or dest_name not in self.components:
                continue
            self._draw_arrow(src, dest_name)

    def _flash_alu(self) -> None:
        """Briefly highlight the ALU block to indicate an ALU operation."""
        comp = self.components.get("ALU")
        if not comp:
            return
        rect_id = comp["rect_id"]
        # Increment write count for ALU for completeness
        comp["writes"] += 1
        self.canvas.itemconfigure(comp["count_id"], text=str(comp["writes"]))
        # Highlight
        self.canvas.itemconfigure(rect_id, fill="yellow")
        def revert():
            self.canvas.itemconfigure(rect_id, fill="lightgray")
        self.canvas.after(350, revert)