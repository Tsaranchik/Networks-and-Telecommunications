import sys
from PyQt6.QtWidgets import (
	QApplication, QWidget, QVBoxLayout, QHBoxLayout,
	QLabel, QComboBox, QStackedWidget
)
from PyQt6.QtCore import Qt
from widgets.ping import PingWidget
from widgets.ipconfig import IpConfigWidget
from widgets.pathping import PathPingWidget
from widgets.route import RouteWidget

class MainWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Лабораторная работа №1 (вариант №10)")
		self.resize(1100, 750)

		self.setStyleSheet(
			"""
			QWidget {
				font-family: 'Seoge UI', 'Ubuntu', sans-serif;
				font-size: 12px;
			}
			QLabel {
				color: #ffffff;
			}
			QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
				background-color: #2d2d2d;
				color: #ffffff;
				border: 1px solid #555555;
				border-radius: 4px;
				padding: 5px;
				selection-background-color: #3d3d3d;
			}
			QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
				border: 1px solid #1e90ff;
			}
			QPushButton {
				background-color: #404040;
				color: #ffffff;
				border: 1px solid #555555;
				border-radius: 4px;
				padding: 8px 15px;
				font-weight: bold;
			}
			QPushButton:hover {
				background-color: #505050;
				border: 1px solid #666666;
			}
			QPushButton:pressed {
				background-color: #303030;
			}
			QPushButton:disabled {
				background-color: #333333;
				color: #888888;
				border: 1px solid #444444;
			}
			QPushButton#run_button {
				background-color: #2e7d32;
			}
			QPushButton#run_button:hover {
				background-color: #388e3c;
			}
			QPushButton#stop_button {
				background-color: #c62828;
			}
			QPushButton#stop_button:hover {
				background-color: #d32f2f;
			}
			QTableWidget {
				background-color: #2d2d2d;
				color: #ffffff;
				gridline-color: #444444;
				border: 1px solid #555555;
			}
			QTableWidget::item {
				padding: 5px;
				border-bottom: 1px solid #444444;
			}
			QTableWidget::item:selected {
				background-color: #3d3d3d;
			}
			QHeaderView::section {
				background-color: #404040;
				color: #ffffff;
				padding: 8px;
				border: 1px solid #555555;
				font-weight: bold;
			}
			QTextEdit {
				background-color: #2d2d2d;
				color: #ffffff;
				border: 1px solid #555555;
				border-radius: 4px;
				padding: 5px;
			}
			QTabWidget::pane {
				border: 1px solid #555555;
				background-color: #353535;
			}
			QTabBar::tab {
				background-color: #404040;
				color: #cccccc;
				padding: 8px 15px;
				margin-right: 2px;
				border-top-left-radius: 4px;
				border-top-right-radius: 4px;
			}
			QTabBar::tab:selected {
				background-color: #353535;
				color: #ffffff;
				font-weight: bold;
			}
			QTabBar::tab:hover:!selected {
				background-color: #505050;
			}
			QGroupBox {
				border: 1px solid #555555;
				border-radius: 4px;
				margin-top: 10px;
				padding-top: 10px;
				color: #ffffff;
				font-weight: bold;
			}
			QGroupBox::title {
				subcontrol-origin: margin;
				left: 10px;
				padding: 0 5px;
			}
			QScrollBar:vertical {
				background-color: #2d2d2d;
				width: 15px;
				border-radius: 4px;
			}
			QScrollBar::handle:vertical {
				background-color: #555555;
				border-radius: 4px;
				min-height: 20px;
			}
			QScrollBar::handle:vertical:hover {
				background-color: #666666;
			}
			QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
				height: 0px;
			}
			QMessageBox {
				background-color: #353535;
				color: #ffffff;
			}
			QMessageBox QLabel {
				color: #ffffff;
			}
			QDialog {
				background-color: #353535;
				color: #ffffff;
			}
			"""
		)

		main_layout = QVBoxLayout()

		top = QHBoxLayout()

		top.addWidget(QLabel("Выберите команду:"))
		self.command_box = QComboBox()
		self.command_box.addItems(["Ping", "IP Config", "PathPing", "Route"])
		top.addWidget(self.command_box)
		top.addStretch()

		main_layout.addLayout(top)

		self.stack = QStackedWidget()
		self.QWidgets = [
			PingWidget(),
			IpConfigWidget(),
			PathPingWidget(),
			RouteWidget()
		]

		for widget in self.QWidgets:
			self.stack.addWidget(widget)
		
		main_layout.addWidget(self.stack)

		info = QLabel("Система: Ubuntu 24 | ping: -c/-W | ipconfig: ip addr | pathping: mtr | route: ip route")
		info.setStyleSheet("color: #666; padding: 5px; font-size: 12px;")
		main_layout.addWidget(info)

		self.setLayout(main_layout)

		self.command_box.currentIndexChanged.connect(self.on_command_change)
		self.on_command_change(0)
	
	def on_command_change(self, idx: int) -> None:
		self.stack.setCurrentIndex(idx)
	

def main() -> None:
	app = QApplication(sys.argv)
	app.setStyle('Fusion')

	window = MainWindow()
	window.show()

	sys.exit(app.exec())


if __name__ == "__main__":
	main()
