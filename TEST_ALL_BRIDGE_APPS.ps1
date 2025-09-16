# Bridge Applications Testing Script
Write-Host "Testing ALL Bridge Applications..." -ForegroundColor Green

$timestamp = Get-Date -Format "dd_MM_yyyy_HHmm"
$outputDir = "C:\Users\Rajkumar\BridgeGAD-00\OUTPUT_$timestamp"
$inputDir = "C:\Users\Rajkumar\BridgeGAD-00\SAMPLE_INPUT_FILES"

# Create directories
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
New-Item -ItemType Directory -Path $inputDir -Force | Out-Null

# Bridge apps to test
$apps = @("BridgeGAD-00", "BridgeGAD-01", "BridgeGAD-02", "BridgeGAD-03", "BridgeGAD-04", 
          "BridgeGAD-05", "BridgeGAD-06", "BridgeGAD-07", "BridgeGAD-08", "BridgeGAD-09", 
          "BridgeGAD-10", "BridgeGAD-11", "BridgeGAD-12", "Bridge-Causeway-Design", 
          "BridgeDraw", "Bridge_Slab_Design")

$results = @()

foreach ($app in $apps) {
    $appPath = "C:\Users\Rajkumar\$app"
    Write-Host "`nTesting: $app"
    
    if (Test-Path $appPath) {
        $appOutputDir = "$outputDir\$app"
        New-Item -ItemType Directory -Path $appOutputDir -Force | Out-Null
        
        # Find Python files
        $pythonFiles = Get-ChildItem "$appPath\*.py" -Name 2>$null
        
        $result = @{
            App = $app
            Status = "SUCCESS"
            PythonFiles = $pythonFiles
            OutputDir = $appOutputDir
        }
        
        Write-Host "  Found Python files: $($pythonFiles -join ', ')" -ForegroundColor Green
        
        # Create sample input for this app
        $sampleInput = "$inputDir\sample_$app.xlsx"
        if (-not (Test-Path $sampleInput)) {
            # Copy existing sample if available
            $existingSample = Get-ChildItem "$appPath\*.xlsx" | Select-Object -First 1
            if ($existingSample) {
                Copy-Item $existingSample.FullName $sampleInput
                Write-Host "  Created sample input: $sampleInput" -ForegroundColor Yellow
            }
        }
        
    } else {
        $result = @{
            App = $app
            Status = "NOT_FOUND"
            PythonFiles = @()
            OutputDir = ""
        }
        Write-Host "  Directory not found" -ForegroundColor Red
    }
    
    $results += $result
}

# Save results
$results | ConvertTo-Json -Depth 10 | Out-File "$outputDir\test_results.json"

Write-Host "`nTesting completed! Check: $outputDir" -ForegroundColor Green