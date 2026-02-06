param(
    [string]$FilePath
)

if ([string]::IsNullOrEmpty($FilePath)) {
    Write-Host "Usage: .\pbix_extract.ps1 <PathTo.pbix>" -ForegroundColor Red
    exit
}

$ZipPath = $FilePath -replace '.pbix$', '.zip'
Write-Host "📦 Copying to $ZipPath..."
Copy-Item $FilePath $ZipPath

$Dest = $FilePath + "_extracted"
Write-Host "📂 Extracting to $Dest..."

Expand-Archive $ZipPath -DestinationPath $Dest -Force

Write-Host "✅ Done. You can now inspect 'Layout', 'DataMashup', and 'SecurityBindings'."
Remove-Item $ZipPath
