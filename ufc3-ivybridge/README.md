# EA SPORTS UFC 3 PS4 Port - Legacy CPU Compatibility Patch v2 (PR-48)

Patch kompatibilitas generasi kedua untuk menjalankan **EA SPORTS UFC 3 PS4 Port (CUSA06534)** pada prosesor lawas tanpa instruksi AVX2/BMI1/LZCNT/MOVBE (seperti Intel Core Generasi ke-3 Ivy Bridge dan Generasi ke-2 Sandy Bridge).

Patch ini mencakup seluruh perbaikan teknis standar upstream PR #48 (`GNSB/UFC-3-PS4-PORT-LINUX-WINDOWS`).

## Fitur & Peningkatan v2 (PR-48)
1. **100% Coverage Translation (6.155 Instruksi, 0 Terlewat)**:
   - Menutup 83 instruksi AVX2 di `libc.prx` yang terlewat pada versi v1 sebelumnya melalui FDE scanning & symbol tracking.
2. **Koreksi Semantik EFLAGS `blsr` & `blsmsk`**:
   - Memperbaiki penanganan register input nol (`dest = 0, CF=1, ZF=1` untuk `blsr`; `dest = -1, CF=1, ZF=0` untuk `blsmsk`) sesuai spesifikasi resmi arsitektur Intel x86-64.
3. **Multi-Instruction Spanning untuk Instruksi Pendek**:
   - Menggabungkan instruksi berukuran `< 5 bytes` dengan instruksi tetangganya sehingga muat disisipkan jump trampoline tanpa ada pergeseran byte (zero byte shift).
4. **Optimasi In-Place `movbe`**:
   - Menerjemahkan 95 instruksi load `movbe` 32-bit langsung di tempat (`mov r32, m32; bswap r32`) tanpa memakan slot trampoline runtime.
5. **BBPROBE5 Handshake & Linker Diagnostic**:
   - Mengaktifkan Bit 1 (`FLAG_LEGACY_CPU_TRANSLATED`) dan mencatat laporan status link lengkap di `link.json``.
6. **Clean Plan Format**:
   - Tidak lagi menyertakan raw byte dump proprietary, hanya RVA offset dan mnemonic yang terikat verifikasi cryptographic hash SHA-256 modul game asli.
7. **Suite Unit Test Lengkap**:
   - Disertai `tests/test_cpu_compat.py` untuk memverifikasi akurasi emulasi instruksi x86.

## Total Instruksi yang Diterjemahkan (6.155 Sites)
- `andn`: 2.927
- `bextr`: 2.537
- `movbe`: 414 (95 in-place, 319 trampolined)
- `lzcnt`: 87
- `blsi`: 56
- `tzcnt`: 50
- `blsr`: 1 (zero-source semantics fixed)
- `blsmsk`: 1 (zero-source semantics fixed)
- `libc.prx strlen`: Baseline SysV x86-64
- **Total Unhandled**: 0 (100.0% coverage)

## Cara Pemasangan Otomatis (PowerShell)
1. Ekstrak file zip ini.
2. Buka PowerShell dan jalankan:
   ```powershell
   .\apply_patch.ps1 -UFC3Path "C:\Path\To\UFC3Native"
   ```
3. Set environment variable:
   ```cmd
   setx BB_SKIP_CPU_CHECK 1
   ```
4. Buka kembali terminal/launcher, lalu jalankan `UFC3.exe`.

## Cara Pemasangan Manual
1. Salin folder `scripts/` (`cpu_compat.py`, `link_modules.py`) ke folder `scripts/` instalasi game.
2. Salin folder `tools/` (`build_cpu_compat.py`, `legacy_plan_data.py`, `legacy_plan_p1.py`, `legacy_plan_p2.py`, `legacy_plan_p3.py`) ke folder `tools/`.
3. Salin folder `tests/` (`test_cpu_compat.py`) ke folder `tests/`.
4. Salin `bbport.ini` ke folder utama game.
5. Set `BB_SKIP_CPU_CHECK=1` dan jalankan game.
