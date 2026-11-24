param([string]$Dist = 'dist', [int]$Repeticiones = 10, [string]$Salida = 'diagnosticos')
# INC-031: repite el diagnóstico del portable. Las iteraciones impares son en frío (descompresión nueva y perfil
# WebView2 nuevo mediante LOCALAPPDATA propio); las pares reutilizan el perfil. Falla si alguna no termina bien.
$ErrorActionPreference = 'Stop'
$Dist = (Resolve-Path -LiteralPath $Dist).Path
$version = (python -c "from src.core.version import VERSION; print(VERSION)").Trim()
$zip = Join-Path $Dist "CalculadoraAlgebraLineal-$version-windows-x64-portable.zip"
New-Item -ItemType Directory -Force -Path $Salida | Out-Null
$Salida = (Resolve-Path -LiteralPath $Salida).Path
$raiz = Join-Path ([IO.Path]::GetTempPath()) ('calculadora-repeticion-' + [guid]::NewGuid())
$localOriginal = $env:LOCALAPPDATA
$filas = @(); $fallos = 0
try {
    for ($i = 1; $i -le $Repeticiones; $i++) {
        $frio = ($i % 2) -eq 1
        if ($frio) {
            $carpeta = Join-Path $raiz "n$i"
            Expand-Archive -LiteralPath $zip -DestinationPath $carpeta
            $env:LOCALAPPDATA = Join-Path $raiz "perfil$i"
            New-Item -ItemType Directory -Path $env:LOCALAPPDATA | Out-Null
        }
        $exe = Join-Path $carpeta 'CalculadoraAlgebraLineal\CalculadoraAlgebraLineal.exe'
        $informe = Join-Path $Salida ("diagnostico-{0:d2}-{1}.json" -f $i, $(if ($frio) { 'frio' } else { 'caliente' }))
        $reloj = [Diagnostics.Stopwatch]::StartNew()
        $p = Start-Process -FilePath $exe -ArgumentList @('--diagnostico', ('"' + $informe + '"')) -WindowStyle Hidden -PassThru
        $termino = $p.WaitForExit(180000)
        if (-not $termino) { $p.Kill() }
        $reloj.Stop()
        $r = if (Test-Path -LiteralPath $informe) { Get-Content -LiteralPath $informe -Raw | ConvertFrom-Json } else { $null }
        $ok = $termino -and $p.ExitCode -eq 0 -and $r -and $r.ok
        if (-not $ok) { $fallos++ }
        $filas += [pscustomobject]@{
            n = $i; modo = $(if ($frio) { 'frío' } else { 'caliente' }); ok = [bool]$ok
            codigo = $(if ($termino) { $p.ExitCode } else { 'tiempo' }); proceso_s = [math]::Round($reloj.Elapsed.TotalSeconds, 1)
            carga_s = $r.tiempos.carga_s; total_s = $r.tiempos.total_s; error = $r.error
        }
    }
} finally {
    $env:LOCALAPPDATA = $localOriginal
}
$filas | Format-Table -AutoSize | Out-String -Width 200 | Write-Output
$filas | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $Salida 'resumen.json') -Encoding utf8
Get-Process -Name CalculadoraAlgebraLineal, msedgewebview2 -ErrorAction SilentlyContinue |
    Select-Object Name, Id | Format-Table | Out-String | Write-Output
if ($fallos) { throw "$fallos de $Repeticiones diagnósticos fallaron" }
