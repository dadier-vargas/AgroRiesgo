# AgroRiesgo IA — Aplicación Web

**Predicción Inteligente del Riesgo de Pérdida de Cultivos en la Agricultura Colombiana**

> **Asignatura:** Inteligencia Artificial  
> **Integrantes:** Verona Andrés, Vargas Dadier, Ballesteros Carlos, Miranda Deiver  
> **ODS Impactados:** ODS 2 (Hambre Cero), ODS 12 (Producción y Consumo Responsables), ODS 1 (Fin de la Pobreza)  
> **Fuente de Datos:** Evaluaciones Agropecuarias Municipales (EVA) — Ministerio de Agricultura y Desarrollo Rural (datos.gov.co)

---

## 🌾 Descripción del Proyecto

Esta aplicación web implementa la solución completa desarrollada en el notebook [`AgroRiesgo_IA_Implementacion.ipynb`](AgroRiesgo_IA_Implementacion.ipynb) y documentada en el informe oficial de la entrega. Permite a cualquier productor o técnico agrícola diligenciar 5 datos de su siembra y recibir de inmediato:

1. **Semáforo de Riesgo**:
   - 🔴 **ALTO** (Probabilidad $\ge$ 70%)
   - 🟡 **MEDIO** (Probabilidad entre 50% y 70%)
   - 🟢 **BAJO** (Probabilidad < 50%)
2. **Modelos de Inteligencia Artificial Utilizados**:
   - **Árbol de Decisión (Modelo Principal)**: Explicable, profundidad máxima calibrada por validación cruzada ($max\_depth = 8$, ponderación balanceada).
   - **Regresión Logística (Segunda Opinión)**: Con estandarización de variables.
   - **Regresión Lineal Múltiple**: Estima el **rendimiento esperado en toneladas por hectárea ($t/ha$)** y la producción total esperada ($t$).
3. **Historial Agronómico Municipal**:
   - Recupera automáticamente el historial de siembras de ese cultivo en ese municipio en las bases oficiales (temporadas previas, tasa media de pérdida y pérdida de la temporada anterior).
4. **Explicabilidad (¿Por qué el modelo tomó esta decisión?)**:
   - Detalla las reglas y bifurcaciones recorridas en el árbol de decisión.
5. **Recomendaciones de Acción Preventiva**:
   - Recomendaciones técnicas fijas calibradas por el equipo (visitas prioritarias UMATA / ICA, seguro agropecuario FINAGRO, manejo de drenajes/riego, diversificación, semillas certificadas).
6. **Panel de Priorización para Extensionistas**:
   - Permite listar por departamento las siembras con mayor riesgo predicho para focalizar las visitas presenciales de asistencia técnica antes de la cosecha.

---

## 🚀 Cómo Iniciar la Aplicación Web

### Opción 1: Con el lanzador rápido (Recomendado en Windows)
Haga doble clic en el archivo:
```
iniciar_servidor.bat
```
Este script abre automáticamente el navegador en `http://127.0.0.1:5000` e inicia el servidor.

### Opción 2: Desde la terminal / consola
```bash
python app.py
```
Luego abra su navegador web en:  
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 📂 Estructura de Archivos

```
Entrega2IA_Verona_Vargas_Ballesteros_Miranda/
│
├── app.py                               # Servidor web Flask y API REST de inferencia
├── build_model.py                       # Script de reentrenamiento y serialización
├── export_panel.py                      # Precalculador del panel del extensionista
├── iniciar_servidor.bat                 # Lanzador automático para Windows
│
├── model_data/
│   ├── modelo_agroriesgo.pkl            # Modelos entrenados y estructuras históricas
│   └── panel_extensionista.json         # Siembras priorizadas por departamento
│
├── templates/
│   └── index.html                       # Interfaz web responsiva con Bootstrap 5
│
├── static/
│   ├── css/
│   │   └── style.css                    # Estilos visuales temáticos agrícolas
│   └── js/
│       └── app.js                       # Lógica dinámica en JavaScript (AJAX y UI)
│
├── AgroRiesgo_IA_Implementacion.ipynb   # Cuaderno Jupyter original
├── Entrega2IA_Verona_Vargas_Ballesteros_Miranda.docx # Informe de entrega
└── Evaluaciones_Agropecuarias_Municipales_EVA.csv    # Conjunto de datos oficial EVA
```

---

## 🧪 Casos de Demostración Disponibles en la Web

La aplicación cuenta con botones de carga rápida con un solo clic para los casos calibrados en el estudio:
- **Caso Alto Riesgo:** Maíz Tradicional en Ariguaní (Magdalena) — 1.000 ha, Temporada B.
- **Caso Riesgo Medio:** Fríjol Arbustivo en Medellín (Antioquia) — 10 ha, Temporada A.
- **Caso Bajo Riesgo:** Papa en Soatá (Boyacá) — 5 ha, Temporada B.
