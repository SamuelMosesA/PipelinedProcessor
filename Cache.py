class Cache:
    def __init__(self, filename, icache):
        self.cache = []
        self.used_read_port = 0
        self.used_write_port = 0
        self.icache = icache
        with open(filename, 'r') as file:
            for i in range(64):
                four_bytes = [file.readline() for i in range(4)]
                self.cache.append(four_bytes)

    def read(self, address: str) -> (int, bool):
        if self.used_read_port == 2:
            return 0, False
        self.used_read_port += 1
        block_index = int(address[:-2], 2)
        block_offset = int(address[-2:], 2)
        cache_block = self.cache[block_index]
        if not self.icache:
            return {"data": cache_block[block_offset], "status": True}
        else:
            return {"data": cache_block[block_offset] + cache_block[block_offset + 1], "status": True}

    def close_read(self):
        self.used_read_port -= 1

    def write(self, address: str, data: str):
        if self.used_write_port == 1 or not self.icache:
            return False
        self.used_read_port += 1
        block_index = int(address[:-2], 2)
        block_offset = int(address[-2:], 2)
        self.cache[block_index][block_offset] = data
        return True

    def close_write(self):
        self.used_write_port -= 1


DCache = Cache("DCache.txt", False)
ICache = Cache("ICache.txt", True)
