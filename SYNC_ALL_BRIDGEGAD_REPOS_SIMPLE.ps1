# Simple Git Synchronization Script for All BridgeGAD Repositories
Write-Host "Synchronizing All BridgeGAD Repositories..." -ForegroundColor Green

$gitUserName = "RAJKUMAR SINGH CHAUHAN"
$gitUserEmail = "crajkumarsingh@hotmail.com"
$syncResults = @()
$successCount = 0
$errorCount = 0

# Get all BridgeGAD repositories
$bridgeGadRepos = Get-ChildItem C:\Users\Rajkumar -Directory | Where-Object {$_.Name -like "BridgeGAD*"}

Write-Host "Found $($bridgeGadRepos.Count) BridgeGAD repositories"
Write-Host ""

foreach ($repo in $bridgeGadRepos) {
    $repoName = $repo.Name
    $repoPath = $repo.FullName
    
    Write-Host "Processing: $repoName" -ForegroundColor Cyan
    
    $result = @{
        Name = $repoName
        Status = "SUCCESS"
        Actions = @()
        Issues = @()
    }
    
    Push-Location $repoPath
    try {
        # Check if Git repository
        if (Test-Path ".git") {
            Write-Host "  Git repository detected"
            
            # Configure Git
            git config user.name $gitUserName
            git config user.email $gitUserEmail
            Write-Host "  Git credentials configured"
            $result.Actions += "Git credentials configured"
            
            # Check status and commit if needed
            $status = git status --porcelain
            if ($status) {
                $changeCount = ($status | Measure-Object).Count
                Write-Host "  Found $changeCount changes, committing..."
                git add .
                git commit -m "Auto-sync: Repository synchronization by $gitUserName"
                $result.Actions += "Committed $changeCount changes"
            } else {
                Write-Host "  Repository is clean"
            }
            
            # Check for remote and sync
            $remotes = git remote
            if ($remotes -contains "origin") {
                Write-Host "  Syncing with remote..."
                
                # Fetch latest
                git fetch origin 2>$null
                $result.Actions += "Fetched from remote"
                
                # Pull if needed
                $pullResult = git pull origin main 2>$null
                if ($LASTEXITCODE -eq 0) {
                    $result.Actions += "Pulled from remote"
                }
                
                # Push changes
                $pushResult = git push origin main 2>$null
                if ($LASTEXITCODE -eq 0) {
                    $result.Actions += "Pushed to remote"
                    Write-Host "  Successfully synced with remote" -ForegroundColor Green
                } else {
                    Write-Host "  Warning: Push may have failed" -ForegroundColor Yellow
                    $result.Issues += "Push may have failed"
                }
            } else {
                Write-Host "  No remote repository configured" -ForegroundColor Yellow
                $result.Issues += "No remote repository"
            }
            
            $successCount++
        } else {
            Write-Host "  Not a Git repository" -ForegroundColor Red
            $result.Status = "ERROR"
            $result.Issues += "Not a Git repository"
            $errorCount++
        }
    }
    catch {
        Write-Host "  Error: $_" -ForegroundColor Red
        $result.Status = "ERROR"
        $result.Issues += "Error: $_"
        $errorCount++
    }
    finally {
        Pop-Location
    }
    
    $syncResults += $result
    Write-Host ""
}

# Summary
Write-Host "SYNCHRONIZATION COMPLETE!" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host "Total Repositories: $($bridgeGadRepos.Count)"
Write-Host "Successful: $successCount" -ForegroundColor Green
Write-Host "Errors: $errorCount" -ForegroundColor Red
Write-Host "Success Rate: $(($successCount/($bridgeGadRepos.Count)*100).ToString('F1'))%"

# Save results
$reportPath = "C:\Users\Rajkumar\BridgeGAD-00\SYNC_RESULTS.json"
$syncResults | ConvertTo-Json -Depth 5 | Out-File -FilePath $reportPath
Write-Host "Results saved to: $reportPath"

Write-Host "All BridgeGAD repositories processed!" -ForegroundColor Green