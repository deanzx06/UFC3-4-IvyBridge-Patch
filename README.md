# UFC 4 (PS4 Port) - Legacy CPU Compatibility Patch

[![Compatibility: Intel Ivy Bridge & Sandy Bridge](https://img.shields.io/badge/CPU%20Support-Ivy%20Bridge%20%7C%20Sandy%20Bridge-blue.svg)](https://github.com/deanzx06/UFC4-IvyBridge-Patch)
[![Game: UFC 4 PS4](https://img.shields.io/badge/Game-CUSA14204%20%2F%20CUSA14209-red.svg)](https://github.com/deanzx06/UFC4-IvyBridge-Patch)
[![Upstream PR](https://img.shields.io/badge/Pull%20Request-%231%20Open-green.svg)](https://github.com/XAndromedaXR/UFC-4-PS4-PORT/pull/1)
[![Status: Verified Working](https://img.shields.io/badge/Testing-76%2C200%2B%20frames%20smooth-success.svg)](https://github.com/deanzx06/UFC4-IvyBridge-Patch)
[![Engineered by Antigravity](https://img.shields.io/badge/Engineered%20by-Antigravity%20(Google%20DeepMind)-8A2BE2.svg)](https://deepmind.google/)

This repository provides an automated, link-time compatibility translation patch allowing **UFC 4 (PS4 Port / Portheon / SacredFire)** to run stably on legacy x86-64 processors lacking **BMI1**, **LZCNT**, or **MOVBE** instruction sets (specifically **Intel 2nd & 3rd Gen Core CPUs: Sandy Bridge & Ivy Bridge**, such as Core i7-3770, i5-3570, i7-2600, Xeon E3-1200 series).

> **Important / Legal Notice**:
> This patch **DOES NOT contain any copyrighted EA game binaries or assets (`eboot.bin`, `*.prx`, models, textures, audio)**.
> All translations are computed and linked locally on the user's machine directly from their own legally dumped game copy.

---

## 🥊 The Problem
UFC 4 (PS4) binaries compiled for the PlayStation 4's Jaguar APU utilize modern x86-64 instructions that do not exist on Intel Ivy Bridge (3rd Gen) and Sandy Bridge (2nd Gen) CPUs:
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

## 🚀 How to Use

### Method 1: Using the Standalone Zip Release (Recommended)
1. Download `UFC4_IvyBridge_Patch.zip` from [Releases](https://github.com/deanzx06/UFC4-IvyBridge-Patch/releases).
2. Extract the contents of the zip file into your UFC 4 installation directory (where `eboot.bin` and the `scripts/` folder are located):
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
3. Launch the game using the Portheon / SacredFire launcher as usual.
   - The linker automatically detects your Ivy Bridge/Sandy Bridge CPU via CPUID.
   - `out/boot-linked.bin` will be generated automatically without modifying your original game files.

### Method 2: Manual Linking via Python
If you prefer to link the binary manually:
```bash
python scripts/link_modules.py "path/to/game/UFC4"
```
The patched guest binary output will be saved to `out/boot-linked.bin`.

---

## ⚡ Performance Optimizations (Recommended Settings)

To achieve maximum performance on legacy CPUs (Ivy Bridge / Sandy Bridge) paired with modern graphics cards (e.g. RX 580 / GTX 1060):

### 1. Enable GPU Compute Skinning
In your emulator patch/configuration file (`UFC4-community.xml`):
```xml
<!-- Offload skeletal skinning computations from the Ivy Bridge CPU to GPU Compute Units -->
<Patch id="force-gpu-skinning" enabled="true">
    <Title>Skinning Method 2 (Force GPU Compute)</Title>
    ...
</Patch>
```

### 2. Disable Object Motion Blur
Reduces heavy vertex/pixel shader overhead in UFC 4:
```xml
<Patch id="disable-motion-blur" enabled="true">
    <Title>Disable Object Motion Blur</Title>
    ...
</Patch>
```

### 3. Configure `bbport.ini`
Ensure your `bbport.ini` contains the following settings:
```ini
[bbport]
legacy_cpu=1
async_pipelines=1
```

---

## 📊 Benchmark & Test Results
- **CPU**: Intel Core i7-3770 (Ivy Bridge, 4 cores / 8 threads @ 3.40 GHz - 3.90 GHz)
- **RAM**: 16 GB DDR3
- **GPU**: AMD Radeon RX 580 8GB
- **Results**: Verified stable gameplay for 76,200+ consecutive frames (>21 minutes of active fight without a single crash or memory fault), Exit Code: `0`.

---

## 🤝 Upstream Pull Request
This patch has also been formally submitted as an upstream contribution to the main UFC 4 PS4 Port repository:
- **Pull Request**: [#1 - feat: Add legacy CPU compatibility (Intel Ivy Bridge / Sandy Bridge support)](https://github.com/XAndromedaXR/UFC-4-PS4-PORT/pull/1)

---

## 🤖 Authorship & Development
This compatibility fix was engineered and developed by **Antigravity (Google DeepMind Advanced Agentic Coding)** in pair programming collaboration with **[@deanzx06](https://github.com/deanzx06)**:
- **Root Cause & Crash Analysis**: Disassembled and analyzed all 9,690 unsupported BMI1/LZCNT/MOVBE sites and 630,394 incoming branch targets in `eboot.bin` to trace the audio thread crash at `0x186dc66`.
- **Engineering & Implementation**: Designed the backward spanning logic, 2-byte short jump stub via function alignment NOPs (`0x186dcc1`), SysV ABI trampoline injection engine, and link-time `libc.prx` strlen baseline replacement.
- **Packaging & Tooling**: Created the portable zero-dependency LZMA-compressed fallback plan (`legacy_plan_data.py`), configuration integration, and distribution package.

---

## 👏 Credits & Acknowledgments
- **Antigravity (Google DeepMind)**: Full automated engineering, binary analysis, instruction translation engine, and crash mitigation.
- **deanzx06**: Project lead, hardware testing, validation on Intel Ivy Bridge (Core i7-3770), and distribution.
- **T0ug**: Pioneer of the Ivy Bridge compatibility approach on [`bloodborne_pc_Ivy-Bridge`](https://github.com/T0ug/bloodborne_pc_Ivy-Bridge).
- **Portheon & ShadPS4 Teams**: For the PS4 runtime emulation and guest-linker framework.
- **XAndromedaXR & GNSB**: UFC 4 PS4 Port project & community maintainers.
