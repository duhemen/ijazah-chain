"""
Konfigurasi client Ijazah Chain.
Ubah MODE ke 'server' untuk terhubung ke server pusat.
"""

# ============================================================
# MODE APLIKASI
# ============================================================
# "server"  → terhubung ke server FastAPI (multi-user, terpusat)
# "local"   → pakai SQLite lokal (offline, single-user)
MODE = "server"


# ============================================================
# SERVER SETTINGS (hanya dipakai jika MODE == "server")
# ============================================================
SERVER_URL = "http://localhost:8000"

# API key universitas Anda.
# Daftar API key tersedia di server/config.py
API_KEY = "ugm_secret_key_2026"

# Timeout request (detik)
REQUEST_TIMEOUT = 15


# ============================================================
# TAMPILAN
# ============================================================
APP_NAME = "Ijazah Chain"
APP_VERSION = "1.0.0"

# Auto-refresh tab verify saat dibuka (detik)
AUTO_REFRESH_INTERVAL = 30