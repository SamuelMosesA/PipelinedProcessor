from util import int_to_bin, bin_to_signed
from Cache import ICache, DCache  # Cache Memory


class Manage:
    def __init__(self, filename):
        self.register_file = [{"data": 0, "busy": 0}] * 16  # Registers
        self.pc = 0  # Program Counter
        self.stall = 0  # Retains stall value - 1 for control hazard, 2 for data hazard, 3 for program halt
        self.MemBuffer = None  # buffer after Memory cycle
        self.ExecBuffer = None  # buffer after Execution cycle
        self.DecodeBuffer = None  # buffer after Decode cycle
        self.FetchBuffer = None  # buffer after Fetch cycle

    def clock(self):  # this function represents one clock cycle
        instcount = self.WriteBack(self.MemBuffer)  # 1 returned if an instruction is completed; -1 for halt
        self.MemBuffer = self.Memory(self.ExecBuffer)
        self.ExecBuffer = self.Execution(self.DecodeBuffer)
        self.DecodeBuffer = self.InstructionDecode(self.FetchBuffer)
        self.FetchBuffer = self.InstructionFetch()
        
        if self.ExecBuffer==None:
    		optype=0 # stall cycle
    	else
    		optype=self.ExecBuffer["optype"]
    	return {instcount, self.stall, optype}

    def InstructionFetch(self):
        if self.stall in [1,
                          3]:  # IF buffer cleared and no instruction pulled if there is a control hazard or program halted
            return None
        elif self.stall == 2:
            return self.FetchBuffer()  # IF buffer retained, without performing new IF, if there is a data hazard holding up ID step
        else:
            cache_out = ICache.read(int_to_bin(self.pc))  # reading instruction
            self.pc += 2  # pc update
            return {"inst": cache_out}

    def InstructionDecode(self, FetchBuffer):
        if self.stall == 3:  # ID buffer cleared if program halted
            return None
        else:
            # decoding last fetched instructions
            opcode = int(FetchBuffer["inst"][0:4], 2)
            dest_ind = None
            a_ind = None
            b_ind = None
            a = None
            b = None
            immval = None

            if opcode > 11:  # program halt initiated
                self.stall = 3
                return None
            elif opcode == 10:
                immval = bin_to_signed(FetchBuffer["inst"][4:12] + '0', 9)
            elif opcode == 11:
                a_ind = int(FetchBuffer["inst"][4:8], 2)
                immval = bin_to_signed(FetchBuffer["inst"][8:16] + '0', 9)
            else:
                dest_ind = int(FetchBuffer["inst"][4:8], 2)
                if opcode == 3:
                    a_ind = int(FetchBuffer["inst"][4:8], 2)
                elif opcode == 6:
                    a_ind = int(FetchBuffer["inst"][8:12], 2)
                elif opcode <= 9:
                    a = bin_to_signed(FetchBuffer["inst"][8:12], 4)
                    b_ind = int(FetchBuffer["inst"][12:16], 2)

            # checking for data hazards - if present, ID buffer cleared and stall initiated/retained
            if a_ind is not None:
                if self.register_file[a_ind]["busy"] > 0:
                    self.stall = 2
                    return None
                else:
                    a = self.register_file[a_ind]["data"]

            if b is not None:
                if self.register_file[b_ind]["busy"] > 0:
                    self.stall = 2
                    return None
                else:
                    a = self.register_file[b_ind]["data"]

            # if instruction is jump/beqz, initiate control hazard
            if opcode >= 10:
                self.stall = 1

            # if this line is reached, there is no data hazard - hence, updated stall status accordingly
            if self.stall == 2:
                self.stall = 0

            # destination register's "busyness" updated
            if dest_ind is not None:
                self.register_file[dest_ind]["busy"] += 1

            return {"opcode": opcode, "dest_ind": dest_ind,
                    "a": a, "b": b, "imm": immval}

    def Execution(self, DecodeBuffer):
        if DecodeBuffer is None:  # step skipped in case of hazard/halt
            return None
        else:
            # performing ALU operation
    		result=None
    		if DecodeBuffer["opcode"] in [0,8,9]:
            		result = DecodeBuffer["a"]+DecodeBuffer["b"]
            		if DecodeBuffer["opcode"]==0:
            			optype = 1 #Arithmetic
            		else:
            			optype = 3 #Memory
            	elif DecodeBuffer["opcode"]==1:
            		result = DecodeBuffer["a"]-DecodeBuffer["b"]
            		optype = 1 #Arithmetic
            	elif DecodeBuffer["opcode"]==2:
            		result = DecodeBuffer["a"]*DecodeBuffer["b"]
            		optype = 1 #Arithmetic
            	elif DecodeBuffer["opcode"]==3:
            		result = DecodeBuffer["a"]+1
            		optype = 1 #Arithmetic
            	elif DecodeBuffer["opcode"]==4:
            		result = DecodeBuffer["a"]&DecodeBuffer["b"]
            		optype = 2 #Logical
            	elif DecodeBuffer["opcode"]==5:
            		result = DecodeBuffer["a"]|DecodeBuffer["b"]
            		optype = 2 #Logical
            	elif DecodeBuffer["opcode"]==6:
            		result = ~DecodeBuffer["a"]
            		optype = 2 #Logical
            	elif DecodeBuffer["opcode"]==7:
            		result = DecodeBuffer["a"]^DecodeBuffer["b"]
            		optype = 2 #Logical
            	elif DecodeBuffer["opcode"]==10:
            		result = self.pc+DecodeBuffer["immval"]
            		optype = 3 #Jump
            	elif DecodeBuffer["a"]==0:
            		result = self.pc+DecodeBuffer["immval"]
            		optype = 3 #Jump
            	else
            		result = self.pc
            		optype = 3 #Jump
            	
            	return {"opcode": opcode, "optype": optype, "dest_ind": dest_ind,
                "result": result}

    def Memory(self, ExecBuffer):
        if ExecBuffer is None:  # step skipped in case of hazard/halt
            return None
        else:
            result = ExecBuffer["result"]
            if ExecBuffer["opcode"] >= 10:
                self.pc = ExecBuffer["result"]  # update pc if there is jump
                if self.stall == 1:
                    self.stall = 0  # clearing the control hazard
            elif ExecBuffer["opcode"] == 8:
                result =  # Reading from result address
            elif ExecBuffer["opcode"] == 9:
            # Writing to result address from dest_ind

            return {"opcode": ExecBuffer["opcode"], "dest_ind": ExecBuffer["dest_ind"],
                    "result": result}

    def WriteBack(self, MemBuffer):
        if MemBuffer is None:  # Hazard/Halt
            if self.FetchBuffer is None and self.DecodeBuffer is None and self.stall == 3:
                return -1  # -1 returned if halt instruction is "completed"
            else:
                return 0  # # step skipped in case of hazard
        else:
            if MemBuffer["opcode"] <= 8:  # writing to destination register
                self.register_file[MemBuffer["dest_ind"]]["data"] = MemBuffer["result"]
                self.register_file[MemBuffer["dest_ind"]][
                    "busy"] -= 1  # decrementing "busyness" of register to clear up data hazards
            return 1  # 1 instruction completed this cycle
