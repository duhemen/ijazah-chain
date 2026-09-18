"""Data statis: mapping fakultas ke program studi."""

import datetime


FAKULTAS_PRODI = {
    "FAKULTAS TEKNIK": [
        "TEKNIK INFORMATIKA",
        "TEKNIK ELEKTRO",
        "TEKNIK MESIN",
        "TEKNIK SIPIL",
        "TEKNIK KIMIA",
        "TEKNIK INDUSTRI",
        "TEKNIK GEOLOGI",
        "ARSITEKTUR",
        "TEKNOLOGI INFORMASI",
        "SISTEM INFORMASI",
        "TEKNIK KOMPUTER",
    ],
    "FAKULTAS EKONOMI & BISNIS": [
        "MANAJEMEN",
        "AKUNTANSI",
        "ILMU EKONOMI",
        "EKONOMI PEMBANGUNAN",
        "BISNIS DIGITAL",
        "KEUANGAN",
    ],
    "FAKULTAS KEDOKTERAN": [
        "PENDIDIKAN DOKTER",
        "KEPERAWATAN",
        "FARMASI",
        "KEDOKTERAN GIGI",
        "GIZI",
        "KESEHATAN MASYARAKAT",
    ],
    "FAKULTAS HUKUM": [
        "ILMU HUKUM",
    ],
    "FAKULTAS ILMU BUDAYA": [
        "SASTRA INDONESIA",
        "SASTRA INGGRIS",
        "SASTRA JEPANG",
        "SASTRA ARAB",
        "ILMU SEJARAH",
        "ANTROPOLOGI",
        "ARKEOLOGI",
    ],
    "FAKULTAS PSIKOLOGI": [
        "PSIKOLOGI",
    ],
    "FAKULTAS KEGURUAN & ILMU PENDIDIKAN": [
        "PENDIDIKAN MATEMATIKA",
        "PENDIDIKAN BAHASA INDONESIA",
        "PENDIDIKAN BAHASA INGGRIS",
        "PENDIDIKAN GURU SEKOLAH DASAR",
        "PENDIDIKAN ANAK USIA DINI",
        "BIMBINGAN & KONSELING",
    ],
    "FAKULTAS ILMU SOSIAL & POLITIK": [
        "ILMU KOMUNIKASI",
        "HUBUNGAN INTERNASIONAL",
        "ILMU POLITIK",
        "SOSIOLOGI",
        "PEMBANGUNAN SOSIAL",
        "ADMINISTRASI PUBLIK",
    ],
    "FAKULTAS PERTANIAN": [
        "AGRONOMI",
        "PETERNAKAN",
        "PERIKANAN",
        "KEHUTANAN",
        "TEKNOLOGI PANGAN",
        "PROTEKSI TANAMAN",
    ],
    "FAKULTAS MATEMATIKA & IPA": [
        "MATEMATIKA",
        "FISIKA",
        "KIMIA",
        "BIOLOGI",
        "STATISTIKA",
        "ILMU KOMPUTER",
    ],
    "FAKULTAS SENI & DESAIN": [
        "DESAIN KOMUNIKASI VISUAL",
        "DESAIN PRODUK",
        "SENI RUPA",
        "DESAIN INTERIOR",
    ],
    "FAKULTAS KEDOKTERAN HEWAN": [
        "KEDOKTERAN HEWAN",
    ],
    "FAKULTAS FILSAFAT": [
        "FILSAFAT",
    ],
    "FAKULTAS GEOGRAFI": [
        "GEOGRAFI",
        "KARTOGRAFI",
    ],
}


def daftar_fakultas():
    """Return list nama fakultas terurut."""
    return sorted(FAKULTAS_PRODI.keys())


def daftar_prodi(fakultas: str):
    """Return list prodi berdasarkan fakultas. Kosong jika tidak ada."""
    return FAKULTAS_PRODI.get(fakultas.upper().strip(), [])


def daftar_tahun(n_back=30, n_forward=1):
    """Return list tahun (default: 30 tahun ke belakang, 1 tahun ke depan)."""
    now = datetime.datetime.now().year
    return [str(y) for y in range(now + n_forward, now - n_back - 1, -1)]


def normalisasi_fakultas(text: str) -> str:
    """Normalisasi input fakultas manual ke format konsisten."""
    return (text or "").strip().upper()


def normalisasi_prodi(text: str) -> str:
    return (text or "").strip().upper()


# Preset warna tema (untuk konsistensi UI)
COLOR_CYAN = "#00f0ff"
COLOR_GREEN = "#2ecc71"
COLOR_AMBER = "#f39c12"
COLOR_RED = "#ff3860"
COLOR_MUTED = "#7c7c8a"