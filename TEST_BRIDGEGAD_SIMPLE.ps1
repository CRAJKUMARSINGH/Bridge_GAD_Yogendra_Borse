# Testing Script for BridgeGAD Applications
Write-Host "Testing BridgeGAD Applications..." -ForegroundColor Green

$bridgeGadApps = @("BridgeGAD-00", "BridgeGAD-01", "BridgeGAD-02", "BridgeGAD-03")
$baseDir = "C:\Users\Rajkumar"
$testResults = @()

foreach ($app in $bridgeGadApps) {
    $appPath = Join-Path $baseDir $app
    Write-Host "Testing: $app"
    
    $result = @{
        AppName = $app
        Status = "UNKNOWN"
        Features = @()
        Issues = @()
    }
    
    if (Test-Path $appPath) {
        $result.Status = "EXISTS"
        
        # Check for Python files
        $pythonFiles = Get-ChildItem -Path $appPath -Filter "*.py" -ErrorAction SilentlyContinue
        if ($pythonFiles.Count -gt 0) {
            $result.Features += "Python: $($pythonFiles.Count) files"
        }
        
        # Check for BAT files
        $batFiles = Get-ChildItem -Path $appPath -Filter "*.bat" -ErrorAction SilentlyContinue
        if ($batFiles.Count -gt 0) {
            $result.Features += "BAT: $($batFiles.Count) files"
        } else {
            $result.Issues += "No BAT files"
        }
        
        # Check for README
        $readmeFiles = Get-ChildItem -Path $appPath -Filter "README*.md" -ErrorAction SilentlyContinue
        if ($readmeFiles.Count -gt 0) {
            $result.Features += "Documentation: $($readmeFiles.Count) files"
        } else {
            $result.Issues += "No README"
        }
        
    } else {
        $result.Status = "NOT_FOUND"
        $result.Issues += "Directory not found"
    }
    
    $testResults += $result
}

# Save results
$reportPath = "C:\Users\Rajkumar\BridgeGAD-00\TEST_RESULTS.json"
$testResults | ConvertTo-Json -Depth 5 | Out-File -FilePath $reportPath

Write-Host "Test completed. Results saved to: $reportPath"