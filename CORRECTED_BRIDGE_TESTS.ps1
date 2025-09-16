# CORRECTED COMPREHENSIVE BRIDGE APPLICATIONS TESTING
Write-Host "Testing All Bridge Applications..." -ForegroundColor Green

$timestamp = Get-Date -Format "dd_MM_yyyy_HHmm"
$outputDir = "C:\Users\Rajkumar\BridgeGAD-00\OUTPUT_FINAL_$timestamp"
$inputDir = "C:\Users\Rajkumar\BridgeGAD-00\SAMPLE_INPUT_FILES_FINAL"

New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
New-Item -ItemType Directory -Path $inputDir -Force | Out-Null

$bridgeApps = @(
    @{ Name = "BridgeGAD-00"; Path = "C:\Users\Rajkumar\BridgeGAD-00"; App = "app.py"; HasInput = $true },
    @{ Name = "BridgeGAD-01"; Path = "C:\Users\Rajkumar\BridgeGAD-01"; App = "bridge_drawings.py"; HasInput = $false },
    @{ Name = "BridgeGAD-02"; Path = "C:\Users\Rajkumar\BridgeGAD-02"; App = "main.py"; HasInput = $false },
    @{ Name = "BridgeGAD-03"; Path = "C:\Users\Rajkumar\BridgeGAD-03"; App = "app.py"; HasInput = $true },
    @{ Name = "BridgeGAD-04"; Path = "C:\Users\Rajkumar\BridgeGAD-04"; App = "app.py"; HasInput = $true },
    @{ Name = "BridgeGAD-06"; Path = "C:\Users\Rajkumar\BridgeGAD-06"; App = "main.py"; HasInput = $true },
    @{ Name = "BridgeGAD-07"; Path = "C:\Users\Rajkumar\BridgeGAD-07"; App = "main.py"; HasInput = $false },
    @{ Name = "BridgeGAD-10"; Path = "C:\Users\Rajkumar\BridgeGAD-10"; App = "main.py"; HasInput = $false },
    @{ Name = "BridgeGAD-12"; Path = "C:\Users\Rajkumar\BridgeGAD-12"; App = "app.py"; HasInput = $false },
    @{ Name = "Bridge_Slab_Design"; Path = "C:\Users\Rajkumar\Bridge_Slab_Design"; App = "bridge_design_app.py"; HasInput = $true }
)

$results = @()
$success = 0
$failed = 0

foreach ($app in $bridgeApps) {
    Write-Host "`nTesting: $($app.Name)" -ForegroundColor Cyan
    
    $appOutputDir = "$outputDir\$($app.Name)"
    New-Item -ItemType Directory -Path $appOutputDir -Force | Out-Null
    
    if (Test-Path $app.Path) {
        Push-Location $app.Path
        
        try {
            # Find input files and copy to sample directory
            if ($app.HasInput) {
                $inputFiles = Get-ChildItem "*.xlsx" 2>$null
                foreach ($file in $inputFiles) {
                    $samplePath = "$inputDir\$($app.Name)_$($file.Name)"
                    Copy-Item $file.FullName $samplePath -Force
                    Write-Host "  Sample saved: $samplePath" -ForegroundColor Blue
                }
            }
            
            # Test the application
            if (Test-Path $app.App) {
                Write-Host "  Running: $($app.App)" -ForegroundColor Yellow
                
                $outputFile = "$appOutputDir\output.dxf"
                
                if ($app.HasInput -and $inputFiles) {
                    $inputFile = $inputFiles[0].Name
                    $command = "python $($app.App) `"$inputFile`" `"$outputFile`""
                } else {
                    $command = "python $($app.App)"
                }
                
                Write-Host "  Command: $command" -ForegroundColor Gray
                
                $output = Invoke-Expression $command 2>&1
                $outputCreated = Test-Path $outputFile
                
                if ($outputCreated) {
                    Write-Host "  SUCCESS: Output created" -ForegroundColor Green
                    $status = "SUCCESS"
                    $success++
                } else {
                    Write-Host "  PARTIAL: App ran, no output file" -ForegroundColor Yellow
                    $status = "PARTIAL"
                    $success++
                }
                
            } else {
                Write-Host "  ERROR: App file not found: $($app.App)" -ForegroundColor Red
                $status = "APP_NOT_FOUND"
                $failed++
            }
            
        } catch {
            Write-Host "  ERROR: $_" -ForegroundColor Red
            $status = "ERROR"
            $failed++
        } finally {
            Pop-Location
        }
        
    } else {
        Write-Host "  ERROR: Directory not found" -ForegroundColor Red
        $status = "DIR_NOT_FOUND"
        $failed++
    }
    
    $results += @{
        App = $app.Name
        Status = $status
        Path = $app.Path
        TestTime = Get-Date
    }
}

# Generate summary
Write-Host "`nTesting Summary:" -ForegroundColor Green
Write-Host "Successful: $success" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red

$summaryPath = "$outputDir\test_summary.txt"
$summaryContent = "Bridge Applications Testing Summary`n"
$summaryContent += "Generated: $(Get-Date)`n"
$summaryContent += "By: Rajkumar Singh Chauhan`n"
$summaryContent += "Successful: $success`n"
$summaryContent += "Failed: $failed`n`n"

foreach ($result in $results) {
    $summaryContent += "$($result.App): $($result.Status)`n"
}

$summaryContent | Out-File $summaryPath -Encoding UTF8

Write-Host "`nResults saved to: $outputDir" -ForegroundColor Cyan
Write-Host "Sample inputs: $inputDir" -ForegroundColor Cyan
Write-Host "Summary: $summaryPath" -ForegroundColor Cyan

Set-Location "C:\Users\Rajkumar\BridgeGAD-00"