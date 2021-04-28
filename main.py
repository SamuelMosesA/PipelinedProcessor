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

        self.afterIF = None

        self.RAW = False
        self.Branch = False

        self.halt = False
        self.startup = True

        self.afterMem = {"data": 0, "reg": 1}
        self.afterExec = {"optype": None, "result": 0, "address": '00', "dest_reg": 1, "jump": False, "new_pc": 2}
        self.afterDecode = None
        self.afterFetch = None

        self.RAWstallDetails =  None

        self.NumBranchStalls = 0
        self.NumRAWStalls = 0

    def clock(self):
        restart_clock = False
        clock_to_restart = [False, False]

        if self.runPerm[4]:
            if self.halt:
                return True
            self.DRF.input(self.afterMem["reg"], self.afterMem["data"])
            self.startup = False
            self.runPerm[0] = True
            self.runPerm[4] = False

            if self.RAW:
                if self.RAWstallDetails["a"] == self.afterMem["reg"]:
                    self.RAWstallDetails["a_valid"] = True

                if self.RAWstallDetails["b"] == self.afterMem["reg"]:
                    self.RAWstallDetails["b_valid"] = True

                if self.RAWstallDetails["a_valid"] and self.RAWstallDetails["b_valid"]:
                    self.RAW = False
                    restart_clock = True
                    clock_to_restart = [True, True]

        if self.runPerm[3]:
            if self.afterExec["optype"] == "load":
                self.afterMem["data"] = self.MA.load(self.afterExec["address"])
                self.afterMem["reg"] = self.afterExec["dest_reg"]
                self.runPerm[4] = True

            elif self.afterExec["optype"] == "store":
                self.MA.store(self.afterExec["address"], self.afterExec["result"])
                self.startup = False
                self.runPerm[0] = True
            else:
                if self.afterExec["optype"] == "halt":
                    self.halt = True
                self.afterMem["data"] = self.afterExec["result"]
                self.afterMem["reg"] = self.afterExec["dest_reg"]
                self.runPerm[4] = True

            self.runPerm[3] = False


        if self.runPerm[2]:
            self.runPerm[3] = True
            self.afterExec = self.EX.execute(self.afterDecode)
            if self.afterExec["optype"] == "branch":
                self.Branch = False
                restart_clock = True
                clock_to_restart = [True, False]
                if self.afterExec["jump"]:
                    self.IF.input(self.afterExec["address"])
                else:
                    self.IF.input(self.afterExec["new_pc"])

            self.runPerm[2] = False


        if self.runPerm[1]:
            self.afterDecode = self.DRF.output(self.afterIF["inst"])
            self.afterDecode["new_pc"] = self.afterIF["npc"]
            self.RAW = False
            if self.afterDecode["optype"] == "branch":
                self.Branch = True
                self.runPerm[0] = False
                self.runPerm[2] = True
                self.NumBranchStalls += 1
            elif not self.afterDecode["status"]:
                self.RAW = True
                self.RAWstallDetails = self.afterDecode
                self.runPerm[0] = False
            else:
                self.IF.input(self.afterIF["npc"])
                self.runPerm[2] = True


        if self.runPerm[0] or self.startup:
            self.afterIF = self.IF.output()
            self.runPerm[1] = True


        self.NumRAWStalls += 1

