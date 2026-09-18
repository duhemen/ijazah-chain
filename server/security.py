"""
Security: API key, admin token, dan rate limiting.
Rate limiting bersifat OPSIONAL — jika slowapi tidak terinstall,
server tetap berjalan tanpa rate limit (mode development).
"""
import logging
from fastapi import Header, HTTPException, status

from server.config import API_KEYS, ADMIN_TOKEN

logger = logging.getLogger("ijazah_server")


# ============================================================
# RATE LIMITER (opsional)
# ============================================================
class _DummyLimiter:
    """
    Fallback limiter yang tidak melakukan apa-apa.
    Dipakai jika slowapi tidak tersedia.
    """

    def limit(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator


try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address)
    RATE_LIMIT_AVAILABLE = True
    logger.info("[SECURITY] slowapi aktif — rate limiting ON")

except ImportError:
    limiter = _DummyLimiter()
    RATE_LIMIT_AVAILABLE = False
    logger.warning(
        "[SECURITY] slowapi tidak terinstall — rate limiting DISABLED. "
        "Untuk production, install: pip install slowapi"
    )


# ============================================================
# AUTH DEPENDENCIES
# ============================================================
async def require_api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key tidak valid atau tidak terdaftar.",
        )
    return API_KEYS[x_api_key]


async def require_admin(x_admin_token: str = Header(...)) -> str:
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin token tidak valid.",
        )
    return "admin"