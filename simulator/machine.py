# simulator/machine.py

from .registers import Register, Flag
from .memory import Memory
from .instruction_set import InstructionSet


class Machine:

    def __init__(self):
        # Registers
        self.AR = Register("AR", 12)
        self.PC = Register("PC", 12)
        self.DR = Register("DR", 16)
        self.AC = Register("AC", 16)
        self.IR = Register("IR", 16)
        self.TR = Register("TR", 16)
        self.SC = Register("SC", 4)   # timing / sequence counter T0–T15

        # Flags / flip-flops
        self.E   = Flag("E")   # carry
        self.I   = Flag("I")   # indirect bit
        self.S   = Flag("S")   # start / halt
        self.R   = Flag("R")
        self.IEN = Flag("IEN")
        self.FGI = Flag("FGI")
        self.FGO = Flag("FGO")

        # Start in running state
        self.S.set()

        # Subsystems
        self.memory = Memory()
        self.iset = InstructionSet(self)

        # Profiler counters
        self.total_cycles = 0
        self.instr_count = 0


    def finish_instruction(self):
        """Reset SC and bump instruction counter at end of an instruction."""
        self.SC.clear()
        self.instr_count += 1


    @staticmethod
    def format_word(val: int) -> str:
        return f"0x{val & 0xFFFF:04X}"

    @staticmethod
    def format_bin16(val: int) -> str:
        s = f"{val & 0xFFFF:016b}"
        return " ".join(s[i:i+4] for i in range(0, 16, 4))

    def load_program_and_data(
        self,
        prog_file: str = "data/program.txt",
        data_file: str = "data/data.txt",
    ):
        prog_start = self.memory.load_file(prog_file)
        self.memory.load_file(data_file)
        if prog_start is not None:
            self.PC.load(prog_start)
        self.SC.clear()
        self.S.set()


    def _reset_updates(self):
        """Clear the 'updated' flag on all registers and flags each cycle."""
        for reg in [self.AR, self.PC, self.DR, self.AC, self.IR, self.TR, self.SC]:
            reg.reset_state()
        for flag in [self.E, self.I, self.S, self.R, self.IEN, self.FGI, self.FGO]:
            flag.reset_state()


    def step_cycle(self):
        """
        Execute a single clock cycle (one T state).
        T0–T2: fetch phase handled here.
        T>=3: delegated to InstructionSet (memory-ref or register-ref).

        Returns: (micro_op_str, changed_components_set)
        """
        self._reset_updates()

        if self.S.value == 0:
            # CPU is halted
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
            self.AR.load(self.IR.value)  # masking inside Register keeps 12 bits
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
                # Register-reference instruction
                micro, changed = self.iset.execute_register_ref(T)
            else:
                # Memory-reference instruction (handles indirect inside)
                micro, changed = self.iset.execute_memory_ref(opcode, T)

        self.total_cycles += 1

        # Track which components changed (based on 'updated' flags)
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

    def step_instruction(self):
        """
        Execute until the end of the current instruction
        (SC reset to 0 by finish_instruction, or HLT).
        Returns the last (micro_op_str, changed_set) of that instruction.
        """
        if self.S.value == 0:
            return "CPU halted (HLT executed)", set()

        last_micro = ""
        last_changed = set()

        while True:
            micro, changed = self.step_cycle()
            last_micro, last_changed = micro, changed
            if self.S.value == 0 or self.SC.value == 0:
                break

        return last_micro, last_changed

    def run_until_halt(self):
        """
        Run continuously until HLT (S=0).
        Returns last (micro_op_str, changed_set).
        """
        last_micro = ""
        last_changed = set()
        while self.S.value != 0:
            last_micro, last_changed = self.step_instruction()
        return last_micro, last_changed


    def show_reg(self, name: str) -> str:
        n = name.upper()
        if n == "AC":
            r = self.AC
        elif n == "DR":
            r = self.DR
        elif n == "AR":
            r = self.AR
        elif n == "PC":
            r = self.PC
        elif n == "IR":
            r = self.IR
        elif n == "TR":
            r = self.TR
        elif n == "SC":
            return f"SC = {self.SC.value}"
        elif n in ["E", "I", "S", "R", "IEN", "FGI", "FGO"]:
            flag = getattr(self, n)
            return f"{n} = {flag.value}"
        else:
            return f"Unknown register {name}"

        return f"{n} = {self.format_word(r.value)} (binary: {self.format_bin16(r.value)})"

    def show_all(self) -> str:
        """
        Single-line snapshot similar to the example in Appendix A.
        """
        return (
            f"AC={self.format_word(self.AC.value)} "
            f"DR={self.format_word(self.DR.value)} "
            f"AR=0x{self.AR.value:03X} "
            f"PC=0x{self.PC.value:03X} "
            f"IR={self.format_word(self.IR.value)} "
            f"TR={self.format_word(self.TR.value)} "
            f"E={self.E.value} I={self.I.value} SC={self.SC.value}"
        )

    def show_mem(self, addr: int, count: int = 1) -> str:
        """
        If count == 1:
          M[112] = 0x2003 (binary: 0010 0000 0000 0011)
        If count > 1:
          0x112 | 0x2003
        """
        lines = []
        for i in range(count):
            a = (addr + i) & 0x0FFF
            val = self.memory.data[a]
            if count == 1:
                lines.append(
                    f"M[{a:03X}] = {self.format_word(val)} "
                    f"(binary: {self.format_bin16(val)})"
                )
            else:
                lines.append(f"0x{a:03X} | {self.format_word(val)}")
        return "\n".join(lines)

    def show_profiler(self) -> str:
        reads = self.memory.reads
        writes = self.memory.writes
        cpi = self.total_cycles / self.instr_count if self.instr_count > 0 else 0.0
        return (
            f"Total cycles: {self.total_cycles}\n"
            f"Instructions executed: {self.instr_count}\n"
            f"Average CPI: {cpi:.2f}\n"
            f"Memory reads: {reads}\n"
            f"Memory writes: {writes}"
        )
