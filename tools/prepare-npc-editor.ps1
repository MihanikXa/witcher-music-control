param(
    [string]$Redkit = 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit',
    [string]$Uncook = 'E:\TheWitcher3RMDepot',
    [string]$Output = 'build\npc-editor'
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$target = [IO.Path]::GetFullPath((Join-Path $repo $Output))
$buildRoot = [IO.Path]::GetFullPath((Join-Path $repo 'build')) + '\'
if (-not $target.StartsWith($buildRoot, [StringComparison]::OrdinalIgnoreCase) -or (Test-Path -LiteralPath $target)) {
    throw 'Use a new directory inside repository build/'
}
if (-not (Test-Path -LiteralPath (Join-Path $Uncook 'depot_info.json'))) { throw 'Existing generated depot required' }
New-Item -ItemType Directory -Path $target | Out-Null
# Full runtime/depot copy: no junctions, moves, deletes or writes to installed files.
# assets/w3_audio is source audio, excluded from this Flash-only experiment.
foreach ($folder in @('bin', 'r4data')) {
    $copyLog = '/LOG:' + (Join-Path $target "$folder-copy.log")
    & robocopy (Join-Path $Redkit $folder) (Join-Path $target $folder) /E /COPY:DAT /DCOPY:T /R:0 /W:0 /MT:16 /NFL /NDL /NP /XF '*.log' $copyLog
    if ($LASTEXITCODE -ge 8) { throw "Copy failed for $folder with code $LASTEXITCODE" }
}
$ini = Join-Path $target 'bin\r4LavaEditor2.ini'
$raw = [IO.File]::ReadAllText($ini)
$raw = [regex]::Replace($raw, '(?m)^workspacePath=.*$', 'workspacePath=')
$raw = [regex]::Replace($raw, '(?m)^uncookPath=.*$', "uncookPath=$Uncook\")
$raw = [regex]::Replace($raw, '\r?\n', "`r`n")
[IO.File]::WriteAllText($ini, $raw)
New-Item -ItemType Directory -Path (Join-Path $target 'projects') | Out-Null
[ordered]@{
    redkit_source = $Redkit
    copied_runtime_and_r4data = $true
    source_audio_not_copied = $true
    uncook_read_only = $Uncook
    working_project_selected = $false
    editor_exe_sha256 = (Get-FileHash -LiteralPath (Join-Path $target 'bin\x64_RedKit\editor.exe')).Hash.ToLower()
    gui_with_alpha_sha256 = (Get-FileHash -LiteralPath (Join-Path $target 'r4data\engine\textures\texturegroups.xml')).Hash.ToLower()
    editor_executed = $false
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $target 'preparation.json') -Encoding utf8
Write-Output "Prepared isolated Editor at $target; no launch or import performed."
