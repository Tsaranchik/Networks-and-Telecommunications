import hashlib
import os
from Crypto.Cipher import DES


class Generator:
	"""
	Класс, объединяющий различные генераторы псевдослучайных битовых последовательностей:
	- Квадратичный конгруэнтный генератор (Quadratic Congruential Generator),
	- Генератор Блюма-Блюма-Шуба (BBS),
	- Генератор Yarrow-160.
	"""	
	class Yarrow160:
		"""
		Реализация криптографического генератора Yarrow-160.

		Генератор основан на идее периодического обновления ключа K и счётчика C
		с использованием блочного шифра (DES) и хеш-функции (SHA-1)
		"""
		def __init__(
				self,
				seed = None,
				n: int = 64,
				k: int = 64,
				Pg: int = 10,
				Pt: int = 20
		) -> None:
			"""
			Инициализирует параметры генератора Yarrow-160.

			Args:
				n: размер блока (бит)
				k: рзамер ключа (бит)
				Pg: порог обновления ключа K
				Pt: порог обновления ключа и счётчика
			"""
			self.n = n
			self.k = k
			self.Pg = Pg
			self.Pt = Pt
			self.curPg = Pg
			self.curPt = Pt
			self.C = 0
			self.t = 0
			self.counter = 0

			if seed is not None:
				if isinstance(seed, int):
					seed_bytes = seed.to_bytes(16, 'big')
				elif isinstance(seed, str):
					seed_bytes = seed.encode('utf-8')
				elif isinstance(seed, bytes):
					seed_bytes = seed
				else:
					try:
						seed_bytes = str(seed).encode('utf-8')
					except:
						seed_bytes = os.urandom(16)
				
				self.K = hashlib.sha1(seed_bytes).digest()[:8]
			else:
				self.K = b'\x01' * 8

				
		def entropy_accumulator(self) -> bytes:
			"""
			Имитация наколепния энтропии.

			Генерирует псевдослучайные данные на основе системного времени, 
			PID процесса и случайных байт.

			Returns:
				bytes: SHA-1 хеш от собранных жнтропийных данных
			"""
			self.counter += 1
			data = self.K + self.C.to_bytes(8, 'big') + self.counter.to_bytes(8, 'big')
			return hashlib.sha1(data).digest()

		
		def update_key(self) -> None:
			"""
			Обновляет внутренний ключ K и счётчик C на сонове новой энтропии.
			"""
			entropy = self.entropy_accumulator()
			self.K = hashlib.sha1(self.K + entropy).digest()[:8]
			self.C = (self.C + 1) % (2 ** self.n)
		
		def encrypt_block(self, data: bytes) -> bytes:
			"""
			Шифрует блок данных с помощью DES в режиме ECB.

			Args:
				data: байты длиной 8 байт.
			
			Returns:
				bytes: зашифрованный блок длиной 8 байт
			"""
			cipher = DES.new(self.K, DES.MODE_ECB)
			return cipher.encrypt(data)
		
		def H(self, v: bytes, K: bytes) -> bytes:
			"""
			Хеш-функция H(v, K) = SHA-1(v || K)[:8].

			Args:
				v: байтовая последовательность
				k: ключ
			
			Returns:
				bytes: результат хеширования длиной 8 байт
			"""
			return hashlib.sha1(v + K).digest()[:8]
		
		def G(self, i: int) -> bytes:
			"""
			Функция G(i), генерирующая новые данные для ключа.

			Args:
				i: индекс итерации

			Returns:
				bytes: результат шифрования счётчика длиной 8 байт

			"""
			Ci = (self.C + i) % (2 ** self.n)
			Ci_bytes = Ci.to_bytes(8, "big")
			return self.encrypt_block(Ci_bytes)
		
		def generate_bits(self, seq_len: int = 10000):
			"""
			Генерирует псевдослучайную битовую последовательность.

			Args:
				seq_len: требуемая длина последовательности (по умолчанию 10000)
			
			Returns:
				List[int]: список битов (0 и 1)
			"""
			bit_seq = []

			while len(bit_seq) < seq_len:
				if self.curPg == 0:
					self.K = self.G(self.C)
					self.curPg = self.Pg
				
				if self.curPt == 0:
					v0 = hashlib.sha1(self.entropy_accumulator() + self.K).digest()[:8]
					v = v0
					for _ in range(2):
						v = hashlib.sha1(v + v0 + self.K).digest()[:8]
					self.K = self.H(v, self.K)
					self.update_key()
					self.curPt = self.Pt
				
				xi = self.encrypt_block(self.C.to_bytes(8, "big"))
				self.C = (self.C + 1) % (2 ** self.n)
				self.curPg -= 1
				self.curPt -= 1

				for byte in xi:
					for bit in range(8):
						bit_seq.append((byte >> (7 - bit)) & 1)
						if len(bit_seq) >= seq_len:
							break
					if len(bit_seq) >= seq_len:
						break
			
			return bit_seq
	
	def yarrow160_generator(self,  seq_len: int = 10000, seed: bytes = None) -> list[int]:
		"""
		Интерфейсная функция для генерации последовательности Yarrow-160.

		Создаёт экземпляр внутреннего класса Yarrow160 и вызывает метод generate_bits.

		Args:
			seq_len: длина генерируемой последовательности (по умолчанию 10000)
		
		Returns:
			List[int]: список битов (0 и 1)
		"""
		gen = self.Yarrow160(seed=seed)
		
		return gen.generate_bits(seq_len)
		
