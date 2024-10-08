@echo off
:: Change to the directory where the Hugo project is located
cd /d D:\ProgramData\junwen_blog\AquariniqueMu.github.io

:: Run Hugo to generate the static site
hugo

:: Prompt the user to enter a commit message
set /p commitMessage="Enter commit message: "

:: Stage all changes
git add .

:: Commit the changes with the provided message
git commit -m "%commitMessage%"

:: Push the changes to the main branch, force pushing
git push -f origin main
