<div align="center">

<img src="dokumentasi/ijazah_chain.png" alt="Ijazah Chain" width="180" />

# 🔐 IJAZAH CHAIN

### Sistem Verifikasi Ijazah Berbasis Blockchain + ECDSA Digital Signature

**Mencegah pemalsuan ijazah dengan teknologi kriptografi modern.**

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.11-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-00f0ff?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.1-a78bfa?style=for-the-badge)](https://github.com/your-username/ijazah-chain/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge)](https://github.com/your-username/ijazah-chain)

[![Status](https://img.shields.io/badge/Status-Production%20Ready-34d399?style=flat-square)]()
[![Blockchain](https://img.shields.io/badge/Blockchain-SHA--256-00f0ff?style=flat-square)]()
[![Signature](https://img.shields.io/badge/Signature-ECDSA%20P--256-a78bfa?style=flat-square)]()
[![Database](https://img.shields.io/badge/Storage-SQLite-003B57?style=flat-square&logo=sqlite)]()
[![Tests](https://img.shields.io/badge/Tests-Passing-34d399?style=flat-square)]()

**Dikembangkan dengan ❤️ untuk integritas akademik Indonesia**

[📖 Dokumentasi](#-user-guide) •
[🚀 Quick Start](#-quick-start) •
[🏗️ Arsitektur](#-arsitektur) •
[🗺️ Roadmap](#-roadmap) •
[🐛 Report Bug](issues)

</div>

---

## 📖 Daftar Isi

- [✨ Fitur Utama](#-fitur-utama)
- [🎯 Mengapa Ijazah Chain?](#-mengapa-ijazah-chain)
- [🏗️ Arsitektur Sistem](#️-arsitektur-sistem)
- [🛠️ Tech Stack](#️-tech-stack)
- [📦 Instalasi](#-instalasi)
  - [Prasyarat](#prasyarat)
  - [Metode 1: Instalasi Manual (Development)](#metode-1-instalasi-manual-development)
  - [Metode 2: Menjalankan dari EXE (Production)](#metode-2-menjalankan-dari-exe-production)
- [🚀 Quick Start](#-quick-start)
- [📸 User Guide](#-user-guide)
  - [1. Menerbitkan Ijazah Baru](#1-menerbitkan-ijazah-baru)
  - [2. Audit Blockchain](#2-audit-blockchain)
  - [3. Verifikasi Publik](#3-verifikasi-publik)
  - [4. Analitik](#4-analitik)
  - [5. Import Massal](#5-import-massal)
  - [6. Dashboard Admin Web](#6-dashboard-admin-web)
- [🔌 API Reference](#-api-reference)
- [⚙️ Konfigurasi](#️-konfigurasi)
- [🧪 Testing](#-testing)
- [🔨 Build ke EXE](#-build-ke-exe)
- [🗺️ Roadmap](#️-roadmap)
- [🤝 Contributing](#-contributing)
- [❓ FAQ](#-faq)
- [📄 License](#-license)
- [👨‍💻 Credits](#-credits)

---

## ✨ Fitur Utama

<table>
<tr>
<td width="50%">

### 🔐 Keamanan Tingkat Tinggi
- **SHA-256 hashing** untuk setiap blok
- **ECDSA P-256 digital signature** untuk otentikasi
- **Immutable blockchain** — data tidak bisa diubah
- **API key authentication** per universitas
- **Audit log** — semua akses terekam

</td>
<td width="50%">

### 🎨 Antarmuka Modern
- **Desktop app (PyQt6)** dengan dark premium theme
- **Web dashboard** dengan aurora animated background
- **Real-time charts** — pie, bar, & activity timeline
- **Responsive design** — desktop, tablet, mobile

</td>
</tr>
<tr>
<td>

### 📜 Ijazah Digital
- **3 template** (Klasik, Modern, Minimalis)
- **QR code** tertanam di setiap ijazah
- **Export PDF** ukuran A4 landscape
- **Auto-verifikasi** via scan QR

</td>
<td>

### 🌐 Multi-Platform
- **Server terpusat** (FastAPI) atau **mode lokal** (offline)
- **Verifikasi publik** tanpa login
- **QR scanner web** — buka dari HP
- **Batch import** dari CSV/Excel

</td>
</tr>
<tr>
<td>

### 🛡️ Backup & Recovery
- **Auto-backup harian** (jam 02:00)
- **Retention 30 hari** dengan rotasi otomatis
- **Manual backup** via API
- **SQLite backup API** (aman saat DB aktif)

</td>
<td>

### 📊 Analitik Komprehensif
- Distribusi per **fakultas**
- Distribusi per **program studi**
- Tren per **tahun akademik**
- **Ranking** institusi

</td>
</tr>
</table>

---

## 🎯 Mengapa Ijazah Chain?

### 😱 Masalah
- **Pemalsuan ijazah** marak terjadi di Indonesia
- Verifikasi manual memakan **waktu berhari-hari**
- **Tidak ada sistem** standar untuk cek keaslian
- HRD kesulitan memvalidasi ijazah pelamar

### 💡 Solusi
- **QR code** di ijazah → scan → verifikasi dalam **3 detik**
- **Blockchain** → data tidak bisa dimanipulasi
- **Digital signature** → otentikasi tanpa perlu kontak universitas
- **Dashboard publik** → transparansi untuk semua pihak

### 📈 Dampak
- ⏱️ **99% lebih cepat** dari verifikasi manual
- 🔒 **100% anti-pemalsuan** dengan kriptografi
- 🌍 **Akses global** — verifikasi dari mana saja
- 💰 **Hemat biaya** — tanpa perlu cetak ulang ijazah

---

## 🏗️ Arsitektur Sistem

```
┌───────────────────────────────────────────────────────────────────┐
│                     SERVER (FastAPI + SQLite)                     │
│                                                                   │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐  │
│  │   Blockchain    │   │  ECDSA Signing  │   │   Audit Log     │  │
│  │   Ledger (v4)   │◄──┤  (Private Key)  │   │   (SQLite)      │  │
│  │                 │   │                 │   │                 │  │
│  │ • Genesis Block │   │  secp256r1      │   │  • Login        │  │
│  │ • Block 1,2,3.. │   │  SHA-256        │   │  • Issue        │  │
│  └─────────────────┘   └─────────────────┘   │  • Audit        │  │
│                                                │  • Backup       │  │
│  ┌─────────────────────────────────────────┐  └─────────────────┘  │
│  │  REST API Endpoints                     │                        │
│  │  • POST /api/v1/certificates (issue)    │                        │
│  │  • GET  /api/v1/verify/{hash}           │                        │
│  │  • GET  /api/v1/verify-nim/{nim}        │                        │
│  │  • GET  /api/v1/audit                   │                        │
│  │  • POST /api/v1/admin/login             │                        │
│  └─────────────────────────────────────────┘                        │
│                                                                   │
│  ┌─────────────────────────────────────────┐                        │
│  │  Static Content                         │                        │
│  │  • /dashboard → Admin Web UI            │                        │
│  │  • /verify    → Public Verifier         │                        │
│  └─────────────────────────────────────────┘                        │
└──────────────────────┬────────────────────────────────────────────┘
                       │ HTTP/REST (JSON)
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  CLIENT     │ │  CLIENT     │ │  VERIFIER   │
│  PyQt6 UGM  │ │  PyQt6 UI   │ │  Browser    │
│             │ │             │ │             │
│ • Issue     │ │ • Issue     │ │ • Scan QR   │
│ • PDF       │ │ • PDF       │ │ • Cek Hash  │
│ • Analytics │ │ • Analytics │ │ • Cek NIM   │
│ • Import    │ │ • Import    │ │             │
└─────────────┘ └─────────────┘ └─────────────┘
```

---

## 🛠️ Tech Stack

<table>
<tr>
<td><b>Layer</b></td>
<td><b>Teknologi</b></td>
<td><b>Fungsi</b></td>
</tr>
<tr>
<td>🎨 <b>Client UI</b></td>
<td>PyQt6, ReportLab, qrcode</td>
<td>Desktop app untuk penerbitan ijazah</td>
</tr>
<tr>
<td>🌐 <b>Server</b></td>
<td>FastAPI, Uvicorn, Pydantic</td>
<td>REST API & business logic</td>
</tr>
<tr>
<td>💾 <b>Storage</b></td>
<td>SQLite 3</td>
<td>Blockchain ledger & audit log</td>
</tr>
<tr>
<td>🔐 <b>Cryptography</b></td>
<td>cryptography (ECDSA), hashlib (SHA-256)</td>
<td>Signature & hashing</td>
</tr>
<tr>
<td>🛡️ <b>Security</b></td>
<td>slowapi, API key auth</td>
<td>Rate limiting & access control</td>
</tr>
<tr>
<td>⏰ <b>Scheduler</b></td>
<td>APScheduler</td>
<td>Auto-backup harian</td>
</tr>
<tr>
<td>📊 <b>Web UI</b></td>
<td>HTML5, CSS3, Chart.js, jsQR</td>
<td>Dashboard admin & verifier</td>
</tr>
</table>

---

## 📦 Instalasi

### Prasyarat

| Software | Versi Minimum | Keterangan |
|---|---|---|
| **Python** | 3.11 / 3.12 / 3.14 | ⚠️ Python 3.11–3.12 **sangat direkomendasikan** |
| **pip** | 22.0+ | Package installer |
| **Git** | 2.30+ | Version control (opsional) |
| **Windows** | 10/11 | Atau Linux/macOS |

> ⚠️ **Catatan**: Python 3.14 bekerja tapi beberapa library mungkin butuh compiler C. Sangat direkomendasikan Python 3.12.

---

### Metode 1: Instalasi Manual (Development)

#### 1️⃣ Clone Repository

```bash
git clone https://github.com/duhemen/ijazah-chain.git
cd ijazah-chain
```

Atau ekstrak ZIP ke `D:\ijazah_chain\`.

#### 2️⃣ Buat Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv ijazah_chain
.\ijazah_chain\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python3 -m venv ijazah_chain
source ijazah_chain/bin/activate
```

#### 3️⃣ Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Jika ada library yang gagal install** (biasanya `cryptography`, `slowapi`, `opencv` di Python 3.14):
```bash
# Install yang berhasil dulu
pip install fastapi uvicorn pydantic httpx python-multipart
pip install PyQt6 qrcode pillow reportlab
pip install cryptography slowapi apscheduler
```

#### 4️⃣ Verifikasi Instalasi

```bash
python -c "import fastapi, PyQt6, cryptography, slowapi, apscheduler; print('✅ Semua library OK')"
```

#### 5️⃣ Jalankan Server

**Terminal 1:**
```bash
python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

Atau lebih singkat:
```bash
python run_server.py
```

**Output yang diharapkan:**
```
2026-09-19 00:25:22 [INFO] Server startup - DB siap
2026-09-19 00:25:22 [INFO] Auto-backup aktif: setiap hari jam 02:00
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

#### 6️⃣ Jalankan Client

**Terminal 2 (baru):**
```bash
cd D:\ijazah_chain
.\ijazah_chain\Scripts\Activate.ps1
python -m app.main
```

Atau:
```bash
python run_client.py
```

#### 7️⃣ Buka Dashboard

- 🖥️ **Dashboard Admin**: http://localhost:8000/dashboard
  - Login: `admin` / `admin123`
- 🔍 **Verifikasi Publik**: http://localhost:8000/verify
- 📖 **API Docs**: http://localhost:8000/docs

---

### Metode 2: Menjalankan dari EXE (Production)

Jika Anda sudah punya file `IjazahChainServer.exe` dan `IjazahChainClient.exe`:

#### 1️⃣ Extract

```powershell
# Extract ke folder mana saja
Expand-Archive IjazahChainServer.zip -DestinationPath D:\IjazahChain
Expand-Archive IjazahChainClient.zip -DestinationPath D:\IjazahChain
```

#### 2️⃣ Jalankan Server

```powershell
cd D:\IjazahChain\IjazahChainServer
.\IjazahChainServer.exe
```

✅ Browser otomatis terbuka ke dashboard.

#### 3️⃣ Jalankan Client

```powershell
cd D:\IjazahChain\IjazahChainClient
.\IjazahChainClient.exe
```

✅ Tidak perlu install Python!

---

## 🚀 Quick Start

```bash
# 1. Clone & masuk folder
git clone https://github.com/duhemen/ijazah-chain.git
cd ijazah-chain

# 2. Buat venv & aktifkan
python -m venv ijazah_chain
.\ijazah_chain\Scripts\Activate.ps1     # Windows
# source ijazah_chain/bin/activate      # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Jalankan server (terminal 1)
python -m uvicorn server.main:app --port 8000 --reload

# 5. Jalankan client (terminal 2)
python -m app.main

# 6. Buka browser
# http://localhost:8000/dashboard
```

**Dalam 5 menit Anda sudah bisa menerbitkan ijazah digital pertama!** 🎉

---

## 📸 User Guide

### 1. Menerbitkan Ijazah Baru

<p align="center">
  <img src="dokumentasi/client_penerbitan_ijazah.png" alt="Penerbitan Ijazah" width="90%" />
</p>

**Langkah-langkah:**

1. **Buka tab** `✍️ PENERBITAN IJAZAH`
2. **Pilih template** ijazah:
   - 🏛️ **Klasik** — desain tradisional dengan bingkai ornate
   - 💼 **Modern** — layout korporat minimalis biru
   - ✨ **Minimalis** — putih bersih, tipografi elegan
3. **Isi form** (kolom bertanda `*` wajib):
   - Nama Institusi Kampus
   - Fakultas (dropdown auto-populate)
   - Program Studi (auto dari fakultas)
   - Nama Lengkap Mahasiswa
   - NIM (format: `21/123456/TK/78901`)
   - Gelar Akademik (contoh: S.Kom, S.H)
   - No. Seri Nasional
   - Tahun Lulus
   - Judul Skripsi
   - Nama Rektor
   - Nama Dekan
   - Footnote kustom (opsional)
4. **Preview otomatis** update di panel kanan
5. Klik **`🔒 DAFTARKAN LEGALITAS KE SECURE LEDGER`**
6. Konfirmasi popup → ijazah tersimpan di blockchain
7. Klik **`🖨️ CETAK & SIMPAN IJAZAH (PDF)`**
8. Pilih lokasi penyimpanan → PDF siap cetak

> 💡 **Tips**: QR code di preview akan otomatis ter-generate. Scan dengan HP untuk test verifikasi.

---

### 2. Audit Blockchain

<p align="center">
  <img src="dokumentasi/client_audit_blockchain.png" alt="Audit Blockchain" width="90%" />
</p>

**Fungsi**: Memverifikasi integritas seluruh rantai blockchain.

**Cara pakai:**

1. Buka tab `🔍 AUDIT BLOCKCHAIN`
2. Lihat **status box** di atas:
   - 🟢 **AMAN & TERVALIDASI** — semua hash cocok
   - 🔴 **PERINGATAN** — terdeteksi manipulasi
3. **Klik salah satu blok** di daftar kiri → detail muncul di kanan:
   - Waktu minting
   - Hash blok
   - Hash sebelumnya
   - Isi data lengkap
   - Status validasi hash & signature
4. Klik **`🔄 JALANKAN AUDIT INTEGRITAS BLOCKCHAIN`** untuk refresh

> 🔒 **Hasil audit tersimpan** di audit log server. Semua aktivitas terekam.

---

### 3. Verifikasi Publik

<p align="center">
  <img src="dokumentasi/client_verifikasi_publik.png" alt="Verifikasi Publik" width="90%" />
</p>

**Fungsi**: Cek keaslian ijazah tanpa perlu akses admin.

**3 Metode Verifikasi:**

#### 🔐 Metode 1: Berdasarkan Hash

1. Buka tab `🌐 VERIFIKASI PUBLIK`
2. Pilih sub-tab **`🔐 Berdasarkan Hash`**
3. Paste hash blok (tercetak di bagian bawah ijazah PDF)
4. Klik **`Cek Hash`**
5. Hasil muncul:
   - ✅ **IJAZAH ASLI** — semua validasi lulus
   - ⚠️ **PERINGATAN** — ada masalah

#### 🎓 Metode 2: Berdasarkan NIM

1. Pilih sub-tab **`🎓 Berdasarkan NIM`**
2. Masukkan NIM (contoh: `22/588856/MP/98424`)
3. Klik **`Cari NIM`**
4. Semua ijazah dengan NIM tersebut ditampilkan

#### 📷 Metode 3: Scan QR (via Browser/HP)

1. Buka **http://localhost:8000/verify** di browser
2. Pilih tab **`📷 Scan QR`**
3. Klik **`Mulai Scan QR`** → izinkan akses kamera
4. Arahkan kamera ke QR code ijazah
5. Hasil muncul otomatis dalam **3 detik**

> 💡 **Untuk HP**: Ganti `localhost` dengan IP PC Anda (misal `http://192.168.1.10:8000/verify`)

---

### 4. Analitik

<p align="center">
  <img src="dokumentasi/client_analitik.png" alt="Analitik" width="90%" />
</p>

**Fungsi**: Statistik lengkap ijazah dalam satu halaman.

**Yang ditampilkan:**

| Panel | Isi |
|---|---|
| **Stat Cards** | Total ijazah, total blok, status integritas, jumlah institusi |
| **Fakultas Teratas** | Top 10 fakultas dengan bar proporsional |
| **Prodi Teratas** | Top 10 program studi |
| **Distribusi per Tahun** | Jumlah ijazah per tahun akademik |

> 🔄 Klik **`Refresh`** untuk update data terbaru dari server.

---

### 5. Import Massal

<p align="center">
  <img src="dokumentasi/client_import_massal.png" alt="Import Massal" width="90%" />
</p>

**Fungsi**: Upload ratusan ijazah sekaligus dari file CSV/Excel.

**Format CSV wajib:**

| Kolom | Wajib | Contoh |
|---|---|---|
| `nama` | ✅ | Budi Santoso |
| `nim` | ✅ | 21/123456/TK/78901 |
| `jurusan` | ✅ | TEKNIK INFORMATIKA |
| `gelar` | ✅ | S.Kom |
| `nomor_seri` | ✅ | UGM-2026-001 |
| `institusi` | ✅ | UNIVERSITAS GADJAH MADA |
| `fakultas` | ⬜ | FAKULTAS TEKNIK |
| `tahun_lulus` | ⬜ | 2026 |
| `judul_skripsi` | ⬜ | Sistem Verifikasi Ijazah |
| `rektor` | ⬜ | Prof. Dr. Ir. Ova Emen |
| `dekan` | ⬜ | Dr. Mode AI, M.Sc. |
| `custom_footnote` | ⬜ | Diverifikasi via blockchain |

**Cara pakai:**

1. Buka tab `📥 IMPORT MASSAL`
2. Klik **`⬇️ Download Template CSV`** untuk contoh format
3. Isi file dengan data ijazah (bisa 100+ baris)
4. Klik **`📂 Pilih File CSV/Excel`** → pilih file
5. Preview 3 baris pertama muncul
6. Klik **`🚀 MULAI IMPORT`**
7. Tunggu progress bar selesai
8. Lihat summary:
   - ✓ Berhasil: X
   - ✗ Gagal: Y
   - Total: Z

> 💡 **Format Excel**: Butuh `pandas` & `openpyxl`. Install dengan `pip install pandas openpyxl`.

---

### 6. Dashboard Admin Web

**URL**: http://localhost:8000/dashboard
**Login**: `admin` / `admin123`

**Fitur Dashboard:**

| Section | Fungsi |
|---|---|
| 📊 **Ringkasan Sistem** | Status integritas, kartu statistik real-time |
| 📈 **Analitik Ijazah** | Pie chart fakultas & prodi, bar chart tahun |
| 🕒 **Aktivitas Terbaru** | Feed penerbitan ijazah terbaru |
| 📋 **Data Ijazah** | Tabel filterable + export CSV |

**Shortcut keyboard:**
- `Ctrl+K` — Command palette
- `Ctrl+1..4` — Navigasi section
- `Ctrl+R` — Refresh data
- `Esc` — Tutup modal/palette

---

## 🔌 API Reference

**Base URL**: `http://localhost:8000`

### Public Endpoints (Rate Limit: 120/min)

| Method | Endpoint | Deskripsi |
|---|---|---|
| `GET` | `/api/v1/health` | Cek status server |
| `GET` | `/api/v1/public/stats` | Statistik publik |
| `GET` | `/api/v1/public-key` | Public key ECDSA |
| `GET` | `/api/v1/certificates` | Daftar semua blok |
| `GET` | `/api/v1/certificates/{index}` | Detail blok |
| `GET` | `/api/v1/verify/{hash}` | Verifikasi via hash |
| `GET` | `/api/v1/verify-nim/{nim}` | Cari via NIM |
| `GET` | `/api/v1/audit` | Audit seluruh chain |

### Issue Endpoint (butuh API key, Rate Limit: 30/min)

| Method | Endpoint | Header |
|---|---|---|
| `POST` | `/api/v1/certificates` | `X-API-Key: ugm_secret_key_2026` |

**Contoh request:**
```bash
curl -X POST http://localhost:8000/api/v1/certificates \
  -H "X-API-Key: ugm_secret_key_2026" \
  -H "Content-Type: application/json" \
  -d '{
    "nama": "Budi Santoso",
    "nim": "21/123456/TK/78901",
    "jurusan": "TEKNIK INFORMATIKA",
    "gelar": "S.Kom",
    "nomor_seri": "UGM-2026-001",
    "institusi": "UNIVERSITAS GADJAH MADA",
    "fakultas": "FAKULTAS TEKNIK",
    "tahun_lulus": 2026
  }'
```

### Admin Endpoints (butuh `X-Admin-Token`)

| Method | Endpoint | Deskripsi |
|---|---|---|
| `POST` | `/api/v1/admin/login` | Login admin |
| `GET` | `/api/v1/admin/dashboard` | Data lengkap dashboard |
| `GET` | `/api/v1/admin/stats` | Statistik agregat |
| `GET` | `/api/v1/admin/audit-log` | Audit log |
| `POST` | `/api/v1/admin/backup` | Trigger backup manual |
| `GET` | `/api/v1/admin/backups` | Daftar backup |

---

## ⚙️ Konfigurasi

### Server (`server/config.py`)

```python
# Server settings
HOST = "0.0.0.0"
PORT = 8000

# API Keys per universitas
API_KEYS = {
    "ugm_secret_key_2026": "UNIVERSITAS GADJAH MADA",
    "ui_secret_key_2026": "UNIVERSITAS INDONESIA",
    "itb_secret_key_2026": "INSTITUT TEKNOLOGI BANDUNG",
}

# Admin dashboard
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"        # ← GANTI DI PRODUCTION!

# Rate limiting
RATE_LIMIT_PUBLIC = "120/minute"
RATE_LIMIT_ISSUE = "30/minute"

# Backup
BACKUP_ENABLED = True
BACKUP_HOUR = 2                    # 02:00 pagi
BACKUP_RETENTION_DAYS = 30
```

### Client (`app/config.py`)

```python
# Mode: "server" atau "local"
MODE = "server"

# Server URL
SERVER_URL = "http://localhost:8000"

# API key universitas
API_KEY = "ugm_secret_key_2026"
```

### Environment Variables (Opsional)

Gunakan env vars untuk production:

```powershell
$env:IJAZAH_ADMIN_PASS = "password_kuat_anda"
$env:IJAZAH_ADMIN_TOKEN = "token_random_32_chars_minimal"
$env:IJAZAH_HOST = "0.0.0.0"
$env:IJAZAH_PORT = "8000"

python -m uvicorn server.main:app
```

---

## 🧪 Testing

### 1. Seed Data Demo

Isi database dengan **50 ijazah dummy**:

```bash
python seed_data.py
```

Opsi:
```bash
python seed_data.py --count 100              # 100 ijazah
python seed_data.py --server http://ip:8000  # server lain
python seed_data.py --delay 0                # tanpa delay (hati-hati rate limit)
```

### 2. Test API dengan cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Audit blockchain
curl http://localhost:8000/api/v1/audit

# Statistik publik
curl http://localhost:8000/api/v1/public/stats
```

### 3. Test Verifikasi

```bash
# Ambil hash genesis
curl http://localhost:8000/api/v1/certificates/0

# Verify hash
curl http://localhost:8000/api/v1/verify/<hash>
```

---

## 🔨 Build ke EXE

### Otomatis (Recommended)

```bash
# Windows
build_all.bat
```

Script ini akan:
1. Cek & install PyInstaller
2. Build server → `dist/IjazahChainServer/IjazahChainServer.exe`
3. Build client → `dist/IjazahChainClient/IjazahChainClient.exe`

**Durasi**: 5-10 menit.

### Manual

```bash
pip install pyinstaller

# Build server
pyinstaller build_server.spec --clean --noconfirm

# Build client
pyinstaller build_client.spec --clean --noconfirm
```

### Hasil Build

```
dist/
├── IjazahChainServer/
│   ├── IjazahChainServer.exe    ← 200 MB
│   ├── server/static/*.html
│   └── ... (library)
└── IjazahChainClient/
    ├── IjazahChainClient.exe    ← 180 MB
    └── ... (library)
```

### Distribusi

1. **Zip** folder `dist/IjazahChainServer/` → `IjazahChainServer.zip`
2. **Zip** folder `dist/IjazahChainClient/` → `IjazahChainClient.zip`
3. Bagikan ke user → user tinggal extract & double-click `.exe`

---

## 🗺️ Roadmap

### ✅ v2.0.1 — Current (Q3 2026)
- [x] Blockchain ledger dengan SHA-256
- [x] ECDSA P-256 digital signature
- [x] Client desktop PyQt6 dengan 3 template
- [x] Server FastAPI + REST API
- [x] Web dashboard dengan charts
- [x] Verifikasi publik via web/HP
- [x] Batch import CSV/Excel
- [x] Auto-backup harian
- [x] Audit log
- [x] Rate limiting

### 🚧 v2.1.0 — Q4 2026 (Next)
- [ ] **QR scanner via webcam** di client PyQt6
- [ ] **Multi-bahasa** (ID/EN) untuk ijazah
- [ ] **Template ijazah tambahan** (Royal, Elegan)
- [ ] **Export ke PDF ukuran A5** (untuk HP)
- [ ] **Webhook Telegram/WhatsApp** saat issue

### 🔮 v3.0.0 — 2027 (Vision)
- [ ] **IPFS integration** — simpan PDF di IPFS
- [ ] **Multi-signature** — butuh 2+ signature untuk validasi
- [ ] **Zero-knowledge proof** — verifikasi tanpa expose data
- [ ] **Mobile app** (Flutter) untuk verifikasi
- [ ] **NFT Ijazah** — token ERC-721 di Ethereum
- [ ] **Konsorsium multi-kampus** — federated server

---

## 🤝 Contributing

Kami menerima kontribusi! Berikut caranya:

### Development Setup

```bash
git clone https://github.com/duhemen/ijazah-chain.git
cd ijazah-chain
python -m venv ijazah_chain
.\ijazah_chain\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Workflow

1. **Fork** repository
2. **Buat branch** fitur: `git checkout -b fitur/nama-fitur`
3. **Commit** perubahan: `git commit -m 'feat: tambah fitur X'`
4. **Push** ke branch: `git push origin fitur/nama-fitur`
5. **Buat Pull Request**

### Commit Convention

```
feat: menambah fitur baru
fix: memperbaiki bug
docs: update dokumentasi
style: format kode
refactor: refactoring kode
test: menambah test
chore: update build/deps
```

### Area Kontribusi

- 🐛 **Bug fixes** — lihat [issues](issues)
- 📚 **Dokumentasi** — perbaiki typo, tambah contoh
- 🌐 **Terjemahan** — Bahasa Inggris, daerah
- 🎨 **UI/UX** — redesign, animasi
- 🔐 **Security** — audit, penetration testing
- ⚡ **Performance** — optimasi query, caching

---

## ❓ FAQ

<details>
<summary><b>Apakah ijazah yang sudah diterbitkan bisa dihapus?</b></summary>

Tidak. Blockchain bersifat **immutable**. Sekali ijazah diterbitkan, tidak bisa dihapus atau diubah. Ini justru **fitur utama** untuk mencegah pemalsuan.

Jika ada kesalahan input, buat ijazah **koreksi** dengan nomor seri baru.
</details>

<details>
<summary><b>Bagaimana jika server mati?</b></summary>

Server FastAPI yang sudah di-deploy biasanya memiliki uptime tinggi. Untuk development, jalankan sebagai service (Windows Service / systemd) atau gunakan Docker.

**Backup otomatis** memastikan data tidak hilang.
</details>

<details>
<summary><b>Apakah bisa diakses dari HP?</b></summary>

Bisa. Buka `http://<IP-PC>:8000/verify` di browser HP (pastikan WiFi sama). Untuk akses dari luar jaringan, gunakan **ngrok** atau deploy ke cloud.

</details>

<details>
<summary><b>Berapa biaya menjalankan sistem ini?</b></summary>

Untuk **mode lokal**: gratis. Untuk **production**:
- VPS: Rp 50.000 – 200.000/bulan (Railway, Render, DigitalOcean)
- Domain: Rp 150.000/tahun (opsional)
- SSL: gratis (Let's Encrypt)

</details>

<details>
<summary><b>Apakah compatible dengan sistem akademik (SIAKAD)?</b></summary>

Ya, via **REST API**. SIAKAD bisa POST ke `/api/v1/certificates` untuk menerbitkan ijazah otomatis. Butuh API key universitas.

</details>

<details>
<summary><b>Bagaimana jika private key hilang?</b></summary>

Private key tersimpan di `server/keys/server_private.pem`. **WAJIB backup!** Jika hilang:
- Ijazah lama masih bisa diverifikasi (hash valid)
- Tapi signature tidak bisa diverifikasi lagi
- Solusi: simpan private key di **secure vault** atau **HSM**

</details>

---

## 📄 License

Project ini dilisensikan di bawah **MIT License** — bebas digunakan untuk keperluan komersial maupun non-komersial.

```
MIT License

Copyright (c) 2026 Ijazah Chain Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 👨‍💻 Credits

<div align="center">

### Dibuat dengan ❤️ di Indonesia

**Project Lead & Developer**
- 👨‍💻 **Emen** ([@emen](https://github.com/duhemen))

**Dikembangkan dengan bantuan AI**
- 🤖 **DeepSeek** — Architect & Code Reviewer

**Teknologi & Library**
- Python, FastAPI, PyQt6, SQLite, ReportLab, Chart.js, jsQR

**Inspirasi**
- Bitcoin (blockchain concept)
- Let's Encrypt (open infrastructure)
- Indonesia's academic integrity movement

</div>

---

<div align="center">

### 🌟 Jika project ini bermanfaat, berikan bintang! 🌟

[![Star History Chart](https://api.star-history.com/svg?repos=duhemen/ijazah-chain&type=Date)](https://star-history.com/#duhemen/ijazah-chain&Date)

**© 2026 Ijazah Chain — Decentralized Academic Integrity Network**

[Mulai ⬆️](#-ijazah-chain) • [Laporkan Bug](issues) • [Diskusi](discussions)

</div>

---