# Simple PowerShell Script to Apply Instructions to All BridgeGAD Apps
Write-Host "Applying comprehensive instructions to all BridgeGAD applications..."

$bridgeGadApps = @("BridgeGAD-01", "BridgeGAD-02", "BridgeGAD-03", "BridgeGAD-04", "BridgeGAD-05", "BridgeGAD-06", "BridgeGAD-07", "BridgeGAD-08", "BridgeGAD-09", "BridgeGAD-10", "BridgeGAD-11", "BridgeGAD-12")
$baseDir = "C:\Users\Rajkumar"

foreach ($app in $bridgeGadApps) {
    $appPath = Join-Path $baseDir $app
    Write-Host "Processing: $app"
    
    if (Test-Path $appPath) {
        # Check for git repository
        $gitPath = Join-Path $appPath ".git"
        if (Test-Path $gitPath) {
            Push-Location $appPath
            try {
                git config user.name "RAJKUMAR SINGH CHAUHAN"
                git config user.email "crajkumarsingh@hotmail.com"
                
                $status = git status --porcelain
                if ($status) {
                    git add .
                    git commit -m "Applied comprehensive instructions from BridgeGAD-00"
                    git push origin main 2>$null
                    Write-Host "  Committed and pushed changes for $app"
                } else {
                    Write-Host "  No changes to commit for $app"
                }
            }
            catch {
                Write-Host "  Git operation failed for $app"
            }
            finally {
                Pop-Location
            }
        }
    }
}

Write-Host "Completed processing all BridgeGAD applications."