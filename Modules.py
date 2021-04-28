from util import int_to_bin, bin_to_signed
from Cache import ICache, DCache


class InstructionFetch:
    def __init__(self):
        self.pc = 0

    def output(self):
        cache_out = ICache.read(int_to_bin(self.pc))
        if not cache_out["status"]:
            return {"npc": 0, "inst": 0, "status": False}
        else:
            ICache.close_read()
            return {"npc": self.pc + 2, "inst": cache_out["data"], "status": True}

    def input(self, new_pc):
        self.pc = new_pc


class DecodeRegFetch:
    def __init__(self):
        self.register_file = [{"data": 0, "busy": False}] * 16

    def output(self, instr: str):
        opcode = int(instr[0:4], 2)
        dest_ind = int(instr[4:8], 2)
        a_ind = int(instr[8:12], 2)
        b_ind = int(instr[12:16], 2)

        immval = bin_to_signed(instr[8:16], 8)

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

        read_validity = (not self.register_file[a_ind]["busy"]) or (not self.register_file[b_ind]["busy"])

        return {"type": op_type, "opcode": opcode, "dest_ind": dest_ind, "a": a, "b": b, "status": read_validity,
                "imm": immval}

    def input(self, reg_ind: int, data: int):
        self.register_file[reg_ind]["data"] = data
        self.register_file[reg_ind]["busy"] = False


class MemAccess:
    def __init__(self):
        self.i = 0
