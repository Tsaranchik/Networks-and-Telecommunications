import re
from PyQt6.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QLabel,
	QPushButton, QTableWidget, QTableWidgetItem,
	QTextEdit, QMessageBox, QDialog,
	QFormLayout, QDialogButtonBox, QLineEdit, QGroupBox
)
from PyQt6.QtCore import QProcess, QTimer

class RouteWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		layout = QVBoxLayout()
		
		# Группа для управления таблицей маршрутизации
		table_group = QGroupBox("Управление таблицей маршрутизации")
		table_layout = QVBoxLayout()
		
		# Кнопки управления
		btn_layout = QHBoxLayout()
		self.refresh_btn = QPushButton("Обновить таблицу маршрутизации")
		self.add_btn = QPushButton("Добавить маршрут")
		self.del_btn = QPushButton("Удалить маршрут")
		
		self.refresh_btn.clicked.connect(self.load_routes)
		self.add_btn.clicked.connect(self.add_route)
		self.del_btn.clicked.connect(self.delete_route)
		
		btn_layout.addWidget(self.refresh_btn)
		btn_layout.addWidget(self.add_btn)
		btn_layout.addWidget(self.del_btn)
		btn_layout.addStretch()
		table_layout.addLayout(btn_layout)
		
		# Таблица маршрутов
		self.table = QTableWidget(0, 6)
		self.table.setHorizontalHeaderLabels([
			"Назначение", "Шлюз", "Метрика", "Интерфейс", "Протокол", "Состояние"
		])
		self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		
		self.table.setColumnWidth(0, 200)
		self.table.setColumnWidth(1, 150)
		self.table.setColumnWidth(2, 80)
		self.table.setColumnWidth(3, 100)
		self.table.setColumnWidth(4, 80)
		self.table.setColumnWidth(5, 100)
		
		table_layout.addWidget(self.table)
		
		# Информация
		self.info_label = QLabel("Выберите маршрут для управления или используйте поиск")
		self.info_label.setStyleSheet("font-weight: bold; color: #ffffff; padding: 5px;")
		table_layout.addWidget(self.info_label)
		
		table_group.setLayout(table_layout)
		layout.addWidget(table_group)
		
		# Лог
		layout.addWidget(QLabel("Лог команд:"))
		self.log = QTextEdit()
		self.log.setReadOnly(True)
		self.log.setFixedHeight(100)
		layout.addWidget(self.log)
		
		self.setLayout(layout)
		
		QTimer.singleShot(100, self.load_routes)

		self.process: QProcess | None = None
	
	def load_routes(self) -> None:
		self.table.setRowCount(0)

		self.process = QProcess(self)
		self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
		self.process.readyReadStandardOutput.connect(self.on_stdout_route)
		self.process.finished.connect(self.on_finished_route)
		self.process.start("ip", ["route", "show"])

	def on_stdout_route(self) -> None:
		data = self.process.readAllStandardOutput().data().decode(errors="ignore")
		self.parse_route_output(data)
	
	def on_finished_route(self, exit_code: int) -> None:
		if exit_code != 0:
			self.log.append("Ошибка загрузки таблицы маршрутизации")
	
	def parse_route_output(self, data: str) -> None:
		for line in data.splitlines():
			parts = line.split()
			if not parts:
				continue

			row = self.table.rowCount()
			self.table.insertRow(row)

			dest = parts[0] if parts else ""
			gateway = ""
			metric = ""
			interface = ""
			protocol = "kernel"
			status = "Активен"

			i = 1

			while i < len(parts):
				if parts[i] == 'via':
					gateway = parts[i + 1] if i + 1 < len(parts) else ""
					i += 2
				elif parts[i] == 'dev':
					interface = parts[i + 1] if i + 1 < len(parts) else ""
					i += 2
				elif parts[i] == 'metric':
					metric = parts[i + 1] if i + 1 < len(parts) else ""
					i += 2
				elif parts[i] == 'proto':
					protocol = parts[i + 1] if i + 1 < len(parts) else ""
					i += 2
				else:
					i += 1
			
			dest_item = QTableWidgetItem(dest)
			gateway_item = QTableWidgetItem(gateway)
			metric_item = QTableWidgetItem(metric)
			interface_item = QTableWidgetItem(interface)
			protocol_item = QTableWidgetItem(protocol)
			status_item = QTableWidgetItem(status)
			
			self.table.setItem(row, 0, dest_item)
			self.table.setItem(row, 1, gateway_item)
			self.table.setItem(row, 2, metric_item)
			self.table.setItem(row, 3, interface_item)
			self.table.setItem(row, 4, protocol_item)
			self.table.setItem(row, 5, status_item)
	
	def add_route(self) -> None:
		dialog = RouteDialog(parent=self)

		if dialog.exec() == QDialog.DialogCode.Accepted:
			dest, gateway, metric, interface = dialog.get_values()

			if not dest:
				QMessageBox(self, "Внимание", "Введите назначение маршрута")
				return

			cmd = ["sudo", "ip", "route", "add", dest]

			if gateway:
				cmd.extend(["via", gateway])
			
			if metric:
				cmd.extend(["metric", metric])
			
			if interface:
				cmd.extend(["dev", interface])
			
			self.run_command(cmd)
			QTimer.singleShot(500, self.load_routes)
	
	def delete_route(self) -> None:
		row = self.table.currentRow()
		
		if row < 0:
			QMessageBox.warning(self, "Внимание", "Выберите маршрут для удаления")
			return

		dest = self.table.item(row, 0).text()

		reply = QMessageBox.question(
			self, "Подтверждение",
			f"Удалить маршрут до {dest}?\n\nЭто действие потребует прав администратора",
			QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
		)

		if reply == QMessageBox.StandardButton.Yes:
			cmd = ["sudo", "ip", "route", "del", dest]
			self.run_command(cmd)
			QTimer.singleShot(500, self.load_routes)
	
	def run_command(self, cmd: list) -> None:
		self.log.append(f"$ {' '.join(cmd)}")

		if cmd[0] == "sudo":
			cmd = ["pkexec"] + cmd[1:]
		
		proc = QProcess(self)

		def on_ready():
			out = proc.readAllStandardOutput().data().decode(errors="ignore")
			err = proc.readAllStandardError().data().decode(errors="ignore")
			if out:
				self.log.append(out)
			if err:
				self.log.append(f"Ошибка: {err}")

		proc.readyReadStandardOutput.connect(on_ready)
		proc.start(cmd[0], cmd[1:])
		

class RouteDialog(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Добавить маршрут")
		self.setMinimumWidth(400)
		
		form = QFormLayout()
		
		self.dest_edit = QLineEdit()
		self.dest_edit.setPlaceholderText("Например: 192.168.1.0/24 или default")
		form.addRow("Назначение (префикс):", self.dest_edit)
		
		self.gateway_edit = QLineEdit()
		self.gateway_edit.setPlaceholderText("Например: 192.168.1.1")
		form.addRow("Шлюз (gateway, опционально):", self.gateway_edit)
		
		self.metric_edit = QLineEdit()
		self.metric_edit.setPlaceholderText("Например: 100")
		form.addRow("Метрика (опционально):", self.metric_edit)
		
		self.interface_edit = QLineEdit()
		self.interface_edit.setPlaceholderText("Например: eth0 или wlan0")
		form.addRow("Интерфейс (dev, опционально):", self.interface_edit)
		
		buttons = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)
		
		form.addWidget(buttons)
		self.setLayout(form)
	
	def get_values(self):
		return (
			self.dest_edit.text().strip(),
			self.gateway_edit.text().strip(),
			self.metric_edit.text().strip(),
			self.interface_edit.text().strip()
		)

