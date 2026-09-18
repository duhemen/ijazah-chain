import datetime
import os
import tempfile
import textwrap
from io import BytesIO

import qrcode
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QFormLayout, QFrame, QGraphicsDropShadowEffect, QScrollArea,
    QMessageBox, QFileDialog, QComboBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QPixmap

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Spacer
from reportlab.graphics.shapes import (
    Drawing, Rect, Line, String, Circle, Image as RLImage,
)

from app.config import MODE
from app.constants import (
    daftar_fakultas, daftar_prodi, daftar_tahun,
    normalisasi_fakultas, normalisasi_prodi,
)
from app.network.api_client import ApiError


# ============================================================
# KONSTANTA TEMPLATE
# ============================================================
TEMPLATE_KLASIK = "Klasik (default)"
TEMPLATE_MODERN = "Modern"
TEMPLATE_MINIMALIS = "Minimalis"
TEMPLATE_LIST = [TEMPLATE_KLASIK, TEMPLATE_MODERN, TEMPLATE_MINIMALIS]

# Warna per template (untuk preview & PDF)
TEMPLATE_COLORS = {
    TEMPLATE_KLASIK: {
        "bg": "#fcf9f2",
        "border": "#3d3023",
        "text": "#1c150f",
        "muted": "#555555",
        "accent": "#b53c26",
        "signature_label": "#5a4a3a",
    },
    TEMPLATE_MODERN: {
        "bg": "#f5f8fb",
        "border": "#1e40af",
        "text": "#0a1832",
        "muted": "#4a5568",
        "accent": "#1e40af",
        "signature_label": "#1e40af",
    },
    TEMPLATE_MINIMALIS: {
        "bg": "#ffffff",
        "border": "#d1d5db",
        "text": "#111827",
        "muted": "#6b7280",
        "accent": "#111827",
        "signature_label": "#6b7280",
    },
}


BULAN_ID = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]


def tanggal_indonesia(dt=None):
    dt = dt or datetime.datetime.now()
    return f"{dt.day} {BULAN_ID[dt.month - 1]} {dt.year}"


def wrap_text_lines(text, max_chars):
    return textwrap.wrap(text, max_chars) or [""]


def make_qr_pixmap(data_str, box_size=4, border=1):
    qr = qrcode.QRCode(version=1, box_size=box_size, border=border)
    qr.add_data(data_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    pixmap = QPixmap()
    pixmap.loadFromData(buf.getvalue(), "PNG")
    return pixmap


# ============================================================
# CERTIFICATE PREVIEW (mendukung 3 template)
# ============================================================
class CertificatePreview(QFrame):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(380, 494)
        self.setStyleSheet("background-color: #fcf9f2; border-radius: 4px;")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(6)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow)

        self.qr_pixmap = None
        self.template = TEMPLATE_KLASIK
        self.cert_data = {
            "nama": "[NAMA LULUSAN LENGKAP]",
            "nim": "[NIM / NO. INDUK]",
            "jurusan": "[PROGRAM STUDI / JURUSAN]",
            "fakultas": "[FAKULTAS]",
            "gelar": "[GELAR RESMI]",
            "nomor_seri": "[NO. SERI NASIONAL]",
            "judul_skripsi": "[JUDUL TUGAS AKHIR / SKRIPSI MAHASISWA]",
            "institusi": "UNIVERSITAS GADJAH MADA",
            "rektor": "Prof. Dr. Ir. Emen",
            "dekan": "Dr. Mode AI, M.Sc.",
            "custom_footnote": (
                "Diverifikasi secara sah melalui sistem kriptografi "
                "Buku Besar Terdesentralisasi."
            ),
            "tanggal": tanggal_indonesia(),
            "hash": "BELUM TERENKRIPSI",
        }

    def set_template(self, template_name: str):
        if template_name not in TEMPLATE_LIST:
            template_name = TEMPLATE_KLASIK
        self.template = template_name
        self.update()

    def set_qr_from_data(self, data_str):
        try:
            self.qr_pixmap = make_qr_pixmap(data_str, box_size=4, border=1)
        except Exception:
            self.qr_pixmap = None
        self.update()

    def clear_qr(self):
        self.qr_pixmap = None
        self.update()

    def update_preview(self, **kwargs):
        for key, value in kwargs.items():
            if value.strip():
                if key in ["nama", "jurusan", "fakultas", "institusi", "judul_skripsi"]:
                    self.cert_data[key] = value.upper()
                else:
                    self.cert_data[key] = value
            else:
                placeholders = {
                    "nama": "[NAMA LULUSAN LENGKAP]",
                    "nim": "[NIM / NO. INDUK]",
                    "jurusan": "[PROGRAM STUDI / JURUSAN]",
                    "fakultas": "[FAKULTAS]",
                    "gelar": "[GELAR RESMI]",
                    "nomor_seri": "[NO. SERI NASIONAL]",
                    "judul_skripsi": "[JUDUL SKRIPSI]",
                    "institusi": "[NAMA INSTITUSI KAMPUS]",
                    "rektor": "[NAMA REKTOR]",
                    "dekan": "[NAMA DEKAN]",
                    "custom_footnote": "[TEKS OTENTIKASI FOOTNOTE]",
                }
                self.cert_data[key] = placeholders.get(key, "")
        self.update()

    # ============================================================
    # PAINT EVENT - dispatch by template
    # ============================================================
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        base_width, base_height = 500, 650
        scale_x = self.width() / base_width
        scale_y = self.height() / base_height
        scale = min(scale_x, scale_y)

        painter.translate(
            (self.width() - base_width * scale) / 2,
            (self.height() - base_height * scale) / 2,
        )
        painter.scale(scale, scale)

        if self.template == TEMPLATE_MODERN:
            self._paint_modern(painter, base_width, base_height)
        elif self.template == TEMPLATE_MINIMALIS:
            self._paint_minimalis(painter, base_width, base_height)
        else:
            self._paint_klasik(painter, base_width, base_height)

    # ---------- TEMPLATE: KLASIK ----------
    def _paint_klasik(self, painter, w, h):
        c = TEMPLATE_COLORS[TEMPLATE_KLASIK]

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(c["bg"])))
        painter.drawRect(0, 0, w, h)

        # Bingkai
        painter.setPen(QPen(QColor(c["border"]), 5, Qt.PenStyle.SolidLine))
        painter.drawRect(15, 15, w - 30, h - 30)
        painter.setPen(QPen(QColor(c["border"]), 1, Qt.PenStyle.DashLine))
        painter.drawRect(22, 22, w - 44, h - 44)

        # Nomor seri
        painter.setPen(QPen(QColor(c["muted"])))
        painter.setFont(QFont("Arial", 7))
        painter.drawText(30, 40, f"No. Seri Nasional: {self.cert_data['nomor_seri']}")

        # QR
        if self.qr_pixmap is not None:
            painter.drawPixmap(400, 30, 75, 75, self.qr_pixmap)

        # Watermark
        wm = QColor(c["border"]); wm.setAlpha(15)
        painter.setPen(QPen(wm, 2))
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.drawEllipse(175, 230, 150, 150)
        painter.drawRect(225, 280, 50, 50)

        # Teks
        painter.setPen(QPen(QColor(c["text"])))
        painter.setFont(QFont("Times New Roman", 13, QFont.Weight.Bold))
        painter.drawText(0, 52, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         self.cert_data["institusi"])

        painter.setFont(QFont("Times New Roman", 22, QFont.Weight.Bold))
        painter.drawText(0, 78, w, 35, int(Qt.AlignmentFlag.AlignCenter), "I J A Z A H")

        painter.setFont(QFont("Georgia", 8, QFont.Weight.Bold))
        painter.drawText(0, 122, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         "MEMBERIKAN KEPADA")

        painter.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
        painter.drawText(0, 155, w, 25, int(Qt.AlignmentFlag.AlignCenter),
                         self.cert_data["nama"])

        painter.setFont(QFont("Georgia", 9))
        painter.drawText(0, 180, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         f"Nomor Induk Mahasiswa: {self.cert_data['nim']}")

        painter.setFont(QFont("Georgia", 8, QFont.Weight.Bold))
        painter.drawText(0, 212, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         "SEBAGAI TANDA KELULUSAN DARI PROGRAM STUDI")

        painter.setFont(QFont("Times New Roman", 12, QFont.Weight.Bold))
        painter.drawText(0, 236, w, 25, int(Qt.AlignmentFlag.AlignCenter),
                         self.cert_data["jurusan"])

        painter.setFont(QFont("Georgia", 8))
        painter.setPen(QPen(QColor(c["signature_label"])))
        painter.drawText(0, 258, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         f"Fakultas: {self.cert_data['fakultas']}")

        painter.setPen(QPen(QColor(c["text"])))
        painter.setFont(QFont("Georgia", 9))
        painter.drawText(0, 278, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         f"Kepadanya disematkan Gelar Akademik resmi: {self.cert_data['gelar']}")

        painter.setFont(QFont("Georgia", 8, QFont.Weight.Bold))
        painter.drawText(40, 308, "Dengan Judul Tugas Akhir / Skripsi:")

        painter.setFont(QFont("Courier New", 9))
        painter.drawText(
            40, 322, w - 80, 45,
            int(Qt.AlignmentFlag.AlignLeft) | int(Qt.TextFlag.TextWordWrap),
            self.cert_data["judul_skripsi"],
        )

        fi = QFont("Georgia", 9); fi.setItalic(True)
        painter.setFont(fi)
        painter.drawText(
            40, 375, w - 80, 50,
            int(Qt.AlignmentFlag.AlignLeft) | int(Qt.TextFlag.TextWordWrap),
            "Ijazah ini ditandatangani secara sah sesuai dengan peraturan "
            "perundang-undangan negara dan hak kesarjanaan yang berlaku.",
        )

        painter.setFont(QFont("Georgia", 9))
        painter.drawText(280, 440, f"Yogyakarta, {self.cert_data['tanggal']}")
        painter.drawText(60, 470, f"Rektor {self.cert_data['institusi']},")
        painter.drawText(310, 470, "Dekan Fakultas,")

        painter.setFont(QFont("Brush Script MT", 15))
        painter.drawText(50, 515, self.cert_data["rektor"])
        painter.drawText(300, 515, self.cert_data["dekan"])

        # Stempel
        cl = QColor(c["accent"]); cl.setAlpha(190)
        cf = QColor(c["accent"]); cf.setAlpha(25)
        painter.setPen(QPen(cl, 2))
        painter.setBrush(QBrush(cf))
        painter.drawEllipse(320, 520, 75, 75)
        painter.setFont(QFont("Arial", 6, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(c["accent"])))
        painter.drawText(320, 550, 75, 15, int(Qt.AlignmentFlag.AlignCenter), "TERVALIDASI")
        painter.drawText(320, 560, 75, 15, int(Qt.AlignmentFlag.AlignCenter), "BLOCKCHAIN")

        # Footnote
        painter.setPen(QPen(QColor("#111111"), 1))
        painter.drawLine(25, 600, w - 25, 600)
        painter.setFont(QFont("Courier New", 6, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(c["muted"])))
        gab = f"{self.cert_data['custom_footnote']} | HASH: {self.cert_data['hash'][:40]}..."
        painter.drawText(
            25, 610, w - 50, 30,
            int(Qt.AlignmentFlag.AlignLeft) | int(Qt.TextFlag.TextWordWrap),
            gab,
        )

    # ---------- TEMPLATE: MODERN ----------
    def _paint_modern(self, painter, w, h):
        c = TEMPLATE_COLORS[TEMPLATE_MODERN]

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(c["bg"])))
        painter.drawRect(0, 0, w, h)

        # Header block warna solid di atas
        painter.setBrush(QBrush(QColor(c["accent"])))
        painter.drawRect(0, 0, w, 8)

        # Aksen garis kiri
        painter.setBrush(QBrush(QColor(c["accent"])))
        painter.drawRect(0, 0, 6, h)

        # Nomor seri
        painter.setPen(QPen(QColor(c["muted"])))
        painter.setFont(QFont("Arial", 7))
        painter.drawText(30, 40, f"No. Seri Nasional: {self.cert_data['nomor_seri']}")

        # QR
        if self.qr_pixmap is not None:
            painter.drawPixmap(400, 30, 75, 75, self.qr_pixmap)

        # Header institusi
        painter.setPen(QPen(QColor(c["accent"])))
        painter.setFont(QFont("Helvetica", 11, QFont.Weight.Bold))
        painter.drawText(0, 55, w, 25, int(Qt.AlignmentFlag.AlignCenter),
                         self.cert_data["institusi"])

        # Garis aksen di bawah institusi
        painter.setPen(QPen(QColor(c["accent"]), 2))
        painter.drawLine(150, 82, w - 150, 82)

        # Judul
        painter.setPen(QPen(QColor(c["text"])))
        painter.setFont(QFont("Helvetica", 26, QFont.Weight.Bold))
        painter.drawText(0, 95, w, 40, int(Qt.AlignmentFlag.AlignCenter), "IJAZAH")

        painter.setFont(QFont("Helvetica", 8))
        painter.setPen(QPen(QColor(c["muted"])))
        painter.drawText(0, 130, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         "DENGAN INI MENYATAKAN BAHWA")

        # Nama
        painter.setPen(QPen(QColor(c["text"])))
        painter.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        painter.drawText(0, 162, w, 25, int(Qt.AlignmentFlag.AlignCenter),
                         self.cert_data["nama"])

        painter.setFont(QFont("Helvetica", 9))
        painter.setPen(QPen(QColor(c["muted"])))
        painter.drawText(0, 188, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         f"NIM: {self.cert_data['nim']}")

        # Divider aksen
        painter.setPen(QPen(QColor(c["accent"]), 1))
        painter.drawLine(80, 210, w - 80, 210)

        # Jurusan
        painter.setPen(QPen(QColor(c["text"])))
        painter.setFont(QFont("Helvetica", 11, QFont.Weight.Bold))
        painter.drawText(0, 222, w, 22, int(Qt.AlignmentFlag.AlignCenter),
                         self.cert_data["jurusan"])

        painter.setFont(QFont("Helvetica", 9))
        painter.setPen(QPen(QColor(c["muted"])))
        painter.drawText(0, 244, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         f"Fakultas {self.cert_data['fakultas']}")

        painter.setPen(QPen(QColor(c["text"])))
        painter.setFont(QFont("Helvetica", 9))
        painter.drawText(0, 264, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         f"Gelar: {self.cert_data['gelar']}")

        # Skripsi
        painter.setFont(QFont("Helvetica", 7, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(c["muted"])))
        painter.drawText(40, 300, "JUDUL TUGAS AKHIR / SKRIPSI:")
        painter.setFont(QFont("Courier New", 9))
        painter.setPen(QPen(QColor(c["text"])))
        painter.drawText(
            40, 316, w - 80, 45,
            int(Qt.AlignmentFlag.AlignLeft) | int(Qt.TextFlag.TextWordWrap),
            self.cert_data["judul_skripsi"],
        )

        # Footnote kutipan
        painter.setFont(QFont("Helvetica", 8))
        painter.setPen(QPen(QColor(c["muted"])))
        painter.drawText(
            40, 375, w - 80, 40,
            int(Qt.AlignmentFlag.AlignLeft) | int(Qt.TextFlag.TextWordWrap),
            "Dokumen ini dilindungi oleh tanda tangan kriptografi "
            "dan tercatat permanen di blockchain.",
        )

        # Tanda tangan
        painter.setFont(QFont("Helvetica", 9))
        painter.setPen(QPen(QColor(c["text"])))
        painter.drawText(280, 445, f"Yogyakarta, {self.cert_data['tanggal']}")
        painter.drawText(60, 475, f"Rektor {self.cert_data['institusi']},")
        painter.drawText(310, 475, "Dekan Fakultas,")

        painter.setFont(QFont("Helvetica", 11, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(c["accent"])))
        painter.drawText(60, 515, self.cert_data["rektor"])
        painter.drawText(310, 515, self.cert_data["dekan"])

        # Garis tanda tangan
        painter.setPen(QPen(QColor(c["muted"]), 1))
        painter.drawLine(50, 495, 260, 495)
        painter.drawLine(300, 495, 460, 495)

        # Badge verified (kotak bukan bulat)
        painter.setPen(QPen(QColor(c["accent"]), 2))
        painter.setBrush(QBrush(QColor(c["accent"])))
        painter.drawRect(360, 530, 100, 30)
        painter.setPen(QPen(QColor("#ffffff")))
        painter.setFont(QFont("Helvetica", 7, QFont.Weight.Bold))
        painter.drawText(360, 540, 100, 12, int(Qt.AlignmentFlag.AlignCenter), "BLOCKCHAIN")
        painter.drawText(360, 552, 100, 12, int(Qt.AlignmentFlag.AlignCenter), "VERIFIED")

        # Footnote bottom
        painter.setPen(QPen(QColor(c["border"]), 1))
        painter.drawLine(25, 600, w - 25, 600)
        painter.setFont(QFont("Courier New", 6))
        painter.setPen(QPen(QColor(c["muted"])))
        gab = f"{self.cert_data['custom_footnote']} | HASH: {self.cert_data['hash'][:40]}..."
        painter.drawText(
            25, 610, w - 50, 30,
            int(Qt.AlignmentFlag.AlignLeft) | int(Qt.TextFlag.TextWordWrap),
            gab,
        )

    # ---------- TEMPLATE: MINIMALIS ----------
    def _paint_minimalis(self, painter, w, h):
        c = TEMPLATE_COLORS[TEMPLATE_MINIMALIS]

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(c["bg"])))
        painter.drawRect(0, 0, w, h)

        # Border tipis
        painter.setPen(QPen(QColor(c["border"]), 1))
        painter.drawRect(30, 30, w - 60, h - 60)

        # Nomor seri
        painter.setPen(QPen(QColor(c["muted"])))
        painter.setFont(QFont("Helvetica", 7))
        painter.drawText(45, 50, f"No. Seri: {self.cert_data['nomor_seri']}")

        # QR
        if self.qr_pixmap is not None:
            painter.drawPixmap(395, 42, 65, 65, self.qr_pixmap)

        # Header - text kecil di atas
        painter.setFont(QFont("Helvetica", 8, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(c["accent"])))
        painter.drawText(0, 65, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         self.cert_data["institusi"])

        # Judul besar minimalis
        painter.setPen(QPen(QColor(c["text"])))
        painter.setFont(QFont("Helvetica", 20))
        painter.drawText(0, 100, w, 35, int(Qt.AlignmentFlag.AlignCenter), "Ijazah")

        # Garis horizontal pendek
        painter.setPen(QPen(QColor(c["accent"]), 2))
        painter.drawLine(w // 2 - 25, 142, w // 2 + 25, 142)

        painter.setFont(QFont("Helvetica", 8))
        painter.setPen(QPen(QColor(c["muted"])))
        painter.drawText(0, 160, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         "Diberikan kepada")

        # Nama
        painter.setPen(QPen(QColor(c["text"])))
        painter.setFont(QFont("Helvetica", 15, QFont.Weight.Bold))
        painter.drawText(0, 195, w, 25, int(Qt.AlignmentFlag.AlignCenter),
                         self.cert_data["nama"])

        painter.setFont(QFont("Helvetica", 9))
        painter.setPen(QPen(QColor(c["muted"])))
        painter.drawText(0, 222, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         self.cert_data["nim"])

        # Info grid
        painter.setPen(QPen(QColor(c["text"])))
        painter.setFont(QFont("Helvetica", 9))
        painter.drawText(0, 262, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         self.cert_data["jurusan"])

        painter.setFont(QFont("Helvetica", 8))
        painter.setPen(QPen(QColor(c["muted"])))
        painter.drawText(0, 282, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         self.cert_data["fakultas"])

        painter.setPen(QPen(QColor(c["text"])))
        painter.setFont(QFont("Helvetica", 8, QFont.Weight.Bold))
        painter.drawText(0, 305, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         f"Gelar {self.cert_data['gelar']}")

        # Skripsi
        painter.setFont(QFont("Helvetica", 7))
        painter.setPen(QPen(QColor(c["muted"])))
        painter.drawText(0, 340, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         "Tugas Akhir / Skripsi:")
        painter.setFont(QFont("Courier New", 8))
        painter.setPen(QPen(QColor(c["text"])))
        painter.drawText(
            70, 356, w - 140, 40,
            int(Qt.AlignmentFlag.AlignHCenter) | int(Qt.TextFlag.TextWordWrap),
            f'"{self.cert_data["judul_skripsi"]}"',
        )

        # Tanda tangan ringkas
        painter.setFont(QFont("Helvetica", 8))
        painter.setPen(QPen(QColor(c["muted"])))
        painter.drawText(0, 440, w, 20, int(Qt.AlignmentFlag.AlignCenter),
                         f"Yogyakarta, {self.cert_data['tanggal']}")

        painter.setFont(QFont("Helvetica", 8))
        painter.setPen(QPen(QColor(c["text"])))
        painter.drawText(60, 480, "Rektor,")
        painter.drawText(320, 480, "Dekan,")

        painter.setFont(QFont("Helvetica", 10, QFont.Weight.Bold))
        painter.drawText(60, 520, self.cert_data["rektor"])
        painter.drawText(320, 520, self.cert_data["dekan"])

        painter.setPen(QPen(QColor(c["border"]), 1))
        painter.drawLine(45, 500, 240, 500)
        painter.drawLine(305, 500, 460, 500)

        # Footer
        painter.setPen(QPen(QColor(c["border"]), 1))
        painter.drawLine(45, 600, w - 45, 600)
        painter.setFont(QFont("Courier New", 6))
        painter.setPen(QPen(QColor(c["muted"])))
        gab = f"{self.cert_data['custom_footnote']} | HASH: {self.cert_data['hash'][:40]}..."
        painter.drawText(
            45, 610, w - 90, 30,
            int(Qt.AlignmentFlag.AlignLeft) | int(Qt.TextFlag.TextWordWrap),
            gab,
        )


# ============================================================
# TAB ISSUE
# ============================================================
class TabIssue(QWidget):
    def __init__(self, blockchain):
        super().__init__()
        self.blockchain = blockchain
        self.last_issued_data = None

        init_layout = QHBoxLayout(self)
        init_layout.setContentsMargins(15, 15, 15, 15)
        init_layout.setSpacing(20)

        # ============ PANEL KIRI ============
        left_container = QWidget()
        left_container.setFixedWidth(420)
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        form_title = QLabel("📝 Registrasi & Penerbitan Ijazah")
        form_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        form_title.setStyleSheet("color: #ffffff; padding-bottom: 5px;")
        left_layout.addWidget(form_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        form_panel = QWidget()
        form_panel_layout = QVBoxLayout(form_panel)
        form_panel_layout.setContentsMargins(0, 0, 10, 0)
        form_panel_layout.setSpacing(8)

        # ---------- Input fields ----------
        self.input_institusi = QLineEdit()
        self.input_institusi.setPlaceholderText("Contoh: Universitas Gadjah Mada")

        self.combo_fakultas = QComboBox()
        self.combo_fakultas.setEditable(True)
        self.combo_fakultas.addItem("")
        for fak in daftar_fakultas():
            self.combo_fakultas.addItem(fak)
        self.combo_fakultas.setCurrentIndex(0)
        self.combo_fakultas.lineEdit().setPlaceholderText("Pilih atau ketik fakultas...")

        self.combo_prodi = QComboBox()
        self.combo_prodi.setEditable(True)
        self.combo_prodi.lineEdit().setPlaceholderText("Pilih prodi (pilih fakultas dulu)")

        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText("Nama lengkap sesuai ijazah")
        self.input_nim = QLineEdit()
        self.input_nim.setPlaceholderText("Contoh: 21/123456/TK/78901")
        self.input_gelar = QLineEdit()
        self.input_gelar.setPlaceholderText("Contoh: S.Kom, S.H, S.E")
        self.input_noseri = QLineEdit()
        self.input_noseri.setPlaceholderText("Contoh: UGM-2026-001")

        self.combo_tahun = QComboBox()
        self.combo_tahun.addItems(daftar_tahun())

        self.input_skripsi = QLineEdit()
        self.input_skripsi.setPlaceholderText("Judul skripsi / tugas akhir")
        self.input_rektor = QLineEdit()
        self.input_rektor.setPlaceholderText("Contoh: Prof. Dr. Ir. Ova Emen")
        self.input_dekan = QLineEdit()
        self.input_dekan.setPlaceholderText("Contoh: Dr. Mode AI, M.Sc.")
        self.input_footnote = QLineEdit()
        self.input_footnote.setPlaceholderText(
            "Contoh: Diverifikasi melalui jaringan blockchain nasional."
        )

        # ============ DROPDOWN TEMPLATE (BARU) ============
        self.combo_template = QComboBox()
        self.combo_template.addItems(TEMPLATE_LIST)
        self.combo_template.setCurrentIndex(0)  # default: Klasik
        self.combo_template.setStyleSheet("""
            QComboBox {
                background-color: #2a2a30;
                border: 1px solid #00f0ff;
                border-radius: 5px;
                padding: 7px;
                color: #00f0ff;
                font-size: 12px;
                font-weight: bold;
            }
            QComboBox:focus { border: 1px solid #00bccc; }
            QComboBox::drop-down { border: none; width: 24px; }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #00f0ff;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #202024;
                border: 1px solid #00f0ff;
                color: #e1e1e6;
                selection-background-color: #00f0ff;
                selection-color: #121214;
                outline: none;
            }
        """)

        input_style = """
            QLineEdit {
                background-color: #202024;
                border: 1px solid #29292e;
                border-radius: 5px;
                padding: 7px;
                color: #ffffff;
                font-size: 12px;
            }
            QLineEdit:focus { border: 1px solid #00f0ff; }
        """

        for inp in [
            self.input_institusi, self.input_nama, self.input_nim,
            self.input_gelar, self.input_noseri, self.input_skripsi,
            self.input_rektor, self.input_dekan, self.input_footnote,
        ]:
            inp.setStyleSheet(input_style)

        # ============ FIELD LAYOUT (dengan Template di atas) ============
        fields = [
            ("🎨 Template Ijazah:", self.combo_template),   # <-- BARU di atas
            ("Nama Institusi Kampus:", self.input_institusi),
            ("Fakultas:", self.combo_fakultas),
            ("Program Studi / Jurusan:", self.combo_prodi),
            ("Nama Lengkap Mahasiswa:", self.input_nama),
            ("Nomor Induk (NIM):", self.input_nim),
            ("Gelar Akademik:", self.input_gelar),
            ("No. Seri Nasional Ijazah:", self.input_noseri),
            ("Tahun Lulus:", self.combo_tahun),
            ("Judul Skripsi / Tugas Akhir:", self.input_skripsi),
            ("Nama Rektor Aktif:", self.input_rektor),
            ("Nama Dekan Fakultas:", self.input_dekan),
            ("Footnote Kustom:", self.input_footnote),
        ]

        fields_layout = QFormLayout()
        fields_layout.setVerticalSpacing(8)
        for label, obj in fields:
            fields_layout.addRow(label, obj)

        form_panel_layout.addLayout(fields_layout)
        scroll.setWidget(form_panel)
        left_layout.addWidget(scroll)

        # ---------- Signals ----------
        self.combo_fakultas.currentTextChanged.connect(self._on_fakultas_changed)
        self.combo_template.currentTextChanged.connect(self._on_template_changed)
        for obj in [
            self.input_institusi, self.input_nama, self.input_nim,
            self.input_gelar, self.input_noseri, self.input_skripsi,
            self.input_rektor, self.input_dekan, self.input_footnote,
        ]:
            obj.textChanged.connect(self.live_update)
        self.combo_prodi.currentTextChanged.connect(self.live_update)
        self.combo_tahun.currentTextChanged.connect(self.live_update)

        # ---------- Buttons ----------
        self.btn_issue = QPushButton("🔒 DAFTARKAN LEGALITAS KE SECURE LEDGER")
        self.btn_issue.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.btn_issue.setStyleSheet("""
            QPushButton {
                background-color: #00f0ff; color: #121214;
                border-radius: 6px; padding: 12px;
            }
            QPushButton:hover { background-color: #00bccc; }
            QPushButton:disabled { background-color: #29292e; color: #555; }
        """)
        self.btn_issue.clicked.connect(self.issue_certificate)
        left_layout.addWidget(self.btn_issue)

        self.btn_print = QPushButton("🖨️ CETAK & SIMPAN IJAZAH (PDF)")
        self.btn_print.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.btn_print.setEnabled(False)
        self.btn_print.setStyleSheet("""
            QPushButton {
                background-color: #29292e; color: #7c7c8a;
                border: 1px solid #3e3e44; border-radius: 6px; padding: 12px;
            }
            QPushButton:enabled {
                background-color: #2ecc71; color: #ffffff; border: none;
            }
            QPushButton:enabled:hover { background-color: #27ae60; }
        """)
        self.btn_print.clicked.connect(self.print_to_pdf)
        left_layout.addWidget(self.btn_print)

        # ============ PANEL KANAN ============
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)

        self.preview_title = QLabel(
            f"🖼️ Pratinjau Ijazah — Template: {TEMPLATE_KLASIK}"
        )
        self.preview_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        self.preview_title.setStyleSheet("color: #7c7c8a;")
        self.preview_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.preview_title)

        center_wrapper = QHBoxLayout()
        center_wrapper.addStretch(1)
        self.cert_preview = CertificatePreview()
        center_wrapper.addWidget(self.cert_preview, stretch=4)
        center_wrapper.addStretch(1)
        right_layout.addLayout(center_wrapper)
        right_layout.setStretch(1, 1)

        init_layout.addWidget(left_container)
        init_layout.addWidget(right_container, stretch=1)

    # ============================================================
    # TEMPLATE CHANGE
    # ============================================================
    def _on_template_changed(self, template_name: str):
        self.cert_preview.set_template(template_name)
        self.preview_title.setText(
            f"🖼️ Pratinjau Ijazah — Template: {template_name}"
        )

    # ============================================================
    # FAKULTAS → PRODI
    # ============================================================
    def _on_fakultas_changed(self):
        fak = self.combo_fakultas.currentText().strip()
        self.combo_prodi.blockSignals(True)
        current_prodi = self.combo_prodi.currentText().strip()
        self.combo_prodi.clear()
        prodi_list = daftar_prodi(fak)
        if prodi_list:
            self.combo_prodi.addItems(prodi_list)
            if current_prodi and current_prodi in prodi_list:
                self.combo_prodi.setCurrentText(current_prodi)
        self.combo_prodi.blockSignals(False)
        self.live_update()

    # ============================================================
    # LIVE PREVIEW
    # ============================================================
    def live_update(self):
        self.cert_preview.update_preview(
            institusi=self.input_institusi.text(),
            fakultas=self.combo_fakultas.currentText(),
            jurusan=self.combo_prodi.currentText(),
            nama=self.input_nama.text(),
            nim=self.input_nim.text(),
            gelar=self.input_gelar.text(),
            nomor_seri=self.input_noseri.text(),
            judul_skripsi=self.input_skripsi.text(),
            rektor=self.input_rektor.text(),
            dekan=self.input_dekan.text(),
            custom_footnote=self.input_footnote.text(),
        )

    # ============================================================
    # CLEAR
    # ============================================================
    def clear_form(self):
        self.input_institusi.clear()
        self.input_nama.clear()
        self.input_nim.clear()
        self.input_gelar.clear()
        self.input_noseri.clear()
        self.input_skripsi.clear()
        self.input_rektor.clear()
        self.input_dekan.clear()
        self.input_footnote.clear()
        self.combo_fakultas.setCurrentIndex(0)
        self.combo_prodi.clear()
        self.combo_tahun.setCurrentIndex(0)
        # Template tidak direset, biarkan pilihan user tetap
        self.cert_preview.cert_data["hash"] = "BELUM TERENKRIPSI"
        self.cert_preview.clear_qr()

    # ============================================================
    # ISSUE
    # ============================================================
    def issue_certificate(self):
        institusi = self.input_institusi.text().strip() or "UNIVERSITAS GADJAH MADA"
        fakultas = normalisasi_fakultas(self.combo_fakultas.currentText())
        prodi = normalisasi_prodi(self.combo_prodi.currentText())
        nama = self.input_nama.text().strip()
        nim = self.input_nim.text().strip()
        gelar = self.input_gelar.text().strip()
        no_seri = self.input_noseri.text().strip()
        tahun = self.combo_tahun.currentText().strip()
        skripsi = self.input_skripsi.text().strip() or "BELUM ADA JUDUL SKRIPSI"
        rektor = self.input_rektor.text().strip() or "Prof. Dr. Ir. Emen"
        dekan = self.input_dekan.text().strip() or "Dr. Mode AI, M.Sc."
        footnote = (
            self.input_footnote.text().strip()
            or "Diverifikasi secara sah melalui sistem kriptografi "
               "Buku Besar Terdesentralisasi."
        )

        errors = []
        if not nama: errors.append("• Nama mahasiswa wajib diisi")
        if not nim: errors.append("• NIM wajib diisi")
        if not prodi: errors.append("• Program studi wajib dipilih")
        if not gelar: errors.append("• Gelar akademik wajib diisi")
        if not no_seri: errors.append("• Nomor seri nasional wajib diisi")

        if errors:
            QMessageBox.warning(
                self, "Validasi Gagal",
                "Mohon lengkapi kolom wajib berikut:\n\n" + "\n".join(errors),
            )
            return

        tanggal = tanggal_indonesia()

        data_ijazah = {
            "nama": nama.upper(),
            "nim": nim,
            "fakultas": fakultas if fakultas else "",
            "jurusan": prodi,
            "gelar": gelar,
            "nomor_seri": no_seri,
            "judul_skripsi": skripsi.upper(),
            "institusi": institusi.upper(),
            "rektor": rektor,
            "dekan": dekan,
            "custom_footnote": footnote,
            "tanggal": tanggal,
            "tahun_lulus": int(tahun) if tahun.isdigit() else None,
            "template": self.combo_template.currentText(),   # simpan pilihan
        }

        try:
            if MODE == "server":
                new_block = self.blockchain.add_block(data_ijazah)
            else:
                new_block = self.blockchain.add_block(data_ijazah)
                from app.blockchain.storage import save_block_to_db
                save_block_to_db(new_block)
        except ApiError as e:
            QMessageBox.critical(
                self, "Gagal Terhubung ke Server",
                f"Server menolak permintaan:\n\n{e}\n\n"
                f"Periksa koneksi & API key di config.py.",
            )
            return
        except Exception as e:
            QMessageBox.critical(
                self, "Error Tidak Terduga",
                f"Terjadi kesalahan:\n\n{e}",
            )
            return

        self.cert_preview.cert_data["hash"] = new_block.hash
        self.cert_preview.cert_data["tanggal"] = tanggal

        self.last_issued_data = data_ijazah.copy()
        self.last_issued_data["hash"] = new_block.hash

        self.cert_preview.set_qr_from_data(self._build_qr_payload(self.last_issued_data))
        self.btn_print.setEnabled(True)

        mode_label = "server" if MODE == "server" else "lokal"
        QMessageBox.information(
            self, "Berhasil Diterbitkan",
            f"✅ Ijazah atas nama {nama.upper()} berhasil diterbitkan!\n\n"
            f"📦 Blok       : #{new_block.index}\n"
            f"🔐 Hash       : {new_block.hash[:32]}...\n"
            f"🎨 Template   : {self.combo_template.currentText()}\n"
            f"🏛️  Fakultas   : {fakultas or '-'}\n"
            f"🎓 Prodi      : {prodi}\n"
            f"📅 Tahun      : {tahun}\n"
            f"💾 Tersimpan  : Mode {mode_label}",
        )

    def _build_qr_payload(self, data):
        return (
            "IJAZAH NETWORK AUTHENTICATION\n"
            "============================\n"
            f"Kampus   : {data.get('institusi', '')}\n"
            f"Fakultas : {data.get('fakultas', '')}\n"
            f"Prodi    : {data.get('jurusan', '')}\n"
            f"Nama     : {data.get('nama', '')}\n"
            f"NIM      : {data.get('nim', '')}\n"
            f"Tahun    : {data.get('tahun_lulus', '')}\n"
            f"Hash     : {data.get('hash', '')}"
        )

    # ============================================================
    # PRINT PDF — dispatch by template
    # ============================================================
    def print_to_pdf(self):
        if not self.last_issued_data:
            QMessageBox.warning(
                self, "Cetak Gagal",
                "Tidak ada data ijazah aktif. Daftarkan legalitas terlebih dahulu.",
            )
            return

        d = self.last_issued_data
        default_name = f"Ijazah_{d['nim']}_{d['nama'].replace(' ', '_')}.pdf"

        filename, _ = QFileDialog.getSaveFileName(
            self, "Simpan Ijazah PDF", default_name, "PDF Files (*.pdf)",
        )
        if not filename:
            return
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        qr_path = None
        try:
            # Generate QR temp file
            qr = qrcode.QRCode(version=1, box_size=10, border=1)
            qr.add_data(self._build_qr_payload(d))
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                qr_path = tmp.name
            qr_img.save(qr_path)

            template = d.get("template", TEMPLATE_KLASIK)
            if template == TEMPLATE_MODERN:
                d_canvas = self._build_canvas_modern(d, qr_path)
            elif template == TEMPLATE_MINIMALIS:
                d_canvas = self._build_canvas_minimalis(d, qr_path)
            else:
                d_canvas = self._build_canvas_klasik(d, qr_path)

            def draw_page(canvas, doc):
                d_canvas.drawOn(canvas, 0, 0)

            doc = SimpleDocTemplate(
                filename, pagesize=landscape(A4),
                leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0,
                title=f"Ijazah {d.get('nama', '')}",
                author=d.get("institusi", ""),
            )
            doc.build([Spacer(1, 1)], onFirstPage=draw_page, onLaterPages=draw_page)

            QMessageBox.information(
                self, "Ekspor Berhasil",
                f"✅ Ijazah berhasil disimpan ke PDF!\n\n"
                f"🎨 Template: {template}\n"
                f"📁 {os.path.abspath(filename)}",
            )
            self.btn_print.setEnabled(False)
            self.last_issued_data = None
            self.clear_form()

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, "Ekspor Gagal",
                f"Terjadi kesalahan saat menyusun PDF:\n\n{e}",
            )
        finally:
            if qr_path and os.path.exists(qr_path):
                try:
                    os.remove(qr_path)
                except OSError:
                    pass

    # ============================================================
    # CANVAS BUILDERS PER TEMPLATE
    # ============================================================
    def _build_canvas_klasik(self, d, qr_path):
        c = TEMPLATE_COLORS[TEMPLATE_KLASIK]
        dc = Drawing(841, 595)

        dc.add(Rect(30, 30, 781, 535, fillColor=c["bg"],
                    strokeColor=c["border"], strokeWidth=5))
        dc.add(Rect(38, 38, 765, 519, fillColor=None,
                    strokeColor=c["border"], strokeWidth=1,
                    strokeDashArray=[4, 4]))

        dc.add(String(55, 535, f"No. Seri Nasional: {d.get('nomor_seri', '')}",
                      fontName="Helvetica", fontSize=8,
                      textAnchor="start", fillColor=c["muted"]))

        dc.add(String(420, 500, d.get("institusi", ""),
                      fontName="Times-Bold", fontSize=16, textAnchor="middle"))
        dc.add(String(420, 465, "I J A Z A H",
                      fontName="Times-Bold", fontSize=26, textAnchor="middle"))
        dc.add(String(420, 430, "MEMBERIKAN KEPADA",
                      fontName="Times-Bold", fontSize=10, textAnchor="middle"))
        dc.add(String(420, 390, d.get("nama", ""),
                      fontName="Times-Bold", fontSize=18, textAnchor="middle"))
        dc.add(String(420, 365, f"Nomor Induk Mahasiswa: {d.get('nim', '')}",
                      fontName="Times-Roman", fontSize=11, textAnchor="middle"))
        dc.add(String(420, 335, "SEBAGAI TANDA KELULUSAN DARI PROGRAM STUDI",
                      fontName="Times-Bold", fontSize=9, textAnchor="middle"))
        dc.add(String(420, 312, d.get("jurusan", ""),
                      fontName="Times-Bold", fontSize=15, textAnchor="middle"))

        if d.get("fakultas"):
            dc.add(String(420, 293, f"Fakultas: {d['fakultas']}",
                          fontName="Times-Italic", fontSize=10,
                          textAnchor="middle", fillColor=c["signature_label"]))

        dc.add(String(420, 272, f"Kepadanya disematkan Gelar Akademik resmi: {d.get('gelar', '')}",
                      fontName="Times-Roman", fontSize=11, textAnchor="middle"))

        dc.add(String(80, 235, "Dengan Judul Tugas Akhir / Skripsi:",
                      fontName="Times-Bold", fontSize=9, textAnchor="start"))
        for i, line in enumerate(wrap_text_lines(d.get("judul_skripsi", ""), 95)[:3]):
            dc.add(String(80, 215 - i * 12, line,
                          fontName="Courier", fontSize=10, textAnchor="start"))

        dc.add(String(80, 170, "Ijazah ini ditandatangani secara sah sesuai dengan peraturan perundang-undangan negara",
                      fontName="Times-Italic", fontSize=10, textAnchor="start"))
        dc.add(String(80, 155, "dan hak kesarjanaan yang berlaku di Republik Indonesia.",
                      fontName="Times-Italic", fontSize=10, textAnchor="start"))

        dc.add(String(590, 170, f"Yogyakarta, {d.get('tanggal', tanggal_indonesia())}",
                      fontName="Times-Roman", fontSize=10, textAnchor="start"))
        dc.add(String(170, 140, f"Rektor {d.get('institusi', '')},",
                      fontName="Times-Roman", fontSize=10, textAnchor="middle"))
        dc.add(String(650, 140, "Dekan Fakultas,",
                      fontName="Times-Roman", fontSize=10, textAnchor="middle"))
        dc.add(String(170, 90, d.get("rektor", ""),
                      fontName="Times-Bold", fontSize=11, textAnchor="middle"))
        dc.add(String(650, 90, d.get("dekan", ""),
                      fontName="Times-Bold", fontSize=11, textAnchor="middle"))

        dc.add(Circle(520, 95, 36, fillColor=c["accent"], fillOpacity=0.1,
                      strokeColor=c["accent"], strokeWidth=2))
        dc.add(String(520, 98, "TERVALIDASI", fontName="Helvetica-Bold",
                      fontSize=7, textAnchor="middle", fillColor=c["accent"]))
        dc.add(String(520, 88, "BLOCKCHAIN", fontName="Helvetica-Bold",
                      fontSize=7, textAnchor="middle", fillColor=c["accent"]))

        dc.add(RLImage(730, 50, 60, 60, qr_path))

        dc.add(Line(55, 75, 786, 75, strokeColor="#111111", strokeWidth=1))
        gab = f"{d.get('custom_footnote', '')} | BLOCKCHAIN HASH: {d.get('hash', '')}"
        for i, line in enumerate(wrap_text_lines(gab, 150)[:2]):
            dc.add(String(55, 60 - i * 8, line, fontName="Courier-Bold",
                          fontSize=6, textAnchor="start", fillColor=c["muted"]))
        return dc

    def _build_canvas_modern(self, d, qr_path):
        c = TEMPLATE_COLORS[TEMPLATE_MODERN]
        dc = Drawing(841, 595)

        # Background
        dc.add(Rect(0, 0, 841, 595, fillColor=c["bg"], strokeColor=None))
        # Header accent bar
        dc.add(Rect(0, 587, 841, 8, fillColor=c["accent"], strokeColor=None))
        # Left accent bar
        dc.add(Rect(0, 0, 6, 595, fillColor=c["accent"], strokeColor=None))

        dc.add(String(55, 535, f"No. Seri Nasional: {d.get('nomor_seri', '')}",
                      fontName="Helvetica", fontSize=8,
                      textAnchor="start", fillColor=c["muted"]))

        # Header institusi
        dc.add(String(420, 510, d.get("institusi", ""),
                      fontName="Helvetica-Bold", fontSize=13,
                      textAnchor="middle", fillColor=c["accent"]))
        dc.add(Line(280, 500, 560, 500, strokeColor=c["accent"], strokeWidth=1.5))

        dc.add(String(420, 460, "IJAZAH",
                      fontName="Helvetica-Bold", fontSize=30,
                      textAnchor="middle", fillColor=c["text"]))
        dc.add(String(420, 435, "DENGAN INI MENYATAKAN BAHWA",
                      fontName="Helvetica", fontSize=8,
                      textAnchor="middle", fillColor=c["muted"]))

        dc.add(String(420, 400, d.get("nama", ""),
                      fontName="Helvetica-Bold", fontSize=19,
                      textAnchor="middle", fillColor=c["text"]))
        dc.add(String(420, 380, f"NIM: {d.get('nim', '')}",
                      fontName="Helvetica", fontSize=10,
                      textAnchor="middle", fillColor=c["muted"]))

        dc.add(Line(320, 368, 520, 368, strokeColor=c["accent"], strokeWidth=1))

        dc.add(String(420, 348, d.get("jurusan", ""),
                      fontName="Helvetica-Bold", fontSize=13,
                      textAnchor="middle", fillColor=c["text"]))
        if d.get("fakultas"):
            dc.add(String(420, 330, f"Fakultas {d['fakultas']}",
                          fontName="Helvetica", fontSize=10,
                          textAnchor="middle", fillColor=c["muted"]))
        dc.add(String(420, 310, f"Gelar: {d.get('gelar', '')}",
                      fontName="Helvetica", fontSize=10,
                      textAnchor="middle", fillColor=c["text"]))

        # Skripsi
        dc.add(String(80, 275, "JUDUL TUGAS AKHIR / SKRIPSI:",
                      fontName="Helvetica-Bold", fontSize=8,
                      textAnchor="start", fillColor=c["muted"]))
        for i, line in enumerate(wrap_text_lines(d.get("judul_skripsi", ""), 100)[:3]):
            dc.add(String(80, 258 - i * 13, line,
                          fontName="Courier", fontSize=10, textAnchor="start"))

        dc.add(String(80, 200, "Dokumen ini dilindungi oleh tanda tangan kriptografi",
                      fontName="Helvetica-Oblique", fontSize=9,
                      textAnchor="start", fillColor=c["muted"]))
        dc.add(String(80, 187, "dan tercatat permanen di blockchain.",
                      fontName="Helvetica-Oblique", fontSize=9,
                      textAnchor="start", fillColor=c["muted"]))

        # Signature
        dc.add(String(580, 200, f"Yogyakarta, {d.get('tanggal', tanggal_indonesia())}",
                      fontName="Helvetica", fontSize=10, textAnchor="start"))
        dc.add(String(170, 170, f"Rektor {d.get('institusi', '')},",
                      fontName="Helvetica", fontSize=10, textAnchor="middle"))
        dc.add(String(650, 170, "Dekan Fakultas,",
                      fontName="Helvetica", fontSize=10, textAnchor="middle"))
        dc.add(Line(60, 115, 280, 115, strokeColor=c["muted"], strokeWidth=0.5))
        dc.add(Line(540, 115, 760, 115, strokeColor=c["muted"], strokeWidth=0.5))
        dc.add(String(170, 100, d.get("rektor", ""),
                      fontName="Helvetica-Bold", fontSize=11,
                      textAnchor="middle", fillColor=c["accent"]))
        dc.add(String(650, 100, d.get("dekan", ""),
                      fontName="Helvetica-Bold", fontSize=11,
                      textAnchor="middle", fillColor=c["accent"]))

        # Badge verified (kotak)
        dc.add(Rect(690, 55, 120, 36, fillColor=c["accent"],
                    strokeColor=c["accent"], strokeWidth=1))
        dc.add(String(750, 72, "BLOCKCHAIN", fontName="Helvetica-Bold",
                      fontSize=7, textAnchor="middle", fillColor="#ffffff"))
        dc.add(String(750, 62, "VERIFIED", fontName="Helvetica-Bold",
                      fontSize=7, textAnchor="middle", fillColor="#ffffff"))

        dc.add(RLImage(60, 55, 60, 60, qr_path))

        dc.add(Line(55, 45, 786, 45, strokeColor=c["border"], strokeWidth=0.5))
        gab = f"{d.get('custom_footnote', '')} | HASH: {d.get('hash', '')}"
        for i, line in enumerate(wrap_text_lines(gab, 150)[:2]):
            dc.add(String(55, 32 - i * 7, line, fontName="Courier",
                          fontSize=6, textAnchor="start", fillColor=c["muted"]))
        return dc

    def _build_canvas_minimalis(self, d, qr_path):
        c = TEMPLATE_COLORS[TEMPLATE_MINIMALIS]
        dc = Drawing(841, 595)

        dc.add(Rect(0, 0, 841, 595, fillColor=c["bg"], strokeColor=None))
        dc.add(Rect(50, 50, 741, 495, fillColor=None,
                    strokeColor=c["border"], strokeWidth=0.8))

        dc.add(String(70, 525, f"No. Seri: {d.get('nomor_seri', '')}",
                      fontName="Helvetica", fontSize=7,
                      textAnchor="start", fillColor=c["muted"]))

        dc.add(String(420, 500, d.get("institusi", ""),
                      fontName="Helvetica-Bold", fontSize=10,
                      textAnchor="middle", fillColor=c["accent"]))

        dc.add(String(420, 450, "Ijazah",
                      fontName="Helvetica", fontSize=28,
                      textAnchor="middle", fillColor=c["text"]))
        dc.add(Line(400, 435, 440, 435, strokeColor=c["accent"], strokeWidth=1.5))

        dc.add(String(420, 405, "Diberikan kepada",
                      fontName="Helvetica", fontSize=8,
                      textAnchor="middle", fillColor=c["muted"]))

        dc.add(String(420, 370, d.get("nama", ""),
                      fontName="Helvetica-Bold", fontSize=17,
                      textAnchor="middle", fillColor=c["text"]))
        dc.add(String(420, 350, d.get("nim", ""),
                      fontName="Helvetica", fontSize=10,
                      textAnchor="middle", fillColor=c["muted"]))

        dc.add(String(420, 315, d.get("jurusan", ""),
                      fontName="Helvetica", fontSize=11,
                      textAnchor="middle", fillColor=c["text"]))
        if d.get("fakultas"):
            dc.add(String(420, 297, d["fakultas"],
                          fontName="Helvetica", fontSize=9,
                          textAnchor="middle", fillColor=c["muted"]))
        dc.add(String(420, 277, f"Gelar {d.get('gelar', '')}",
                      fontName="Helvetica-Bold", fontSize=10,
                      textAnchor="middle", fillColor=c["text"]))

        # Skripsi
        dc.add(String(420, 240, "Tugas Akhir / Skripsi:",
                      fontName="Helvetica", fontSize=8,
                      textAnchor="middle", fillColor=c["muted"]))
        for i, line in enumerate(wrap_text_lines(d.get("judul_skripsi", ""), 80)[:2]):
            dc.add(String(420, 222 - i * 12, f'"{line}"' if i == 0 else line,
                          fontName="Courier-Oblique", fontSize=9,
                          textAnchor="middle", fillColor=c["text"]))

        # Signature
        dc.add(String(420, 165, f"Yogyakarta, {d.get('tanggal', tanggal_indonesia())}",
                      fontName="Helvetica", fontSize=9,
                      textAnchor="middle", fillColor=c["muted"]))

        dc.add(String(170, 130, "Rektor,", fontName="Helvetica",
                      fontSize=9, textAnchor="middle", fillColor=c["text"]))
        dc.add(String(650, 130, "Dekan,", fontName="Helvetica",
                      fontSize=9, textAnchor="middle", fillColor=c["text"]))

        dc.add(Line(90, 105, 250, 105, strokeColor=c["border"], strokeWidth=0.5))
        dc.add(Line(570, 105, 730, 105, strokeColor=c["border"], strokeWidth=0.5))

        dc.add(String(170, 92, d.get("rektor", ""),
                      fontName="Helvetica-Bold", fontSize=10,
                      textAnchor="middle", fillColor=c["accent"]))
        dc.add(String(650, 92, d.get("dekan", ""),
                      fontName="Helvetica-Bold", fontSize=10,
                      textAnchor="middle", fillColor=c["accent"]))

        # QR + footnote
        dc.add(RLImage(720, 70, 55, 55, qr_path))

        dc.add(Line(65, 65, 776, 65, strokeColor=c["border"], strokeWidth=0.5))
        gab = f"{d.get('custom_footnote', '')} | HASH: {d.get('hash', '')}"
        for i, line in enumerate(wrap_text_lines(gab, 140)[:2]):
            dc.add(String(65, 52 - i * 7, line, fontName="Courier",
                          fontSize=6, textAnchor="start", fillColor=c["muted"]))
        return dc