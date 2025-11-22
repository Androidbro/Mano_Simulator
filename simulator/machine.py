# simulator/machine.py

def step_cycle(self):

    self._reset_updates()

    if self.S.value == 0:
        self.total_cycles += 1
        return "CPU halted (HLT executed)", set()

    T = self.SC.value
    changed = set()

    if T == 0:
        # T0: AR <- PC
        self.AR.load(self.PC.value)
        self.SC.increment()
        micro = "T0: AR ← PC"

    elif T == 1:
        # T1: IR <- M[AR], PC <- PC + 1
        word = self.memory.read(self.AR.value)
        self.IR.load(word)
        self.PC.increment()
        self.SC.increment()
        micro = "T1: IR ← M[AR], PC ← PC + 1"

    elif T == 2:
        # T2: AR <- IR(0-11), I <- IR(15)
        self.AR.load(self.IR.value)
        indirect_bit = (self.IR.value >> 15) & 1
        if indirect_bit:
            self.I.set()
        else:
            self.I.clear()
        self.SC.increment()
        micro = "T2: AR ← IR(0–11), I ← IR(15)"

    else:
        opcode = (self.IR.value >> 12) & 0x7

        if opcode == 0b111 and self.I.value == 0:
            # Register-reference instructions
            micro, changed = self.iset.execute_register_ref(T)
        else:
            # Memory-reference instructions
            micro, changed = self.iset.execute_memory_ref(opcode, T)

    self.total_cycles += 1

    # Detect updated registers/flags
    reg_map = {
        "AR": self.AR,
        "PC": self.PC,
        "DR": self.DR,
        "AC": self.AC,
        "IR": self.IR,
        "TR": self.TR,
        "SC": self.SC,
    }
    flag_map = {
        "E": self.E,
        "I": self.I,
        "S": self.S,
        "R": self.R,
        "IEN": self.IEN,
        "FGI": self.FGI,
        "FGO": self.FGO,
    }

    for name, reg in reg_map.items():
        if reg.updated:
            changed.add(name)
    for name, flag in flag_map.items():
        if flag.updated:
            changed.add(name)

    return micro, changed

