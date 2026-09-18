"""
ECDSA Digital Signature untuk blok ijazah.
BERSIFAT OPSIONAL — jika library `cryptography` tidak terinstall,
fungsi signature akan mengembalikan string kosong dan verifikasi
dianggap "tidak tersedia" (bukan gagal).
"""
import base64
import json
import logging
from typing import Optional

from server.config import ECDSA_PRIVATE_KEY_PATH, ECDSA_PUBLIC_KEY_PATH

logger = logging.getLogger("ijazah_server")


# ============================================================
# CEK KETERSEDIAAN LIBRARY
# ============================================================
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.exceptions import InvalidSignature

    CRYPTO_AVAILABLE = True
    logger.info("[CRYPTO] cryptography tersedia — ECDSA signature ON")

except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning(
        "[CRYPTO] cryptography TIDAK terinstall — signature ECDSA DISABLED. "
        "Untuk production, install: pip install cryptography "
        "(butuh Python 3.11/3.12 untuk wheel pre-built)"
    )


_private_key = None
_public_key = None


# ============================================================
# GENERATE & LOAD KEYS
# ============================================================
def generate_keys():
    """Generate ECDSA keypair jika belum ada. Skip jika crypto tidak ada."""
    if not CRYPTO_AVAILABLE:
        return
    if ECDSA_PRIVATE_KEY_PATH.exists() and ECDSA_PUBLIC_KEY_PATH.exists():
        return

    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    ECDSA_PRIVATE_KEY_PATH.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    ECDSA_PUBLIC_KEY_PATH.write_bytes(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    print(f"[CRYPTO] ECDSA keypair dibuat di {ECDSA_PRIVATE_KEY_PATH.parent}")


def _load_private():
    global _private_key
    if not CRYPTO_AVAILABLE:
        return None
    if _private_key is None:
        generate_keys()
        pem = ECDSA_PRIVATE_KEY_PATH.read_bytes()
        _private_key = serialization.load_pem_private_key(pem, password=None)
    return _private_key


def _load_public():
    global _public_key
    if not CRYPTO_AVAILABLE:
        return None
    if _public_key is None:
        generate_keys()
        pem = ECDSA_PUBLIC_KEY_PATH.read_bytes()
        _public_key = serialization.load_pem_public_key(pem)
    return _public_key


# ============================================================
# SIGN & VERIFY
# ============================================================
def _block_payload(block) -> bytes:
    return json.dumps({
        "index": block.index,
        "timestamp": block.timestamp,
        "data": block.data,
        "previous_hash": block.previous_hash,
        "hash": block.hash,
    }, sort_keys=True, ensure_ascii=False).encode("utf-8")


def sign_block(block) -> str:
    """
    Sign block dengan ECDSA. Return base64-encoded signature.
    Jika crypto tidak tersedia, return string kosong.
    """
    if not CRYPTO_AVAILABLE:
        return ""
    try:
        signature = _load_private().sign(_block_payload(block), ec.ECDSA(hashes.SHA256()))
        return base64.b64encode(signature).decode("ascii")
    except Exception as e:
        logger.warning(f"[CRYPTO] Gagal sign: {e}")
        return ""


def verify_signature(block, signature_b64: str) -> bool:
    """
    Verifikasi tanda tangan blok.
    - Jika signature kosong → return True (tidak ada signature = tidak diverifikasi,
      bukan berarti gagal; caller harus cek CRYPTO_AVAILABLE untuk konteks).
    - Jika crypto tidak tersedia → return True (skip, agar tidak false-positive).
    """
    if not signature_b64:
        return True  # Tidak ada signature = belum ditandatangani, anggap bukan error
    if not CRYPTO_AVAILABLE:
        return True  # Tidak bisa verifikasi tanpa library, jangan blokir

    try:
        signature = base64.b64decode(signature_b64)
    except Exception:
        return False

    try:
        _load_public().verify(signature, _block_payload(block), ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False
    except Exception as e:
        logger.warning(f"[CRYPTO] Error saat verifikasi: {e}")
        return False


def get_public_key_pem() -> str:
    """Return public key dalam format PEM (untuk di-share ke publik)."""
    if not CRYPTO_AVAILABLE:
        return (
            "-----BEGIN PUBLIC KEY-----\n"
            "ECDSA signature belum aktif. Install: pip install cryptography\n"
            "(butuh Python 3.11/3.12 untuk wheel pre-built)\n"
            "-----END PUBLIC KEY-----"
        )
    generate_keys()
    return ECDSA_PUBLIC_KEY_PATH.read_text(encoding="utf-8")


def is_crypto_available() -> bool:
    """Cek apakah fitur signature aktif."""
    return CRYPTO_AVAILABLE