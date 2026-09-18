"""Tab verifikasi publik di client: cek hash/NIM, tanpa perlu akses admin."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QFrame, QMessageBox, QTabWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.config import MODE
from app.network.api_client import ApiError


class TabPublicVerify(QWidget):
    def __init__(self, blockchain):
        super().__init__()
        self.blockchain = blockchain
        self.is_server_mode = hasattr(blockchain, "server_url")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("🌐 Verifikasi Publik Ijazah")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        sub = QLabel(
            "Cek keaslian ijazah menggunakan hash blok atau NIM. "
            "Tidak perlu login admin. Cocok untuk HRD, verifikator eksternal."
        )
        sub.setStyleSheet("color: #7c7c8a; font-size: 12px;")
        sub.setWordWrap(True)
        layout.addWidget(sub)

        if not self.is_server_mode:
            warn = QLabel(
                "⚠️ Mode LOCAL aktif. Verifikasi publik hanya tersedia saat MODE='server'."
            )
            warn.setStyleSheet(
                "color: #f39c12; background-color: rgba(243, 156, 18, 0.1); "
                "border: 1px solid #f39c12; border-radius: 6px; padding: 10px;"
            )
            layout.addWidget(warn)

        # ============ INPUT TABS ============
        self.input_tabs = QTabWidget()

        # Tab 1: Hash
        hash_widget = QWidget()
        hash_layout = QHBoxLayout(hash_widget)
        hash_layout.setContentsMargins(16, 16, 16, 16)
        self.input_hash = QLineEdit()
        self.input_hash.setPlaceholderText("Masukkan hash blok (64 karakter hex)...")
        self.input_hash.setStyleSheet(self._input_style())
        self.input_hash.returnPressed.connect(self.verify_hash)
        btn_hash = QPushButton("🔍 Cek Hash")
        btn_hash.setStyleSheet(self._btn_style())
        btn_hash.clicked.connect(self.verify_hash)
        hash_layout.addWidget(self.input_hash, stretch=1)
        hash_layout.addWidget(btn_hash)

        # Tab 2: NIM
        nim_widget = QWidget()
        nim_layout = QHBoxLayout(nim_widget)
        nim_layout.setContentsMargins(16, 16, 16, 16)
        self.input_nim = QLineEdit()
        self.input_nim.setPlaceholderText("Masukkan NIM (contoh: 21/123456/TK/78901)")
        self.input_nim.setStyleSheet(self._input_style())
        self.input_nim.returnPressed.connect(self.verify_nim)
        btn_nim = QPushButton("🔍 Cari NIM")
        btn_nim.setStyleSheet(self._btn_style())
        btn_nim.clicked.connect(self.verify_nim)
        nim_layout.addWidget(self.input_nim, stretch=1)
        nim_layout.addWidget(btn_nim)

        self.input_tabs.addTab(hash_widget, "🔐 Berdasarkan Hash")
        self.input_tabs.addTab(nim_widget, "🎓 Berdasarkan NIM")
        layout.addWidget(self.input_tabs)

        # ============ RESULT ============
        self.txt_result = QTextEdit()
        self.txt_result.setReadOnly(True)
        self.txt_result.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1e;
                border: 1px solid #29292e;
                border-radius: 8px;
                padding: 16px;
                color: #a9a9b2;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.txt_result, stretch=1)

        self._show_welcome()

    def _input_style(self):
        return """
            QLineEdit {
                background-color: #202024;
                border: 1px solid #29292e;
                border-radius: 6px;
                padding: 10px;
                color: #ffffff;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
            QLineEdit:focus { border: 1px solid #00f0ff; }
        """

    def _btn_style(self):
        return """
            QPushButton {
                background-color: #00f0ff;
                color: #121214;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #00bccc; }
        """

    def _show_welcome(self):
        self.txt_result.setPlainText(
            "═══════════════════════════════════════════════\n"
            "   VERIFIKASI PUBLIK IJAZAH CHAIN\n"
            "═══════════════════════════════════════════════\n\n"
            "Masukkan hash blok atau NIM di atas, lalu tekan\n"
            "tombol cek untuk memverifikasi keaslian ijazah.\n\n"
            "💡 Tips: Hash blok tercetak di bagian bawah\n"
            "   ijazah PDF, dan juga ada di QR code.\n"
        )

    def _require_server(self) -> bool:
        if not self.is_server_mode:
            QMessageBox.warning(
                self, "Mode Local",
                "Fitur ini hanya tersedia saat MODE='server' di config.py.",
            )
            return False
        return True

    def verify_hash(self):
        if not self._require_server():
            return
        h = self.input_hash.text().strip()
        if not h:
            QMessageBox.warning(self, "Input Kosong", "Masukkan hash terlebih dahulu.")
            return
        self.txt_result.setPlainText("⏳ Memverifikasi hash...")
        try:
            data = self.blockchain.verify_public_by_hash(h)
            self._render_hash_result(data, h)
        except ApiError as e:
            self.txt_result.setPlainText(f"❌ Gagal verifikasi:\n\n{e}")

    def verify_nim(self):
        if not self._require_server():
            return
        n = self.input_nim.text().strip()
        if not n:
            QMessageBox.warning(self, "Input Kosong", "Masukkan NIM terlebih dahulu.")
            return
        self.txt_result.setPlainText("⏳ Mencari ijazah dengan NIM...")
        try:
            data = self.blockchain.verify_public_by_nim(n)
            self._render_nim_result(data, n)
        except ApiError as e:
            self.txt_result.setPlainText(f"❌ Gagal mencari:\n\n{e}")

    def _render_hash_result(self, data, hash_input):
        lines = []
        lines.append("═" * 50)
        if not data.get("found"):
            lines.append("  ❌ HASIL: IJAZAH TIDAK DITEMUKAN")
            lines.append("═" * 50)
            lines.append("")
            lines.append(data.get("message", "Hash tidak ada di ledger."))
            self.txt_result.setPlainText("\n".join(lines))
            return

        sig_ok = data.get("signature_valid", False)
        block = data.get("block") or {}
        d = data.get("data") or block.get("data") or {}

        lines.append("  ✅ HASIL: IJAZAH ASLI & TERVERIFIKASI")
        lines.append("═" * 50)
        lines.append("")
        lines.append(f"  Blok              : #{block.get('index')}")
        lines.append(f"  Nama              : {d.get('nama', '-')}")
        lines.append(f"  NIM               : {d.get('nim', '-')}")
        lines.append(f"  Program Studi     : {d.get('jurusan', '-')}")
        lines.append(f"  Fakultas          : {d.get('fakultas', '-')}")
        lines.append(f"  Gelar             : {d.get('gelar', '-')}")
        lines.append(f"  Institusi         : {d.get('institusi', '-')}")
        lines.append(f"  Tahun Lulus       : {d.get('tahun_lulus', '-')}")
        lines.append(f"  Tanggal Ijazah    : {d.get('tanggal', '-')}")
        lines.append(f"  Nomor Seri        : {d.get('nomor_seri', '-')}")
        lines.append("")
        lines.append("─" * 50)
        lines.append("  STATUS VALIDASI")
        lines.append("─" * 50)
        lines.append(f"  Hash              : {'✓ VALID' if data.get('found') else '✗ TIDAK VALID'}")
        lines.append(f"  Signature ECDSA   : {'✓ VALID' if sig_ok else '⚠ TIDAK ADA/INVALID'}")
        lines.append("")
        lines.append(f"  Pesan server      : {data.get('message', '-')}")
        self.txt_result.setPlainText("\n".join(lines))

    def _render_nim_result(self, data, nim):
        lines = []
        lines.append("═" * 50)
        if not data.get("found"):
            lines.append("  ❌ NIM TIDAK DITEMUKAN")
            lines.append("═" * 50)
            lines.append("")
            lines.append(data.get("message", ""))
            self.txt_result.setPlainText("\n".join(lines))
            return

        certs = data.get("certificates", [])
        lines.append(f"  ✅ DITEMUKAN {len(certs)} IJAZAH")
        lines.append("═" * 50)
        lines.append("")

        for i, b in enumerate(certs, 1):
            d = b.get("data") or {}
            lines.append(f"─── IJAZAH #{i} ───")
            lines.append(f"  Blok          : #{b.get('index')}")
            lines.append(f"  Nama          : {d.get('nama', '-')}")
            lines.append(f"  Program Studi : {d.get('jurusan', '-')}")
            lines.append(f"  Fakultas      : {d.get('fakultas', '-')}")
            lines.append(f"  Tanggal       : {d.get('tanggal', '-')}")
            lines.append(f"  Hash          : {b.get('hash', '')[:40]}...")
            lines.append("")

        self.txt_result.setPlainText("\n".join(lines))