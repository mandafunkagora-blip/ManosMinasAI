@echo off
setlocal EnableExtensions
title MANOS E MINAS AI
cd /d D:\ManosMinasAI

echo ==========================================================
echo              MANOS E MINAS AI
echo              INICIALIZADOR OFICIAL
echo ==========================================================
echo.

if not exist "D:\ManosMinasAI\backend\main.py" goto ERRO_BACKEND
if not exist "D:\ManosMinasAI\ManosMinasAI_Abertura_v2\index.html" goto ERRO_SITE

echo [1/3] INICIANDO API 8001...
start "" /D "D:\ManosMinasAI\backend" cmd /k python -m uvicorn main:app --host 127.0.0.1 --port 8001
timeout /t 3 /nobreak >nul

echo [2/3] INICIANDO SITE 8000...
start "" /D "D:\ManosMinasAI\ManosMinasAI_Abertura_v2" cmd /k python -m http.server 8000
timeout /t 3 /nobreak >nul

echo [3/3] ABRINDO MANOS E MINAS AI...
start "" "http://127.0.0.1:8000/index.html"

echo ==========================================================
echo FLUXO:
echo ABERTURA
echo    |
echo    v
echo VIDEO BEM VINDO
echo    |
echo    v
echo LOGIN
echo    |
echo    v
echo VIDEO PAPEL DE PAREDE
echo    |
echo    v
echo ENTRAR COM GOOGLE
echo    |
echo    v
echo PAINEL PRINCIPAL
echo    |
echo    v
echo STUDIO
echo ==========================================================
echo.
echo SITE: http://127.0.0.1:8000/
echo API:  http://127.0.0.1:8001/
echo.
echo NAO FECHE AS JANELAS DA API E DO SITE.
echo ==========================================================
pause
goto FIM

:ERRO_BACKEND
echo ERRO: backend\main.py nao encontrado.
pause
goto FIM

:ERRO_SITE
echo ERRO: index.html nao encontrado.
pause
goto FIM

:FIM
