# Original preview helper. Downloads licensed upstream sources only into ignored build/.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$fontOutput = Join-Path $projectRoot 'build/fonts'
New-Item -ItemType Directory -Path $fontOutput -Force | Out-Null
Invoke-WebRequest 'https://software.sil.org/downloads/r/gentium/GentiumBook-7.000.zip' -OutFile (Join-Path $fontOutput 'GentiumBook-7.000.zip')
Expand-Archive -LiteralPath (Join-Path $fontOutput 'GentiumBook-7.000.zip') -DestinationPath (Join-Path $fontOutput 'gentium') -Force
$downloads = @{
    'Alegreya.ttf' = 'https://raw.githubusercontent.com/google/fonts/main/ofl/alegreya/Alegreya%5Bwght%5D.ttf'
    'SourceSans3.ttf' = 'https://raw.githubusercontent.com/google/fonts/main/ofl/sourcesans3/SourceSans3%5Bwght%5D.ttf'
    'alegreya-OFL.txt' = 'https://raw.githubusercontent.com/google/fonts/main/ofl/alegreya/OFL.txt'
    'sourcesans3-OFL.txt' = 'https://raw.githubusercontent.com/google/fonts/main/ofl/sourcesans3/OFL.txt'
}
foreach ($download in $downloads.GetEnumerator()) {
    Invoke-WebRequest $download.Value -OutFile (Join-Path $fontOutput $download.Key)
}
$expected = @{
    'Alegreya.ttf' = 'BA5564634B93A8F8BA57B48CD4F1AE7417D2B4656FBAC779028679B00DE3CF12'
    'SourceSans3.ttf' = '042FE2CC0B933E328410D7ACBD0AA6A1873DCA5AEF81875F4BC214B08825C7B9'
    'gentium/GentiumBook-7.000/GentiumBook-Regular.ttf' = '2027F6A864E5A9907C113438969D1D03FA91DFDD1A3885FA0FDEB496F0F682E4'
    'gentium/GentiumBook-7.000/GentiumBook-Bold.ttf' = 'ED788447EA4298DD44AC62034B9A6849003BDFEA256757CB4A5D599C8B09A365'
}
foreach ($entry in $expected.GetEnumerator()) {
    if ((Get-FileHash -LiteralPath (Join-Path $fontOutput $entry.Key) -Algorithm SHA256).Hash -ne $entry.Value) {
        throw "Upstream font changed: $($entry.Key). Review the new version and license before previewing."
    }
}
Write-Output 'Preview fonts downloaded and hashes verified. No system fonts installed.'
