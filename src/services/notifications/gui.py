"""
GUI Popup Notification Strategy using PyQt6 with Plyer fallback.
"""
import sys
import webbrowser
import multiprocessing
from src.services.notifications.base import NotificationStrategy
from src.services.sentry_service import SentryService

# Try importing PyQt6
try:
    from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QFont, QColor, QPalette
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

# Try importing Plyer
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

def _launch_pyqt_gui(url: str):
    """
    Internal function to run the GUI in a separate process using PyQt6.
    """
    app = QApplication(sys.argv)
    
    # Create Main Window
    window = QWidget()
    window.setWindowTitle("TicketSentry: Link Detected")
    window.setFixedSize(500, 220)
    
    # Always on Top & Focus
    window.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
    
    # Dark Theme Styling
    palette = window.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
    window.setPalette(palette)
    
    # Layout
    layout = QVBoxLayout()
    layout.setContentsMargins(20, 20, 20, 20)
    
    # Header
    header = QLabel("🚨 Link Detected!")
    header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
    header.setStyleSheet("color: #ff4444;")
    header.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(header)
    
    # URL Display
    display_url = url if len(url) < 50 else url[:47] + "..."
    lbl_url = QLabel(display_url)
    lbl_url.setFont(QFont("Consolas", 11))
    lbl_url.setStyleSheet("background-color: #2d2d2d; color: #00ff00; padding: 10px; border-radius: 5px;")
    lbl_url.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(lbl_url)
    
    # Buttons Layout
    btn_layout = QHBoxLayout()
    btn_layout.setSpacing(10)
    
    # Button Styles
    btn_style = """
        QPushButton {
            background-color: #3b8ed0;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover { background-color: #347ab0; }
    """
    
    # Copy Button
    btn_copy = QPushButton("Copy to Clipboard")
    btn_copy.setStyleSheet(btn_style)
    def copy_action():
        clipboard = QApplication.clipboard()
        clipboard.setText(url)
        btn_copy.setText("Copied!")
        btn_copy.setStyleSheet("background-color: #28a745; color: white; border: none; padding: 8px 15px; border-radius: 4px; font-weight: bold;")
        QTimer.singleShot(2000, lambda: btn_copy.setText("Copy to Clipboard"))
        QTimer.singleShot(2000, lambda: btn_copy.setStyleSheet(btn_style))
    btn_copy.clicked.connect(copy_action)
    btn_layout.addWidget(btn_copy)
    
    # Open Button
    btn_open = QPushButton("Open Link")
    btn_open.setStyleSheet(btn_style.replace("#3b8ed0", "#555555"))
    def open_action():
        webbrowser.open(url)
        window.close()
    btn_open.clicked.connect(open_action)
    btn_layout.addWidget(btn_open)
    
    # Dismiss Button
    btn_close = QPushButton("Dismiss")
    btn_close.setStyleSheet(btn_style.replace("#3b8ed0", "#d9534f"))
    btn_close.clicked.connect(window.close)
    btn_layout.addWidget(btn_close)
    
    layout.addLayout(btn_layout)
    window.setLayout(layout)
    
    # Center on Screen
    screen_geometry = app.primaryScreen().geometry()
    x = (screen_geometry.width() - window.width()) // 2
    y = (screen_geometry.height() - window.height()) // 2
    window.move(x, y)
    
    window.show()
    sys.exit(app.exec())

def _launch_plyer_notification(url: str):
    """
    Internal function to send a native notification using Plyer.
    """
    try:
        notification.notify(
            title='TicketSentry: Link Detected',
            message=f'Found: {url}',
            app_name='TicketSentry',
            timeout=10
        )
    except Exception as e:
        print(f"[!] Plyer notification failed: {e}")

class GuiNotification(NotificationStrategy):
    """
    Spawns a visual alert window using PyQt6, with Plyer as fallback.
    """
    def send(self, message: str, **kwargs):
        try:
            if PYQT_AVAILABLE:
                p = multiprocessing.Process(target=_launch_pyqt_gui, args=(message,))
                p.start()
            elif PLYER_AVAILABLE:
                print("[*] PyQt6 not found. Falling back to Plyer notification.")
                p = multiprocessing.Process(target=_launch_plyer_notification, args=(message,))
                p.start()
            else:
                print("[!] Neither PyQt6 nor Plyer found. GUI notification skipped.")
                print("    Install with: pip install PyQt6 plyer")
        except Exception as e:
            print(f"[!] Failed to launch notification: {e}")
            SentryService.capture_exception(e)



