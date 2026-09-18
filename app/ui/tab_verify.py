import datetime
import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QTextEdit, QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class TabVerify(QWidget):
    def __init__(self, blockchain):
        super().__init__()
        self.blockchain = blockchain
        self.is_server_mode = hasattr(blockchain, "server_url")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ============ STATUS BOX ============
        self.status_box = QWidget()
        self.status_box.setObjectName("StatusBox")
        self.status_layout = QHBoxLayout(self.status_box)
        self.status_label = QLabel("⚪ Memuat status integritas...")
        self.status_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.status_layout.addWidget(self.status_label)
        self.status_box.setStyleSheet(
            "QWidget#StatusBox {"
            "  background-color: rgba(124, 124, 138, 0.1);"
            "  border: 1px solid #7c7c8a; border-radius: 8px;"
            "}"
            "QLabel { color: #7c7c8a; }"
        )
        layout.addWidget(self.status_box)

        # ============ CONTENT ============
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # LEFT: list blok
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        mode_label = "🌐 Server Ledger" if self.is_server_mode else "💾 Local Ledger"
        list_title = QLabel(f"📦 Daftar Blok Ijazah ({mode_label})")
        list_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        left_layout.addWidget(list_title)

        self.list_blocks = QListWidget()
        self.list_blocks.setStyleSheet("""
            QListWidget {
                background-color: #202024;
                border: 1px solid #29292e;
                border-radius: 8px;
                padding: 10px;
                color: #ffffff;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #29292e;
            }
            QListWidget::item:selected {
                background-color: #00f0ff;
                color: #121214;
                font-weight: bold;
                border-radius: 4px;
            }
        """)
        self.list_blocks.itemClicked.connect(self.show_block_details)
        left_layout.addWidget(self.list_blocks)
        content_layout.addWidget(left_panel, stretch=1)

        # RIGHT: detail audit
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        detail_title = QLabel("🔬 Data Audit Forensik Kriptografi")
        detail_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        right_layout.addWidget(detail_title)

        self.txt_details = QTextEdit()
        self.txt_details.setReadOnly(True)
        self.txt_details.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1e;
                border: 1px solid #29292e;
                border-radius: 8px;
                padding: 15px;
                color: #a9a9b2;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        right_layout.addWidget(self.txt_details)
        content_layout.addWidget(right_panel, stretch=1)

        layout.addLayout(content_layout)

        # ============ ACTION BUTTON ============
        self.btn_refresh = QPushButton("🔄 JALANKAN AUDIT INTEGRITAS BLOCKCHAIN")
        self.btn_refresh.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #202024;
                color: #ffffff;
                border: 1px solid #29292e;
                border-radius: 6px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #29292e;
                border: 1px solid #00f0ff;
            }
        """)
        self.btn_refresh.clicked.connect(lambda: self.perform_audit(show_popup=True))
        layout.addWidget(self.btn_refresh)

        # Muat pertama kali tanpa popup
        self.perform_audit(show_popup=False)

    # ============================================================
    # AUDIT
    # ============================================================
    def perform_audit(self, show_popup=True):
        # Server mode: refresh chain dari server dulu
        if self.is_server_mode:
            try:
                self.blockchain.refresh_chain()
            except Exception as e:
                QMessageBox.warning(
                    self, "Gagal Memuat Data",
                    f"Tidak dapat memuat blok dari server:\n\n{e}",
                )
                return

        self.list_blocks.clear()

        is_valid = self.blockchain.is_chain_valid()
        total_blocks = len(self.blockchain.chain)
        ijazah_count = max(0, total_blocks - 1)

        # Update status box
        if is_valid:
            self.status_box.setStyleSheet(
                "QWidget#StatusBox {"
                "  background-color: rgba(0, 240, 255, 0.1);"
                "  border: 1px solid #00f0ff; border-radius: 8px;"
                "}"
                "QLabel { color: #00f0ff; }"
            )
            self.status_label.setText(
                "🟢 SISTEM INTEGRITAS JARINGAN: AMAN & TERVALIDASI (100% ASLI)"
            )
        else:
            self.status_box.setStyleSheet(
                "QWidget#StatusBox {"
                "  background-color: rgba(255, 0, 76, 0.1);"
                "  border: 1px solid #ff004c; border-radius: 8px;"
                "}"
                "QLabel { color: #ff004c; }"
            )
            self.status_label.setText(
                "🔴 PERINGATAN: TERDETEKSI MANIPULASI DATA PADA DATABASE!"
            )

        # Isi list
        for block in self.blockchain.chain:
            if block.index == 0:
                self.list_blocks.addItem("📦 Blok 0 : [Genesis Root Block]")
            else:
                if isinstance(block.data, dict):
                    nama_mhs = block.data.get("nama", "UNKNOWN")
                    fak = block.data.get("fakultas", "")
                    suffix = f" — {fak}" if fak else ""
                else:
                    nama_mhs = "UNKNOWN"
                    suffix = ""
                self.list_blocks.addItem(
                    f"📦 Blok {block.index} : {nama_mhs}{suffix}"
                )

        # Popup konfirmasi
        if show_popup:
            source = "server" if self.is_server_mode else "database lokal"
            if is_valid:
                QMessageBox.information(
                    self,
                    "Audit Selesai — VALID",
                    f"✅ Audit integritas blockchain BERHASIL!\n\n"
                    f"• Sumber data   : {source}\n"
                    f"• Total blok    : {total_blocks}\n"
                    f"• Blok ijazah   : {ijazah_count}\n"
                    f"• Status        : SEMUA HASH COCOK\n"
                    f"• Rantai kripto : TERHUBUNG\n\n"
                    f"Sistem dinyatakan AMAN dan tidak ada manipulasi data.",
                )
            else:
                QMessageBox.critical(
                    self,
                    "Audit Selesai — TERDETEKSI MANIPULASI",
                    f"❌ Audit integritas blockchain GAGAL!\n\n"
                    f"• Sumber data   : {source}\n"
                    f"• Total blok    : {total_blocks}\n"
                    f"• Blok ijazah   : {ijazah_count}\n"
                    f"• Status        : HASH TIDAK COCOK\n"
                    f"• Rantai kripto : TERPUTUS\n\n"
                    f"Segera periksa file database di server!",
                )

    # ============================================================
    # DETAIL BLOK
    # ============================================================
    def show_block_details(self, item):
        index = self.list_blocks.row(item)
        if index < 0 or index >= len(self.blockchain.chain):
            return

        block = self.blockchain.chain[index]

        waktu_lokal = datetime.datetime.fromtimestamp(block.timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        if isinstance(block.data, dict):
            data_rapi = json.dumps(block.data, indent=4, ensure_ascii=False)
        else:
            data_rapi = f'"{block.data}"'

        # Verifikasi hash
        if self.is_server_mode:
            # Query server untuk verifikasi per-blok
            try:
                result = self.blockchain.verify_by_hash(block.hash)
                hash_valid = result.get("is_valid", False)
                server_note = result.get("message", "")
            except Exception as e:
                hash_valid = False
                server_note = f"Gagal verifikasi: {e}"
        else:
            # Mode lokal
            try:
                hash_valid = (block.hash == block.calculate_hash())
                server_note = "Verifikasi lokal SHA-256."
            except Exception:
                hash_valid = False
                server_note = "Tidak dapat menghitung ulang hash."

        # Verifikasi chain
        if block.index == 0:
            chain_valid = block.previous_hash == "0"
        else:
            previous_block = self.blockchain.chain[block.index - 1]
            chain_valid = block.previous_hash == previous_block.hash

        status_hash = "✓ OK" if hash_valid else "✗ TIDAK VALID"
        status_chain = "✓ TERHUBUNG" if chain_valid else "✗ TERPUTUS"

        detail_text = f"""========================================
METADATA AUDIT BLOK KE-{block.index}
========================================
[+] Waktu Minting    : {waktu_lokal}
[+] Hash Blok Ini    : {block.hash}
[+] Hash Sebelumnya  : {block.previous_hash}

[+] ISI DATA AKADEMIK:
{data_rapi}

----------------------------------------
STATUS VALIDASI BLOK:
👉 Hash Validasi Cocok?       {status_hash}
👉 Rantai Kriptografi Kunci?  {status_chain}

Catatan server:
{server_note}
========================================
"""
        self.txt_details.setText(detail_text)