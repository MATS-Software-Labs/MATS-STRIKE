import sys
import psutil
import platform
import wmi  # Echte Hardware-Schnittstelle
from PyQt6.QtWidgets import (QApplication, QMainWindow, QFrame, QLabel, 
                             QPushButton, QListWidget, QListWidgetItem)
from PyQt6.QtCore import QTimer, Qt

# --- ECHTE HARDWARE INITIALISIERUNG ---
try:
    c = wmi.WMI()
    # Holt den exakten Namen der CPU und GPU
    RAW_CPU = c.Win32_Processor()[0].Name
    RAW_GPU = c.Win32_VideoController()[0].Name
    # Bereinigung der Namen für das schicke UI
    REAL_CPU = RAW_CPU.replace("(TM)", "").replace("(R)", "").strip()
    REAL_GPU = RAW_GPU.replace("NVIDIA ", "").strip()
except Exception as e:
    REAL_CPU = "x86 Processor"
    REAL_GPU = "High-Perf Graphics"

class MatsStrike(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MATS-STRIKE // HARDWARE CONTROL")
        self.setFixedSize(900, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Haupt-Rahmen (Vantablack)
        self.main_frame = QFrame(self)
        self.main_frame.setGeometry(10, 10, 880, 580)
        self.main_frame.setStyleSheet("""
            QFrame {
                background-color: #050505;
                border: 2px solid #00FF00;
                border-radius: 15px;
            }
        """)

        # Header mit echtem CPU-Namen
        self.header = QLabel(f"MATS-STRIKE // CORE: {REAL_CPU}", self.main_frame)
        self.header.setGeometry(20, 15, 800, 30)
        self.header.setStyleSheet("color: #00FF00; font-family: 'Consolas'; font-size: 16px; border: none; font-weight: bold;")

        # Prozess-Liste
        self.process_list = QListWidget(self.main_frame)
        self.process_list.setGeometry(20, 60, 500, 480)
        self.process_list.setStyleSheet("""
            QListWidget {
                background-color: #080808;
                border: 1px solid #1a1a1a;
                color: #00FF00;
                font-family: 'Consolas';
                font-size: 12px;
            }
            QListWidget::item:selected { background-color: #00FF00; color: black; }
        """)

        # Hardware-Monitor Panel
        self.hw_label = QLabel(self.main_frame)
        self.hw_label.setGeometry(540, 60, 320, 220)
        self.hw_label.setStyleSheet("""
            color: white; 
            font-family: 'Consolas'; 
            background: #0a0a0a; 
            border: 1px solid #333; 
            padding: 15px;
            font-size: 12px;
        """)
        self.hw_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Purge Button
        self.purge_btn = QPushButton("TERMINATE PROCESS", self.main_frame)
        self.purge_btn.setGeometry(540, 300, 320, 80)
        self.purge_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.purge_btn.setStyleSheet("""
            QPushButton { 
                background: #000; color: #00FF00; border: 2px solid #00FF00; 
                font-family: 'Consolas'; font-weight: bold; font-size: 16px;
            }
            QPushButton:hover { background: #00FF00; color: black; }
        """)
        self.purge_btn.clicked.connect(self.kill_process)

        # Close
        self.close_btn = QPushButton("CLOSE INTERFACE", self.main_frame)
        self.close_btn.setGeometry(540, 530, 320, 30)
        self.close_btn.setStyleSheet("color: #444; background: transparent; border: 1px solid #222; font-family: 'Consolas';")
        self.close_btn.clicked.connect(self.close)

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_stats)
        self.timer.start(1000)
        self.refresh_stats()

    def refresh_stats(self):
        # Echte Echtzeit-Berechnung
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        
        status_text = (
            f"SYSTEM ANALYSIS\n"
            f"======================\n\n"
            f"GPU: {REAL_GPU}\n"
            f"STATUS: ONLINE\n\n"
            f"CPU LOAD: {cpu}%\n"
            f"RAM LOAD: {ram.percent}%\n"
            f"AVAILABLE: {round(ram.available / (1024**3), 2)} GB\n\n"
            f"ARCH: {platform.machine()}\n"
            f"OS: {platform.system()} {platform.release()}\n\n"
            f"MATS-STRIKE STATUS: OK"
        )
        self.hw_label.setText(status_text)

        # Prozess-Update
        current_row = self.process_list.currentRow()
        self.process_list.clear()
        for proc in sorted(psutil.process_iter(['pid', 'name', 'memory_percent']), key=lambda x: x.info['memory_percent'], reverse=True)[:18]:
            try:
                self.process_list.addItem(f"[{proc.info['pid']}] {proc.info['name']} ({proc.info['memory_percent']:.1f}%)")
            except: pass
        self.process_list.setCurrentRow(current_row)

    def kill_process(self):
        selected = self.process_list.currentItem()
        if selected:
            pid = int(selected.text().split(']')[0][1:])
            try:
                psutil.Process(pid).terminate()
            except Exception as e: print(f"ACCESS DENIED: {e}")

    # Dragging Logic
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: self.drag_pos = event.globalPosition().toPoint()
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MatsStrike()
    window.show()
    sys.exit(app.exec())