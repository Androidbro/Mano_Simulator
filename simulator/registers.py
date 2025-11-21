# simulator/registers.py

class Register:
    def __init__(self, name: str, bits: int):
        self.name = name
        self.bits = bits
        self.value = 0
        # Mask is used to enforce bit width (e.g., 0xFFF for 12-bit)
        self._mask = (1 << bits) - 1
        # specific flag to track if this register changed in the current step
        self.updated = False 

    def load(self, val: int):
        #Loads a value, handling bit-masking automatically.
        previous_value = self.value
        self.value = val & self._mask
        
        # Mark as updated if value changed (or even if written to same value, 
        # depending on strict hardware simulation preference)
        self.updated = True 

    def increment(self):
        #Increments the register, wrapping around if it overflows.
        self.value = (self.value + 1) & self._mask
        self.updated = True

    def clear(self):
        #Clears the register to 0. 
        self.value = 0
        self.updated = True
        
    def reset_state(self):
        #Call this at the start of every cycle to reset the 'updated' status. 
        self.updated = False

    def __str__(self):
        # Format as Hex (e.g., 0x123)
        return f"0x{self.value:X}"

    def get_binary(self):
        # Helper for the 'show' command binary display
        return format(self.value, f'0{self.bits}b')

# Special 1-bit register for Flags E (Carry), I (Indirect), etc.
class Flag:
    def __init__(self, name: str):
        self.name = name
        self.value = 0 # 0 or 1
        self.updated = False

    def set(self):
        self.value = 1
        self.updated = True

    def clear(self):
        self.value = 0
        self.updated = True
        
    def complement(self):
        self.value = 1 - self.value
        self.updated = True
        
    def reset_state(self):
        self.updated = False