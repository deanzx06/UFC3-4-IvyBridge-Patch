# EA SPORTS UFC 3 PS4 Port - Sandy Bridge & Legacy CPU Compatibility Patch v2

Patch kompatibilitas untuk menjalankan **EA SPORTS UFC 3 PS4 Port (CUSA06534)** pada prosesor lawas **Intel Sandy Bridge (Core Generasi ke-2: i3/i5/i7-2xxx, Xeon E3-12xx v1)** serta kompatibel penuh dengan **Ivy Bridge (Core Generasi ke-3 / Xeon v2)**.

---

## Pembaruan di Versi v2:
* **Perbaikan Fatal Crash saat Loading 100% (`read access to 0000000000000001 at guest offset 0x12131cf`)**:
  Menambahkan proteksi CPU EFLAGS (`pushfq` / `popfq`) pada seluruh 331 titik translasi instruksi F16C (`vcvtph2ps` dan `vcvtps2ph`). Pada versi v1, operasi aritmetika pada trampoline emulasi F16C secara tidak sengaja merusak Zero Flag (ZF) dari instruksi pembanding objek sebelumnya (`test r9, r9`), mengakibatkan compiler salah mengambil percabangan memori vertex 3D saat inisialisasi match/in-game.
* **Preservasi Subnormal / DAZ**:
  Menambahkan penanganan float subnormal pada konversi half-float agar selaras dengan standar engine game x86-64 (Denormals-Are-Zero).
* **Pembaruan Unit Test Suite**:
  Ditambahkan unit test verifikasi proteksi register flag EFLAGS untuk memastikan integritas logika percabangan game.

---

## Mengapa Patch Khusus Sandy Bridge Diperlukan?

Prosesor PS4 (AMD Jaguar) menggunakan arsitektur x86-64 dengan set instruksi modern:
1. **BMI1** (`andn`, `bextr`, `blsi`, `blsr`, `blsmsk`, `tzcnt`) - *Tidak ada di Sandy Bridge maupun Ivy Bridge*
2. **MOVBE** - *Tidak ada di Sandy Bridge maupun Ivy Bridge*
3. **LZCNT** - *Tidak ada di Sandy Bridge maupun Ivy Bridge*
4. **F16C** (`vcvtph2ps`, `vcvtps2ph` - Half-Precision 16-bit Float Conversion) - *Ada di Ivy Bridge, tetapi **TIDAK ADA di Sandy Bridge***

Patch Ivy Bridge standar hanya mentranslasikan BMI1/MOVBE/LZCNT. Pada Sandy Bridge, prosesor akan mengalami crash `SIGILL (Illegal Instruction)` ketika game mengeksekusi instruksi konversi Float16 (F16C) pada sistem rendering 3D, mesh, dan animasi.

Patch Sandy Bridge ini menyertakan seluruh translasi instruksi BMI1/MOVBE/LZCNT **ditambah emulasi penuh untuk 331 instruksi F16C**.

---

## Statistik & Rincian Translasi

* **Total Instruksi Ditranslasikan**: **6.486 sites** (100% lengkap)
* **Instruksi Tidak Tertangani (Unhandled)**: **0 sites**
* **Rincian Per Instruksi**:
  * `andn`: 2.930 sites
  * `bextr`: 2.572 sites
  * `movbe`: 414 sites (termasuk 95 in-place `bswap` optimization)
  * `vcvtph2ps` (F16C): **211 sites** (konversi Float16 ke Float32)
  * `vcvtps2ph` (F16C): **120 sites** (konversi Float32 ke Float16)
  * `lzcnt`: 121 sites
  * `tzcnt`: 60 sites
  * `blsi`: 56 sites
  * `blsr`: 1 site
  * `blsmsk`: 1 site

---

## Cara Pemasangan

### Opsi A: Menggunakan PowerShell (Otomatis)
1. Ekstrak file zip patch ini.
2. Buka PowerShell dan jalankan:
   ```powershell
   .\apply_patch.ps1 -UFC3Path "D:\Path\Ke\Folder\UFC3Native"
   ```
3. Pastikan environment variable `BB_SKIP_CPU_CHECK` sudah aktif:
   ```cmd
   setx BB_SKIP_CPU_CHECK 1
   ```
4. Jalankan game melalui `UFC3.exe`.

### Opsi B: Pemasangan Manual
1. Salin seluruh isi folder `scripts/` ke folder `scripts/` pada game UFC 3 kamu.
2. Salin seluruh isi folder `tools/` ke folder `tools/` pada game UFC 3 kamu.
3. Salin file `bbport.ini` ke folder utama game UFC 3 kamu (pastikan berisi `legacy_cpu=1`).
4. Setel environment variable `BB_SKIP_CPU_CHECK=1` di Windows.
5. Jalankan `UFC3.exe`.

---

## Fitur Teknis & Keamanan
* **Zero Proprietary Bytes**: Dataset plan tidak menyimpan byte kode game, bebas dari pelanggaran hak cipta/redistribusi biner.
* **Smart Binary Detection**: Kompatibel baik dengan rilis publik saat ini (`v0.1.11` s/d `v0.1.14`) maupun update build upstream mendatang (`probe.c` relaxation).
* **Paritas Byte-for-Byte**: Jika fitur dinonaktifkan (`BB_LEGACY_CPU=0`), output biner identik 100% dengan hash resmi upstream (`cea8cdf4...`).
* **Unit Test Suite**: Disertai 12 unit test otomatis di `tests/test_cpu_compat.py` yang memverifikasi presisi konversi matematika IEEE 754.

---

## Lisensi & Kredit
* Berlisensi **GPL-2.0-only** sesuai lisensi upstream UFC 3 Port.
* Dikembangkan oleh **@deanzx06** dengan *AI-assisted engineering*.
* Mengembangkan karya pionir dari T0ug (`T0ug/bloodborne_pc_Ivy-Bridge`) dan Supermedo (`deadinside28/bloodborne_pc`).
