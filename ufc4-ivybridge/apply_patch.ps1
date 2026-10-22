param (
    [Parameter(Mandatory=$true)]
    [string]$UFC4Path
)

if (-not (Test-Path "$UFC4Path\scripts")) {
    Write-Error "Folder '$UFC4Path' bukan direktori UFC-4-PS4-PORT yang valid (folder scripts tidak ditemukan)."
    exit 1
}

$patchRoot = $PSScriptRoot

Write-Host "[1/4] Menyalin scripts/cpu_compat.py..." -ForegroundColor Cyan
Copy-Item "$patchRoot\scripts\cpu_compat.py" -Destination "$UFC4Path\scripts\cpu_compat.py" -Force

Write-Host "[2/4] Menyalin scripts/link_modules.py..." -ForegroundColor Cyan
Copy-Item "$patchRoot\scripts\link_modules.py" -Destination "$UFC4Path\scripts\link_modules.py" -Force

Write-Host "[3/4] Menyalin tools/build_cpu_compat.py..." -ForegroundColor Cyan
if (-not (Test-Path "$UFC4Path\tools")) { New-Item -ItemType Directory -Path "$UFC4Path\tools" | Out-Null }
Copy-Item "$patchRoot\tools\build_cpu_compat.py" -Destination "$UFC4Path\tools\build_cpu_compat.py" -Force

Write-Host "[4/4] Menyalin pre-compiled translation plan (9,690 sites)..." -ForegroundColor Cyan
Copy-Item "$patchRoot\tools\legacy_plan_data.py" -Destination "$UFC4Path\tools\legacy_plan_data.py" -Force
Copy-Item "$patchRoot\tools\legacy_plan_p1.py" -Destination "$UFC4Path\tools\legacy_plan_p1.py" -Force
Copy-Item "$patchRoot\tools\legacy_plan_p2.py" -Destination "$UFC4Path\tools\legacy_plan_p2.py" -Force
Copy-Item "$patchRoot\tools\legacy_plan_p3.py" -Destination "$UFC4Path\tools\legacy_plan_p3.py" -Force
Copy-Item "$patchRoot\tools\legacy_plan_p4.py" -Destination "$UFC4Path\tools\legacy_plan_p4.py" -Force

if (Test-Path "$patchRoot\bbport.ini") {
    Copy-Item "$patchRoot\bbport.ini" -Destination "$UFC4Path\bbport.ini" -Force
}

Write-Host "`nPatch UFC 4 Ivy Bridge berhasil dipasang ke '$UFC4Path'!" -ForegroundColor Green
Write-Host "Langkah selanjutnya:"
Write-Host "1. Pastikan environment variable diset untuk CPU Ivy Bridge:"
Write-Host "   setx BB_SKIP_CPU_CHECK 1"
Write-Host "2. Jalankan game: UFC4.exe atau bash run.sh"
