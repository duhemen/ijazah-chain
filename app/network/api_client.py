"""
HTTP client untuk berkomunikasi dengan server Ijazah Chain.
Menggantikan peran Blockchain lokal saat MODE == 'server'.
"""

import datetime as _dt
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx

from app.config import SERVER_URL, API_KEY, REQUEST_TIMEOUT


class ApiError(Exception):
    """Exception untuk error komunikasi dengan server."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class RemoteBlock:
    """
    Representasi blok yang diterima dari server.
    Menyerupai interface `Block` di client lokal (calculate_hash, to_dict, dll)
    agar kode lama tetap kompatibel.
    """

    def __init__(self, payload: dict):
        self.index: int = payload["index"]
        self.timestamp: float = payload["timestamp"]
        self.data: Any = payload["data"]
        self.previous_hash: str = payload["previous_hash"]
        self.hash: str = payload["hash"]
        self.signature: str = payload.get("signature", "")

    def calculate_hash(self) -> str:
        """Stub — hash resmi sudah dihitung oleh server."""
        return self.hash

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "signature": self.signature,
        }


class RemoteBlockchain:
    """
    Adapter menyerupai interface Blockchain lokal.
    Semua operasi dikirim ke server lewat HTTP.
    """

    def __init__(self, server_url: str = SERVER_URL, api_key: str = API_KEY):
        self.server_url = (server_url or "").rstrip("/")
        self.api_key = api_key
        self.chain: List[RemoteBlock] = []
        self._headers = {"X-API-Key": self.api_key}
        self._client = httpx.Client(timeout=REQUEST_TIMEOUT)

    # ============================================================
    # HTTP HELPERS
    # ============================================================
    def _handle_response(self, r: httpx.Response) -> Any:
        if r.status_code == 401:
            raise ApiError(
                "Akses ditolak (401). Periksa API key atau kredensial Anda.",
                status_code=401,
            )
        if r.status_code == 403:
            try:
                detail = r.json().get("detail", "Akses ditolak.")
            except Exception:
                detail = "Akses ditolak."
            raise ApiError(detail, status_code=403)
        if r.status_code == 404:
            raise ApiError("Data tidak ditemukan di server.", status_code=404)
        if r.status_code == 429:
            raise ApiError(
                "Terlalu banyak permintaan (rate limit). Coba lagi nanti.",
                status_code=429,
            )
        if r.status_code >= 400:
            try:
                detail = r.json().get("detail", r.text)
            except Exception:
                detail = r.text
            raise ApiError(
                f"Server error {r.status_code}: {detail}",
                status_code=r.status_code,
            )
        try:
            return r.json()
        except Exception as e:
            raise ApiError(f"Respons server tidak valid: {e}")

    def _get(self, path: str) -> Any:
        try:
            r = self._client.get(f"{self.server_url}{path}", headers=self._headers)
        except httpx.RequestError as e:
            raise ApiError(f"Tidak dapat terhubung ke server: {e}")
        return self._handle_response(r)

    def _post(self, path: str, json_body: Dict[str, Any]) -> Any:
        try:
            r = self._client.post(
                f"{self.server_url}{path}",
                json=json_body,
                headers=self._headers,
            )
        except httpx.RequestError as e:
            raise ApiError(f"Tidak dapat terhubung ke server: {e}")
        return self._handle_response(r)

    # ============================================================
    # HEALTH
    # ============================================================
    def health(self) -> Dict[str, Any]:
        return self._get("/api/v1/health")

    # ============================================================
    # ISSUE CERTIFICATE
    # ============================================================
    def add_block(self, data: Dict[str, Any]) -> RemoteBlock:
        """Kirim request issue ke server, return objek mirip Block lokal."""
        payload: Dict[str, Any] = {
            "nama": data["nama"],
            "nim": data["nim"],
            "jurusan": data["jurusan"],
            "gelar": data["gelar"],
            "nomor_seri": data["nomor_seri"],
            "judul_skripsi": data.get("judul_skripsi", ""),
            "institusi": data["institusi"],
            "rektor": data.get("rektor", ""),
            "dekan": data.get("dekan", ""),
            "custom_footnote": data.get("custom_footnote", ""),
        }
        if data.get("fakultas"):
            payload["fakultas"] = data["fakultas"]
        if data.get("tahun_lulus"):
            try:
                payload["tahun_lulus"] = int(data["tahun_lulus"])
            except (ValueError, TypeError):
                pass

        result = self._post("/api/v1/certificates", payload)
        block = RemoteBlock(result["block"])
        self.chain.append(block)
        return block

    # ============================================================
    # AUDIT
    # ============================================================
    def is_chain_valid(self) -> bool:
        """Cek integritas seluruh chain via server."""
        try:
            data = self._get("/api/v1/audit")
            return bool(data.get("is_valid", False))
        except ApiError:
            return False

    def audit(self) -> Dict[str, Any]:
        """Return full audit response."""
        return self._get("/api/v1/audit")

    # ============================================================
    # FETCH CHAIN
    # ============================================================
    def refresh_chain(self) -> List[RemoteBlock]:
        """Muat ulang daftar blok dari server."""
        blocks_data = self._get("/api/v1/certificates")
        self.chain = [RemoteBlock(b) for b in blocks_data]
        return self.chain

    # ============================================================
    # VERIFY (single block)
    # ============================================================
    def verify_by_hash(self, block_hash: str) -> Dict[str, Any]:
        """
        Minta server memverifikasi blok berdasarkan hash.
        Return: {"found": bool, "is_valid": bool, "message": str, ...}
        """
        data = self._get(f"/api/v1/verify/{quote(block_hash, safe='')}")
        found = bool(data.get("found", False))
        msg_upper = (data.get("message") or "").upper()

        # Logika validasi:
        # - Block valid jika hash cocok (server bilang VALID)
        # - Block TIDAK valid jika server bilang "TIDAK VALID"
        # - Signature boleh kosong (blok lama) — dianggap non-error
        is_valid = found and ("VALID" in msg_upper) and ("TIDAK VALID" not in msg_upper)

        return {
            "found": found,
            "is_valid": is_valid,
            "message": data.get("message", ""),
            "signature_valid": bool(data.get("signature_valid", False)),
            "block": data.get("block"),
        }

    # ============================================================
    # VERIFY PUBLIK
    # ============================================================
    def verify_public_by_hash(self, hash_str: str) -> Dict[str, Any]:
        return self._get(f"/api/v1/verify/{quote(hash_str, safe='')}")

    def verify_public_by_nim(self, nim: str) -> Dict[str, Any]:
        """
        Encode per-segment agar `/` tetap sebagai path separator.
        Contoh: '22/588856/MP/98424' → '22/588856/MP/98424' (tetap)
        Tapi karakter khusus (spasi, %, dll) akan di-encode.
        """
        encoded = "/".join(quote(seg, safe="") for seg in nim.split("/"))
        return self._get(f"/api/v1/verify-nim/{encoded}")

    # ============================================================
    # PUBLIC STATS
    # ============================================================
    def get_public_stats(self) -> Dict[str, Any]:
        return self._get("/api/v1/public/stats")

    # ============================================================
    # ANALYTICS (client-side aggregation)
    # ============================================================
    def get_analytics(self) -> Dict[str, Any]:
        """
        Hitung analytics di sisi client dari endpoint publik.
        Tidak butuh admin token, hanya API key universitas.
        """
        blocks_data = self._get("/api/v1/certificates")
        certs = [b for b in blocks_data if b.get("index", 0) > 0]

        by_year: Dict[str, int] = {}
        by_faculty: Dict[str, int] = {}
        by_prodi: Dict[str, int] = {}
        by_institusi: Dict[str, int] = {}

        for b in certs:
            data = b.get("data") or {}
            if not isinstance(data, dict):
                continue

            tahun = self._extract_year(data, b.get("timestamp", 0))
            fak = (
                data.get("fakultas")
                or self._infer_fakultas(data.get("jurusan", ""))
            ).upper()
            prodi = (data.get("jurusan") or "TIDAK DIKETAHUI").upper()
            institusi = (data.get("institusi") or "").upper()

            by_year[tahun] = by_year.get(tahun, 0) + 1
            by_faculty[fak] = by_faculty.get(fak, 0) + 1
            by_prodi[prodi] = by_prodi.get(prodi, 0) + 1
            by_institusi[institusi] = by_institusi.get(institusi, 0) + 1

        by_year = dict(sorted(by_year.items()))
        by_faculty = dict(sorted(by_faculty.items(), key=lambda x: -x[1]))
        by_prodi = dict(sorted(by_prodi.items(), key=lambda x: -x[1]))
        by_institusi = dict(sorted(by_institusi.items(), key=lambda x: -x[1]))

        return {
            "stats": {
                "total_certificates": len(certs),
                "total_blocks": len(blocks_data),
                "is_valid": self.is_chain_valid(),
                "by_year": by_year,
                "by_faculty": by_faculty,
                "by_prodi": by_prodi,
                "by_institusi": by_institusi,
            }
        }

    # ============================================================
    # PRIVATE HELPERS
    # ============================================================
    @staticmethod
    def _extract_year(data: dict, timestamp: float) -> str:
        """Ambil tahun lulus: dari tahun_lulus, dari tanggal, atau dari timestamp."""
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
        return str(_dt.datetime.fromtimestamp(timestamp).year)

    @staticmethod
    def _infer_fakultas(jurusan: str) -> str:
        """Heuristik klasifikasi fakultas dari nama jurusan."""
        j = (jurusan or "").upper()
        rules = [
            (("TEKNIK", "INFORMATIKA", "KOMPUTER", "ELEKTRO", "MESIN", "SIPIL", "ARSITEKTUR"),
             "FAKULTAS TEKNIK"),
            (("EKONOMI", "MANAJEMEN", "AKUNTANSI", "BISNIS", "KEUANGAN"),
             "FAKULTAS EKONOMI & BISNIS"),
            (("KEDOKTERAN", "KEPERAWATAN", "FARMASI", "GIZI"),
             "FAKULTAS KEDOKTERAN"),
            (("HUKUM",), "FAKULTAS HUKUM"),
            (("SASTRA", "BAHASA", "BUDAYA", "SEJARAH", "ANTROPOLOGI", "ARKEOLOGI"),
             "FAKULTAS ILMU BUDAYA"),
            (("PSIKOLOGI",), "FAKULTAS PSIKOLOGI"),
            (("PENDIDIKAN", "KEGURUAN", "KONSELING"),
             "FAKULTAS KEGURUAN & ILMU PENDIDIKAN"),
            (("SOSIAL", "POLITIK", "KOMUNIKASI", "HUBUNGAN INTERNASIONAL", "SOSIOLOGI"),
             "FAKULTAS ILMU SOSIAL & POLITIK"),
            (("PERTANIAN", "PETERNAKAN", "PERIKANAN", "KEHUTANAN", "AGRONOMI", "PANGAN"),
             "FAKULTAS PERTANIAN"),
            (("MATEMATIKA", "FISIKA", "KIMIA", "BIOLOGI", "MIPA", "STATISTIKA"),
             "FAKULTAS MATEMATIKA & IPA"),
            (("SENI", "DESAIN", "VISUAL", "INTERIOR"),
             "FAKULTAS SENI & DESAIN"),
            (("HEWAN", "VETERINER"), "FAKULTAS KEDOKTERAN HEWAN"),
            (("FILSAFAT",), "FAKULTAS FILSAFAT"),
            (("GEOGRAFI", "KARTOGRAFI"), "FAKULTAS GEOGRAFI"),
        ]
        for keywords, fak in rules:
            if any(k in j for k in keywords):
                return fak
        return "BELUM DIKATEGORIKAN"

    # ============================================================
    # LIFECYCLE
    # ============================================================
    def close(self):
        """Tutup HTTP client (opsional, dipanggil saat app shutdown)."""
        try:
            self._client.close()
        except Exception:
            pass