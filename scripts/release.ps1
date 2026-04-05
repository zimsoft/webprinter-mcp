param(
    [switch]$Upload
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "python is not available on PATH. Install Python 3.10+ first."
}

python -m pip install --upgrade pip
python -m pip install build twine

if (Test-Path dist) {
    Remove-Item -Recurse -Force dist
}

if (Test-Path build) {
    Remove-Item -Recurse -Force build
}

Get-ChildItem -Path . -Filter *.egg-info -Force | Remove-Item -Recurse -Force

python -m build
python -m twine check dist/*

if ($Upload) {
    python -m twine upload dist/*
} else {
    Write-Host "Build complete. Artifacts are in dist/ ."
    Write-Host "Run .\\scripts\\release.ps1 -Upload to publish to PyPI."
}
