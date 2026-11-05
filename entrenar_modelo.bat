@echo off
title AgroRiesgo IA - Entrenamiento de Modelos
cls
echo =====================================================================
echo                  AGRORIESGO IA - ENTRENAMIENTO EN VIVO
echo       Entrenando Arbol de Decision, Regresion Logistica y Lineal
echo =====================================================================
echo.
echo Leyendo Evaluaciones_Agropecuarias_Municipales_EVA.csv (206.068 registros)...
echo.
python build_model.py
echo.
echo =====================================================================
echo  MODELO ENTRENADO CON EXITO Y GUARDADO EN: model_data/modelo_agroriesgo.pkl
echo =====================================================================
pause
