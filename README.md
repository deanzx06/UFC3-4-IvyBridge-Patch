# EA Sports UFC 4 (PS4 Port) - Legacy CPU Compatibility Patch

[![Compatibility: Intel Ivy Bridge & Sandy Bridge](https://img.shields.io/badge/CPU%20Support-Ivy%20Bridge%20%7C%20Sandy%20Bridge-blue.svg)](https://github.com/deanzx06/UFC4-IvyBridge-Patch)
[![Game: EA Sports UFC 4 PS4](https://img.shields.io/badge/Game-CUSA14204%20%2F%20CUSA14209-red.svg)](https://github.com/deanzx06/UFC4-IvyBridge-Patch)
[![Upstream PR](https://img.shields.io/badge/Pull%20Request-%231%20Open-green.svg)](https://github.com/XAndromedaXR/UFC-4-PS4-PORT/pull/1)
[![Status: Verified Working](https://img.shields.io/badge/Testing-76%2C200%2B%20frames%20smooth-success.svg)](https://github.com/deanzx06/UFC4-IvyBridge-Patch)

This repository provides an automated, link-time compatibility translation patch allowing **EA Sports UFC 4 (PS4 Port / Portheon / SacredFire)** to run stably on legacy x86-64 processors lacking **BMI1**, **LZCNT**, or **MOVBE** instruction sets (specifically **Intel 2nd & 3rd Gen Core CPUs: Sandy Bridge & Ivy Bridge**, such as Core i7-3770, i5-3570, i7-2600, Xeon E3-1200 series).

> **Important / Legal Notice**:
> This patch **DOES NOT contain any copyrighted EA game binaries or assets (`eboot.bin`, `*.prx`, models, textures, audio)**.
> All translations are computed and linked locally on the user's machine directly from their own legally dumped game copy.

---

## 🥊 The Problem
EA Sports UFC 4 (PS4) binaries compiled for the PlayStation 4's Jaguar APU utilize modern x86-64 instructions that do not exist on Intel Ivy Bridge (3rd Gen) and Sandy Bridge (2nd Gen) CPUs:
- **BMI1**: `andn`, `bextr`, `blsr`, `blsi`, `blsmsk`, `tzcnt`
- **LZCNT**: Leading Zero Count
- **MOVBE**: Move Big-Endian (extensively used in audio and physics subsystems)
- **SysV ABI strlen**: Modern AVX2/BMI1-optimized `strlen` inside guest `libc.prx`

On Sandy Bridge and Ivy Bridge systems, attempting to execute these instructions causes fatal crashes:
- `0xC000001D: STATUS_ILLEGAL_INSTRUCTION`
- Access violations (`0xC0000005`) due to corrupted register states or mid-instruction branch destinations

---

## 🛠️ The Solution

1. **Link-Time Dynamic Trampolines**:
   - Replaces all 9,690 unsupported instructions in `eboot.bin` with `jmp rel32` redirections pointing to an executable SysV ABI trampoline table generated at the end of the guest image.
   - Automatically saves and restores SysV red zone (`lea rsp, [rsp-128]`) and scratch registers (`rax`, `rdx`, `rsi`, `r8-r11`).

2. **Branch-Target Safe Spanning**:
   - For instructions shorter than 5 bytes (such as 4-byte `movbe`), forward spanning is verified against a global database of 630,394 incoming branch targets.
   - If forward spanning would overwrite an incoming jump target (e.g. `0x186dc66` spanned with `0x186dc6a`), the engine uses **backward spanning** or a **2-byte short jump (`eb 59`)** into adjacent function alignment NOP padding (`0x186dcc1`) to prevent crash loops.

3. **`libc.prx` Baseline `strlen` Replacement**:
   - Overwrites the AVX2/BMI1-dependent `strlen` symbol in `libc.prx` with a clean baseline x86-64 scan routine.

4. **Zero-Dependency Plan Fallback**:
   - Includes `tools/legacy_plan_data.py`, a pre-computed and LZMA-compressed translation plan. Users do not need disassemblers (`capstone`) or assemblers (`keystone`) installed to patch their game!

---

## 🚀 How to Use / Cara Pemasangan

### Cara 1: Menggunakan Standalone Zip Release (Direkomendasikan)
1. Unduh `UFC4_IvyBridge_Patch.zip` dari [Releases](https://github.com/deanzx06/UFC4-IvyBridge-Patch/releases).
2. Ekstrak isi file zip ke dalam folder instalasi UFC 4 Anda (tempat file `eboot.bin` dan folder `scripts/` berada):
   ```text
   games/UFC4/
   ├── bbport.ini
   ├── scripts/
   │   ├── cpu_compat.py
   │   └── link_modules.py
   └── tools/
       ├── build_cpu_compat.py
       └── legacy_plan_data.py
   ```
3. Jalankan game melalui launcher Portheon / SacredFire seperti biasa.
   - Linker akan secara otomatis mendeteksi CPU Ivy Bridge/Sandy Bridge Anda melalui CPUID.
   - File `out/boot-linked.bin` akan dihasilkan secara otomatis tanpa mengubah file game asli Anda.

### Cara 2: Manual Link via Python
Jika Anda ingin me-link binary secara manual:
```bash
python scripts/link_modules.py "path/ke/folder/game/UFC4"
```
Output patched guest binary akan tersimpan di `out/boot-linked.bin`.

---

## ⚡ Performance Optimizations (Rekomendasi Setting)

Untuk mendapatkan performa maksimal pada CPU lawas (Ivy Bridge) yang dipadukan dengan GPU modern (misal RX 580 / GTX 1060):

### 1. Aktifkan GPU Compute Skinning
Di file patch/konfigurasi emulator (`UFC4-community.xml`):
```xml
<!-- Mengalihkan beban animasi skinning dari CPU Ivy Bridge ke GPU Compute Units -->
<Patch id="force-gpu-skinning" enabled="true">
    <Title>Skinning Method 2 (Force GPU Compute)</Title>
    ...
</Patch>
```

### 2. Disable Object Motion Blur
Mengurangi overhead vertex/pixel shader yang berat di UFC 4:
```xml
<Patch id="disable-motion-blur" enabled="true">
    <Title>Disable Object Motion Blur</Title>
    ...
</Patch>
```

### 3. Konfigurasi `bbport.ini`
Pastikan file `bbport.ini` memiliki:
```ini
[bbport]
legacy_cpu=1
async_pipelines=1
```

---

## 📊 Hasil Pengujian (Benchmark)
- **CPU**: Intel Core i7-3770 (Ivy Bridge, 4 cores / 8 threads @ 3.40 GHz - 3.90 GHz)
- **RAM**: 16 GB DDR3
- **GPU**: AMD Radeon RX 580 8GB
- **Hasil**: Berjalan stabil 76,200+ frame berturut-turut (>21 menit pertarungan tanpa crash), Exit Code: `0`.

---

## 🤝 Upstream Pull Request
Patch ini juga telah diajukan secara resmi sebagai kontribusi ke repositori utama UFC 4 PS4 Port:
- **Pull Request**: [#1 - feat(compat): Ivy Bridge & Sandy Bridge legacy CPU compatibility](https://github.com/XAndromedaXR/UFC-4-PS4-PORT/pull/1)

---

## 👏 Credits & Acknowledgments
- **T0ug**: Proyek pelopor kompatibilitas Ivy Bridge pada [`bloodborne_pc_Ivy-Bridge`](https://github.com/T0ug/bloodborne_pc_Ivy-Bridge).
- **Tim Pengembang Portheon & ShadPS4**: Untuk emulasi PS4 runtime dan guest-linker framework.
- **XAndromedaXR & GNSB**: UFC 4 PS4 Port project & community maintainers.
- **deanzx06**: Analisis target branch, mitigasi tabrakan jump offset audio engine, packaging & implementasi UFC 4.
