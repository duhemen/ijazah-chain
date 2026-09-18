from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from app.ui.tab_issue import TabIssue
from app.ui.tab_verify import TabVerify

from app.ui.tab_public_verify import TabPublicVerify
from app.ui.tab_analytics import TabAnalytics
from app.ui.tab_bulk import TabBulk


class MainWindow(QMainWindow):
    def __init__(self, blockchain):
        super().__init__()
        self.blockchain = blockchain
        self.is_server_mode = hasattr(blockchain, "server_url")

        version = "v1.0"
        self.setWindowTitle(f"IJAZAH CHAIN {version} - Blockchain Verification System")
        self.resize(1280, 800)

        self.setStyleSheet(self._build_stylesheet())

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ============ HEADER ============
        header_layout = QHBoxLayout()

        title_label = QLabel("🔐 IJAZAH_CHAIN")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #00f0ff; letter-spacing: 1px;")

        # Server status badge
        self.status_badge = QLabel()
        self.status_badge.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_status_badge("unknown")

        header_layout.addWidget(title_label)
        header_layout.addSpacing(16)
        header_layout.addWidget(self.status_badge)
        header_layout.addStretch()

        subtitle_label = QLabel("Decentralized Academic Integrity Network")
        subtitle_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        subtitle_label.setStyleSheet("color: #7c7c8a;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        header_layout.addWidget(subtitle_label)
        main_layout.addLayout(header_layout)

        # Divider
        line = QWidget()
        line.setFixedHeight(2)
        line.setStyleSheet(
            "background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #00f0ff, stop:1 #121214); margin-bottom: 15px;"
        )
        main_layout.addWidget(line)

        # ============ TABS ============
        self.tabs = QTabWidget()
        self.tab_issue = TabIssue(self.blockchain)
        self.tab_verify = TabVerify(self.blockchain)
        self.tab_public_verify = TabPublicVerify(self.blockchain)
        self.tab_analytics = TabAnalytics(self.blockchain)
        self.tab_bulk = TabBulk(self.blockchain)

        self.tabs.addTab(self.tab_issue, "✍️  PENERBITAN IJAZAH")
        self.tabs.addTab(self.tab_verify, "🔍  AUDIT BLOCKCHAIN")
        self.tabs.addTab(self.tab_public_verify, "🌐 VERIFIKASI PUBLIK")
        self.tabs.addTab(self.tab_analytics, "📊 ANALITIK")
        self.tabs.addTab(self.tab_bulk, "📥 IMPORT MASSAL")

        main_layout.addWidget(self.tabs)

        # Cek status server setelah UI tampil
        QTimer.singleShot(500, self._check_server_status)

    # ============================================================
    # STATUS BADGE
    # ============================================================
    def _update_status_badge(self, state: str, detail: str = ""):
        """
        state: 'connected' | 'offline' | 'local' | 'unknown'
        """
        styles = {
            "connected": ("🟢 SERVER CONNECTED", "#2ecc71", "rgba(46, 204, 113, 0.12)"),
            "offline":   ("🔴 SERVER OFFLINE",   "#ff3860", "rgba(255, 56, 96, 0.12)"),
            "local":     ("🟡 LOCAL MODE",       "#f39c12", "rgba(243, 156, 18, 0.12)"),
            "unknown":   ("⚪ CEK KONEKSI...",    "#7c7c8a", "rgba(124, 124, 138, 0.12)"),
        }
        text, color, bg = styles.get(state, styles["unknown"])
        self.status_badge.setText(text)
        self.status_badge.setStyleSheet(
            f"color: {color}; background-color: {bg}; "
            f"border: 1px solid {color}; border-radius: 10px; "
            f"padding: 4px 12px;"
        )
        if detail:
            self.status_badge.setToolTip(detail)

    def _check_server_status(self):
        if not self.is_server_mode:
            self._update_status_badge("local", "Berjalan di SQLite lokal.")
            return
        try:
            health = self.blockchain.health()
            self._update_status_badge(
                "connected",
                f"Total blok: {health.get('total_blocks', '?')} | "
                f"Waktu server: {health.get('server_time', '?')}"
            )
        except Exception as e:
            self._update_status_badge("offline", str(e))

    # ============================================================
    # STYLESHEET
    # ============================================================
    @staticmethod
    def _build_stylesheet() -> str:
        return """
            QMainWindow { background-color: #121214; }
            QWidget {
                color: #e1e1e6;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #29292e;
                background-color: #1a1a1e;
                border-radius: 12px;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #121214;
                color: #7c7c8a;
                border: 1px solid #29292e;
                border-bottom: none;
                padding: 12px 30px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1a1a1e;
                color: #00f0ff;
                border-top: 3px solid #00f0ff;
            }
            QTabBar::tab:hover {
                color: #ffffff;
                background-color: #202024;
            }
            QComboBox {
                background-color: #202024;
                border: 1px solid #29292e;
                border-radius: 5px;
                padding: 7px;
                color: #ffffff;
                font-size: 12px;
            }
            QComboBox:focus { border: 1px solid #00f0ff; }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #7c7c8a;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #202024;
                border: 1px solid #29292e;
                color: #e1e1e6;
                selection-background-color: #00f0ff;
                selection-color: #121214;
                outline: none;
            }
        """