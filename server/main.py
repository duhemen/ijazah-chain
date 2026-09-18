import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

try:
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    _SLOWAPI_AVAILABLE = True
except ImportError:
    _SLOWAPI_AVAILABLE = False

from server.config import (
    HOST, PORT, STATIC_DIR, ALLOWED_ORIGINS,
    ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_TOKEN,
    RATE_LIMIT_PUBLIC, RATE_LIMIT_ISSUE,
    BACKUP_ENABLED, BACKUP_HOUR,
)
from server.core import Blockchain, Block
from server.crypto import sign_block, verify_signature, get_public_key_pem
from server.models import (
    IssueRequest, IssueResponse, BlockResponse,
    AuditResponse, VerifyResponse, VerifyByNimResponse,
    AdminLoginRequest, AdminLoginResponse,
    StatsOverviewResponse, DashboardResponse, CertificateRow,
    PublicStatsResponse, BackupInfo, AuditLogEntry,
)
from server.security import limiter, require_api_key, require_admin
from server.storage import (
    load_blockchain, save_block, reload_blockchain,
    get_stats, get_certificates_list, find_certificate_by_hash,
    find_certificates_by_nim, log_action, get_audit_log,
    create_backup, cleanup_old_backups, list_backups, init_db,
)

logger = logging.getLogger("ijazah_server")


# ============================================================
# HELPER: Tanggal format Indonesia
# ============================================================
BULAN_ID = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]


def _tanggal_ijazah(dt: datetime.datetime = None) -> str:
    """Return tanggal dalam format Indonesia: '19 September 2026'."""
    dt = dt or datetime.datetime.now()
    return f"{dt.day} {BULAN_ID[dt.month - 1]} {dt.year}"


# ============================================================
# SCHEDULER (auto backup)
# ============================================================
_scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler
    init_db()
    logger.info("Server startup - DB siap")

    if BACKUP_ENABLED:
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from apscheduler.triggers.cron import CronTrigger
            _scheduler = AsyncIOScheduler()
            _scheduler.add_job(create_backup, CronTrigger(hour=BACKUP_HOUR, minute=0))
            _scheduler.add_job(cleanup_old_backups, CronTrigger(hour=BACKUP_HOUR, minute=30))
            _scheduler.start()
            logger.info(f"Auto-backup aktif: setiap hari jam {BACKUP_HOUR:02d}:00")
        except Exception as e:
            logger.warning(f"Gagal start scheduler backup: {e}")

    yield

    if _scheduler:
        _scheduler.shutdown()


# ============================================================
# APP
# ============================================================
blockchain: Blockchain = load_blockchain()

app = FastAPI(
    title="Ijazah Chain API",
    description="Sistem verifikasi ijazah berbasis blockchain + ECDSA signature",
    version="2.0.1",
    lifespan=lifespan,
)

app.state.limiter = limiter
if _SLOWAPI_AVAILABLE:
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _block_to_response(b) -> BlockResponse:
    return BlockResponse(
        index=b.index,
        timestamp=b.timestamp,
        data=b.data,
        previous_hash=b.previous_hash,
        hash=b.hash,
        signature=getattr(b, "signature", "") or "",
    )


def _get_client_ip(request: Request) -> str:
    if request.client:
        return request.client.host
    return "unknown"


# ============================================================
# HEALTH
# ============================================================
@app.get("/api/v1/health")
def health():
    reload_blockchain(blockchain)
    from server.crypto import is_crypto_available
    from server.security import RATE_LIMIT_AVAILABLE
    return {
        "status": "ok",
        "server_time": datetime.datetime.now().isoformat(),
        "total_blocks": len(blockchain.chain),
        "version": "2.0.1",
        "features": {
            "ecdsa_signature": is_crypto_available(),
            "rate_limiting": RATE_LIMIT_AVAILABLE,
            "backup": BACKUP_ENABLED,
        },
    }


@app.get("/health", include_in_schema=False)
def health_alias():
    return health()


# ============================================================
# PUBLIC: STATS
# ============================================================
@app.get("/api/v1/public/stats", response_model=PublicStatsResponse)
@limiter.limit(RATE_LIMIT_PUBLIC)
def public_stats(request: Request):
    reload_blockchain(blockchain)
    stats = get_stats()
    years = list(stats["by_year"].keys())
    return PublicStatsResponse(
        total_certificates=stats["total_certificates"],
        total_institusi=len(stats["by_institusi"]),
        total_fakultas=len(stats["by_faculty"]),
        total_prodi=len(stats["by_prodi"]),
        tahun_terakhir=years[-1] if years else "-",
        is_valid=blockchain.is_chain_valid(),
    )


# ============================================================
# PUBLIC: PUBLIC KEY
# ============================================================
@app.get("/api/v1/public-key")
def public_key():
    return {
        "algorithm": "ECDSA P-256 (secp256r1)",
        "hash": "SHA-256",
        "public_key_pem": get_public_key_pem(),
        "message": "Gunakan public key ini untuk verifikasi tanda tangan blok secara independen.",
    }


# ============================================================
# PUBLIC: ISSUE (butuh API key)
# ============================================================
@app.post(
    "/api/v1/certificates",
    response_model=IssueResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(RATE_LIMIT_ISSUE)
def issue_certificate(
    request: Request,
    req: IssueRequest,
    institusi_pengaju: str = Depends(require_api_key),
):
    if req.institusi.upper() != institusi_pengaju.upper():
        log_action("issue", f"{req.nim}", "fail",
                   f"API key untuk '{institusi_pengaju}' tidak boleh issue '{req.institusi}'",
                   _get_client_ip(request))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"API key Anda terdaftar untuk '{institusi_pengaju}', "
                f"tidak boleh menerbitkan atas nama '{req.institusi}'."
            ),
        )

    reload_blockchain(blockchain)
    tanggal = _tanggal_ijazah()  # ← FIX: Indonesian month

    data_ijazah = {
        "nama": req.nama.upper(),
        "nim": req.nim,
        "jurusan": req.jurusan.upper(),
        "gelar": req.gelar,
        "nomor_seri": req.nomor_seri,
        "judul_skripsi": req.judul_skripsi.upper(),
        "institusi": req.institusi.upper(),
        "rektor": req.rektor,
        "dekan": req.dekan,
        "custom_footnote": req.custom_footnote,
        "tanggal": tanggal,
        "issued_by": institusi_pengaju,
        "issued_at": datetime.datetime.now().isoformat(),
    }
    if req.fakultas:
        data_ijazah["fakultas"] = req.fakultas.upper()
    if req.tahun_lulus:
        data_ijazah["tahun_lulus"] = int(req.tahun_lulus)

    new_block = blockchain.add_block(data_ijazah)
    signature = sign_block(new_block)
    new_block.signature = signature
    save_block(new_block, signature=signature)

    logger.info(f"[ISSUE] Blok #{new_block.index} oleh {institusi_pengaju} a.n. {req.nama}")
    log_action("issue", f"block#{new_block.index}", "ok",
               f"{req.nama} ({req.nim}) oleh {institusi_pengaju}",
               _get_client_ip(request))

    return IssueResponse(
        success=True,
        block=_block_to_response(new_block),
        message=f"Ijazah a.n. {req.nama} berhasil diterbitkan di blok #{new_block.index}.",
    )


# ============================================================
# PUBLIC: LIST
# ============================================================
@app.get("/api/v1/certificates", response_model=list[BlockResponse])
@limiter.limit(RATE_LIMIT_PUBLIC)
def list_certificates(request: Request):
    reload_blockchain(blockchain)
    return [_block_to_response(b) for b in blockchain.chain]


@app.get("/api/v1/certificates/{index}", response_model=BlockResponse)
@limiter.limit(RATE_LIMIT_PUBLIC)
def get_certificate(request: Request, index: int):
    reload_blockchain(blockchain)
    if index < 0 or index >= len(blockchain.chain):
        raise HTTPException(404, "Blok tidak ditemukan.")
    return _block_to_response(blockchain.chain[index])


# ============================================================
# PUBLIC: VERIFY BY HASH
# ============================================================
@app.get("/api/v1/verify/{block_hash}", response_model=VerifyResponse)
@limiter.limit(RATE_LIMIT_PUBLIC)
def verify_by_hash(request: Request, block_hash: str):
    cert = find_certificate_by_hash(block_hash)
    if not cert:
        return VerifyResponse(
            found=False, message="Hash tidak ditemukan di ledger.",
            signature_valid=False,
        )

    # Recalculate hash dari data
    temp = Block(
        cert["block_index"],
        cert["timestamp"],
        cert["data"],
        cert["previous_hash"],
    )
    hash_valid = (temp.calculate_hash() == block_hash)

    # Verify signature (jika ada)
    has_sig = bool(cert.get("signature"))
    sig_valid = False
    if has_sig:
        temp.signature = cert["signature"]
        sig_valid = verify_signature(temp, cert["signature"])

    # Message yang informatif
    if not hash_valid:
        msg = "Hash TIDAK VALID (data dimanipulasi)"
    elif not has_sig:
        msg = "Hash VALID (block belum memiliki signature)"
    elif sig_valid:
        msg = "Hash VALID & SIGNATURE terverifikasi ✓"
    else:
        msg = "Hash valid tapi SIGNATURE tidak cocok"

    return VerifyResponse(
        found=True,
        block=BlockResponse(
            index=cert["block_index"],
            timestamp=cert["timestamp"],
            data=cert["data"],
            previous_hash=cert["previous_hash"],
            hash=cert["hash"],
            signature=cert.get("signature", ""),
        ),
        message=msg,
        signature_valid=sig_valid,
        data=cert["data"],
    )


# ============================================================
# PUBLIC: VERIFY BY NIM
# ============================================================
@app.get("/api/v1/verify-nim/{nim:path}", response_model=VerifyByNimResponse)
@limiter.limit(RATE_LIMIT_PUBLIC)
def verify_by_nim(request: Request, nim: str):
    """
    FIX: gunakan {nim:path} agar NIM dengan slash (21/123456/TK/78901) bisa di-route.
    """
    certs = find_certificates_by_nim(nim)
    if not certs:
        return VerifyByNimResponse(
            found=False, count=0, certificates=[],
            message=f"Tidak ada ijazah dengan NIM '{nim}'.",
        )

    blocks = [
        BlockResponse(
            index=c["block_index"],
            timestamp=c["timestamp"],
            data=c["data"],
            previous_hash=c["previous_hash"],
            hash=c["hash"],
            signature=c.get("signature", ""),
        )
        for c in certs
    ]

    return VerifyByNimResponse(
        found=True, count=len(blocks), certificates=blocks,
        message=f"Ditemukan {len(blocks)} ijazah untuk NIM '{nim}'.",
    )


# ============================================================
# PUBLIC: AUDIT
# ============================================================
@app.get("/api/v1/audit", response_model=AuditResponse)
@limiter.limit(RATE_LIMIT_PUBLIC)
def audit_chain(request: Request):
    reload_blockchain(blockchain)
    is_valid = blockchain.is_chain_valid()

    sig_all_valid = True
    for b in blockchain.chain:
        sig = getattr(b, "signature", "")
        if sig and not verify_signature(b, sig):
            sig_all_valid = False
            break

    total = len(blockchain.chain)
    cert_count = max(0, total - 1)

    log_action("audit", "chain", "ok" if is_valid else "fail",
               f"total={total}", _get_client_ip(request))

    return AuditResponse(
        is_valid=is_valid and sig_all_valid,
        total_blocks=total,
        certificate_count=cert_count,
        message=(
            "Sistem AMAN, hash & signature valid."
            if is_valid and sig_all_valid
            else "PERINGATAN: Terdeteksi manipulasi atau signature tidak valid!"
        ),
        signature_valid=sig_all_valid,
    )


# ============================================================
# ADMIN: LOGIN
# ============================================================
@app.post("/api/v1/admin/login", response_model=AdminLoginResponse)
def admin_login(request: Request, creds: AdminLoginRequest):
    if creds.username != ADMIN_USERNAME or creds.password != ADMIN_PASSWORD:
        log_action("login", "admin", "fail", f"user={creds.username}",
                   _get_client_ip(request))
        raise HTTPException(401, "Username atau password salah.")
    log_action("login", "admin", "ok", f"user={creds.username}",
               _get_client_ip(request))
    return AdminLoginResponse(
        token=ADMIN_TOKEN, username=creds.username,
        message="Login berhasil.",
    )


# ============================================================
# ADMIN: DASHBOARD
# ============================================================
@app.get("/api/v1/admin/stats", response_model=StatsOverviewResponse)
def admin_stats(request: Request, _: str = Depends(require_admin)):
    reload_blockchain(blockchain)
    stats = get_stats()
    return StatsOverviewResponse(
        total_certificates=stats["total_certificates"],
        total_blocks=len(blockchain.chain),
        is_valid=blockchain.is_chain_valid(),
        by_year=stats["by_year"],
        by_faculty=stats["by_faculty"],
        by_prodi=stats["by_prodi"],
        by_institusi=stats["by_institusi"],
    )


@app.get("/api/v1/admin/dashboard", response_model=DashboardResponse)
def admin_dashboard(request: Request, _: str = Depends(require_admin)):
    reload_blockchain(blockchain)
    stats = get_stats()
    certs = get_certificates_list()
    return DashboardResponse(
        stats=StatsOverviewResponse(
            total_certificates=stats["total_certificates"],
            total_blocks=len(blockchain.chain),
            is_valid=blockchain.is_chain_valid(),
            by_year=stats["by_year"],
            by_faculty=stats["by_faculty"],
            by_prodi=stats["by_prodi"],
            by_institusi=stats["by_institusi"],
        ),
        certificates=[CertificateRow(**c) for c in certs],
    )


# ============================================================
# ADMIN: BACKUP
# ============================================================
@app.post("/api/v1/admin/backup", response_model=BackupInfo)
def manual_backup(request: Request, _: str = Depends(require_admin)):
    f = create_backup()
    stat = f.stat()
    log_action("backup", f.name, "ok", "", _get_client_ip(request))
    return BackupInfo(
        name=f.name, size_bytes=stat.st_size,
        created_at=datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
    )


@app.get("/api/v1/admin/backups", response_model=list[BackupInfo])
def get_backups(request: Request, _: str = Depends(require_admin)):
    return [BackupInfo(**b) for b in list_backups()]


# ============================================================
# ADMIN: AUDIT LOG
# ============================================================
@app.get("/api/v1/admin/audit-log", response_model=list[AuditLogEntry])
def admin_audit_log(
    request: Request,
    limit: int = 200,
    offset: int = 0,
    _: str = Depends(require_admin),
):
    rows = get_audit_log(limit=limit, offset=offset)
    return [AuditLogEntry(**r) for r in rows]


# ============================================================
# STATIC
# ============================================================
STATIC_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/dashboard")
def dashboard_page():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/verify")
def verify_page():
    verify_path = STATIC_DIR / "verify.html"
    if not verify_path.exists():
        return Response(
            content="<h1>verify.html belum ada</h1>",
            media_type="text/html",
        )
    return FileResponse(verify_path)


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="0.9em" font-size="90">🔐</text></svg>'
    return Response(content=svg, media_type="image/svg+xml")


if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Server Ijazah Chain v2.0.1: http://localhost:{PORT}")
    print(f"📊 Dashboard Admin : http://localhost:{PORT}/dashboard")
    print(f"🔍 Verifikasi Publik: http://localhost:{PORT}/verify")
    print(f"📖 API Docs        : http://localhost:{PORT}/docs")
    uvicorn.run(app, host=HOST, port=PORT)