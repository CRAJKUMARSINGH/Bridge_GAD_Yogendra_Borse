# Deploy BAT files and documentation to all BridgeGAD applications
Write-Host "Deploying BAT files and documentation..." -ForegroundColor Green

$bridgeGadApps = @("BridgeGAD-01", "BridgeGAD-02", "BridgeGAD-03", "BridgeGAD-04", "BridgeGAD-05", "BridgeGAD-06", "BridgeGAD-07", "BridgeGAD-08", "BridgeGAD-09", "BridgeGAD-10", "BridgeGAD-11", "BridgeGAD-12")
$baseDir = "C:\Users\Rajkumar"
$sourceDir = "C:\Users\Rajkumar\BridgeGAD-00"

foreach ($app in $bridgeGadApps) {
    $appPath = Join-Path $baseDir $app
    Write-Host "Processing: $app"
    
    if (Test-Path $appPath) {
        # Copy ONE_CLICK_START.bat
        $sourceBat = Join-Path $sourceDir "ONE_CLICK_START_TEMPLATE.bat"
        $destBat = Join-Path $appPath "ONE_CLICK_START.bat"
        Copy-Item $sourceBat $destBat -Force
        
        # Copy HOW_TO_USE.md
        $sourceDoc = Join-Path $sourceDir "HOW_TO_USE_TEMPLATE.md"
        $destDoc = Join-Path $appPath "HOW_TO_USE.md"
        Copy-Item $sourceDoc $destDoc -Force
        
        Write-Host "  Deployed to $app" -ForegroundColor Green
    } else {
        Write-Host "  Directory not found: $appPath" -ForegroundColor Red
    }
}

Write-Host "Deployment completed!" -ForegroundColor Green