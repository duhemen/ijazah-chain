import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "ijazah_server_ledger.db"
STATIC_DIR = BASE_DIR / "static"
KEYS_DIR = BASE_DIR / "keys"
BACKUP_DIR = BASE_DIR / "backups"
AUDIT_DB_PATH = BASE_DIR / "ijazah_audit_log.db"

# Pastikan folder ada
KEYS_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

# API Keys per universitas
API_KEYS = {
    "ugm_secret_key_2026": "UNIVERSITAS GADJAH MADA",
    "ui_secret_key_2026": "UNIVERSITAS INDONESIA",
    "itb_secret_key_2026": "INSTITUT TEKNOLOGI BANDUNG",
}

# Admin dashboard
ADMIN_USERNAME = os.getenv("IJAZAH_ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("IJAZAH_ADMIN_PASS", "admin123")
ADMIN_TOKEN = os.getenv("IJAZAH_ADMIN_TOKEN", "admin_master_token_2026")

# Server
HOST = os.getenv("IJAZAH_HOST", "0.0.0.0")
PORT = int(os.getenv("IJAZAH_PORT", "8000"))
ALLOWED_ORIGINS = ["*"]

# === Paket B: Rate Limiting ===
RATE_LIMIT_PUBLIC = "120/minute"      # Endpoint publik
RATE_LIMIT_ISSUE = "30/minute"        # Endpoint issue

# === Paket B: Backup ===
BACKUP_ENABLED = True
BACKUP_HOUR = 2                        # Jam 02:00 pagi
BACKUP_RETENTION_DAYS = 30

# === Paket B: ECDSA Signature ===
ECDSA_PRIVATE_KEY_PATH = KEYS_DIR / "server_private.pem"
ECDSA_PUBLIC_KEY_PATH = KEYS_DIR / "server_public.pem"


def infer_fakultas(jurusan: str) -> str:
    j = (jurusan or "").upper()
    rules = [
        (("TEKNIK", "INFORMATIKA", "KOMPUTER", "ELEKTRO", "MESIN", "SIPIL"),
         "FAKULTAS TEKNIK"),
        (("EKONOMI", "MANAJEMEN", "AKUNTANSI", "BISNIS"),
         "FAKULTAS EKONOMI & BISNIS"),
        (("KEDOKTERAN", "KEPERAWATAN", "FARMASI", "KEDOKTERAN GIGI"),
         "FAKULTAS KEDOKTERAN"),
        (("HUKUM",), "FAKULTAS HUKUM"),
        (("SASTRA", "BAHASA", "BUDAYA"), "FAKULTAS ILMU BUDAYA"),
        (("PSIKOLOGI",), "FAKULTAS PSIKOLOGI"),
        (("PENDIDIKAN", "KEGURUAN"), "FAKULTAS KEGURUAN"),
        (("SOSIAL", "POLITIK", "KOMUNIKASI", "HUBUNGAN INTERNASIONAL"),
         "FAKULTAS ILMU SOSIAL & POLITIK"),
        (("PERTANIAN", "PETERNAKAN", "PERIKANAN", "KEHUTANAN"),
         "FAKULTAS PERTANIAN"),
        (("MATEMATIKA", "FISIKA", "KIMIA", "BIOLOGI", "MIPA", "STATISTIKA"),
         "FAKULTAS MIPA"),
        (("KODING", "GABUT", "PROGRAMMER"), "FAKULTAS TEKNIK"),
    ]
    for keywords, fak in rules:
        if any(k in j for k in keywords):
            return fak
    return "BELUM DIKATEGORIKAN"