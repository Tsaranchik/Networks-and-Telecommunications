from typing import Callable
from generator import Generator
from hash_functions import HashFunctions
import hashlib

class StreamCipher:
	def __init__(self) -> None:
		self.generator = Generator()
		self.hash_func = HashFunctions()

	def encrypt_decrypt_data(self, data: bytes, password) -> bool:
		try:
			key = self._generate_key_from_password(password)
			keystream = self._generate_keystream(len(data), key, password)
			result = bytearray()

			for i, byte in enumerate(data):
				result.append(byte ^ keystream[i % len(keystream)])
			
			return bytes(result)
		except Exception as e:
			print(f"Error: {e}")
			return b""
	
	def _generate_key_from_password(self, password: str) -> bytes:
		password_bytes = password.encode('utf-8')
		return self.hash_func.gost_341194_hash(password_bytes)
	
	def _generate_keystream(self, length: int, key: bytes, password: str) -> bytes:
		seed_data = password.encode() + key
		seed_bytes = hashlib.sha256(seed_data).digest()

		needed_bits = int(length * 8 * 1.1)
		bits = self.generator.yarrow160_generator(needed_bits, seed_bytes)

		keystream = self._bits_to_bytes(bits)

		return keystream[:length]
	
	def _bits_to_bytes(self, bits: list) -> bytes:
		bytes_list = []

		num_bytes = len(bits) // 8

		for i in range(num_bytes):
			byte = 0
			for j in range(8):
				if i + j < len(bits):
					byte = (byte << 1) | bits[i * 8 + j]
			bytes_list.append(byte)
		
		return bytes(bytes_list)
