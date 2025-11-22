import tkinter as tk


class DatapathView(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        tk.Label(self, text="Register Transfer Datapath", font=("Arial", 12, "bold")).pack(pady=(5, 5))
        self.canvas_width = 520
        self.canvas_height = 550
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="white", highlightthickness=1, relief="sunken")
        self.canvas.pack(expand=True)
        self.reg_boxes = {}
        self.flag_widgets = {}
        self.alu_x1 = None
        self.alu_x2 = None
        self.alu_y1 = None
        self.alu_y2 = None
        self.mem_addr_x = None
        self.mem_addr_y_ar = None
        self.mem_addr_y_mem = None
        self._draw_layout()
        self._build_flags()

    def _draw_layout(self):
        center_x = self.canvas_width / 2
        reg_width = 160
        self.reg_x1 = center_x - (reg_width / 2)
        self.reg_x2 = center_x + (reg_width / 2)
        self.bus_right_x = self.canvas_width - 50
        self.bus_left_x = 50
        self.bus_bottom_y = 500
        self.bus_top_y = 30
        self.canvas.create_line(self.bus_right_x, self.bus_top_y, self.bus_right_x, self.bus_bottom_y, width=4, fill="#444", arrow=tk.LAST)
        self.canvas.create_text(self.bus_right_x, 20, text="BUS", font=("Arial", 8, "bold"), fill="#444")
        self.canvas.create_line(self.bus_right_x, self.bus_bottom_y, self.bus_left_x, self.bus_bottom_y, width=4, fill="#444", arrow=tk.LAST)
        self.canvas.create_line(self.bus_left_x, self.bus_bottom_y, self.bus_left_x, self.bus_top_y, width=4, fill="#444", arrow=tk.LAST)

        def make_reg(name, row):
            y1 = 50 + row * 65
            y2 = y1 + 45
            mid_y = (y1 + y2) / 2
            if name != "AC":
                self.canvas.create_line(self.bus_left_x, mid_y, self.reg_x1, mid_y, width=2, fill="#888", arrow=tk.LAST)
            self.canvas.create_line(self.reg_x2, mid_y, self.bus_right_x, mid_y, width=2, fill="#888", arrow=tk.LAST)
            rect = self.canvas.create_rectangle(self.reg_x1, y1, self.reg_x2, y2, outline="#333", width=2, fill="#F9F9F9")
            self.canvas.create_text(self.reg_x1 + 15, y1 + 12, text=name, font=("Arial", 8, "bold"), fill="#555", anchor="w")
            txt = self.canvas.create_text((self.reg_x1 + self.reg_x2) / 2, mid_y + 5, text="0000", font=("Consolas", 14, "bold"))
            self.reg_boxes[name] = {"rect": rect, "text": txt, "cx": (self.reg_x1 + self.reg_x2) / 2, "cy": mid_y, "y_center": mid_y}

        make_reg("MEM", 0)
        make_reg("AR", 1)
        make_reg("PC", 2)
        make_reg("DR", 3)
        make_reg("AC", 4)
        make_reg("IR", 5)
        make_reg("TR", 6)
        self._draw_alu_block()
        self._draw_mem_addr_line()

    def _draw_alu_block(self):
        dr = self.reg_boxes["DR"]
        ac = self.reg_boxes["AC"]
        y_dr = dr["y_center"]
        y_ac = ac["y_center"]
        alu_center_y = (y_dr + y_ac) / 2
        alu_height = 40
        alu_width = 60
        self.alu_y1 = alu_center_y - (alu_height / 2)
        self.alu_y2 = alu_center_y + (alu_height / 2)
        self.alu_x2 = self.reg_x1 - 25
        self.alu_x1 = self.alu_x2 - alu_width
        self.canvas.create_rectangle(self.alu_x1, self.alu_y1, self.alu_x2, self.alu_y2, fill="#EFEFEF", outline="#333", width=2)
        self.canvas.create_text((self.alu_x1 + self.alu_x2) / 2, (self.alu_y1 + self.alu_y2) / 2, text="ALU", font=("Arial", 10, "bold"))
        self.canvas.create_line(self.reg_x1, y_dr, self.alu_x2, alu_center_y, width=2, fill="#888", arrow=tk.LAST)
        self.canvas.create_line(self.alu_x1, alu_center_y, self.reg_x1, y_ac, width=2, fill="#888", arrow=tk.LAST)
        e_x = (self.alu_x1 + self.reg_x1) / 2
        e_y = alu_center_y - 20
        self.canvas.create_rectangle(e_x - 12, e_y - 10, e_x + 12, e_y + 10, fill="#FFFFFF", outline="#333")
        self.canvas.create_text(e_x, e_y, text="E", font=("Arial", 8, "bold"))

    def _draw_mem_addr_line(self):
        ar = self.reg_boxes["AR"]
        mem = self.reg_boxes["MEM"]
        y_ar = ar["y_center"]
        y_mem = mem["y_center"]
        self.mem_addr_x = self.reg_x2
        self.mem_addr_y_ar = y_ar
        self.mem_addr_y_mem = y_mem
        self.canvas.create_line(self.mem_addr_x, y_ar, self.mem_addr_x, y_mem, width=2, fill="#AA0000", arrow=tk.LAST)

    def _build_flags(self):
        f_frame = tk.Frame(self)
        f_frame.pack(side="bottom", pady=5)
        for n in ["E", "I", "S"]:
            lbl = tk.Label(f_frame, text=f"{n}: 0", font=("Arial", 12, "bold"), width=6, bd=1, relief="solid", bg="white")
            lbl.pack(side="left", padx=5)
            self.flag_widgets[n] = lbl

    def update_from_machine(self, machine, changed_set, micro_op_str=""):
        reg_map = {"MEM": None, "AR": machine.AR, "PC": machine.PC, "DR": machine.DR, "AC": machine.AC, "IR": machine.IR, "TR": machine.TR}
        for name, reg in reg_map.items():
            box = self.reg_boxes[name]
            if name == "MEM":
                r = machine.memory.reads
                w = machine.memory.writes
                text = f"R:{r} W:{w}"
            else:
                text = f"{reg.value & 0xFFFF:04X}"
            self.canvas.itemconfigure(box["text"], text=text)
            self.canvas.itemconfigure(box["rect"], fill="#F9F9F9")

        m = micro_op_str.replace("←", "<-")
        alu_ops = ["AC <- DR", "AC <- AC + DR", "AC <- AC & DR", "AC <- AC ∧ DR"]
        alu_event = any(p in m for p in alu_ops)
        reg_ref = m.startswith("T3:") and any(k in m for k in ["CLA", "CLE", "CMA", "CME", "CIR", "CIL", "INC", "SPA", "SNA", "SZA", "SZE", "HLT"])
        mem_ref = "M[AR]" in m
        dest = None
        internal = False
        animated = False
        no_bus_regs = set()
        for r in ["AR", "PC", "DR", "AC", "IR", "TR"]:
            if f"{r} <- {r} + 1" in m or f"{r} <- 0" in m:
                no_bus_regs.add(r)

        if mem_ref:
            self._animate_mem_address()

        if alu_event:
            self._animate_alu()
            internal = True
            animated = True

        if "<-" in m and not alu_event:
            first = m.split(",", 1)[0]
            if "<-" in first:
                lhs, rhs = first.split("<-")
                lhs = lhs.split(":")[-1].strip().upper()
                rhs = rhs.strip().upper()
                dest = self._map_reg(lhs)
                src = self._map_reg(rhs)
                same = lhs in rhs
                aluop = any(op in rhs for op in ["+", "-", "&", "|", "^"])
                imm = rhs in ("0", "1", "CLR", "INC")
                internal = same or aluop or imm
                if (not internal) and dest and src:
                    self._animate_packet(src, "source", "blue")
                    if dest != "AC" and dest not in no_bus_regs:
                        self._animate_packet(dest, "dest", "red")
                    animated = True

        if reg_ref:
            internal = True

        for name in changed_set:
            if name in self.reg_boxes:
                self.canvas.itemconfigure(self.reg_boxes[name]["rect"], fill="#FFEB3B")
                if reg_ref or alu_event or mem_ref:
                    continue
                if name in no_bus_regs:
                    continue
                if internal and dest and name == dest:
                    continue
                if animated and dest and name == dest:
                    continue
                if name != "AC":
                    self._animate_packet(name, "dest", "red")

        for f in ["E", "I", "S"]:
            v = int(getattr(machine, f).value)
            self.flag_widgets[f].config(text=f"{f}: {v}", bg="#FFEB3B" if f in changed_set else "white")

    def _map_reg(self, s):
        if "M[" in s or "MEM" in s:
            return "MEM"
        for r in ["AR", "PC", "DR", "AC", "IR", "TR"]:
            if r in s:
                return r
        return None

    def _animate_packet(self, reg, direction, color):
        box = self.reg_boxes[reg]
        y = box["y_center"]
        if direction == "source":
            start = self.reg_x2
            end = self.bus_right_x
        else:
            start = self.bus_left_x
            end = self.reg_x1
        r = 6
        ball = self.canvas.create_oval(start - r, y - r, start + r, y + r, fill=color, outline="black")
        steps = 20
        dx = (end - start) / steps

        def step(i):
            if i >= steps:
                self.canvas.delete(ball)
                return
            self.canvas.move(ball, dx, 0)
            self.after(25, lambda: step(i + 1))

        step(0)

    def _animate_alu(self):
        dr = self.reg_boxes["DR"]
        ac = self.reg_boxes["AC"]
        y_dr = dr["y_center"]
        y_ac = ac["y_center"]
        alu_center_y = (y_dr + y_ac) / 2
        start1 = self.reg_x1
        end1 = self.alu_x2
        start2 = self.alu_x1
        end2 = self.reg_x1
        r = 6
        ball1 = self.canvas.create_oval(start1 - r, y_dr - r, start1 + r, y_dr + r, fill="blue", outline="black")
        steps = 20
        dx1 = (end1 - start1) / steps
        dy1 = (alu_center_y - y_dr) / steps

        def move1(i):
            if i >= steps:
                self.canvas.delete(ball1)
                move2(0)
                return
            self.canvas.move(ball1, dx1, dy1)
            self.after(20, lambda: move1(i + 1))

        def move2(i):
            ball2 = self.canvas.create_oval(start2 - r, alu_center_y - r, start2 + r, alu_center_y + r, fill="red", outline="black")
            dx2 = (end2 - start2) / steps
            dy2 = (y_ac - alu_center_y) / steps

            def m2(j):
                if j >= steps:
                    self.canvas.delete(ball2)
                    return
                self.canvas.move(ball2, dx2, dy2)
                self.after(20, lambda: m2(j + 1))

            m2(0)

        move1(0)

    def _animate_mem_address(self):
        if self.mem_addr_x is None:
            return
        x = self.mem_addr_x
        start_y = self.mem_addr_y_ar
        end_y = self.mem_addr_y_mem
        r = 5
        ball = self.canvas.create_oval(x - r, start_y - r, x + r, start_y + r, fill="purple", outline="black")
        steps = 16
        dy = (end_y - start_y) / steps

        def step(i):
            if i >= steps:
                self.canvas.delete(ball)
                return
            self.canvas.move(ball, 0, dy)
            self.after(20, lambda: step(i + 1))

        step(0)
