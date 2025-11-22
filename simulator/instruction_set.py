# simulator/instruction_set.py

class InstructionSet:
    def __init__(self, machine):
        self.m = machine

    def execute_memory_ref(self, opcode: int, T: int):
        changed = set()
        I = self.m.I.value

        if I == 1 and T == 3:
            word = self.m.memory.read(self.m.AR.value)
            self.m.AR.load(word)
            self.m.SC.increment()
            return "T3: AR <- M[AR](0-11) (indirect)", changed

        effT = T if I == 0 else T - 1

        if opcode == 0: #000 = AND
            return self._mem_AND(effT, T, changed)
        if opcode == 1: #001 = ADD
            return self._mem_ADD(effT, T, changed)
        if opcode == 2: #010 = LDA
            return self._mem_LDA(effT, T, changed)
        if opcode == 3: #011 = STA
            return self._mem_STA(effT, T, changed)
        if opcode == 4: #100 = BUN
            return self._mem_BUN(effT, T, changed)
        if opcode == 5: #101 = BSA
            return self._mem_BSA(effT, T, changed)
        if opcode == 6: #110 = ISZ
            return self._mem_ISZ(effT, T, changed)
        else:
            return f"T{T}: (unknown memory-reference opcode)", changed

    def _mem_AND(self, effT, T, changed):

        if effT == 3:
            # DR <- M[AR]
            self.m.DR.load(self.m.memory.read(self.m.AR.value))
            self.m.SC.increment()
            return f"T{T}: DR ← M[AR]", changed

        if effT == 4:
            # AC <- AC & DR
            self.m.AC.load(self.m.AC.value & self.m.DR.value)
            self.m.finish_instruction()
            return f"T{T}: AC ← AC ∧ DR", changed

        return f"T{T}: (no-op for AND)", changed

    def _mem_ADD(self, effT, T, changed):
        if effT == 3:
            self.m.DR.load(self.m.memory.read(self.m.AR.value))
            self.m.SC.increment()
            return f"T{T}: DR ← M[AR]", changed

        if effT == 4:
            result = self.m.AC.value + self.m.DR.value
            self.m.AC.load(result)
            # E holds carry out from the 16-bit addition
            if result > 0xFFFF:
                self.m.E.set()
            else:
                self.m.E.clear()
            self.m.finish_instruction()
            return f"T{T}: AC ← AC + DR, E ← carry", changed

        return f"T{T}: (no-op for ADD)", changed

    def _mem_LDA(self, effT, T, changed):
        if effT == 3:
            self.m.DR.load(self.m.memory.read(self.m.AR.value))
            self.m.SC.increment()
            return f"T{T}: DR ← M[AR]", changed

        if effT == 4:
            self.m.AC.load(self.m.DR.value)
            self.m.finish_instruction()
            return f"T{T}: AC ← DR", changed

        return f"T{T}: (no-op for LDA)", changed

    def _mem_STA(self, effT, T, changed):
        if effT == 3:
            self.m.memory.write(self.m.AR.value, self.m.AC.value)
            changed.add(f"M[{self.m.AR.value:03X}]")
            self.m.finish_instruction()
            return f"T{T}: M[AR] ← AC", changed

        return f"T{T}: (no-op for STA)", changed

    def _mem_BUN(self, effT, T, changed):
        if effT == 3:
            self.m.PC.load(self.m.AR.value)
            self.m.finish_instruction()
            return f"T{T}: PC ← AR", changed

        return f"T{T}: (no-op for BUN)", changed

    def _mem_BSA(self, effT, T, changed):
        # BSA: store return address, then jump to AR+1
        if effT == 3:
            # M[AR] <- PC
            self.m.memory.write(self.m.AR.value, self.m.PC.value)
            changed.add(f"M[{self.m.AR.value:03X}]")
            self.m.SC.increment()
            return f"T{T}: M[AR] ← PC", changed

        if effT == 4:
            # PC <- AR + 1
            self.m.PC.load(self.m.AR.value + 1)
            self.m.finish_instruction()
            return f"T{T}: PC ← AR + 1", changed

        return f"T{T}: (no-op for BSA)", changed

    def _mem_ISZ(self, effT, T, changed):
        if effT == 3:
            self.m.DR.load(self.m.memory.read(self.m.AR.value))
            self.m.SC.increment()
            return f"T{T}: DR ← M[AR]", changed

        if effT == 4:
            self.m.DR.load(self.m.DR.value + 1)
            self.m.SC.increment()
            return f"T{T}: DR ← DR + 1", changed

        if effT == 5:
            self.m.memory.write(self.m.AR.value, self.m.DR.value)
            changed.add(f"M[{self.m.AR.value:03X}]")
            micro = f"T{T}: M[AR] ← DR"

            # If result is zero, skip the next instruction
            if self.m.DR.value == 0:
                self.m.PC.increment()
                changed.add("PC")
                micro += "; if DR = 0 then PC ← PC + 1"

            self.m.finish_instruction()
            return micro, changed

        return f"T{T}: (no-op for ISZ)", changed

    def execute_register_ref(self, T: int):
        changed = set()
        if T != 3:
            # For T != 3, nothing happens
            return f"T{T}: (idle for register-reference)", changed

        # Only lower 12 bits of IR are relevant for register-reference
        instr = self.m.IR.value & 0x0FFF
        parts = []  # collect mnemonic names like "CLA", "INC" for display

        def bit(n: int) -> int:
            # Returns IR[n] for 0 <= n <= 11
            return (instr >> n) & 1

            # Bit positions 11..0: CLA CLE CMA CME CIR CIL INC SPA SNA SZA SZE HLT

        if bit(11):  # CLA: Clear AC
            self.m.AC.clear()
            parts.append("CLA")
            changed.add("AC")

        if bit(10):  # CLE: Clear E
            self.m.E.clear()
            parts.append("CLE")
            changed.add("E")

        if bit(9):  # CMA: Complement AC
            self.m.AC.load(~self.m.AC.value)
            parts.append("CMA")
            changed.add("AC")

        if bit(8):  # CME: Complement E
            self.m.E.complement()
            parts.append("CME")
            changed.add("E")

        if bit(7):  # CIR: Rotate right (AC and E)
            combined = (self.m.E.value << 16) | self.m.AC.value
            lsb = combined & 1
            combined >>= 1
            # New E is old bit0
            if lsb:
                self.m.E.set()
            else:
                self.m.E.clear()
            # Lower 16 bits back to AC
            self.m.AC.load(combined)
            parts.append("CIR")
            changed.update({"AC", "E"})

        if bit(6):  # CIL: Rotate left (AC and E)
            combined = (self.m.E.value << 16) | self.m.AC.value
            msb = (combined >> 16) & 1
            combined = (combined << 1) & 0x1FFFF
            # New E is old MSB
            if msb:
                self.m.E.set()
            else:
                self.m.E.clear()
            self.m.AC.load(combined)
            parts.append("CIL")
            changed.update({"AC", "E"})

        if bit(5):  # INC: Increment AC
            self.m.AC.load(self.m.AC.value + 1)
            parts.append("INC")
            changed.add("AC")

        if bit(4):  # SPA: Skip next instruction if AC is positive
            if (self.m.AC.value & 0x8000) == 0:
                self.m.PC.increment()
                changed.add("PC")
            parts.append("SPA")

        if bit(3):  # SNA: Skip if AC negative
            if (self.m.AC.value & 0x8000) != 0:
                self.m.PC.increment()
                changed.add("PC")
            parts.append("SNA")

        if bit(2):  # SZA: Skip if AC zero
            if self.m.AC.value == 0:
                self.m.PC.increment()
                changed.add("PC")
            parts.append("SZA")

        if bit(1):  # SZE: Skip if E zero
            if self.m.E.value == 0:
                self.m.PC.increment()
                changed.add("PC")
            parts.append("SZE")

        if bit(0):  # HLT: Halt the machine (S = 0)
            self.m.S.clear()
            parts.append("HLT")
            changed.add("S")

            # Register-reference instructions all complete at T3
        self.m.finish_instruction()

        if not parts:
            return "T3: (no register-reference bit set)", changed
        return "T3: " + ", ".join(parts), changed