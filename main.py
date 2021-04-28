from Modules import InstructionFetch, DecodeRegFetch, MemAccess
class Manage:
    def __init__(self):
        self.stall = False
        self.stallPoint = 0
        self.IF = InstructionFetch()
        self.DRF = DecodeRegFetch()
        self.MA = MemAccess()
        self.pc_input = 0
        self.pc_out = None

    def tick(self):
        if not self.stall or self.stallPoint < 1:
            self.IF.input(self.pc_input)

