# EA SPORTS UFC 3 PS4 Port - Sandy Bridge & Legacy CPU Compatibility Patch

Compatibility patch to run **EA SPORTS UFC 3 PS4 Port (CUSA06534)** on legacy **Intel Sandy Bridge (2nd Gen Core: i3/i5/i7-2xxx, Xeon E3-12xx v1)** processors, with full backward compatibility for **Ivy Bridge (3rd Gen Core / Xeon v2)**.

---

## Updates in thid Version:

* **Fixed Fatal Crash at 100% Loading (`read access to 0000000000000001 at guest offset 0x12131cf`)**:
Added CPU EFLAGS protection (`pushfq` / `popfq`) across all 331 F16C instruction translation sites (`vcvtph2ps` and `vcvtps2ph`). In v1, arithmetic operations within the F16C emulation trampoline inadvertently clobbered the Zero Flag (ZF) set by preceding object comparison instructions (`test r9, r9`), causing the compiler to take the wrong 3D vertex memory branch during match/in-game initialization.
* **Subnormal / DAZ Preservation**:
Added subnormal float handling for half-float conversions to align with x86-64 game engine standards (Denormals-Are-Zero).
* **Updated Unit Test Suite**:
Added unit tests verifying EFLAGS register flag protection to ensure game branching logic integrity.

---

## Why is a Dedicated Sandy Bridge Patch Needed?

The PS4 processor (AMD Jaguar) uses the x86-64 architecture with modern instruction sets:

1. **BMI1** (`andn`, `bextr`, `blsi`, `blsr`, `blsmsk`, `tzcnt`) - *Missing on both Sandy Bridge and Ivy Bridge*
2. **MOVBE** - *Missing on both Sandy Bridge and Ivy Bridge*
3. **LZCNT** - *Missing on both Sandy Bridge and Ivy Bridge*
4. **F16C** (`vcvtph2ps`, `vcvtps2ph` - Half-Precision 16-bit Float Conversion) - *Present on Ivy Bridge, but **MISSING on Sandy Bridge***

Standard Ivy Bridge patches only translate BMI1/MOVBE/LZCNT. On Sandy Bridge, the processor triggers a `SIGILL (Illegal Instruction)` crash whenever the game executes Float16 conversion instructions (F16C) in the 3D rendering, mesh, and animation systems.

This Sandy Bridge patch includes all BMI1/MOVBE/LZCNT instruction translations **plus full emulation for 331 F16C instructions**.

---

## Statistics & Translation Details

* **Total Instructions Translated**: **6,486 sites** (100% complete)
* **Unhandled Instructions**: **0 sites**
* **Breakdown by Instruction**:
* `andn`: 2,930 sites
* `bextr`: 2,572 sites
* `movbe`: 414 sites (including 95 in-place `bswap` optimizations)
* `vcvtph2ps` (F16C): **211 sites** (Float16 to Float32 conversion)
* `vcvtps2ph` (F16C): **120 sites** (Float32 to Float16 conversion)
* `lzcnt`: 121 sites
* `tzcnt`: 60 sites
* `blsi`: 56 sites
* `blsr`: 1 site
* `blsmsk`: 1 site



---

## Installation Guide

### Option A: Using PowerShell (Automated)

1. Extract this patch zip file.
2. Open PowerShell and run:
```powershell
.\apply_patch.ps1 -UFC3Path "D:\Path\To\UFC3Native"

```


3. Ensure the `BB_SKIP_CPU_CHECK` environment variable is set:
```cmd
setx BB_SKIP_CPU_CHECK 1

```


4. Launch the game via `UFC3.exe`.

### Option B: Manual Installation

1. Copy the entire contents of the `scripts/` folder to the `scripts/` folder of your UFC 3 game directory.
2. Copy the entire contents of the `tools/` folder to the `tools/` folder of your UFC 3 game directory.
3. Copy the `bbport.ini` file to the root UFC 3 game folder (ensure it contains `legacy_cpu=1`).
4. Set the environment variable `BB_SKIP_CPU_CHECK=1` in Windows.
5. Launch `UFC3.exe`.

---

## Technical & Safety Features

* **Zero Proprietary Bytes**: Plan datasets contain no game code bytes, free from copyright infringement or binary redistribution issues.
* **Smart Binary Detection**: Compatible with current public releases (`v0.1.11` through `v0.1.14`) as well as future upstream builds (`probe.c` relaxation).
* **Byte-for-Byte Parity**: When the feature is disabled (`BB_LEGACY_CPU=0`), the binary output is 100% identical to the official upstream hash (`cea8cdf4...`).
* **Unit Test Suite**: Includes 12 automated unit tests in `tests/test_cpu_compat.py` verifying IEEE 754 mathematical conversion precision.

---

## License & Credits

* Licensed under **GPL-2.0-only**, consistent with the upstream UFC 3 Port license.
* Developed by **@deanzx06** with *AI-assisted engineering*.
* Builds upon pioneering work by T0ug (`T0ug/bloodborne_pc_Ivy-Bridge`) and Supermedo (`deadinside28/bloodborne_pc`).
