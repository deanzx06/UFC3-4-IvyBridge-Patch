param (
    [Parameter(Mandatory=$true)]
    [string]$UFC3Path
)

if (-not (Test-Path "$UFC3Path\scripts")) {
    Write-Error "Folder '$UFC3Path' bukan direktori UFC-3-PS4-PORT yang valid (folder scripts tidak ditemukan)."
    exit 1
}

$patchRoot = $PSScriptRoot

Write-Host "[1/6] Menyalin scripts/cpu_compat.py (Sandy Bridge + Ivy Bridge)..." -ForegroundColor Cyan
Copy-Item "$patchRoot\scripts\cpu_compat.py" -Destination "$UFC3Path\scripts\cpu_compat.py" -Force

Write-Host "[2/6] Menyalin scripts/link_modules.py..." -ForegroundColor Cyan
Copy-Item "$patchRoot\scripts\link_modules.py" -Destination "$UFC3Path\scripts\link_modules.py" -Force

Write-Host "[3/6] Menyalin tools/build_cpu_compat.py..." -ForegroundColor Cyan
if (-not (Test-Path "$UFC3Path\tools")) { New-Item -ItemType Directory -Path "$UFC3Path\tools" | Out-Null }
Copy-Item "$patchRoot\tools\build_cpu_compat.py" -Destination "$UFC3Path\tools\build_cpu_compat.py" -Force

Write-Host "[4/6] Menyalin Sandy Bridge translation plan (6,486 sites: BMI1 + MOVBE + LZCNT + F16C)..." -ForegroundColor Cyan
Copy-Item "$patchRoot\tools\legacy_plan_data.py" -Destination "$UFC3Path\tools\legacy_plan_data.py" -Force
Copy-Item "$patchRoot\tools\legacy_plan_p1.py" -Destination "$UFC3Path\tools\legacy_plan_p1.py" -Force
Copy-Item "$patchRoot\tools\legacy_plan_p2.py" -Destination "$UFC3Path\tools\legacy_plan_p2.py" -Force
Copy-Item "$patchRoot\tools\legacy_plan_p3.py" -Destination "$UFC3Path\tools\legacy_plan_p3.py" -Force

Write-Host "[5/6] Menyalin unit test suite..." -ForegroundColor Cyan
if (-not (Test-Path "$UFC3Path\tests")) { New-Item -ItemType Directory -Path "$UFC3Path\tests" | Out-Null }
Copy-Item "$patchRoot\tests\test_cpu_compat.py" -Destination "$UFC3Path\tests\test_cpu_compat.py" -Force

Write-Host "[6/6] Memastikan bbport.ini terpasang..." -ForegroundColor Cyan
if (Test-Path "$patchRoot\bbport.ini") {
    Copy-Item "$patchRoot\bbport.ini" -Destination "$UFC3Path\bbport.ini" -Force
}

Write-Host "`nPatch Sandy Bridge v2 berhasil dipasang ke '$UFC3Path'!" -ForegroundColor Green
Write-Host "Langkah selanjutnya:"
Write-Host "1. Pastikan environment variable diset untuk melewati pengecekan CPU lama:"
Write-Host "   setx BB_SKIP_CPU_CHECK 1"
Write-Host "2. Jalankan game: UFC3.exe atau bash run.sh"
