import os
import json
import pickle
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

# Cargar el bundle del modelo previamente entrenado
MODEL_PATH = os.path.join(BASE_DIR, 'model_data', 'modelo_agroriesgo.pkl')
PANEL_PATH = os.path.join(BASE_DIR, 'model_data', 'panel_extensionista.json')

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"No se encontró el archivo de modelo en {MODEL_PATH}. Ejecute build_model.py primero.")

print("Cargando modelo y metadatos de AgroRiesgo IA...")
with open(MODEL_PATH, 'rb') as f:
    bundle = pickle.load(f)

arbol = bundle['arbol']
log_reg = bundle['log_reg']
escalador = bundle['escalador']
lin_reg = bundle['lin_reg']
X_columns = bundle['X_columns']
Xr_columns = bundle['Xr_columns']
PERDIDA_MEDIA = bundle['PERDIDA_MEDIA']
depto_mun = bundle['depto_mun']
cultivo_info = bundle['cultivo_info']
historial_dict = bundle['historial_dict']
recomendaciones_dict = bundle['recomendaciones']

departamentos_disponibles = sorted(list(depto_mun.keys()))
cultivos_disponibles = sorted(list(cultivo_info.keys()))

panel_data = {}
if os.path.exists(PANEL_PATH):
    with open(PANEL_PATH, 'r', encoding='utf-8') as f:
        panel_data = json.load(f)

print(f"Modelo cargado. {len(departamentos_disponibles)} departamentos y {len(cultivos_disponibles)} cultivos disponibles.")


def nivel_riesgo(probabilidad):
    """Clasificación según los umbrales definidos en el documento y notebook:
    - ALTO: >= 70%
    - MEDIO: >= 50% y < 70%
    - BAJO: < 50%
    """
    if probabilidad >= 0.70:
        return 'ALTO', 'danger', 'Alto Riesgo de Pérdida'
    elif probabilidad >= 0.50:
        return 'MEDIO', 'warning', 'Riesgo Moderado'
    else:
        return 'BAJO', 'success', 'Bajo Riesgo de Pérdida'


def extraer_reglas_arbol(entrada_df):
    """Extrae las reglas y decisiones tomadas en el camino del árbol de decisión."""
    t = arbol.tree_
    pasos = []
    indices = arbol.decision_path(entrada_df).indices
    
    traducciones_vars = {
        'log_area_sembrada': 'Logaritmo del área sembrada',
        'perdida_historica': 'Pérdida histórica promedio del municipio',
        'perdida_anterior': 'Pérdida en la temporada anterior inmediata',
        'temporadas_previas': 'Historial de temporadas previas',
        'sin_historial': '¿Sin registros históricos previos?'
    }
    
    for n in indices:
        if t.children_left[n] == t.children_right[n]:
            continue
        feat_idx = t.feature[n]
        var = X_columns[feat_idx]
        umbral = t.threshold[n]
        valor = entrada_df.iloc[0][var]
        signo = '<=' if valor <= umbral else '>'
        
        prefijo = var.split('_')[0]
        if prefijo in ('departamento', 'grupo', 'cultivo', 'temporada', 'ciclo'):
            nombre_cat = var.replace('_', ': ')
            pasos.append({
                'tipo': 'categorica',
                'variable': nombre_cat,
                'condicion': 'Coincide' if valor == 1 else 'No coincide',
                'texto': f"{nombre_cat} = {'Sí' if valor == 1 else 'No'}"
            })
        else:
            nombre_var = traducciones_vars.get(var, var)
            if 'perdida' in var:
                pasos.append({
                    'tipo': 'porcentaje',
                    'variable': nombre_var,
                    'condicion': f"{valor*100:.1f}% ({signo} {umbral*100:.1f}%)",
                    'texto': f"{nombre_var}: {valor*100:.1f}% {signo} {umbral*100:.1f}%"
                })
            elif var == 'log_area_sembrada':
                ha_real = np.expm1(valor)
                ha_umbral = np.expm1(umbral)
                pasos.append({
                    'tipo': 'numerica',
                    'variable': 'Área sembrada',
                    'condicion': f"{ha_real:.1f} ha ({signo} {ha_umbral:.1f} ha)",
                    'texto': f"Área sembrada: {ha_real:.1f} ha {signo} {ha_umbral:.1f} ha (log {valor:.2f} {signo} {umbral:.2f})"
                })
            else:
                pasos.append({
                    'tipo': 'numerica',
                    'variable': nombre_var,
                    'condicion': f"{valor:.2f} ({signo} {umbral:.2f})",
                    'texto': f"{nombre_var}: {valor:.2f} {signo} {umbral:.2f}"
                })
    return pasos


@app.route('/')
def index():
    return render_template(
        'index.html',
        departamentos=departamentos_disponibles,
        cultivos=cultivos_disponibles,
        cultivo_info=cultivo_info
    )


@app.route('/api/municipios/<departamento>')
def get_municipios(departamento):
    """Devuelve los municipios disponibles para un departamento."""
    depto = departamento.strip().upper()
    municipios = depto_mun.get(depto, [])
    return jsonify({'departamento': depto, 'municipios': municipios})


@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(force=True) if request.is_json else request.form
        
        departamento = str(data.get('departamento', '')).strip().upper()
        municipio = str(data.get('municipio', '')).strip().upper()
        cultivo = str(data.get('cultivo', '')).strip().upper()
        temporada = str(data.get('temporada', 'A')).strip()
        
        try:
            area_sembrada = float(data.get('area_sembrada', 1.0))
            if area_sembrada <= 0:
                area_sembrada = 1.0
        except (ValueError, TypeError):
            area_sembrada = 1.0
            
        try:
            anio = int(data.get('anio', 2024))
        except (ValueError, TypeError):
            anio = 2024

        if not departamento or not municipio or not cultivo:
            return jsonify({'error': 'Faltan campos obligatorios (departamento, municipio, cultivo).'}), 400

        # Mapeo de temporada a orden numérico
        orden_t = {'A': 1, 'B': 2, 'Anual': 3}.get(temporada, 1)

        # 1. Recuperar historial municipal del cultivo
        key = (departamento, municipio, cultivo)
        records = historial_dict.get(key, [])
        # Filtrar registros anteriores al año o temporada evaluada
        hist = [r for r in records if (r[0] < anio) or (r[0] == anio and r[1] < orden_t)]
        
        tasas = [r[2] for r in hist]
        temporadas_previas = len(hist)
        sin_historial = int(temporadas_previas == 0)
        perdida_historica = float(np.mean(tasas)) if tasas else PERDIDA_MEDIA
        perdida_anterior = float(tasas[-1]) if tasas else PERDIDA_MEDIA
        log_area = float(np.log1p(area_sembrada))

        # Información agronómica (grupo y ciclo)
        c_info = cultivo_info.get(cultivo, {'grupo': 'OTROS', 'ciclo': 'TRANSITORIO'})
        grupo = c_info['grupo']
        ciclo = c_info['ciclo']

        # 2. Construir vector de entrada para clasificación
        fila = {c: 0 for c in X_columns}
        fila.update({
            'log_area_sembrada': log_area,
            'perdida_historica': perdida_historica,
            'perdida_anterior': perdida_anterior,
            'temporadas_previas': temporadas_previas,
            'sin_historial': sin_historial
        })

        for var, val in [('departamento', departamento), ('grupo', grupo), ('cultivo', cultivo),
                         ('temporada', temporada), ('ciclo', ciclo)]:
            col = f"{var}_{val}"
            if col in fila:
                fila[col] = 1

        entrada_df = pd.DataFrame([fila], columns=X_columns)

        # 3. Predicciones de clasificación
        prob_arbol = float(arbol.predict_proba(entrada_df)[0, 1])
        prob_log = float(log_reg.predict_proba(escalador.transform(entrada_df))[0, 1])

        # Nivel y semáforo
        nivel, color_tag, label_tag = nivel_riesgo(prob_arbol)
        recomendaciones = recomendaciones_dict.get(nivel, [])

        # 4. Reglas del árbol (explicabilidad)
        reglas = extraer_reglas_arbol(entrada_df)

        # 5. Predicción de rendimiento (Regresión Lineal Múltiple)
        fr = {c: 0 for c in Xr_columns}
        fr.update({'anio': anio, 'log_area_sembrada': log_area})
        for var, val in [('departamento', departamento), ('cultivo', cultivo), ('temporada', temporada)]:
            col = f"{var}_{val}"
            if col in fr:
                fr[col] = 1

        rendimiento_estimado = float(np.expm1(lin_reg.predict(pd.DataFrame([fr], columns=Xr_columns))[0]))
        if rendimiento_estimado < 0:
            rendimiento_estimado = 0.0
        produccion_total = rendimiento_estimado * area_sembrada

        # Respuesta estructurada
        resultado = {
            'success': True,
            'consulta': {
                'departamento': departamento,
                'municipio': municipio,
                'cultivo': cultivo,
                'grupo': grupo,
                'ciclo': ciclo,
                'temporada': temporada,
                'area_sembrada': area_sembrada,
                'anio': anio
            },
            'diagnostico': {
                'nivel': nivel,
                'color': color_tag,
                'label': label_tag,
                'prob_arbol': round(prob_arbol * 100, 1),
                'prob_logistica': round(prob_log * 100, 1),
                'es_perdida_alta': prob_arbol >= 0.50
            },
            'historial_municipal': {
                'temporadas_previas': temporadas_previas,
                'sin_historial': bool(sin_historial),
                'perdida_historica_pct': round(perdida_historica * 100, 1),
                'perdida_anterior_pct': round(perdida_anterior * 100, 1),
                'perdida_media_nacional_pct': round(PERDIDA_MEDIA * 100, 1)
            },
            'estimacion_agronomica': {
                'rendimiento_t_ha': round(rendimiento_estimado, 2),
                'produccion_total_toneladas': round(produccion_total, 1)
            },
            'explicabilidad_reglas': reglas[:6],
            'recomendaciones': recomendaciones
        }

        return jsonify(resultado)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/demo-cases')
def demo_cases():
    """Retorna los casos de prueba y calibración demostrados en el notebook y documento oficial."""
    return jsonify({
        'alto': {
            'departamento': 'MAGDALENA',
            'municipio': 'ARIGUANI',
            'cultivo': 'MAIZ TRADICIONAL',
            'temporada': 'B',
            'area_sembrada': 1000,
            'anio': 2017,
            'descripcion': 'Maíz Tradicional en Ariguaní (Magdalena) - Siembra extensiva con historial de alta pérdida.'
        },
        'medio': {
            'departamento': 'ANTIOQUIA',
            'municipio': 'MEDELLIN',
            'cultivo': 'FRIJOL ARBUSTIVO',
            'temporada': 'A',
            'area_sembrada': 10,
            'anio': 2017,
            'descripcion': 'Fríjol Arbustivo en Medellín (Antioquia) - Siembra intermedia con riesgo moderado.'
        },
        'bajo': {
            'departamento': 'BOYACA',
            'municipio': 'SOATA',
            'cultivo': 'PAPA',
            'temporada': 'B',
            'area_sembrada': 5,
            'anio': 2017,
            'descripcion': 'Papa en Soatá (Boyacá) - Pequeña parcela con historial de excelente rendimiento y baja pérdida.'
        }
    })


@app.route('/api/panel-extensionista/<departamento>')
def get_panel_extensionista(departamento):
    """Retorna las siembras priorizadas por riesgo para las visitas de asistencia técnica en un departamento."""
    depto = departamento.strip().upper()
    items = panel_data.get(depto, [])
    return jsonify({'departamento': depto, 'items': items})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Iniciando servidor web AgroRiesgo IA en http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
