# Simple BridgeGAD Repository Synchronization
Write-Host "Synchronizing all BridgeGAD repositories..." -ForegroundColor Green

$repos = @("BridgeGAD-00", "BridgeGAD-01", "BridgeGAD-02", "BridgeGAD-03", "BridgeGAD-04", "BridgeGAD-05", "BridgeGAD-06", "BridgeGAD-07", "BridgeGAD-08", "BridgeGAD-09", "BridgeGAD-10", "BridgeGAD-11", "BridgeGAD-12")
$base = "C:\Users\Rajkumar"
$success = 0
$failed = 0

foreach ($repo in $repos) {
    $path = "$base\$repo"
    Write-Host "`nProcessing: $repo"
    
    if (Test-Path $path) {
        if (Test-Path "$path\.git") {
            try {
                Set-Location $path
                
                # Configure Git
                git config user.name "RAJKUMAR SINGH CHAUHAN"
                git config user.email "crajkumarsingh@hotmail.com"
                
                # Check status and sync
                $status = git status --porcelain
                if ($status) {
                    git add .
                    git commit -m "Repository synchronization update"
                }
                
                # Try to pull and push
                git fetch origin 2>$null
                git pull origin main 2>$null
                git push origin main 2>$null
                
                Write-Host "  Synchronized: $repo" -ForegroundColor Green
                $success++
            }
            catch {
                Write-Host "  Failed: $repo - $_" -ForegroundColor Red
                $failed++
            }
        } else {
            Write-Host "  Not a git repo: $repo" -ForegroundColor Yellow
            $failed++
        }
    } else {
        Write-Host "  Not found: $repo" -ForegroundColor Red
        $failed++
    }
}

Set-Location "C:\Users\Rajkumar\BridgeGAD-00"
Write-Host "`nSynchronization complete!"
Write-Host "Success: $success, Failed: $failed"