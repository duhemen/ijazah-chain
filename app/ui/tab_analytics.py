"""Tab analitik di client: tampilkan statistik server tanpa buka browser."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QFrame, QPushButton, QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.network.api_client import ApiError


class StatCard(QFrame):
    """Kartu statistik kecil untuk menampilkan angka utama."""

    def __init__(self, label, value, color="#00f0ff"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1a1a1e;
                border: 1px solid #29292e;
                border-left: 3px solid {color};
                border-radius: 10px;
                padding: 16px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        lbl = QLabel(label)
        lbl.setStyleSheet("color: #7c7c8a; font-size: 11px; letter-spacing: 1px;")
        layout.addWidget(lbl)

        self.value_lbl = QLabel(str(value))
        self.value_lbl.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.value_lbl.setStyleSheet(f"color: {color};")
        layout.addWidget(self.value_lbl)


class RankingList(QFrame):
    """Panel ranking dengan bar proporsional."""

    def __init__(self, title, data: dict, color="#00f0ff"):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a1e;
                border: 1px solid #29292e;
                border-radius: 10px;
                padding: 16px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        t = QLabel(title)
        t.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(t)

        if not data:
            empty = QLabel("Belum ada data")
            empty.setStyleSheet("color: #7c7c8a; font-size: 12px; padding: 10px;")
            layout.addWidget(empty)
            return

        max_v = max(data.values()) if data else 1
        for i, (k, v) in enumerate(list(data.items())[:10]):
            row = QHBoxLayout()
            row.setSpacing(10)

            rank = QLabel(f"#{i + 1}")
            rank.setFixedWidth(28)
            rank.setStyleSheet("color: #7c7c8a; font-size: 11px;")
            row.addWidget(rank)

            name = QLabel(k if len(k) < 40 else k[:37] + "...")
            name.setStyleSheet("font-size: 12px;")
            row.addWidget(name, stretch=1)

            bar = QLabel()
            bar.setFixedHeight(8)
            bar_width = int((v / max_v) * 150) if max_v else 0
            bar.setFixedWidth(max(bar_width, 4))
            bar.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
            row.addWidget(bar)

            count = QLabel(str(v))
            count.setFixedWidth(40)
            count.setAlignment(Qt.AlignmentFlag.AlignRight)
            count.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px;")
            row.addWidget(count)

            layout.addLayout(row)


class TabAnalytics(QWidget):
    """Tab analitik — statistik ijazah langsung di client."""

    def __init__(self, blockchain):
        super().__init__()
        self.blockchain = blockchain
        self.is_server_mode = hasattr(blockchain, "server_url")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(12)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("📊 Analitik Ijazah")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        hdr.addWidget(title)
        hdr.addStretch()

        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #202024; color: #ffffff;
                border: 1px solid #29292e; border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover { border-color: #00f0ff; color: #00f0ff; }
        """)
        self.btn_refresh.clicked.connect(self.load_data)
        hdr.addWidget(self.btn_refresh)
        outer.addLayout(hdr)

        # Scroll area (content)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(16)
        scroll.setWidget(self.content)
        outer.addWidget(scroll, stretch=1)

        # Muat data pertama kali
        self.load_data()

    # ============================================================
    # LOAD
    # ============================================================
    def load_data(self):
        if not self.is_server_mode:
            self._show_local_message()
            return
        try:
            # Pakai endpoint publik + client-side aggregation
            # (client tidak punya admin token)
            data = self.blockchain.get_analytics()
            self._render(data)
        except ApiError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(f"Kesalahan tak terduga: {e}")

    # ============================================================
    # CLEAR
    # ============================================================
    def _clear(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    # ============================================================
    # STATES
    # ============================================================
    def _show_local_message(self):
        self._clear()
        msg = QLabel(
            "⚠️ Mode LOCAL aktif.\n\n"
            "Analitik memerlukan koneksi ke server.\n"
            "Ubah MODE='server' di app/config.py."
        )
        msg.setStyleSheet("color: #f39c12; font-size: 13px; padding: 20px;")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(msg)

    def _show_error(self, err):
        self._clear()
        msg = QLabel(f"❌ Gagal memuat: {err}")
        msg.setStyleSheet("color: #ff3860; font-size: 13px; padding: 20px;")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        self.content_layout.addWidget(msg)

    # ============================================================
    # RENDER
    # ============================================================
    def _render(self, data):
        self._clear()
        stats = data.get("stats", {})

        # Kartu statistik
        cards_layout = QGridLayout()
        cards_layout.setSpacing(12)

        total_certs = stats.get("total_certificates", 0)
        total_blocks = stats.get("total_blocks", 0)
        is_valid = stats.get("is_valid", False)
        total_inst = len(stats.get("by_institusi", {}))

        status_color = "#34d399" if is_valid else "#ff3860"
        status_text = "AMAN" if is_valid else "BERMASALAH"

        cards_layout.addWidget(
            StatCard("TOTAL IJAZAH", total_certs, "#00f0ff"), 0, 0
        )
        cards_layout.addWidget(
            StatCard("TOTAL BLOK", total_blocks, "#a78bfa"), 0, 1
        )
        cards_layout.addWidget(
            StatCard("STATUS", status_text, status_color), 0, 2
        )
        cards_layout.addWidget(
            StatCard("INSTITUSI", total_inst, "#f472b6"), 0, 3
        )
        self.content_layout.addLayout(cards_layout)

        # Ranking fakultas + prodi (side by side)
        grids = QGridLayout()
        grids.setSpacing(12)
        grids.addWidget(
            RankingList("🏛️ Fakultas Teratas",
                        stats.get("by_faculty", {}), "#00f0ff"),
            0, 0,
        )
        grids.addWidget(
            RankingList("🎓 Prodi Teratas",
                        stats.get("by_prodi", {}), "#a78bfa"),
            0, 1,
        )
        self.content_layout.addLayout(grids)

        # Distribusi per tahun
        self.content_layout.addWidget(
            RankingList("📅 Distribusi per Tahun",
                        stats.get("by_year", {}), "#34d399")
        )

        self.content_layout.addStretch()