import sys
import socket
import os
import base64
from typing import Any
from datetime import datetime
from PyQt6.QtWidgets import (
	QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
	QLineEdit, QPushButton, QTextEdit, QFileDialog, QMessageBox,
	QGroupBox, QTabWidget, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, QMetaObject, Qt, Q_ARG, pyqtSlot
from PyQt6.QtCore import pyqtSignal as Signal

BLOCK_SIZE = 4096
VARIANT = '10'

class FileOperationThread(QThread):
	operation_started = Signal(str)
	operation_progress = Signal(int)
	operation_finished = Signal(str, bool)
	save_path_request = Signal(str, bool)

	def __init__(self, sock: socket.socket, key: str, operation_type: str, file_path: str) -> None:
		super().__init__()
		self.sock = sock
		self.key = key
		self.operation_type = operation_type
		self.file_path = file_path
		self.save_path: str | None = None

	def run(self) -> None:
		try:
			self.operation_started.emit(f"Starting {self.operation_type} operation...")

			is_encryption = 'encrypt' in self.operation_type
			self.save_path_request.emit(self.file_path, is_encryption)

			for _ in range(300):
				if self.save_path is not None:
					break
				self.msleep(100)

			if not self.save_path:
				self.operation_finished.emit("Save operation cancelled", False)
				return

			if 'encrypt' in self.operation_type:
				self.perform_encryption()
			else:
				self.perform_decryption()
			
			self.operation_finished.emit(f"File saved to: {self.save_path}", True)
		except Exception as e:
			self.operation_finished.emit(f"Error: {str(e)}", False)
	
	def perform_encryption(self) -> None:
		filename = os.path.basename(self.file_path)
		command = f"encrypt file {self.key} {filename}\n"
		self.sock.sendall(command.encode())

		response = self.receive_line()
		if "READY" not in response:
			raise Exception("Server is not ready")
		
		with open(self.file_path, 'rb') as f:
			file_data = f.read()
		
		self.sock.sendall(len(file_data).to_bytes(8, 'big'))
		self.sock.sendall(file_data)

		response = self.receive_line()
		if "DONE" not in response:
			raise Exception("Server processing error")
		
		size_bytes = self.sock.recv(8)
		if len(size_bytes) != 8:
			raise Exception("Invalid result size")
		
		result_size = int.from_bytes(size_bytes, 'big')
		received_data = self.receive_data(result_size)

		with open(self.save_path, 'wb') as f:
			f.write(received_data)
	
	def perform_decryption(self) -> None:
		filename = os.path.basename(self.file_path)
		command = f"decrypt file {self.key} {filename}\n"
		self.sock.sendall(command.encode())

		response = self.receive_line()
		if "READY" not in response:
			raise Exception("Server is not ready")
		
		with open(self.file_path, 'rb') as f:
			file_data = f.read()
		
		self.sock.sendall(len(file_data).to_bytes(8, 'big'))
		self.sock.sendall(file_data)

		response = self.receive_line()
		if "DONE" not in response:
			raise Exception("Server processing error")
		
		size_bytes = self.sock.recv(8)
		if len(size_bytes) != 8:
			raise Exception("Invalid result size")
		
		result_size = int.from_bytes(size_bytes, 'big')
		received_data = self.receive_data(result_size)

		with open(self.save_path, 'wb') as f:
			f.write(received_data)
	
	def receive_line(self) -> str:
		buffer = b""
		
		while not buffer.endswith(b"\n"):
			data = self.sock.recv(1)
			if not data:
				return ""
			buffer += data
		
		return buffer.decode('utf-8', errors='ignore').strip()

	def receive_data(self, size: int) -> bytes:
		received_data = b""
		
		while len(received_data) < size:
			chunk = self.sock.recv(min(BLOCK_SIZE, size - len(received_data)))
			if not chunk:
				break
			received_data += chunk
			progress = int((len(received_data) / size) * 100)
			self.operation_progress.emit(progress)
		
		return received_data

	def set_save_path(self, path: str) -> None:
		self.save_path = path


class Client(QWidget):
	def __init__(self) -> None:
		super().__init__()
		self.sock: socket.socket | None = None
		self.current_thread: FileOperationThread | None = None
		self.current_file_path: str | None = None

		self.host_input: QLineEdit
		self.port_input: QLineEdit
		self.key_input: QLineEdit
		self.connect_btn: QPushButton
		self.disconnect_btn: QPushButton
		self.text_input: QTextEdit
		self.encrypt_text_btn: QPushButton
		self.decrypt_text_btn: QPushButton
		self.file_path_label: QLabel
		self.select_file_btn: QPushButton
		self.encrypt_file_btn: QPushButton
		self.decrypt_file_btn: QPushButton
		self.log_output: QTextEdit

		self.init_ui()
	
	def init_ui(self) -> None:
		self.setWindowTitle(f"Encryption Client - Variant {VARIANT}")
		self.resize(800, 700)

		main_layout = QVBoxLayout()

		connection_group = QGroupBox('Server Connection')
		connection_layout = QVBoxLayout()

		host_port_layout = QHBoxLayout()
		host_port_layout.addWidget(QLabel("Host:"))
		self.host_input = QLineEdit("127.0.0.1")
		host_port_layout.addWidget(self.host_input)
		host_port_layout.addWidget(QLabel('Port:'))
		self.port_input = QLineEdit("27490")
		host_port_layout.addWidget(self.port_input)
		connection_layout.addLayout(host_port_layout)

		key_layout = QHBoxLayout()
		key_layout.addWidget(QLabel("Encryption Key:"))
		self.key_input = QLineEdit()
		self.key_input.setPlaceholderText("Enter key for encryption/decryption")
		self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
		key_layout.addWidget(self.key_input)
		connection_layout.addLayout(key_layout)

		button_layout = QHBoxLayout()
		self.connect_btn = QPushButton("Connect")
		self.connect_btn.clicked.connect(self.connect_to_server)
		self.disconnect_btn = QPushButton("Disconnect")
		self.disconnect_btn.clicked.connect(self.disconnect_from_server)
		self.disconnect_btn.setEnabled(False)

		button_layout.addWidget(self.connect_btn)
		button_layout.addWidget(self.disconnect_btn)
		button_layout.addStretch()
		connection_layout.addLayout(button_layout)

		connection_group.setLayout(connection_layout)
		main_layout.addWidget(connection_group)

		self.progress_bar = QProgressBar()
		self.progress_bar.setVisible(False)
		main_layout.addWidget(self.progress_bar)

		tabs = QTabWidget()
		text_tab = QWidget()
		text_layout = QVBoxLayout()

		text_layout.addWidget(QLabel("Text for processing:"))
		self.text_input = QTextEdit()
		self.text_input.setPlaceholderText("Enter text for encryption or encrypted text for decryption...")
		text_layout.addWidget(self.text_input)

		text_buttons_layout = QHBoxLayout()
		self.encrypt_text_btn = QPushButton("Encrypt Text")
		self.encrypt_text_btn.clicked.connect(lambda: self.send_text_operation(True))
		self.encrypt_text_btn.setEnabled(False)

		self.decrypt_text_btn = QPushButton("Decrypt Text")
		self.decrypt_text_btn.clicked.connect(lambda: self.send_text_operation(False))
		self.decrypt_text_btn.setEnabled(False)

		text_buttons_layout.addWidget(self.encrypt_text_btn)
		text_buttons_layout.addWidget(self.decrypt_text_btn)
		text_buttons_layout.addStretch()
		text_layout.addLayout(text_buttons_layout)

		text_tab.setLayout(text_layout)
		tabs.addTab(text_tab, "Text")

		file_tab = QWidget()
		file_layout = QVBoxLayout()

		file_info_layout = QHBoxLayout()
		self.file_path_label = QLabel("No file selected")
		self.file_path_label.setStyleSheet("color: gray;")
		file_info_layout.addWidget(self.file_path_label)
		file_info_layout.addStretch()

		self.select_file_btn = QPushButton("Select File")
		self.select_file_btn.clicked.connect(self.select_file)
		file_info_layout.addWidget(self.select_file_btn)
		file_layout.addLayout(file_info_layout)
		

		file_buttons_layout = QHBoxLayout()
		self.encrypt_file_btn = QPushButton("Ecnrypt File")
		self.encrypt_file_btn.clicked.connect(lambda: self.start_file_operation(True))
		self.encrypt_file_btn.setEnabled(False)

		self.decrypt_file_btn = QPushButton("Decrypt File")
		self.decrypt_file_btn.clicked.connect(lambda: self.start_file_operation(False))
		self.decrypt_file_btn.setEnabled(False)

		file_buttons_layout.addWidget(self.encrypt_file_btn)
		file_buttons_layout.addWidget(self.decrypt_file_btn)
		file_buttons_layout.addStretch()
		file_layout.addLayout(file_buttons_layout)

		file_tab.setLayout(file_layout)
		tabs.addTab(file_tab, "Files")

		main_layout.addWidget(tabs)

		main_layout.addWidget(QLabel("Operation Log:"))
		self.log_output = QTextEdit()
		self.log_output.setReadOnly(True)
		main_layout.addWidget(self.log_output)

		self.setLayout(main_layout)
	
	def log_message(self, message: str) -> None:
		self.log_output.append(f"[{self.get_current_time()}] {message}")
	
	def get_current_time(self) -> str:
		return datetime.now().strftime("%H:%M:%S")
	
	def connect_to_server(self) -> None:
		host = self.host_input.text()

		try:
			port = int(self.port_input.text())
		except ValueError:
			QMessageBox.warning(self, "Error", "Port must be a number")
			return

		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect((host, port))

			self.sock.sendall(f"hello {VARIANT}\n".encode())
			response = self.recv_response()
			self.log_message(f"Connected to server: {response}")
			
			self.set_operations_enabled(True)
			self.connect_btn.setEnabled(False)
			self.disconnect_btn.setEnabled(True)
		except Exception as e:
			QMessageBox.critical(self, "Error", f"Failed to connect: {str(e)}")
			if self.sock:
				self.sock.close()
				self.sock = None
		
	def disconnect_from_server(self) -> None:
		if self.sock:
			try:
				self.sock.sendall(f"bye {VARIANT}\n".encode())
				response = self.recv_response()
				self.log_message(f"Disconnected from server: {response}")
			except:
				pass
			self.sock.close()
			self.sock = None
		
		self.set_operations_enabled(False)
		self.connect_btn.setEnabled(True)
		self.disconnect_btn.setEnabled(False)
		self.log_message("Connection closed")
	
	def set_operations_enabled(self, enabled: bool) -> None:
		self.encrypt_text_btn.setEnabled(enabled)
		self.decrypt_text_btn.setEnabled(enabled)
		self.encrypt_file_btn.setEnabled(enabled and self.current_file_path is not None)
		self.decrypt_file_btn.setEnabled(enabled and self.current_file_path is not None)
	
	def recv_line(self) -> str | None:
		if not self.sock:
			return None
		
		buffer = b""
		
		while not buffer.endswith(b"\n"):
			data = self.sock.recv(1)
			if not data:
				return None
			buffer += data
		
		return buffer.decode('utf-8', errors='ignore').strip()
	
	def recv_response(self) -> str:
		response = self.recv_line()
		
		return response if response else "No response"
	
	def send_text_operation(self, encrypt: bool) -> None:
		if not self.sock:
			QMessageBox.warning(self, "Error", "No connection to server")
			return

		text = self.text_input.toPlainText().strip()
		if not text:
			QMessageBox.warning(self, "Error", "Enter text for processing")
			return
		
		key = self.key_input.text().strip()
		if not key:
			QMessageBox.warning(self, "Error", "Enter encryption key")
			return

		operation = "encrypt" if encrypt else "decrypt"

		try:
			command = f"{operation} text {key} {text}\n"
			self.sock.sendall(command.encode())
			response = self.recv_response()

			if encrypt:
				self.log_message("Text encrypted")
				self.save_text_result(response, ".encrypted.txt")
			else:
				self.log_message("Text decrypted")
				self.text_input.setPlainText(response)
		except Exception as e:
			QMessageBox.critical(self, "Error", f"Error processing text: {str(e)}")
			self.disconnect_from_server()
	
	def select_file(self) -> None:
		file_path, _ = QFileDialog.getOpenFileName(self, "Select File")

		if file_path:
			self.current_file_path = file_path
			self.file_path_label.setText(os.path.basename(file_path))
			self.file_path_label.setStyleSheet("color: black;")
			self.set_operations_enabled(self.sock is not None)

	def start_file_operation(self, encrypt: bool) -> None:
		if not self.current_file_path:
			QMessageBox.warning(self, "Error", "Select a file")
			return

		if not self.key_input.text().strip():
			QMessageBox.warning(self, "Error", "Enter encryption key")
			return
		
		self.set_operations_enabled(False)
		self.progress_bar.setVisible(True)
		self.progress_bar.setValue(0)

		operation_type = "file_encrypt" if encrypt else "file_decrypt"
		self.current_thread = FileOperationThread(
			self.sock,
			self.key_input.text().strip(),
			operation_type,
			self.current_file_path
		)

		self.current_thread.operation_started.connect(self.log_message)
		self.current_thread.operation_progress.connect(self.progress_bar.setValue)
		self.current_thread.operation_finished.connect(self.on_file_operation_done)
		self.current_thread.save_path_request.connect(self.get_save_path)

		self.current_thread.start()

		self.log_message("File processing started...")
	
	@pyqtSlot(str, bool)
	def get_save_path(self, file_path: str, is_encryption: bool) -> None:
		directory = os.path.dirname(file_path)
		filename = os.path.basename(file_path)

		if is_encryption:
			name_without_ext, original_ext = os.path.splitext(filename)
			if original_ext:
				suggested_name = f"{name_without_ext}{original_ext}.encrypted"
			else:
				suggested_name = f"{filename}.encrypted"
		else:
			if filename.endswith('.encrypted'):
				suggested_name = filename[:-10]
			else:
				name_without_ext, _ = os.path.splitext(filename)
				suggested_name = f"{name_without_ext}.decrypted"
		
		suggested_path = os.path.join(directory, suggested_name)

		save_path, _ = QFileDialog.getSaveFileName(
			self,
			'Save Result',
			suggested_path,
			"All Files (*.*)"
		)

		if save_path and self.current_thread:
			self.current_thread.set_save_path(save_path)
		else:
			if self.current_thread:
				self.current_thread.terminate()
				self.current_thread.wait()
				self.log_message("Operation canceled by user")
				self.set_operations_enabled(True)
				self.progress_bar.setVisible(False)

	def on_file_operation_done(self, message: str, success: bool) -> None:
		if success:
			self.log_message(message)
		else:
			QMessageBox.critical(self, "Error", message)
			self.log_message(f"Error: {message }")
		
		self.set_operations_enabled(True)
		self.progress_bar.setVisible(False)

		if self.current_thread:
			self.current_thread.quit()
			self.current_thread.wait()
			self.current_thread = None
		
	def save_text_result(self, result: str, extension: str) -> None:
		save_path, _ = QFileDialog.getSaveFileName(
			self,
			"Save Encrypted Text",
			f"encrypted_text{extension}",
			"Text Files (*.txt);;All Files (*.*)"
		)

		if save_path:
			try:
				with open(save_path, 'w', encoding='utf-8') as f:
					f.write(result)
				self.log_message(f"Result saved to: {save_path}")
			except Exception as e:
				QMessageBox.warning(self, "Error", f"Failed to save file: {str(e)}")
	
	def closeEvent(self, event: Any) -> None:
		self.disconnect_from_server()
		event.accept()
	

def main() -> None:
	app = QApplication(sys.argv)
	client = Client()
	client.show()
	sys.exit(app.exec())


if __name__ == "__main__":
	main()
		
		