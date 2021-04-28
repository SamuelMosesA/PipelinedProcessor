from Modules import InstructionFetch, DecodeRegFetch, MemAccess, ExecuteAddrCalc
class Manage:
    def __init__(self):
        self.IF = InstructionFetch()
        self.DRF = DecodeRegFetch()
        self.EX = ExecuteAddrCalc()
        self.MA = MemAccess()


        self.stall = False
        self.stallPoint = 0
        self.runPerm = [False] * 5
        self.runPerm[0] = True

        self.pc_input = 0
        self.pc_out = None

        self.RAW = False
        self.Branch = False

        self.halt = False

        self.afterMem = {"data":0, "reg": 1}
        self.afterExec = {"opcode": None,  "result":0, "address":'00', "dest_reg": 1}
        self.afterDecode = None
        self.afterFetch = None

    def clock(self):
        if self.runPerm[4]:
            self.DRF.input(self.afterMem["reg"], self.afterMem["data"])
            self.runPerm[0] = True
            self.runPerm[4] = False

        if self.runPerm[3]:
            if self.afterExec["opcode"] == "load":
                self.afterMem["data"] = self.MA.load(self.afterExec["address"])
                self.afterMem["reg"] = self.afterExec["dest_reg"]
                self.runPerm[4] = True

            elif self.afterExec["opcode"] == "store":
                self.MA.store(self.afterExec["address"], self.afterExec["result"])
                self.runPerm[0] = True
            else:
                self.afterMem["data"] = self.afterExec["data"]
                self.afterMem["reg"] = self.afterExec["dest_reg"]
                self.runPerm[4] = True

            self.runPerm[3] = False

        if self.runPerm[2]:
            self.EX.execute()





        if not self.stall or self.stallPoint > 0:
            self.IF.input(self.pc_input)

