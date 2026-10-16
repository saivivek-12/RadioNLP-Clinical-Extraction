@echo off
title RadioNLP Interactive Clinical Dashboard
echo ========================================================
echo   RadioNLP: Clinical NLP Interactive System
echo   Course: 23CSE301 Machine Learning Capstone Phase 3
echo ========================================================
echo.
echo Loading clinical AI models and starting dashboard...
echo Please wait a moment...
echo.
python "%~dp0src\app_server.py"
pause
