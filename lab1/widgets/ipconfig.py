import re
from PyQt6.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout,
	QPushButton, QTabWidget, QTextEdit
)
from PyQt6.QtCore import QProcess, QTimer

class IpConfigWidget(QWidget):
	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		layout = QVBoxLayout()

		# Панель управления
		controls = QHBoxLayout()

		self.refresh_btn = QPushButton("Обновить информацию о сетевых интерфейсах")
		self.refresh_btn.clicked.connect(self.refresh_ip)
		
		controls.addWidget(self.refresh_btn)
		controls.addStretch()

		layout.addLayout(controls)

		# Вкладки для интерфейсов
		self.tabs = QTabWidget()
		layout.addWidget(self.tabs)

		self.setLayout(layout)

		QTimer.singleShot(100, self.refresh_ip)
	
	def refresh_ip(self) -> None:
		self.tabs.clear()

		self.process = QProcess(self)
		self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
		self.process.readyReadStandardOutput.connect(self.on_stdout_ip)
		self.process.finished.connect(self.on_finished_ip)
		self.process.start("ip", ["addr", "show"])
	
	def on_stdout_ip(self) -> None:
		data = self.process.readAllStandardOutput().data().decode(errors="ignore")
		self.parse_ip_output(data)

	def on_finished_ip(self, exit_code: int) -> None:
		if exit_code != 0:
			from PyQt6.QtWidgets import QMessageBox
			QMessageBox.warning(self, "Ошибка", "Не удалось получить информацию об интерфейсах")
	
	def parse_ip_output(self, data: str) -> None:
		interfaces = {}
		current_iface = None

		for line in data.splitlines():
			if re.match(r"^\d+:", line):
				parts = line.split(":")
				if len(parts) >= 2:
					current_iface = parts[1].strip()
					interfaces[current_iface] = line + '\n'
			elif current_iface:
				interfaces[current_iface] += line + '\n'
		
		for iface_name, content in interfaces.items():
			tab = QWidget()
			layout = QVBoxLayout()

			text = QTextEdit()
			text.setReadOnly(True)
			text.setPlainText(content)

			layout.addWidget(text)
			tab.setLayout(layout)

			self.tabs.addTab(tab, iface_name)
