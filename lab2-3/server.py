import socket
import threading
import base64
import logging
from datetime import datetime
from stream_cipher import StreamCipher

HOST = '127.0.0.1'
PORT = 27490
BLOCK_SIZE = 4096
VARIANT = '10'

logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s -%(levelname)s - %(message)s',
	handlers=[
		logging.FileHandler('server.log'),
		logging.StreamHandler()
	]
)

class Server:
	def __init__(self) -> None:
		self.server_socket = None
		self.running = False
		self.cipher = StreamCipher()
		self.client_count = 0

		logging.info('Server initialized')
	
	def start_server(self) -> None:
		try:
			self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.server_socket.bind((HOST, PORT))
			self.server_socket.listen(128)
			self.running = True

			logging.info(f"Server started on {HOST}:{PORT}")

			while self.running:
				try:
					client_socket, addr = self.server_socket.accept()
					self.client_count += 1
					thread_id = self.client_count

					logging.info(f"Client {addr} is connected. Thread: {thread_id}")

					client_thread = threading.Thread(
						target=self.handle_client,
						args=(client_socket, addr, thread_id),
						daemon=True
					)
					client_thread.start()
				except Exception as e:
					if self.running:
						logging.error(f"An error occurred while accepting a connection: {e}")
		except Exception as e:
			logging.error(f"An error while starting the server: {e}")
		finally:
			self.stop_server()
	
	def stop_server(self) -> None:
		self.running = False

		if self.server_socket:
			self.server_socket.close()
		logging.info("Server stopped")
	
	def handle_client(self, client_socket: socket.socket, addr: tuple[str, int], thread_id: int) -> None:
		client_info = f"{addr} (thread {thread_id})"

		try:
			client_socket.send(b"")

			while True:
				command_line = self.recv_line(client_socket)
				if not command_line:
					break

				command_line = command_line.strip()
				if not command_line:
					continue

				logging.info(f"Client {client_info}: recieved command - {command_line}")

				response = self.process_command(command_line, client_socket, client_info)

				if response == 'DISCONNECT':
					break
		except ConnectionResetError:
			logging.info(f"Client {client_info} disconnected")
		except Exception as e:
			logging.error(f"An error occurred: {e}")
		finally:
			client_socket.close()
			logging.info(f"Client {client_info} connection closed")
	
	def recv_line(self, socket: socket.socket) -> str | None:
		buffer = b""
		
		while not buffer.endswith(b'\n'):
			data = socket.recv(1)
			if not data:
				return None
			buffer += data
		
		return buffer.decode('utf-8', errors='ignore')
	
	def process_command(self, command_line: str, client_socket: socket.socket, client_info: str) -> str | None:
		parts = command_line.split()
		
		if not parts:
			client_socket.send(b"unknown command\n")
			return None
		
		command = parts[0].lower()

		try:
			if command == 'hello':
				return self.handle_hello(parts, client_socket, client_info)
			elif command == 'bye':
				return self.handle_bye(parts, client_socket, client_info)
			elif command == 'encrypt':
				return self.handle_encrypt_decrypt(parts, client_socket, client_info, encrypt=True)
			elif command == 'decrypt':
				return self.handle_encrypt_decrypt(parts, client_socket, client_info, encrypt=False)
			else:
				client_socket.send(b"unknown command\n")
				return None
		except Exception as e:
			error_msg = f"Command execution error: {str(e)}\n"
			client_socket.send(error_msg.encode())
			logging.error(f"Command execution error for {client_info}: {e}")
			return None
	
	def handle_hello(self, parts: list[str], client_socket: socket.socket, client_info: str) -> None:
		if len(parts) < 2 or parts[1] != VARIANT:
			client_socket.send(f"Usage: hello {VARIANT}\n".encode())
			return None

		response = f"hello variant {VARIANT}\n"
		client_socket.send(response.encode())
		logging.info(f"Client {client_info} is registered")
	
	def handle_bye(self, parts: list[str], client_socket: socket.socket, client_info: str) -> str | None:
		if len(parts) < 2 or parts[1] != VARIANT:
			client_socket.send(f"Usage: bye {VARIANT}\n".encode())
			return None
		
		response = f"bye variant {VARIANT}\n"
		client_socket.send(response.encode())
		logging.info(f"Client {client_info} is disconnected")
		
		return "DISCONNECT"
	
	def handle_encrypt_decrypt(self, parts: list[str], client_socket: socket.socket, client_info: str, encrypt: bool) -> str | None:
		if len(parts) < 3:
			client_socket.send(b"Usage: encrypt|decrypt text|file <key> [data]\n")
			return None
		
		operation = 'encrypt' if encrypt else 'decrypt'
		target_type = parts[1].lower()
		key = parts[2]

		if target_type == 'text':
			return self.handle_text_operation(parts, client_socket, client_info, key, encrypt, operation)
		elif target_type == 'file':
			return self.handle_file_operation(client_socket, client_info, key, encrypt, operation)
		else:
			client_socket.send(b"Unknown target type. Use 'text or 'file'\n")
			return None
	
	def handle_text_operation(
			self,
			parts: list[str],
			client_socket: socket.socket,
			client_info: str,
			key: str,
			encrypt: bool,
			operation: str
	) -> None:
		if len(parts) < 4:
			client_socket.send(b"Insufficient parameters for text operation\n")
			return None
		
		text_data = " ".join(parts[3:])

		try:
			logging.info(f"Client {client_info}: {operation} of text, length: {len(text_data)}")

			if encrypt:
				encrypted_data = self.cipher.encrypt_decrypt_data(text_data.encode('utf-8'), key)
				result = base64.b64encode(encrypted_data).decode('utf-8')
			else:
				encrypted_bytes = base64.b64decode(text_data)
				decrypted_data = self.cipher.encrypt_decrypt_data(encrypted_bytes, key)
				result = decrypted_data.decode('utf-8', errors='ignore')
			
			client_socket.send(f"{result}\n".encode())
			logging.info(f"Client {client_info}: {operation} of text is done")
		except Exception as e:
			error_msg = f"An error occurred during {operation}: {str(e)}"
			client_socket.send(error_msg.encode())
			logging.error(f"{operation} of text error for {client_info}: {e}")

	def handle_file_operation(
			self,
			client_socket: socket.socket,
			client_info: str,
			key: str,
			encrypt: bool,
			operation: str
	) -> None:
		try:
			client_socket.send(b"READY\n")
			
			size_bytes = client_socket.recv(8)
			if len(size_bytes) != 8:
				raise ValueError("Incorrect file size")
			
			file_size = int.from_bytes(size_bytes, 'big')
			logging.info(f"Client {client_info}: {operation} of file, size: {file_size} bytes")

			received_data = b""

			while len(received_data) < file_size:
				chunk = client_socket.recv(min(BLOCK_SIZE, file_size - len(received_data)))
				if not chunk:
					break
				received_data += chunk
			
			if len(received_data) != file_size:
				raise ValueError(f"Got {len(received_data)} bytes instead {file_size}")
			
			processed_data = self.cipher.encrypt_decrypt_data(received_data, key)

			client_socket.send(b"DONE\n")
			client_socket.send(len(processed_data).to_bytes(8, 'big'))
			client_socket.send(processed_data)

			logging.info(f"Client {client_info}: {operation} of file completed, result: {len(processed_data)} byte")
		except Exception as e:
			error_msg = f"An error occured during {operation}: {str(e)}"
			client_socket.send(error_msg.encode())
			logging.error(f"{operation} of text error for {client_info}: {e}")

def main() -> None:
	server = Server()

	try:
		server.start_server()
	except KeyboardInterrupt:
		server.stop_server()


if __name__ == "__main__":
	main()
