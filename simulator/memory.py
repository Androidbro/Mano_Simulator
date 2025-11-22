# simulator/memory.py

class Memory:
    """4096 x 16 """

    def __init__(self, size: int = 4096):
        self.size = size
        self.data = [0] * size
        self.reads = 0
        self.writes = 0

    def _mask_addr(self, addr: int) -> int:
        return addr & 0x0FFF

    def read(self, addr: int) -> int:
        addr = self._mask_addr(addr)
        self.reads += 1
        return self.data[addr]

    def write(self, addr: int, value: int):
        addr = self._mask_addr(addr)
        self.data[addr] = value & 0xFFFF
        self.writes += 1

    def load_file(self, filename: str):

        try:
            lowest = None
            with open(filename, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or line.startswith(";"):
                        continue
                    parts = line.replace(":", " ").split()
                    if len(parts) < 2:
                        continue
                    addr = int(parts[0], 16)
                    val = int(parts[1], 16)
                    if 0 <= addr < self.size:
                        self.data[addr] = val & 0xFFFF
                        if lowest is None or addr < lowest:
                            lowest = addr
            return lowest
        except FileNotFoundError:
            return None
