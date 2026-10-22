param (
    [Parameter(Mandatory=$true)]
    [string]$UFC4Path
)

if (-not (Test-Path "$UFC4Path\scripts")) {
    Write-Error "Folder '$UFC4Path' bukan direktori UFC-4-PS4-PORT yang valid (folder scripts tidak ditemukan)."
    exit 1
}

$patchRoot = $PSScriptRoot

Write-Host "[1/3] Menyalin scripts/cpu_compat.py..." -ForegroundColor Cyan
Copy-Item "$patchRoot\scripts\cpu_compat.py" -Destination "$UFC4Path\scripts\cpu_compat.py" -Force

Write-Host "[2/3] Menyalin scripts/link_modules.py..." -ForegroundColor Cyan
Copy-Item "$patchRoot\scripts\link_modules.py" -Destination "$UFC4Path\scripts\link_modules.py" -Force

Write-Host "[3/3] Menyalin tools/build_cpu_compat.py..." -ForegroundColor Cyan
if (-not (Test-Path "$UFC4Path\tools")) { New-Item -ItemType Directory -Path "$UFC4Path\tools" | Out-Null }
Copy-Item "$patchRoot\tools\build_cpu_compat.py" -Destination "$UFC4Path\tools\build_cpu_compat.py" -Force

if (Test-Path "$UFC4Path\src\probe.c") {
    Write-Host "[+] Menyalin src/probe.c..." -ForegroundColor Cyan
    Copy-Item "$patchRoot\src\probe.c" -Destination "$UFC4Path\src\probe.c" -Force
}

Write-Host "`nPatch berhasil dipasang ke '$UFC4Path'!" -ForegroundColor Green
Write-Host "Langkah selanjutnya:"
Write-Host "1. Pastikan modul python terpasang: pip install capstone keystone-engine"
Write-Host "2. Generate legacy CPU plan: python tools/build_cpu_compat.py <folder_game_CUSA06534>"
Write-Host "3. Jalankan game: UFC3.exe atau bash run.sh"
