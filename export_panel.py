import pickle
import json
import numpy as np
import pandas as pd

print("Generando datos para el Panel de Priorización del Extensionista...")
with open('model_data/modelo_agroriesgo.pkl', 'rb') as f:
    bundle = pickle.load(f)

arbol = bundle['arbol']
X_columns = bundle['X_columns']
PERDIDA_MEDIA = bundle['PERDIDA_MEDIA']
historial_dict = bundle['historial_dict']
cultivo_info = bundle['cultivo_info']

# Cargar CSV original rápidamente
ARCHIVO = 'Evaluaciones_Agropecuarias_Municipales_EVA.csv'
df = pd.read_csv(ARCHIVO)
df.columns = ['cod_dep', 'departamento', 'cod_mun', 'municipio', 'grupo', 'subgrupo', 'cultivo',
              'desagregacion', 'anio', 'periodo', 'area_sembrada', 'area_cosechada', 'produccion',
              'rendimiento', 'estado_fisico', 'nombre_cientifico', 'ciclo']

nombres_mun = df.dropna(subset=['municipio']).groupby('cod_mun')['municipio'].agg(lambda s: s.mode()[0])
df['municipio'] = df['municipio'].fillna(df['cod_mun'].map(nombres_mun)).fillna('DESCONOCIDO')

d = df[df['ciclo'].isin(['TRANSITORIO', 'ANUAL'])].copy()
d['cultivo'] = d['desagregacion']
d = d[(d.area_sembrada > 0) & (d.area_cosechada <= d.area_sembrada)].copy()
d = d[d.anio <= 2017].copy()
d['temporada'] = d['periodo'].astype(str).str[-1].map({'A': 'A', 'B': 'B'}).fillna('Anual')
d['orden'] = d['temporada'].map({'A': 1, 'B': 2, 'Anual': 3})
d['tasa_perdida'] = (d.area_sembrada - d.area_cosechada) / d.area_sembrada

# Solo para 2017 como muestra el notebook
d_2017 = d[d.anio == 2017].copy()

def nivel_str(p):
    return 'ALTO' if p >= 0.70 else ('MEDIO' if p >= 0.50 else 'BAJO')

panel_por_depto = {}

for depto, grp in d_2017.groupby('departamento'):
    records = []
    for idx, row in grp.iterrows():
        # Calcular variables
        mun = row['municipio']
        cult = row['cultivo']
        temp = row['temporada']
        orden_t = row['orden']
        area = row['area_sembrada']
        
        # Historial
        key = (depto, mun, cult)
        h = historial_dict.get(key, [])
        h_prev = [r for r in h if (r[0] < 2017) or (r[0] == 2017 and r[1] < orden_t)]
        tasas = [r[2] for r in h_prev]
        t_previas = len(h_prev)
        sin_h = int(t_previas == 0)
        p_hist = float(np.mean(tasas)) if tasas else PERDIDA_MEDIA
        p_ant = float(tasas[-1]) if tasas else PERDIDA_MEDIA
        
        c_i = cultivo_info.get(cult, {'grupo': 'OTROS', 'ciclo': 'TRANSITORIO'})
        
        fila = {c: 0 for c in X_columns}
        fila.update({
            'log_area_sembrada': np.log1p(area),
            'perdida_historica': p_hist,
            'perdida_anterior': p_ant,
            'temporadas_previas': t_previas,
            'sin_historial': sin_h
        })
        for var, val in [('departamento', depto), ('grupo', c_i['grupo']), ('cultivo', cult),
                         ('temporada', temp), ('ciclo', c_i['ciclo'])]:
            col = f"{var}_{val}"
            if col in fila:
                fila[col] = 1
                
        df_in = pd.DataFrame([fila], columns=X_columns)
        p_arb = float(arbol.predict_proba(df_in)[0, 1])
        
        records.append({
            'municipio': mun,
            'cultivo': cult,
            'temporada': temp,
            'area_sembrada': float(area),
            'riesgo_pct': round(p_arb * 100, 1),
            'nivel': nivel_str(p_arb),
            'perdida_real_pct': round(row['tasa_perdida'] * 100, 1)
        })
        
    # Ordenar por riesgo descendente y tomar top 15
    records.sort(key=lambda x: x['riesgo_pct'], reverse=True)
    panel_por_depto[depto] = records[:15]

with open('model_data/panel_extensionista.json', 'w', encoding='utf-8') as f:
    json.dump(panel_por_depto, f, ensure_ascii=False, indent=2)

print(f"Panel generado para {len(panel_por_depto)} departamentos.")
