param (
    [string]$Path = "."
)

Write-Host "🏷️  Hunting for hardcoded labels in: $Path"

# Regex to find double-quoted strings that don't look like typical code strings
# Very basic heuristic: looks for "Text with spaces" or "Capitalized Text"
# Ignored: empty strings, single words (might be map keys), all caps (might be consts)

Get-ChildItem -Path $Path -Recurse -Include *.xml,*.xpp | ForEach-Object {
    $content = Get-Content $_.FullName
    $lineNum = 0
    $content | ForEach-Object {
        $lineNum++
        $line = $_
        
        # Match "String Like This" but not "@Labels" or "ClassNames"
        if ($line -match '"[A-Z][a-z]+ [A-Za-z0-9 ]+"') {
            Write-Host "[$($_.Name):$lineNum] Possible hardcoded: $line" -ForegroundColor Yellow
        }
    }
}
