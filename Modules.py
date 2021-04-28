from util import int_to_bin, bin_to_signed
from Cache import ICache, DCache


class InstructionFetch:
    def __init__(self):
        self.pc = 0
        self.pc_available = True

    def output(self):
        if not self.pc_available:
            return {"npc": 0, "inst": 0, "status": False}
        else:
            cache_out = ICache.read(int_to_bin(self.pc))
            self.pc_available = False
            return {"npc": self.pc + 2, "inst": cache_out, "status": True}

    def input(self, new_pc):
        self.pc = new_pc
        self.pc_available = True


class DecodeRegFetch:
    def __init__(self):
        self.register_file = [{"data": 0, "busy": False}] * 16

    def output(self, instr: str):
        opcode = int(instr[0:4], 2)
        dest_ind = int(instr[4:8], 2)
        a_ind = int(instr[8:12], 2)
        b_ind = int(instr[12:16], 2)

        #todo: change it for jmp and bneq instr
        immval = bin_to_signed(instr[8:16] + '0', 9)

        op_type = ""
        if opcode <= 7:
            op_type = "arith_or_logic"
        elif opcode == 8:
            op_type = "load"
        elif opcode == 9:
            op_type = "store"
        elif opcode <= 11:
            op_type = "branch"
        else:
            op_type = "halt"

        if op_type in ["arith_or_logic", "load"]:
            self.register_file[dest_ind]["busy"] = True

        a = self.register_file[a_ind]["data"]
        if type not in ["load", "store"]:
            b = self.register_file[b_ind]["data"]
        else:
            b = bin_to_signed(instr[12:16], 4)

        read_validity = True
        a_valid = True
        b_valid = True

        if self.register_file[a_ind]["busy"]:
            read_validity = False
            a_valid = False
            a = a_ind

        if self.register_file[b_ind]["busy"]:
            read_validity = False
            b_valid = False
            b = b_ind

        return {"type": op_type, "opcode": opcode, "dest_ind": dest_ind,
                "a": a, "a_valid": a_valid, "b": b, "b_valid": b_valid,
                "imm": immval,
                "status": read_validity}

    def input(self, reg_ind: int, data: int):
        self.register_file[reg_ind]["data"] = data
        self.register_file[reg_ind]["busy"] = False


class MemAccess:
    def __init__(self):
        self.i = 0


class ExecuteAddrCalc:
    def __init__(self):
        self.i = 0

    def execute(self, afterDecode):
        if afterDecode["opcode"]==0:
            result = afterDecode["a"]+afterDecode["b"]
            address = 0
            optype = "add"
        elif afterDecode["opcode"]==1:
            result = afterDecode["a"]-afterDecode["b"]
            address = 0
            optype = "subtract"
        elif afterDecode["opcode"]==2:
            result = afterDecode["a"]*afterDecode["b"]
            address = 0
            optype = "multiply"
        elif afterDecode["opcode"]==3:
            result = afterDecode["a"] + 1
            address = 0
            optype = "add"
        elif afterDecode["opcode"]==4:
            result = afterDecode["new_pc"] + afterDecode["imm"]
        elif afterDecode["opcode"]==5:
            result = afterDecode["new_pc"] + afterDecode["imm"]
        elif afterDecode["opcode"]==6:
            result = afterDecode["new_pc"] + afterDecode["imm"]
        elif afterDecode["opcode"]==7:
            result = afterDecode["new_pc"] + afterDecode["imm"]
        elif afterDecode["opcode"]==8:
            result = afterDecode["new_pc"] + afterDecode["imm"]
        elif afterDecode["opcode"]==9:
            result = afterDecode["new_pc"] + afterDecode["imm"]
        elif afterDecode["opcode"]==10:
            result = afterDecode["new_pc"] + afterDecode["imm"]
        elif afterDecode["opcode"]==11:
            if afterDecode["a"]==0:
                result = afterDecode["new_pc"] + afterDecode["imm"]
        else:
            result=0
        return {"optype": afterDecode["opcode"], "result": result, "address": '00', "dest_reg": 1, "jump": False, "new_pc": 2}
