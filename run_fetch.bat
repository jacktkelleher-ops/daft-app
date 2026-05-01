@echo off
cd /d "C:\Users\jackt\Projects\daft-app"

echo [1/3] Fetching listings from Daft.ie...
C:\Users\jackt\anaconda3\python.exe fetch_daft.py
if errorlevel 1 (
    echo Fetch failed. Aborting.
    exit /b 1
)

echo [2/3] Generating HTML...
C:\Users\jackt\anaconda3\python.exe main.py 1000

echo [3/3] Pushing to GitHub...
git add docs/index.html
git diff --cached --quiet || git commit -m "chore: auto-update listings [skip ci]"
git push

echo Done!
