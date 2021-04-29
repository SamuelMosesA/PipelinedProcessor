from util import int_to_bin, bin_to_signed
from Cache import ICache, DCache

class Manage:
    def __init__(self, filename):
    	self.register_file = [{"data": 0, "busy": False}] * 16
    	self.pc = 0
    	self.stall=0
    	self.MemBuffer = None #{"data": 0, "reg": 1}
        self.ExecBuffer = None #{"optype": None, "result": 0, "address": '00', "dest_reg": 1, "jump": False, "new_pc": 2}
        self.DecodeBuffer = None
        self.FetchBuffer = None
    
    def clock(self):
    	running=self.WriteBack(self.MemBuffer)
    	self.MemBuffer = self.Memory(self.ExecBuffer)
    	self.ExecBuffer = self.Execution(self.DecodeBuffer)
    	self.DecodeBuffer = self.IntstructionDecode(self.FetchBuffer)
    	self.FetchBuffer = self.InstructionFetch()
    	return running
    
    
    	
    def InstructionFetch(self):
    	if self.stall in [1,3]:
    		return None
    	elif self.stall==2:
    		return self.FetchBuffer()
    	else
    		cache_out = ICache.read(int_to_bin(self.pc))
    		self.pc+=2
        	return {"inst": cache_out}
       
    
    
    def InstructionDecode(self, FetchBuffer):
    	if self.stall==3:
    		return None
    	else
    		opcode = int(MemBuffer[inst][0:4], 2)
        	dest_ind = None
        	a_ind = None
        	b_ind = None
        	a=None
        	b=None
        	
        	 #todo: change it for jmp and bneq instr
	        immval = None

        	if opcode>11:
        		self.stall=3
        		return None
        	elif opcode==10:
        		immval = bin_to_signed(FetchBuffer[inst][8:16] + '0', 9)
        	elif opcode==11:
        		a_ind = int(instr[4:8], 2)
        		immval = bin_to_signed(FetchBuffer[inst][8:16] + '0', 9)
        	else:
        		dest_ind = int(FetchBuffer[inst][4:8], 2)
        		if opcode == 3:
	        		a_ind = int(FetchBuffer[inst][4:8], 2)
        		elif opcode == 6:
        			a_ind = int(FetchBuffer[inst][8:12], 2)
        		elif opcode <=9:
        			a_ind = int(FetchBuffer[inst][8:12], 2)
        			b_ind = int(FetchBuffer[inst][12:16], 2)
        	    
        	if a_ind!=None:
        		if self.register_file[a_ind]["busy"] == True:
        			self.stall = 2
        			return None
        		else:
        			a=self.register_file[a_ind]["data"]

        	
        	if b!=None:
        		if self.register_file[b_ind]["busy"] == True:
        			self.stall = 2
        			return None
        		else:
        			a=self.register_file[b_ind]["data"]
        	
        	if opcode>=10:
        		self.stall=1
        	
        	if self.stall==2:
        		self.stall=0
        	
        	if dest_ind!=None:
        		self.register_file[dest_ind]["busy"] = True
        		
        	return {"opcode": opcode, "dest_ind": dest_ind,
                "a": a, "b": b, "imm": immval}
    	
    
    def Execution(self, DecodeBuffer):
    	if DecodeBuffer==None:
    		return None
    	else:
    		result=None
    		
    		if DecodeBuffer["opcode"] in [0,8,9]:
            		result = DecodeBuffer["a"]+DecodeBuffer["b"]
            	elif DecodeBuffer["opcode"]==1:
            		result = DecodeBuffer["a"]-DecodeBuffer["b"]
            	elif DecodeBuffer["opcode"]==2:
            		result = DecodeBuffer["a"]*DecodeBuffer["b"]
            	elif DecodeBuffer["opcode"]==3:
            		result = DecodeBuffer["a"]+1
            	elif DecodeBuffer["opcode"]==4:
            		result = DecodeBuffer["a"]&DecodeBuffer["b"]
            	elif DecodeBuffer["opcode"]==5:
            		result = DecodeBuffer["a"]|DecodeBuffer["b"]
            	elif DecodeBuffer["opcode"]==6:
            		result = ~DecodeBuffer["a"]
            	elif DecodeBuffer["opcode"]==7:
            		result = DecodeBuffer["a"]^DecodeBuffer["b"]
            	elif DecodeBuffer["opcode"]==10:
            		result = self.pc+DecodeBuffer["immval"]
            	elif DecodeBuffer["a"]==0:
            		result = self.pc+DecodeBuffer["immval"]
            	else
            		result = self.pc
            	
            	return {"opcode": opcode, "dest_ind": dest_ind,
                "result": result}
	
    
    def Memory(self, ExecBuffer):
    	if ExecBuffer==None:
    		return None
    	else:
    		if opcode>=10:
    			self.pc = ExecBuffer["result"]
    			if self.stall==1:
    				self.stall=0
    		elif opcode=8:
    			self.register_file[ExecBuffer["dest_ind"]]["data"]=#Reading from result address
    			self.register_file[ExecBuffer["dest_ind"]]["busy"]=False
    		elif opcode=9:
    			#Writing to result address from dest_ind
    		return ExecBuffer
    		
    def WriteBack(self, MemBuffer):
    	if MemBuffer==None:
    		if self.FetchBuffer==None and self.DecodeBuffer=None:
    			return False
    	else:
    		if opcode<=7:
    			self.register_file[MemBuffer["dest_ind"]]["data"]=result
    			self.register_file[ExecBuffer["dest_ind"]]["busy"]=False
    		return True
    		
	
