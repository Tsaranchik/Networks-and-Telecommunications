import re
from PyQt6.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
	QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
	QTextEdit, QSpinBox, QMessageBox
)
from PyQt6.QtCore import QProcess

class PathPingWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		layout = QVBoxLayout()
		
		# Панель управления
		controls = QHBoxLayout()
		
		controls.addWidget(QLabel("Адрес:"))
		self.addr_edit = QLineEdit("8.8.8.8")
		self.addr_edit.setPlaceholderText("google.com или 8.8.8.8")
		controls.addWidget(self.addr_edit)
		
		controls.addWidget(QLabel("Количество пакетов:"))
		self.count_spinbox = QSpinBox()
		self.count_spinbox.setRange(1, 100)
		self.count_spinbox.setValue(10)
		controls.addWidget(self.count_spinbox)
		
		self.run_btn = QPushButton("Запустить mtr (аналог pathping)")
		self.run_btn.setObjectName("run_button")
		self.stop_btn = QPushButton("Остановить")
		self.stop_btn.setObjectName("stop_button")
		self.stop_btn.setEnabled(False)
		
		self.run_btn.clicked.connect(self.on_run)
		self.stop_btn.clicked.connect(self.terminate_previous)
		
		controls.addWidget(self.run_btn)
		controls.addWidget(self.stop_btn)
		controls.addStretch()
		layout.addLayout(controls)
		
		# Таблица для результатов
		self.table = QTableWidget(0, 9)
		self.table.setHorizontalHeaderLabels([
			"№", "Хост", "Потери %", "Отпр.", "Последние", 
			"Средние", "Лучшие", "Худшие", "StdDev", "Статус"
		])
		
		# Настраиваем ширину столбцов
		self.table.setColumnWidth(0, 40)
		self.table.setColumnWidth(1, 180)
		self.table.setColumnWidth(2, 80)
		self.table.setColumnWidth(3, 80)
		self.table.setColumnWidth(4, 80)
		self.table.setColumnWidth(5, 80)
		self.table.setColumnWidth(6, 80)
		self.table.setColumnWidth(7, 80)
		self.table.setColumnWidth(8, 70)
		self.table.setColumnWidth(9, 120)
		
		layout.addWidget(self.table)
		
		# Лог
		layout.addWidget(QLabel("Лог команды:"))
		self.log = QTextEdit()
		self.log.setReadOnly(True)
		self.log.setFixedHeight(100)
		layout.addWidget(self.log)
		
		self.setLayout(layout)
		self.process = None

		self.hops_with_problems = 0
		self.total_hops = 0
	
	def terminate_previous(self):
		if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
			self.process.kill()
			self.process.waitForFinished(1000)
			self.stop_btn.setEnabled(False)
			self.run_btn.setEnabled(True)
			self.log.append("MTR остановлен\n")
	
	def on_run(self):
		addr = self.addr_edit.text().strip()
		if not addr:
			QMessageBox.warning(self, "Внимание", "Введите адрес")
			return
		
		check_process = QProcess(self)
		check_process.start("which", ["mtr"])
		check_process.waitForFinished(1000)
		
		if check_process.readAllStandardOutput().data().decode().strip() == "":
			QMessageBox.warning(
				self, "Утилита не найдена",
				"Утилита mtr не установлена.\n\nУстановите командой:\nsudo apt-get install mtr"
			)
			return
		
		self.table.setRowCount(0)
		self.log.clear()
		
		args = [
			"--report",
			"--report-cycles", str(self.count_spinbox.value()),
			addr
		]
		
		self.run_btn.setEnabled(False)
		self.stop_btn.setEnabled(True)
		
		self.process = QProcess(self)
		self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
		self.process.readyReadStandardOutput.connect(self.on_stdout)
		self.process.readyReadStandardError.connect(self.on_stderr)
		self.process.finished.connect(self.on_finished)
		
		self.log.append(f"$ mtr {' '.join(args)}\n")
		self.process.start("mtr", args)
	
	def on_stdout(self):
		data = self.process.readAllStandardOutput().data().decode(errors='ignore')
		self.log.insertPlainText(data)
		self.parse_mtr_output(data)
	
	def on_stderr(self):
		data = self.process.readAllStandardError().data().decode(errors='ignore')
		if data:
			self.log.append(f"Ошибка: {data}\n")
	
	def on_finished(self, exit_code):
		if exit_code == 0:
			self.log.append(f"\nMTR завершен успешно\n")
		else:
			self.log.append(f"\nMTR завершен с кодом {exit_code}\n")
		
		self.stop_btn.setEnabled(False)
		self.run_btn.setEnabled(True)
	
	def parse_mtr_output(self, data):
		lines = data.strip().split('\n')
		
		for line in lines:
			if not line.strip():
				continue
			
			if (line.startswith('Start:') or 
				line.startswith('HOST:') or 
				'Loss%' in line or 
				'Snt' in line):
				continue
			
			line = line.rstrip()
			self.total_hops += 1
			
			pattern = r'^\s*(\d+)\.\s*(?:\|\-\-\s+)?(\S+)\s+([\d\.]+%?)\s+(\d+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)$'
			
			match = re.search(pattern, line)
			if match:
				hop_num = match.group(1)
				host = match.group(2)
				loss = match.group(3)
				sent = match.group(4)
				last = match.group(5)
				avg = match.group(6)
				best = match.group(7)
				worst = match.group(8)
				stddev = match.group(9)
				
				if '%' not in loss and loss != '???':
					loss = f"{loss}%"
				
				status, problem = self.determine_status(host, loss, last, avg)
				
				if problem:
					self.hops_with_problems += 1
				
				row = self.table.rowCount()
				self.table.insertRow(row)
				
				hop_item = QTableWidgetItem(hop_num)
				host_item = QTableWidgetItem(host)
				loss_item = QTableWidgetItem(loss)
				sent_item = QTableWidgetItem(sent)
				last_item = QTableWidgetItem(last)
				avg_item = QTableWidgetItem(avg)
				best_item = QTableWidgetItem(best)
				worst_item = QTableWidgetItem(worst)
				stddev_item = QTableWidgetItem(stddev)
				status_item = QTableWidgetItem(status)
				
				self.table.setItem(row, 0, hop_item)
				self.table.setItem(row, 1, host_item)
				self.table.setItem(row, 2, loss_item)
				self.table.setItem(row, 3, sent_item)
				self.table.setItem(row, 4, last_item)
				self.table.setItem(row, 5, avg_item)
				self.table.setItem(row, 6, best_item)
				self.table.setItem(row, 7, worst_item)
				self.table.setItem(row, 8, stddev_item)
				self.table.setItem(row, 9, status_item)
	
	def determine_status(self, host, loss, last_time, avg_time) -> tuple:
		try:
			if host == "???":
				return "Неизвестный хост", True
			
			loss_percent = float(loss.replace('%', ''))
			
			last = float(last_time)
			avg = float(avg_time)
			
			if loss_percent >= 100:
				return "Хост недоступен", True
			elif loss_percent > 20:
				return "Высокие потери", True
			elif loss_percent > 5:
				if avg > 100:
					return "Потери + высокая задержка",True
				return "Умеренные потери", True
			elif avg > 200:
				return "Высокая задержка", True
			elif avg > 100:
				return "Повышенная задержка", False
			else:
				return "Норма", False
				
		except (ValueError, AttributeError):
			return "Данные неполные", True
