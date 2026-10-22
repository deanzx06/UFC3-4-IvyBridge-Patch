# EA SPORTS UFC 3 PS4 Port - Legacy CPU Compatibility Patch v2 (PR-48)

Compatibility patch to run **EA SPORTS UFC 3 PS4 Port (CUSA06534)** on legacy processors lacking AVX2/BMI1/LZCNT/MOVBE instructions (such as 3rd Gen Intel Core Ivy Bridge and 2nd Gen Sandy Bridge).

This patch includes all standard upstream technical fixes from PR #48 (`GNSB/UFC-3-PS4-PORT-LINUX-WINDOWS`).

## Features & Improvements v2 (PR-48)

1. **100% Translation Coverage (6,155 Instructions, 0 Missed)**:
* Covers 83 AVX2 instructions in `libc.prx` that were missed in v1 via FDE scanning and symbol tracking.


2. **EFLAGS Semantics Correction for `blsr` & `blsmsk**`:
* Fixes handling for zero input registers (`dest = 0, CF=1, ZF=1` for `blsr`; `dest = -1, CF=1, ZF=0` for `blsmsk`) according to official Intel x86-64 architecture specifications.


3. **Multi-Instruction Spanning for Short Instructions**:
* Combines instructions smaller than 5 bytes (`< 5 bytes`) with neighboring instructions to fit jump trampolines with zero byte shift.


4. **In-Place `movbe` Optimization**:
* Translates 95 32-bit `movbe` load instructions directly in-place (`mov r32, m32; bswap r32`) without consuming runtime trampoline slots.


5. **BBPROBE5 Handshake & Linker Diagnostics**:
* Enables Bit 1 (`FLAG_LEGACY_CPU_TRANSLATED`) and logs a full link status report in `link.json`.


6. **Clean Plan Format**:
* No longer includes proprietary raw byte dumps; only includes RVA offsets and mnemonics bound to SHA-256 cryptographic hash verification of the original game module.


7. **Complete Unit Test Suite**:
* Includes `tests/test_cpu_compat.py` to verify x86 instruction emulation accuracy.



## Total Translated Instructions (6,155 Sites)

* `andn`: 2,927
* `bextr`: 2,537
* `movbe`: 414 (95 in-place, 319 trampolined)
* `lzcnt`: 87
* `blsi`: 56
* `tzcnt`: 50
* `blsr`: 1 (zero-source semantics fixed)
* `blsmsk`: 1 (zero-source semantics fixed)
* `libc.prx strlen`: Baseline SysV x86-64
* **Total Unhandled**: 0 (100.0% coverage)

## Automated Installation (PowerShell)

1. Extract this zip file.
2. Open PowerShell and run:
```powershell
.\apply_patch.ps1 -UFC3Path "C:\Path\To\UFC3Native"

```


3. Set the environment variable:
```cmd
setx BB_SKIP_CPU_CHECK 1

```


4. Reopen the terminal/launcher, then launch `UFC3.exe`.

## Manual Installation

1. Copy the `scripts/` folder (`cpu_compat.py`, `link_modules.py`) to the game installation's `scripts/` directory.
2. Copy the `tools/` folder (`build_cpu_compat.py`, `legacy_plan_data.py`, `legacy_plan_p1.py`, `legacy_plan_p2.py`, `legacy_plan_p3.py`) to the `tools/` directory.
3. Copy the `tests/` folder (`test_cpu_compat.py`) to the `tests/` directory.
4. Copy `bbport.ini` to the game's root directory.
5. Set `BB_SKIP_CPU_CHECK=1` and launch the game.
