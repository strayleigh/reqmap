# ReqMap - Desktop Requirements Engineering Application with ISO/IEC 25023 NFR Mapping

A local-first desktop requirements engineering application inspired by the dense, structured requirements-management workflow of professional tools like ReqView, featuring an explainable, rule-based mapping engine that links Functional Requirements (FR) to Non-Functional Requirements (NFR) based on **ISO/IEC 25023:2016** software product quality standards and research-based **Table III** function character rules.

---

## Fitur Utama

1. **Workspace Rekayasa Kebutuhan Profesional**:
   - **Project Explorer**: Navigasi hierarkis kebutuhan fungsional (FR), non-fungsional (NFR), dan 8 kategori mutu ISO/IEC 25023.
   - **Tabel Kebutuhan Utama**: Tampilan terpadu dengan pencarian real-time, penyaringan tipe (FR/NFR), prioritas, status rekayasa, dan status pemetaan.
   - **Panel Analisis NFR**: Menampilkan karakteristik FR terpilih, rekomendasi atribut kualitas ISO 25023, sumber aturan, sitasi, dan tindakan terima/tolak/pemetaan manual.

2. **Katalog Mutu Lengkap ISO/IEC 25023:2016**:
   - Mencakup seluruh 8 karakteristik produk perangkat lunak:
     1. *Functional suitability*
     2. *Performance efficiency*
     3. *Compatibility*
     4. *Usability*
     5. *Reliability*
     6. *Security*
     7. *Maintainability*
     8. *Portability*
   - Dilengkapi 31 subkarakteristik resmi dan 34 ukuran mutu (*quality measures*) dengan rumus/fungsi matematis, satuan ukur, arah optimasi, dan metode verifikasi.
   - Dialog penjelajah katalog terintegrasi (`Ctrl+K`).

3. **Engine Pemetaan FR-ke-NFR Berbasis Aturan (Table III)**:
   - Mengimplementasikan pemetaan aturan dari penelitian:
     - *Runs according to the actor* $\rightarrow$ **Functional suitability**
     - *CRUD / database process* $\rightarrow$ **Performance efficiency**
     - *File transfer* $\rightarrow$ **Compatibility**
     - *Makes tasks easier for users and reduces human error* $\rightarrow$ **Usability**
     - *Failure/error detection in the system* $\rightarrow$ **Reliability**
     - *Security of transfers, data, access rights, and controls* $\rightarrow$ **Security**
     - *Module-related functions: reusability, logging, analysis, modification, testability* $\rightarrow$ **Maintainability**
     - *Application configuration and adaptation to other environments, applications, or software* $\rightarrow$ **Portability**
   - Menghasilkan rekomendasi transparan dengan sitasi sumber dan catatan rasional.
   - Mendukung hubungan many-to-many (1 FR ke banyak NFR, 1 NFR ke banyak FR).

4. **Pengelolaan Target Nilai Metrik & Pemisahan Data Dummy**:
   - Konfigurasi ambang batas target pengguna dengan operator perbandingan (`<=`, `>=`, `=`, `<`, `>`, `range`).
   - Penandaan tegas bahwa nilai target simulasi adalah **data dummy** pengguna dan bukan standar baku empiris ISO.
   - Fitur tombol *Reset ke Nilai Dummy Default*.

5. **Penyimpanan Lokal Persisten & Tema Visual**:
   - Penyimpanan lokal SQLite (`reqmap.db`) dengan schema ternormalisasi, foreign key aktif, dan integritas referensial.
   - Dukungan tema visual **Dark Mode** dan **Light Mode**.
   - Ekspor data ke JSON dan CSV.
   - Dilengkapi data contoh berbahasa Indonesia (*Sistem Rekam Medis Elektronik RS Harapan Sehat*).

---

## Persyaratan Sistem

- Python 3.10 atau lebih baru
- PySide6 (Qt 6)
- SQLite3 (tersedia bawaan di Python)
- Sistem Operasi: Linux atau Windows

---

## Panduan Menjalankan Aplikasi

### Linux

1. Masuk ke direktori proyek:
   ```bash
   cd req-map
   ```

2. Jalankan aplikasi menggunakan script runner:
   ```bash
   ./run.sh
   ```
   *atau langsung dengan virtualenv:*
   ```bash
   .venv/bin/python run.py
   ```

### Windows

1. Buka PowerShell atau Command Prompt pada direktori proyek.
2. Buat virtual environment jika belum ada:
   ```cmd
   python -m venv .venv
   .venv\Scripts\pip install PySide6 pytest pytest-qt
   ```
3. Jalankan aplikasi:
   ```cmd
   .venv\Scripts\python.exe run.py
   ```

---

## Menjalankan Unit & Integration Test

Seluruh modul backend, mesin aturan Table III, persistence SQLite, dan antarmuka PySide6 diuji menggunakan `pytest`:

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/pytest -v tests
```

---

## Panduan Packaging (Linux & Windows)

Aplikasi dapat dikompilasi menjadi berkas executable portabel menggunakan **PyInstaller**:

```bash
.venv/bin/pip install pyinstaller

# Pembuatan executable single-file
pyinstaller --name "ReqMap" \
            --windowed \
            --add-data "app/database/schema.sql:app/database" \
            run.py
```
Hasil executable mandiri akan tersedia di folder `dist/ReqMap/`.
