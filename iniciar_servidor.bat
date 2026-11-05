@echo off
title AgroRiesgo IA - Servidor Web
cls
echo =====================================================================
echo                  AGRORIESGO IA - PREVENCION AGRICOLA
echo        Prediccion Inteligente del Riesgo de Perdida de Cultivos
echo =====================================================================
echo.
echo Iniciando servidor Flask...
echo Abriendo en su navegador: http://127.0.0.1:5000
echo.
start http://127.0.0.1:5000
python app.py
pause
