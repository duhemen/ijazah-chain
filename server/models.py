from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IssueRequest(BaseModel):
    nama: str = Field(..., min_length=1, max_length=120)
    nim: str = Field(..., min_length=1, max_length=40)
    jurusan: str = Field(..., min_length=1, max_length=120)
    gelar: str = Field(..., min_length=1, max_length=80)
    nomor_seri: str = Field(..., min_length=1, max_length=60)
    judul_skripsi: str = Field("", max_length=300)
    institusi: str = Field(..., min_length=1, max_length=120)
    rektor: str = Field("", max_length=120)
    dekan: str = Field("", max_length=120)
    custom_footnote: str = Field("", max_length=300)
    fakultas: str = Field("", max_length=120)
    tahun_lulus: Optional[int] = Field(None, ge=1900, le=2200)


class BlockResponse(BaseModel):
    index: int
    timestamp: float
    data: Any
    previous_hash: str
    hash: str
    signature: str = ""


class IssueResponse(BaseModel):
    success: bool
    block: BlockResponse
    message: str


class AuditResponse(BaseModel):
    is_valid: bool
    total_blocks: int
    certificate_count: int
    message: str
    signature_valid: bool = True


class VerifyResponse(BaseModel):
    found: bool
    block: Optional[BlockResponse] = None
    message: str
    signature_valid: bool = False
    data: Optional[Any] = None


class VerifyByNimResponse(BaseModel):
    found: bool
    count: int
    certificates: List[BlockResponse] = []
    message: str


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    token: str
    username: str
    message: str


class StatsOverviewResponse(BaseModel):
    total_certificates: int
    total_blocks: int
    is_valid: bool
    by_year: Dict[str, int]
    by_faculty: Dict[str, int]
    by_prodi: Dict[str, int]
    by_institusi: Dict[str, int]


class CertificateRow(BaseModel):
    block_index: int
    timestamp: float
    hash: str
    previous_hash: str
    signature: str = ""
    data: Dict[str, Any]
    tahun: str
    fakultas: str
    prodi: str
    nama: str
    nim: str
    institusi: str
    gelar: str


class DashboardResponse(BaseModel):
    stats: StatsOverviewResponse
    certificates: List[CertificateRow]


class PublicStatsResponse(BaseModel):
    total_certificates: int
    total_institusi: int
    total_fakultas: int
    total_prodi: int
    tahun_terakhir: str
    is_valid: bool


class BackupInfo(BaseModel):
    name: str
    size_bytes: int
    created_at: str


class AuditLogEntry(BaseModel):
    id: int
    timestamp: float
    ip_address: Optional[str] = None
    action: str
    resource: str = ""
    status: str = "ok"
    detail: str = ""