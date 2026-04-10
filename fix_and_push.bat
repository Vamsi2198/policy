@echo off
echo Removing sensitive files...

REM Remove SSH key files
if exist ssh_key del ssh_key
if exist ssh_key.pub del ssh_key.pub

echo Staging changes...
git add .

echo Committing changes...
git commit -m "Remove sensitive SSH keys and replace hardcoded API keys with environment variables"

echo Pushing to GitHub...
git push -u origin main

echo Done!