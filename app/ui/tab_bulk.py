"""Tab import massal dari CSV / Excel."""

import csv
import os
from typing import Any, Dict, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFileDialog, QMessageBox, QProgressBar,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from app.config import MODE
from app.network.api_client import ApiError


REQUIRED_COLUMNS = ["nama", "nim", "jurusan", "gelar", "nomor_seri", "institusi"]
OPTIONAL_COLUMNS = [
    "fakultas", "tahun_lulus", "judul_skripsi",
    "rektor", "dekan", "custom_footnote",
]


class ImportWorker(QThread):
    """Worker thread untuk import, agar UI tidak freeze."""

    progress = pyqtSignal(int, int, str)  # current, total, message
    finished_ok = pyqtSignal(int, int, list)  # success, failed, errors

    def __init__(self, blockchain, rows: List[Dict[str, str]]):
        super().__init__()
        self.blockchain = blockchain
        self.rows = rows

    def run(self):
        success = 0
        failed = 0
        errors = []
        total = len(self.rows)

        for i, row in enumerate(self.rows, 1):
            nim = row.get("nim", "?")
            nama = row.get("nama", "?")
            try:
                data = {
                    "nama": str(row.get("nama", "")).strip().upper(),
                    "nim": str(row.get("nim", "")).strip(),
                    "jurusan": str(row.get("jurusan", "")).strip().upper(),
                    "gelar": str(row.get("gelar", "")).strip(),
                    "nomor_seri": str(row.get("nomor_seri", "")).strip(),
                    "institusi": str(row.get("institusi", "")).strip().upper(),
                    "judul_skripsi": str(row.get("judul_skripsi", "") or "").strip().upper(),
                    "rektor": str(row.get("rektor", "") or "").strip(),
                    "dekan": str(row.get("dekan", "") or "").strip(),
                    "custom_footnote": str(row.get("custom_footnote", "") or "").strip(),
                }
                if row.get("fakultas"):
                    data["fakultas"] = str(row["fakultas"]).strip().upper()
                if row.get("tahun_lulus"):
                    try:
                        data["tahun_lulus"] = int(row["tahun_lulus"])
                    except (ValueError, TypeError):
                        pass

                # Validasi minimal
                missing = [k for k in REQUIRED_COLUMNS if not data.get(k)]
                if missing:
                    raise ValueError(f"Kolom kosong: {', '.join(missing)}")

                # Kirim
                if MODE == "server":
                    self.blockchain.add_block(data)
                else:
                    block = self.blockchain.add_block(data)
                    from app.blockchain.storage import save_block_to_db
                    save_block_to_db(block)

                success += 1
                self.progress.emit(i, total, f"✓ #{i} {nama} ({nim})")
            except ApiError as e:
                failed += 1
                errors.append(f"Row {i} [{nim}]: Server error - {e}")
                self.progress.emit(i, total, f"✗ #{i} GAGAL: {e}")
            except Exception as e:
                failed += 1
                errors.append(f"Row {i} [{nim}]: {e}")
                self.progress.emit(i, total, f"✗ #{i} GAGAL: {e}")

        self.finished_ok.emit(success, failed, errors)


class TabBulk(QWidget):
    def __init__(self, blockchain):
        super().__init__()
        self.blockchain = blockchain
        self.is_server_mode = hasattr(blockchain, "server_url")
        self.rows: List[Dict[str, str]] = []
        self.worker = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Title
        title = QLabel("📥 Import Massal Ijazah")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        sub = QLabel(
            "Upload file CSV atau Excel berisi banyak ijazah sekaligus. "
            f"Mode: {'SERVER' if self.is_server_mode else 'LOCAL'}"
        )
        sub.setStyleSheet("color: #7c7c8a; font-size: 12px;")
        layout.addWidget(sub)

        # Template info
        info = QLabel(
            "📋 Format kolom wajib: nama, nim, jurusan, gelar, nomor_seri, institusi\n"
            "📋 Kolom opsional: fakultas, tahun_lulus, judul_skripsi, rektor, dekan, custom_footnote"
        )
        info.setStyleSheet(
            "background-color: rgba(0, 240, 255, 0.06); "
            "border: 1px solid rgba(0, 240, 255, 0.2); "
            "border-radius: 8px; padding: 12px; "
            "color: #a9a9b2; font-size: 11px; font-family: 'Courier New', monospace;"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # Buttons row
        btn_row = QHBoxLayout()
        self.btn_load = QPushButton("📂 Pilih File CSV/Excel")
        self.btn_load.setStyleSheet("""
            QPushButton {
                background-color: #202024; color: #ffffff;
                border: 1px solid #29292e; border-radius: 6px;
                padding: 10px 20px; font-weight: bold;
            }
            QPushButton:hover { border-color: #00f0ff; color: #00f0ff; }
        """)
        self.btn_load.clicked.connect(self.choose_file)
        btn_row.addWidget(self.btn_load)

        self.btn_download = QPushButton("⬇️ Download Template CSV")
        self.btn_download.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #7c7c8a;
                border: 1px solid #29292e; border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover { color: #00f0ff; border-color: #00f0ff; }
        """)
        self.btn_download.clicked.connect(self.download_template)
        btn_row.addWidget(self.btn_download)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        # File info
        self.lbl_file = QLabel("Belum ada file yang dipilih.")
        self.lbl_file.setStyleSheet("color: #7c7c8a; font-size: 12px; padding: 6px;")
        layout.addWidget(self.lbl_file)

        # Progress
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #202024; border: 1px solid #29292e;
                border-radius: 6px; height: 24px; text-align: center;
                color: #ffffff; font-size: 11px; font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00f0ff, stop:1 #a78bfa);
                border-radius: 5px;
            }
        """)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Log
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("""
            QTextEdit {
                background-color: #0f0f14; border: 1px solid #29292e;
                border-radius: 8px; padding: 12px;
                color: #a9a9b2; font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        self.txt_log.setPlainText("Ready. Pilih file CSV/Excel untuk memulai import.\n")
        layout.addWidget(self.txt_log, stretch=1)

        # Action buttons
        action_row = QHBoxLayout()
        action_row.addStretch()

        self.btn_import = QPushButton("🚀 MULAI IMPORT")
        self.btn_import.setEnabled(False)
        self.btn_import.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; color: #ffffff;
                border: none; border-radius: 6px;
                padding: 12px 32px; font-weight: bold;
                font-size: 12px; letter-spacing: 1px;
            }
            QPushButton:hover { background-color: #27ae60; }
            QPushButton:disabled {
                background-color: #29292e; color: #555;
            }
        """)
        self.btn_import.clicked.connect(self.start_import)
        action_row.addWidget(self.btn_import)
        layout.addLayout(action_row)

    def choose_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih File CSV / Excel",
            "",
            "CSV / Excel Files (*.csv *.xlsx *.xls);;All Files (*)",
        )
        if not filename:
            return

        try:
            self.rows = self._read_file(filename)
            self.lbl_file.setText(
                f"📄 {os.path.basename(filename)} — {len(self.rows)} baris terdeteksi"
            )
            self.lbl_file.setStyleSheet("color: #34d399; font-size: 12px; padding: 6px;")

            preview = f"✓ File berhasil dibaca: {os.path.basename(filename)}\n"
            preview += f"✓ Total baris: {len(self.rows)}\n\n"
            preview += "Preview 3 baris pertama:\n"
            preview += "─" * 60 + "\n"
            for row in self.rows[:3]:
                preview += f"  • {row.get('nama', '?')} | {row.get('nim', '?')} | {row.get('jurusan', '?')}\n"

            self.txt_log.setPlainText(preview)
            self.btn_import.setEnabled(len(self.rows) > 0)
            self.progress.setMaximum(len(self.rows))
            self.progress.setValue(0)
        except Exception as e:
            QMessageBox.critical(self, "Gagal Membaca File", str(e))
            self.rows = []
            self.btn_import.setEnabled(False)

    def _read_file(self, filename: str) -> List[Dict[str, str]]:
        ext = os.path.splitext(filename)[1].lower()
        rows: List[Dict[str, str]] = []

        if ext == ".csv":
            with open(filename, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cleaned = {
                        (k or "").strip().lower(): (v or "").strip()
                        for k, v in row.items()
                    }
                    if cleaned.get("nama"):
                        rows.append(cleaned)
        elif ext in (".xlsx", ".xls"):
            try:
                import pandas as pd
            except ImportError:
                raise RuntimeError(
                    "Butuh pandas & openpyxl untuk baca Excel. Install:\n"
                    "pip install pandas openpyxl"
                )
            df = pd.read_excel(filename)
            df.columns = [str(c).strip().lower() for c in df.columns]
            df = df.fillna("")
            for _, r in df.iterrows():
                d = {k: str(v).strip() for k, v in r.to_dict().items()}
                if d.get("nama"):
                    rows.append(d)
        else:
            raise ValueError(f"Format file tidak didukung: {ext}")

        # Validasi kolom wajib
        if rows:
            sample = rows[0]
            missing_cols = [c for c in REQUIRED_COLUMNS if c not in sample]
            if missing_cols:
                raise ValueError(
                    f"Kolom wajib berikut tidak ditemukan di file: {missing_cols}\n\n"
                    f"Kolom yang ada: {list(sample.keys())}"
                )

        return rows

    def download_template(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Simpan Template CSV", "template_ijazah.csv", "CSV Files (*.csv)"
        )
        if not filename:
            return
        if not filename.lower().endswith(".csv"):
            filename += ".csv"

        headers = REQUIRED_COLUMNS + OPTIONAL_COLUMNS
        sample = {
            "nama": "Budi Santoso",
            "nim": "21/123456/TK/78901",
            "jurusan": "TEKNIK INFORMATIKA",
            "gelar": "S.Kom",
            "nomor_seri": "UGM-2026-001",
            "institusi": "UNIVERSITAS GADJAH MADA",
            "fakultas": "FAKULTAS TEKNIK",
            "tahun_lulus": "2026",
            "judul_skripsi": "SISTEM VERIFIKASI IJAZAH BERBASIS BLOCKCHAIN",
            "rektor": "Prof. Dr. Ir. Ova Emen",
            "dekan": "Dr. Mode AI, M.Sc.",
            "custom_footnote": "Diverifikasi melalui jaringan blockchain nasional.",
        }

        with open(filename, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
            w.writerow(sample)

        QMessageBox.information(
            self, "Template Dibuat",
            f"Template berhasil disimpan di:\n\n{os.path.abspath(filename)}",
        )

    def start_import(self):
        if not self.rows:
            QMessageBox.warning(self, "Tidak Ada Data", "Pilih file terlebih dahulu.")
            return

        reply = QMessageBox.question(
            self,
            "Konfirmasi Import",
            f"Akan mengimport {len(self.rows)} ijazah ke "
            f"{'SERVER' if self.is_server_mode else 'DATABASE LOKAL'}.\n\n"
            f"Lanjutkan?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.btn_import.setEnabled(False)
        self.btn_load.setEnabled(False)
        self.progress.setValue(0)
        self.progress.setMaximum(len(self.rows))
        self.txt_log.setPlainText(f"⏳ Memulai import {len(self.rows)} ijazah...\n\n")

        self.worker = ImportWorker(self.blockchain, self.rows)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished_ok.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, current, total, message):
        self.progress.setValue(current)
        self.txt_log.append(message)

    def _on_finished(self, success, failed, errors):
        self.btn_import.setEnabled(True)
        self.btn_load.setEnabled(True)

        summary = f"\n{'═' * 60}\n"
        summary += f"  IMPORT SELESAI\n"
        summary += f"{'═' * 60}\n"
        summary += f"  ✓ Berhasil : {success}\n"
        summary += f"  ✗ Gagal    : {failed}\n"
        summary += f"  Total      : {success + failed}\n"

        if errors:
            summary += f"\n  Error pertama:\n"
            for err in errors[:5]:
                summary += f"    - {err}\n"

        self.txt_log.append(summary)

        if failed == 0:
            QMessageBox.information(
                self, "Import Berhasil",
                f"✅ {success} ijazah berhasil diimport!\n\n"
                f"Refresh dashboard analitik untuk melihat data.",
            )
        elif success == 0:
            QMessageBox.critical(
                self, "Import Gagal",
                f"❌ Semua {failed} baris gagal.\n\nPeriksa log untuk detail.",
            )
        else:
            QMessageBox.warning(
                self, "Import Sebagian Berhasil",
                f"⚠ {success} berhasil, {failed} gagal.\n\nPeriksa log untuk detail.",
            )