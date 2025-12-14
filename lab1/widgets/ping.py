import re
from datetime import datetime
from PyQt6.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QLabel,
	QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
	QTextEdit, QSpinBox, QDoubleSpinBox, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import QProcess

class PingWidget(QWidget):
	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		layout = QVBoxLayout()

		# Панель управления
		controls = QHBoxLayout()

		controls.addWidget(QLabel("Адрес:"))
		self.addr_edit = QLineEdit("google.com")
		self.addr_edit.setPlaceholderText("google.com или 8.8.8.8")
		controls.addWidget(self.addr_edit)

		controls.addWidget(QLabel("Количество:"))
		self.count_spinbox = QSpinBox()
		self.count_spinbox.setRange(1, 100)
		self.count_spinbox.setValue(4)
		controls.addWidget(self.count_spinbox)

		controls.addWidget(QLabel("Размер:"))
		self.size = QSpinBox()
		self.size.setRange(1, 65500)
		self.size.setValue(56)
		controls.addWidget(self.size)

		controls.addWidget(QLabel("Интервал:"))
		self.interval = QDoubleSpinBox()
		self.interval.setRange(0.1, 10.0)
		self.interval.setValue(1.0)
		controls.addWidget(self.interval)

		controls.addWidget(QLabel("Таймаут:"))
		self.timeout = QSpinBox()
		self.timeout.setRange(1, 60)
		self.timeout.setValue(5)
		controls.addWidget(self.timeout)

		layout.addLayout(controls)

		# Кнопки
		btn_layout = QHBoxLayout()
		
		self.run_btn = QPushButton("Запустить ping")
		self.stop_btn = QPushButton("Остановить")
		self.stop_btn.setEnabled(False)
		self.clear_btn = QPushButton("Очистить")

		self.run_btn.clicked.connect(self.on_run)
		self.stop_btn.clicked.connect(self.terminate_previous)
		self.clear_btn.clicked.connect(self.on_clear)

		btn_layout.addWidget(self.run_btn)
		btn_layout.addWidget(self.stop_btn)
		btn_layout.addWidget(self.clear_btn)
		btn_layout.addStretch()

		layout.addLayout(btn_layout)

		# Таблица для результатов
		self.table = QTableWidget(0, 7)

		self.table.setHorizontalHeaderLabels([
			"Время", "IP адрес", "Размер", "TTL",
			"Время ответа (мс)", "Статус", "Потери"
		])
		self.table.setSizePolicy(
			QSizePolicy.Policy.Expanding,
			QSizePolicy.Policy.Expanding
		)

		self.table.setColumnWidth(0, 80)
		self.table.setColumnWidth(1, 150)
		self.table.setColumnWidth(2, 70)
		self.table.setColumnWidth(3, 50)
		self.table.setColumnWidth(4, 120)
		self.table.setColumnWidth(5, 100)
		self.table.setColumnWidth(6, 70)

		layout.addWidget(self.table)

		# Статистика
		self.stats_label = QLabel("Статистика: ожидание запуска...")
		self.stats_label.setStyleSheet("font-weight: bold; color: #333; padding: 5px;")
		
		layout.addWidget(self.stats_label)

		# Лог
		self.log = QTextEdit()

		self.log.setReadOnly(True)
		self.log.setFixedHeight(100)
		
		layout.addWidget(QLabel("Лог команды:"))
		layout.addWidget(self.log)

		self.setLayout(layout)

		self.process: QProcess | None = None
		self.loss_count = 0
		self.success_count = 0
		self.response_times = []
	
	def terminate_previous(self) -> None:
		if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
			self.process.kill()
			self.process.waitForFinished(100)
			self.stop_btn.setEnabled(False)
			self.run_btn.setEnabled(True)
			self.log.append("Ping остановлен")
	
	def on_stdout(self) -> None:
		data = self.process.readAllStandardOutput().data().decode(errors="ignore")
		self.log.insertPlainText(data)
		self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

		for line in data.splitlines():
			self.parse_ping_line(line)
	
	def on_stderr(self) -> None:
		data = self.process.readAllStandardError().data().decode(erros="ignore")
		
		if data:
			self.log.append(f"Ошибка: {data}")
	
	def on_finished(self, exit_code: int) -> None:
		if exit_code == 0:
			self.log.append("\nPing завершен успешно")
		else:
			self.log.append(f"\nPing завершен с кодом ошибки {exit_code}")
		
		total = self.loss_count + self.success_count

		if total > 0:
			loss_percent = (self.loss_count / total) * 100
			avg_time = (
				sum(self.response_times) / len(self.response_times) 
				if self.response_times 
				else 0
			)
			match loss_percent:
				case p if p < 5:
					status = "Норма"
				case p if p < 20:
					status = "Проблемы"
				case _:
					status = "Критично"
			
			stats = (
				f"Статистика: Отправлено: {total}, получено: {self.success_count}, "
				f"Потеряно: {self.loss_count} ({loss_percent:1f}%), "
				f"Среднее время: {avg_time:1f}мс - {status}"
			)
			self.stats_label.setText(stats)
		self.stop_btn.setEnabled(False)
		self.run_btn.setEnabled(True)
	
	def parse_ping_line(self, line: str):
		patterns = [
			# С IP и именем хоста
			r'(\d+) bytes from ([\w\.-]+) \(([\d\.]+)\): icmp_seq=\d+ ttl=(\d+) time=([\d\.]+) ms',
			# Только с IP
			r'(\d+) bytes from ([\d\.]+): icmp_seq=\d+ ttl=(\d+) time=([\d\.]+) ms',
			# Более общий паттерн
			r'(\d+) bytes from ([\w\.-]+): icmp_seq=\d+ ttl=(\d+) time=([\d\.]+) ms'
		]
		
		for pattern in patterns:
			m = re.search(pattern, line)
			if m:
				groups = m.groups()
				if len(groups) == 5:  # С IP и именем хоста
					size, hostname, ip, ttl, time = groups
				else:  # Только IP или только имя хоста
					size, source, ttl, time = groups
					# Определяем, что это - IP или имя хоста
					if re.match(r'\d+\.\d+\.\d+\.\d+', source):
						ip = source
						hostname = ""
					else:
						ip = source
						hostname = source
				
				row = self.table.rowCount()
				self.table.insertRow(row)
				
				timestamp = datetime.now().strftime("%H:%M:%S")
				time_ms = float(time)
				self.response_times.append(time_ms)
				self.success_count += 1
				
				time_item = QTableWidgetItem(f"{time}")
				
				status_item = QTableWidgetItem("Успешно")
				
				loss_item = QTableWidgetItem("0%")
				
				# Определяем, что отображать в колонке IP
				display_ip = ip if 'ip' in locals() else source
				
				self.table.setItem(row, 0, QTableWidgetItem(timestamp))
				self.table.setItem(row, 1, QTableWidgetItem(display_ip))
				self.table.setItem(row, 2, QTableWidgetItem(size))
				self.table.setItem(row, 3, QTableWidgetItem(ttl))
				self.table.setItem(row, 4, time_item)
				self.table.setItem(row, 5, status_item)
				self.table.setItem(row, 6, loss_item)
				return
		
		pattern_loss = r'no answer yet for icmp_seq=\d+|Request timeout for icmp_seq=\d+'
		if re.search(pattern_loss, line):
			row = self.table.rowCount()
			self.table.insertRow(row)
			self.loss_count += 1
			
			timestamp = datetime.now().strftime("%H:%M:%S")
			
			status_item = QTableWidgetItem("Потерян")
			
			loss_item = QTableWidgetItem("100%")
			
			self.table.setItem(row, 0, QTableWidgetItem(timestamp))
			self.table.setItem(row, 1, QTableWidgetItem("N/A"))
			self.table.setItem(row, 2, QTableWidgetItem("N/A"))
			self.table.setItem(row, 3, QTableWidgetItem("N/A"))
			self.table.setItem(row, 4, QTableWidgetItem("Таймаут"))
			self.table.setItem(row, 5, status_item)
			self.table.setItem(row, 6, loss_item)
			return
		
		pattern_stats = r'(\d+) packets transmitted, (\d+) (?:packets )?received, ([\d\.]+)% packet loss'
		pattern_rtt = r'round-trip min/avg/max/stddev = ([\d\.]+)/([\d\.]+)/([\d\.]+)/([\d\.]+) ms'
		
		m = re.search(pattern_stats, line)
		if m:
			transmitted, received, loss = m.groups()
			self.log.append(f"Статистика: Передано: {transmitted}, Получено: {received}, Потери: {loss}%\n")
			
			m2 = re.search(pattern_rtt, line)
			if m2:
				min_time, avg_time, max_time, stddev = m2.groups()
				self.log.append(f"Время: мин={min_time}мс, средн={avg_time}мс, макс={max_time}мс, отклонение={stddev}мс\n")
	
	def on_run(self) -> None:
		addr = self.addr_edit.text().strip()
		
		if not addr:
			QMessageBox.warning(self, "Внимание", "Введите адрес для ping")
			return

		self.table.setRowCount(0)
		self.log.clear()
		self.loss_count = 0
		self.success_count = 0
		self.response_times = []

		args = [
			"-c", str(self.count_spinbox.value()),
			"-s", str(self.size.value()),
			"-i", str(self.interval.value()),
			"-W", str(self.timeout.value()),
			addr
		]

		self.run_btn.setEnabled(False)
		self.stop_btn.setEnabled(True)
		self.stats_label.setText("Выполняется ping...")

		self.process = QProcess(self)
		self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
		self.process.readyReadStandardOutput.connect(self.on_stdout)
		self.process.readyReadStandardError.connect(self.on_stderr)
		self.process.finished.connect(self.on_finished)

		self.log.append(f"$ ping {' '.join(args)}")
		self.process.start('ping', args)
	
	def on_clear(self):
		self.table.setRowCount(0)
		self.log.clear()
		self.stats_label.setText("Статистика: очищено")
