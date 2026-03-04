@echo off
echo Configuring Git...
git config --global user.email "crajkumarsingh@hotmail.com"
git config --global user.name "RAJKUMAR SINGH CHAUHAN"

echo.
echo Checking Git status...
git status

echo.
echo Adding files...
git add .

echo.
echo Committing changes...
git commit -m "feat: Add dirt wall to foundation plan and fix abutment labels"

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo Done!
pause
