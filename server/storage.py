import json
import shutil
import sqlite3
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from server.config import (
    DB_PATH, AUDIT_DB_PATH, BACKUP_DIR, BACKUP_RETENTION_DAYS, infer_fakultas,
)
from server.core import Block, Blockchain


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def _audit_conn():
    c = sqlite3.connect(AUDIT_DB_PATH)
    c.row_factory = sqlite3.Row
    return c


# ============================================================
# INIT
# ============================================================
def init_db():
    conn = _conn()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS blockchain_ledger (
                block_index INTEGER PRIMARY KEY,
                timestamp REAL NOT NULL,
                data_json TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                block_hash TEXT NOT NULL UNIQUE,
                signature TEXT DEFAULT ''
            )
        """)
        # Migrasi: tambah kolom signature kalau belum ada (DB lama)
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(blockchain_ledger)").fetchall()]
        if "signature" not in cols:
            conn.execute("ALTER TABLE blockchain_ledger ADD COLUMN signature TEXT DEFAULT ''")

        conn.execute("CREATE INDEX IF NOT EXISTS idx_block_hash ON blockchain_ledger(block_hash)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON blockchain_ledger(timestamp)")
        conn.commit()
    finally:
        conn.close()

    # Init audit log DB
    aconn = _audit_conn()
    try:
        aconn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                ip_address TEXT,
                action TEXT NOT NULL,
                resource TEXT,
                status TEXT,
                detail TEXT
            )
        """)
        aconn.execute("CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_log(timestamp)")
        aconn.execute("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action)")
        aconn.commit()
    finally:
        aconn.close()


# ============================================================
# BLOCKCHAIN CRUD
# ============================================================
def save_block(block: Block, signature: str = ""):
    conn = _conn()
    try:
        conn.execute("""
            INSERT OR REPLACE INTO blockchain_ledger
            (block_index, timestamp, data_json, previous_hash, block_hash, signature)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            block.index,
            block.timestamp,
            json.dumps(block.data, ensure_ascii=False, sort_keys=True),
            block.previous_hash,
            block.hash,
            signature,
        ))
        conn.commit()
    finally:
        conn.close()


def load_all_blocks() -> List[Block]:
    conn = _conn()
    try:
        rows = conn.execute(
            "SELECT * FROM blockchain_ledger ORDER BY block_index ASC"
        ).fetchall()
    finally:
        conn.close()

    blocks = []
    for r in rows:
        b = Block(
            r["block_index"],
            r["timestamp"],
            json.loads(r["data_json"]),
            r["previous_hash"],
        )
        b.hash = r["block_hash"]
        # Simpan signature sebagai attribute dinamis
        b.signature = r["signature"] if "signature" in r.keys() else ""
        blocks.append(b)
    return blocks


def load_blockchain() -> Blockchain:
    init_db()
    bc = Blockchain()
    blocks = load_all_blocks()
    if blocks:
        bc.chain = blocks
    else:
        save_block(bc.chain[0])
    return bc


def reload_blockchain(bc: Blockchain) -> Blockchain:
    blocks = load_all_blocks()
    if blocks:
        bc.chain = blocks
    return bc


# ============================================================
# AUDIT LOG (Paket B)
# ============================================================
def log_action(
    action: str,
    resource: str = "",
    status: str = "ok",
    detail: str = "",
    ip: Optional[str] = None,
):
    conn = _audit_conn()
    try:
        conn.execute("""
            INSERT INTO audit_log (timestamp, ip_address, action, resource, status, detail)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (datetime.now().timestamp(), ip, action, resource, status, detail[:500]))
        conn.commit()
    except Exception as e:
        print(f"[AUDIT] Gagal log: {e}")
    finally:
        conn.close()


def get_audit_log(limit: int = 200, offset: int = 0) -> List[Dict[str, Any]]:
    conn = _audit_conn()
    try:
        rows = conn.execute("""
            SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ? OFFSET ?
        """, (limit, offset)).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


# ============================================================
# BACKUP (Paket B)
# ============================================================
def create_backup() -> Path:
    """Buat backup DB + audit log. Return path file backup."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"backup_{ts}.db"
    # SQLite backup API (aman untuk DB sedang aktif)
    src = sqlite3.connect(DB_PATH)
    dst = sqlite3.connect(backup_file)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    print(f"[BACKUP] Tersimpan: {backup_file.name}")
    return backup_file


def cleanup_old_backups():
    """Hapus backup lebih tua dari BACKUP_RETENTION_DAYS."""
    cutoff = datetime.now() - timedelta(days=BACKUP_RETENTION_DAYS)
    removed = 0
    for f in BACKUP_DIR.glob("backup_*.db"):
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime < cutoff:
                f.unlink()
                removed += 1
        except Exception:
            pass
    if removed:
        print(f"[BACKUP] {removed} backup lama dihapus.")


def list_backups() -> List[Dict[str, Any]]:
    result = []
    for f in sorted(BACKUP_DIR.glob("backup_*.db"), reverse=True):
        stat = f.stat()
        result.append({
            "name": f.name,
            "size_bytes": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })
    return result


# ============================================================
# QUERIES UNTUK DASHBOARD
# ============================================================
def _extract_year(data: Dict[str, Any], timestamp: float) -> str:
    if data.get("tahun_lulus"):
        try:
            return str(int(data["tahun_lulus"]))
        except (ValueError, TypeError):
            pass
    tanggal = str(data.get("tanggal", "")).strip()
    if tanggal:
        parts = tanggal.split()
        if parts:
            try:
                year = int(parts[-1])
                if 1900 <= year <= 2200:
                    return str(year)
            except ValueError:
                pass
    return str(datetime.fromtimestamp(timestamp).year)


def get_certificates_list() -> List[Dict[str, Any]]:
    conn = _conn()
    try:
        rows = conn.execute(
            "SELECT block_index, timestamp, data_json, block_hash, previous_hash, signature "
            "FROM blockchain_ledger WHERE block_index > 0 ORDER BY block_index ASC"
        ).fetchall()
    finally:
        conn.close()

    result = []
    for r in rows:
        try:
            data = json.loads(r["data_json"])
        except json.JSONDecodeError:
            data = {}
        if not isinstance(data, dict):
            data = {"_raw": data}

        result.append({
            "block_index": r["block_index"],
            "timestamp": r["timestamp"],
            "hash": r["block_hash"],
            "previous_hash": r["previous_hash"],
            "signature": r["signature"] if "signature" in r.keys() else "",
            "data": data,
            "tahun": _extract_year(data, r["timestamp"]),
            "fakultas": (data.get("fakultas") or infer_fakultas(data.get("jurusan", ""))).upper(),
            "prodi": (data.get("jurusan") or "TIDAK DIKETAHUI").upper(),
            "nama": (data.get("nama") or "TIDAK DIKETAHUI").upper(),
            "nim": data.get("nim", ""),
            "institusi": (data.get("institusi") or "").upper(),
            "gelar": data.get("gelar", ""),
        })
    return result


def get_stats() -> Dict[str, Any]:
    certs = get_certificates_list()
    by_year = Counter()
    by_faculty = Counter()
    by_prodi = Counter()
    by_institusi = Counter()

    for c in certs:
        by_year[c["tahun"]] += 1
        by_faculty[c["fakultas"]] += 1
        by_prodi[c["prodi"]] += 1
        by_institusi[c["institusi"]] += 1

    return {
        "total_certificates": len(certs),
        "by_year": dict(sorted(by_year.items())),
        "by_faculty": dict(by_faculty.most_common()),
        "by_prodi": dict(by_prodi.most_common()),
        "by_institusi": dict(by_institusi.most_common()),
    }


def find_certificate_by_hash(block_hash: str):
    """
    Cari blok berdasarkan hash. Skip genesis (index 0) karena bukan ijazah.
    """
    conn = _conn()
    try:
        row = conn.execute(
            "SELECT block_index, timestamp, data_json, block_hash, previous_hash, signature "
            "FROM blockchain_ledger "
            "WHERE block_hash = ? AND block_index > 0",
            (block_hash,),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        return None
    try:
        data = json.loads(row["data_json"])
    except json.JSONDecodeError:
        data = {}
    return {
        "block_index": row["block_index"],
        "timestamp": row["timestamp"],
        "data": data,
        "hash": row["block_hash"],
        "previous_hash": row["previous_hash"],
        "signature": row["signature"] if "signature" in row.keys() else "",
    }

def find_certificates_by_nim(nim: str) -> List[Dict[str, Any]]:
    """Cari semua ijazah berdasarkan NIM (bisa banyak jika NIM unik per prodi)."""
    conn = _conn()
    try:
        rows = conn.execute(
            "SELECT block_index, timestamp, data_json, block_hash, previous_hash, signature "
            "FROM blockchain_ledger WHERE block_index > 0 ORDER BY block_index ASC"
        ).fetchall()
    finally:
        conn.close()

    result = []
    nim_norm = (nim or "").strip().lower()
    for r in rows:
        try:
            data = json.loads(r["data_json"])
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        if (data.get("nim") or "").strip().lower() == nim_norm:
            result.append({
                "block_index": r["block_index"],
                "timestamp": r["timestamp"],
                "data": data,
                "hash": r["block_hash"],
                "previous_hash": r["previous_hash"],
                "signature": r["signature"] if "signature" in r.keys() else "",
            })
    return result