# Simple Bridge Applications Testing
Write-Host "Testing All Bridge Applications..." -ForegroundColor Green

$timestamp = Get-Date -Format "dd_MM_yyyy_HHmm"
$outputDir = "C:\Users\Rajkumar\BridgeGAD-00\OUTPUT_$timestamp"
$inputDir = "C:\Users\Rajkumar\BridgeGAD-00\SAMPLE_INPUT_FILES"

New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
New-Item -ItemType Directory -Path $inputDir -Force | Out-Null

$apps = @(
    @{Name="BridgeGAD-00"; Path="C:\Users\Rajkumar\BridgeGAD-00"; App="app.py"},
    @{Name="BridgeGAD-01"; Path="C:\Users\Rajkumar\BridgeGAD-01"; App="bridge_drawings.py"},
    @{Name="BridgeGAD-02"; Path="C:\Users\Rajkumar\BridgeGAD-02"; App="main.py"},
    @{Name="BridgeGAD-03"; Path="C:\Users\Rajkumar\BridgeGAD-03"; App="app.py"},
    @{Name="BridgeGAD-04"; Path="C:\Users\Rajkumar\BridgeGAD-04"; App="app.py"},
    @{Name="BridgeGAD-06"; Path="C:\Users\Rajkumar\BridgeGAD-06"; App="main.py"},
    @{Name="BridgeGAD-07"; Path="C:\Users\Rajkumar\BridgeGAD-07"; App="main.py"},
    @{Name="BridgeGAD-10"; Path="C:\Users\Rajkumar\BridgeGAD-10"; App="main.py"},
    @{Name="BridgeGAD-12"; Path="C:\Users\Rajkumar\BridgeGAD-12"; App="app.py"},
    @{Name="Bridge_Slab_Design"; Path="C:\Users\Rajkumar\Bridge_Slab_Design"; App="bridge_design_app.py"}
)

$results = @()

foreach ($appInfo in $apps) {
    Write-Host "`nTesting: $($appInfo.Name)" -ForegroundColor Cyan
    
    $appOutputDir = "$outputDir\$($appInfo.Name)"
    New-Item -ItemType Directory -Path $appOutputDir -Force | Out-Null
    
    if (Test-Path $appInfo.Path) {
        Set-Location $appInfo.Path
        
        # Find input file
        $inputFile = Get-ChildItem "*.xlsx" | Select-Object -First 1
        
        if ($inputFile) {
            # Copy to sample inputs
            $samplePath = "$inputDir\sample_$($appInfo.Name).xlsx"
            Copy-Item $inputFile.FullName $samplePath -Force
            Write-Host "  Sample input saved: $samplePath"
        }
        
        # Test the application
        if (Test-Path $appInfo.App) {
            Write-Host "  Running: $($appInfo.App)"
            
            if ($inputFile) {
                $outputFile = "$appOutputDir\output.dxf"
                $cmd = "python $($appInfo.App) $($inputFile.Name) $outputFile"
            } else {
                $cmd = "python $($appInfo.App)"
            }
            
            Write-Host "  Command: $cmd" -ForegroundColor Gray
            
            try {
                Invoke-Expression $cmd
                Write-Host "  Status: SUCCESS" -ForegroundColor Green
                $status = "SUCCESS"
            } catch {
                Write-Host "  Status: ERROR - $_" -ForegroundColor Red
                $status = "ERROR"
            }
        } else {
            Write-Host "  App not found: $($appInfo.App)" -ForegroundColor Red
            $status = "APP_NOT_FOUND"
        }
    } else {
        Write-Host "  Directory not found" -ForegroundColor Red
        $status = "DIR_NOT_FOUND"
    }
    
    $results += @{
        App = $appInfo.Name
        Status = $status
        Time = Get-Date
    }
}

Set-Location "C:\Users\Rajkumar\BridgeGAD-00"

Write-Host "`nTesting completed!" -ForegroundColor Green
Write-Host "Output directory: $outputDir" -ForegroundColor Cyan
Write-Host "Sample inputs: $inputDir" -ForegroundColor Cyan

$results | ConvertTo-Json | Out-File "$outputDir\test_summary.json"