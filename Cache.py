from util import int_to_bin


class Cache:
    def __init__(self, filename, icache):
        self.cache = []
        self.icache = icache
        with open(filename, 'r') as file:
            for i in range(64):
                four_bytes = [int(file.readline(), 16) for i in range(4)]
                self.cache.append(four_bytes)

    def read(self, address: str) -> str:
        block_index = int(address[:-2], 2)
        block_offset = int(address[-2:], 2)
        cache_block = self.cache[block_index]
        if not self.icache:
            return int_to_bin(cache_block[block_offset])
        else:
            return int_to_bin(cache_block[block_offset]) + int_to_bin(cache_block[block_offset + 1])

    def write(self, address: str, data: int):
        block_index = int(address[:-2], 2)
        block_offset = int(address[-2:], 2)
        self.cache[block_index][block_offset] = data


DCache = Cache("DCache.txt", False)
ICache = Cache("ICache.txt", True)
