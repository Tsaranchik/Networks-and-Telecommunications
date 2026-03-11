class HashFunctions:
	@staticmethod
	def gost_341194_hash(data: bytes) -> bytes:
		BLOCK_SIZE = 32
		h = bytearray([0] * BLOCK_SIZE)
		N = bytearray([0] * BLOCK_SIZE)
		Sigma = bytearray([0] * BLOCK_SIZE)
		original_len = len(data)
		data = bytearray(data)
		data.append(0x01)

		while len(data) % BLOCK_SIZE != 0:
			data.append(0x00)
		
		for i in range(0, len(data), BLOCK_SIZE):
			block = data[i:i + BLOCK_SIZE]
			h = HashFunctions._gost_compression_function(h, block, N, Sigma)
			
			N = HashFunctions._add_mod_2_512(N, [BLOCK_SIZE * 8] * BLOCK_SIZE)
			Sigma = HashFunctions._add_mod_2_512(Sigma, [int(b) for b in block])
		
		return bytes(h)
	
	@staticmethod
	def _gost_compression_function(
		h: bytearray,
		m: bytes,
		N: bytearray,
		Sigma: bytearray
	) -> bytearray:
		keys = HashFunctions._gost_key_schedule(h, N)
		result = bytearray(32)

		for i in range(4):
			block_start = i * 8
			block_end = block_start + 8
			data_block = m[block_start:block_end]
			h_block = h[block_start:block_end]

			transformed = HashFunctions._gost_transform_block(data_block, keys)

			for j in range(8):
				result[block_start + j] = transformed[j] ^ h_block[j]
		
		return result
		
	@staticmethod
	def _gost_key_schedule(K: bytearray, N: bytearray) -> list:
		keys = []

		k_blocks = [K[i:i + 8] for i in range(0, 32, 8)]
		n_blocks = [N[i:i + 8] for i in range(0, 32, 8)]

		for round_num in range(32):
			if round_num < 8:
				key_source = k_blocks
				key_index = round_num % 4
			else:
				key_source = n_blocks
				key_index = (round_num // 4) % 4
			
			key = bytearray(key_source[key_index])
			key[0] ^= round_num
			key[7] ^= 0xFF - round_num

			keys.append(bytes(key))
		
		return keys
	
	@staticmethod
	def _gost_transform_block(block: bytes, keys: list) -> bytes:
		state = bytearray(block)

		for round_num in range(32):
			key = keys[round_num]
			
			for j in range(8):
				state[j] ^= key[j]
			
			for j in range(8):
				state[j] = HashFunctions._gost_sbox(state[j])
			
			state = HashFunctions._gost_rotate_left(state, 11)
		
		return bytes(state)

	@staticmethod
	def _gost_sbox(value: int) -> int:
		return (value * 17 + 173) & 0xFF

	@staticmethod
	def _gost_rotate_left(data: bytearray, bits: int) -> bytearray:
		result = bytearray(len(data))
		byte_shift = bits // 8
		bit_shft = bits % 8

		for i in range(len(data)):
			byte1 = data[(i - byte_shift) % len(data)]
			byte2 = data[(i - byte_shift - 1) % len(data)]
			result[i] = ((byte1 << bit_shft) | (byte2 >> (8 - bit_shft))) & 0xFF
		
		return result

	
	@staticmethod
	def _add_mod_2_512(a: bytearray, b: list) -> bytearray:
		result = bytearray(32)
		carry = 0
		
		for i in range(31, -1, -1):
			total = a[i] + b[i] + carry
			result[i] = total & 0xFF
			carry = total >> 8
		
		return result
		