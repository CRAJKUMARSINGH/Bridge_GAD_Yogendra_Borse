# Comprehensive Git Synchronization Script for All BridgeGAD Repositories
# Author: Rajkumar Singh Chauhan
# Email: crajkumarsingh@hotmail.com

Write-Host "🔄 SYNCHRONIZING ALL BRIDGEGAD REPOSITORIES" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green

# Initialize counters and results
$syncResults = @()
$totalRepos = 0
$successfulSync = 0
$failedSync = 0
$reposWithChanges = 0
$reposUpToDate = 0

# Git configuration from memory
$gitUserName = "RAJKUMAR SINGH CHAUHAN"
$gitUserEmail = "crajkumarsingh@hotmail.com"

# Discover all BridgeGAD repositories
$bridgeGadRepos = Get-ChildItem C:\Users\Rajkumar -Directory | Where-Object {$_.Name -like "BridgeGAD*"}
$totalRepos = $bridgeGadRepos.Count

Write-Host "`n📋 Found $totalRepos BridgeGAD repositories" -ForegroundColor Yellow
Write-Host "Git Configuration: $gitUserName <$gitUserEmail>" -ForegroundColor Blue
Write-Host ""

foreach ($repo in $bridgeGadRepos) {
    $repoName = $repo.Name
    $repoPath = $repo.FullName
    
    Write-Host "🔧 Processing: $repoName" -ForegroundColor Cyan
    Write-Host "   Path: $repoPath" -ForegroundColor Gray
    
    $repoResult = @{
        Name = $repoName
        Path = $repoPath
        IsGitRepo = $false
        HasRemote = $false
        Status = "UNKNOWN"
        Changes = 0
        Issues = @()
        Actions = @()
    }
    
    # Change to repository directory
    Push-Location $repoPath
    try {
        # Check if it's a Git repository
        $gitDir = Join-Path $repoPath ".git"
        if (Test-Path $gitDir) {
            $repoResult.IsGitRepo = $true
            Write-Host "   ✅ Git repository detected" -ForegroundColor Green
            
            # Configure Git user credentials
            try {
                git config user.name $gitUserName
                git config user.email $gitUserEmail
                Write-Host "   🔧 Git credentials configured" -ForegroundColor Green
                $repoResult.Actions += "Git credentials configured"
            }
            catch {
                Write-Host "   ⚠️  Failed to configure Git credentials: $_" -ForegroundColor Yellow
                $repoResult.Issues += "Git config failed: $_"
            }
            
            # Check for remote repository
            try {
                $remotes = git remote
                if ($remotes) {
                    $repoResult.HasRemote = $true
                    $remoteUrl = git remote get-url origin 2>$null
                    if ($remoteUrl) {
                        Write-Host "   🌐 Remote repository: $remoteUrl" -ForegroundColor Green
                        $repoResult.Actions += "Remote detected: $remoteUrl"
                    }
                } else {
                    Write-Host "   ⚠️  No remote repository configured" -ForegroundColor Yellow
                    $repoResult.Issues += "No remote repository"
                }
            }
            catch {
                Write-Host "   ⚠️  Error checking remote: $_" -ForegroundColor Yellow
                $repoResult.Issues += "Remote check failed: $_"
            }
            
            # Check repository status
            try {
                $statusOutput = git status --porcelain
                $repoResult.Changes = if ($statusOutput) { ($statusOutput | Measure-Object).Count } else { 0 }
                
                if ($repoResult.Changes -gt 0) {
                    Write-Host "   📝 Found $($repoResult.Changes) uncommitted changes" -ForegroundColor Yellow
                    $reposWithChanges++
                    
                    # Add all changes
                    git add .
                    Write-Host "   ➕ Staged all changes" -ForegroundColor Green
                    $repoResult.Actions += "Staged $($repoResult.Changes) changes"
                    
                    # Commit changes
                    $commitMessage = "🔄 Repository synchronization - Auto-commit by sync script`n`nSynchronized as part of BridgeGAD portfolio maintenance`nBy: $gitUserName`nEmail: $gitUserEmail"
                    git commit -m $commitMessage
                    Write-Host "   💾 Committed changes" -ForegroundColor Green
                    $repoResult.Actions += "Committed changes with sync message"
                } else {
                    Write-Host "   ✅ Repository is clean (no uncommitted changes)" -ForegroundColor Green
                    $reposUpToDate++
                }
            }
            catch {
                Write-Host "   ❌ Error processing repository status: $_" -ForegroundColor Red
                $repoResult.Issues += "Status check failed: $_"
            }
            
            # Fetch latest changes from remote
            if ($repoResult.HasRemote) {
                try {
                    Write-Host "   🔄 Fetching from remote..." -ForegroundColor Yellow
                    git fetch origin
                    Write-Host "   ✅ Fetch completed" -ForegroundColor Green
                    $repoResult.Actions += "Fetched from remote"
                }
                catch {
                    Write-Host "   ⚠️  Fetch failed: $_" -ForegroundColor Yellow
                    $repoResult.Issues += "Fetch failed: $_"
                }
                
                # Check if local is behind remote
                try {
                    $behindCount = git rev-list --count HEAD..origin/main 2>$null
                    if ($behindCount -and $behindCount -gt 0) {
                        Write-Host "   📥 Local is $behindCount commits behind remote, pulling..." -ForegroundColor Yellow
                        git pull origin main
                        Write-Host "   ✅ Pull completed" -ForegroundColor Green
                        $repoResult.Actions += "Pulled $behindCount commits from remote"
                    }
                }
                catch {
                    Write-Host "   ⚠️  Pull check/operation failed: $_" -ForegroundColor Yellow
                    $repoResult.Issues += "Pull failed: $_"
                }
                
                # Push any local changes
                try {
                    $aheadCount = git rev-list --count origin/main..HEAD 2>$null
                    if ($aheadCount -and $aheadCount -gt 0) {
                        Write-Host "   📤 Local is $aheadCount commits ahead, pushing..." -ForegroundColor Yellow
                        git push origin main
                        Write-Host "   ✅ Push completed" -ForegroundColor Green
                        $repoResult.Actions += "Pushed $aheadCount commits to remote"
                    } elseif ($repoResult.Changes -gt 0) {
                        Write-Host "   📤 Pushing committed changes..." -ForegroundColor Yellow
                        git push origin main
                        Write-Host "   ✅ Push completed" -ForegroundColor Green
                        $repoResult.Actions += "Pushed committed changes"
                    } else {
                        Write-Host "   ✅ Repository is up to date with remote" -ForegroundColor Green
                    }
                }
                catch {
                    Write-Host "   ⚠️  Push failed: $_" -ForegroundColor Yellow
                    $repoResult.Issues += "Push failed: $_"
                }
            }
            
            # Determine final status
            if ($repoResult.Issues.Count -eq 0) {
                $repoResult.Status = "SUCCESS"
                $successfulSync++
                Write-Host "   🎉 Synchronization: SUCCESS" -ForegroundColor Green
            } else {
                $repoResult.Status = "PARTIAL_SUCCESS"
                $successfulSync++
                Write-Host "   ✅ Synchronization: PARTIAL SUCCESS" -ForegroundColor Yellow
            }
            
        } else {
            Write-Host "   ❌ Not a Git repository" -ForegroundColor Red
            $repoResult.Status = "NOT_GIT_REPO"
            $repoResult.Issues += "Not a Git repository"
            $failedSync++
        }
    }
    catch {
        Write-Host "   ❌ Critical error: $_" -ForegroundColor Red
        $repoResult.Status = "CRITICAL_ERROR"
        $repoResult.Issues += "Critical error: $_"
        $failedSync++
    }
    finally {
        Pop-Location
    }
    
    $syncResults += $repoResult
    Write-Host ""
}

# Generate comprehensive summary
Write-Host "🎉 SYNCHRONIZATION COMPLETED!" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green

Write-Host "`n📊 SUMMARY STATISTICS:" -ForegroundColor Yellow
Write-Host "   Total Repositories: $totalRepos" -ForegroundColor White
Write-Host "   Successful Sync: $successfulSync" -ForegroundColor Green
Write-Host "   Failed Sync: $failedSync" -ForegroundColor Red
Write-Host "   Repositories with Changes: $reposWithChanges" -ForegroundColor Yellow
Write-Host "   Repositories Up-to-Date: $reposUpToDate" -ForegroundColor Green
Write-Host "   Success Rate: $(($successfulSync/$totalRepos*100).ToString('F1'))%" -ForegroundColor Cyan

Write-Host "`n📋 DETAILED RESULTS:" -ForegroundColor Yellow
foreach ($result in $syncResults) {
    $statusColor = switch ($result.Status) {
        "SUCCESS" { "Green" }
        "PARTIAL_SUCCESS" { "Yellow" }
        "NOT_GIT_REPO" { "DarkYellow" }
        "CRITICAL_ERROR" { "Red" }
        default { "Gray" }
    }
    
    Write-Host "`n   🔧 $($result.Name): $($result.Status)" -ForegroundColor $statusColor
    
    if ($result.Actions.Count -gt 0) {
        Write-Host "      ✅ Actions Performed:" -ForegroundColor Green
        foreach ($action in $result.Actions) {
            Write-Host "         - $action" -ForegroundColor Gray
        }
    }
    
    if ($result.Issues.Count -gt 0) {
        Write-Host "      ⚠️  Issues Encountered:" -ForegroundColor Yellow
        foreach ($issue in $result.Issues) {
            Write-Host "         - $issue" -ForegroundColor Gray
        }
    }
}

# Save detailed results to file
$reportPath = "C:\Users\Rajkumar\BridgeGAD-00\SYNC_RESULTS_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$syncResults | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportPath -Encoding UTF8

Write-Host "`n💾 Detailed sync results saved to:" -ForegroundColor Blue
Write-Host "   $reportPath" -ForegroundColor Gray

Write-Host "`n🎯 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "   1. Review any repositories with issues" -ForegroundColor White
Write-Host "   2. Set up remote repositories for repos without remotes" -ForegroundColor White
Write-Host "   3. Verify all changes have been properly synchronized" -ForegroundColor White
Write-Host "   4. Consider setting up automated sync schedules" -ForegroundColor White

Write-Host "`n✅ All BridgeGAD repositories have been processed!" -ForegroundColor Green
Write-Host "By: $gitUserName ($gitUserEmail)" -ForegroundColor Green