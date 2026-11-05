import os
import time
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import StandardScaler

print("Iniciando preparación y entrenamiento de modelos de AgroRiesgo IA...")
t0 = time.time()

ARCHIVO = 'Evaluaciones_Agropecuarias_Municipales_EVA.csv'
if not os.path.exists(ARCHIVO):
    raise FileNotFoundError(f"No se encontró {ARCHIVO}")

print("1. Cargando CSV...")
df = pd.read_csv(ARCHIVO)
df.columns = ['cod_dep', 'departamento', 'cod_mun', 'municipio', 'grupo', 'subgrupo', 'cultivo',
              'desagregacion', 'anio', 'periodo', 'area_sembrada', 'area_cosechada', 'produccion',
              'rendimiento', 'estado_fisico', 'nombre_cientifico', 'ciclo']

print("2. Imputando municipios faltantes...")
nombres_mun = df.dropna(subset=['municipio']).groupby('cod_mun')['municipio'].agg(lambda s: s.mode()[0])
df['municipio'] = df['municipio'].fillna(df['cod_mun'].map(nombres_mun)).fillna('DESCONOCIDO')

print("3. Filtrando cultivos transitorios y anuales...")
d = df[df['ciclo'].isin(['TRANSITORIO', 'ANUAL'])].copy()
d['cultivo'] = d['desagregacion']

print("4. Filtrando registros válidos y excluyendo 2018...")
d = d[(d.area_sembrada > 0) & (d.area_cosechada <= d.area_sembrada)].copy()
d = d[d.anio <= 2017].copy()

d['log_area_sembrada'] = np.log1p(d.area_sembrada)
d['tasa_perdida'] = (d.area_sembrada - d.area_cosechada) / d.area_sembrada
d['perdida_alta'] = (d.tasa_perdida >= 0.20).astype(int)

d['temporada'] = d['periodo'].astype(str).str[-1].map({'A': 'A', 'B': 'B'}).fillna('Anual')
d['orden'] = d['temporada'].map({'A': 1, 'B': 2, 'Anual': 3})
d = d.sort_values(['cod_mun', 'cultivo', 'anio', 'orden']).reset_index(drop=True)

print("5. Calculando historial temporal...")
grupo_mc = d.groupby(['cod_mun', 'cultivo'])['tasa_perdida']
d['perdida_historica'] = grupo_mc.transform(lambda s: s.shift(1).expanding().mean())
d['perdida_anterior']  = grupo_mc.shift(1)
d['temporadas_previas'] = d.groupby(['cod_mun', 'cultivo']).cumcount()
d['sin_historial'] = d['perdida_historica'].isnull().astype(int)

PERDIDA_MEDIA = float(d['tasa_perdida'].mean())
d['perdida_historica'] = d['perdida_historica'].fillna(PERDIDA_MEDIA)
d['perdida_anterior']  = d['perdida_anterior'].fillna(PERDIDA_MEDIA)

print(f"Perdida media global: {PERDIDA_MEDIA:.4f}")

# Diccionarios de metadatos útiles
print("6. Construyendo metadatos geográficos y agronómicos...")
# Relación de departamento -> municipios
depto_mun = {}
for depto, grp in d.groupby('departamento'):
    muns = sorted(grp['municipio'].unique().tolist())
    depto_mun[str(depto)] = muns

# Cultivo -> info (grupo, ciclo)
cultivo_info = {}
for cult, grp in d.groupby('cultivo'):
    first = grp.iloc[0]
    cultivo_info[str(cult)] = {
        'grupo': str(first['grupo']),
        'ciclo': str(first['ciclo'])
    }

# Historial municipal compacto para inferencia rápida:
# clave: (departamento, municipio, cultivo) -> lista de registros [(anio, orden, tasa_perdida)]
historial_dict = {}
for (depto, mun, cult), grp in d.groupby(['departamento', 'municipio', 'cultivo']):
    records = list(zip(grp['anio'].astype(int), grp['orden'].astype(int), grp['tasa_perdida'].astype(float)))
    historial_dict[(str(depto), str(mun), str(cult))] = records

print(f"Total combinaciones históricas: {len(historial_dict)}")

print("7. Entrenando modelos de clasificación de riesgo...")
NUMERICAS   = ['log_area_sembrada', 'perdida_historica', 'perdida_anterior', 'temporadas_previas', 'sin_historial']
CATEGORICAS = ['departamento', 'grupo', 'cultivo', 'temporada', 'ciclo']

X = pd.concat([d[NUMERICAS], pd.get_dummies(d[CATEGORICAS], dtype=int)], axis=1)
y = d['perdida_alta']
X_columns = list(X.columns)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

# Árbol de decisión
PROFUNDIDAD = 8
arbol = DecisionTreeClassifier(max_depth=PROFUNDIDAD, class_weight='balanced', random_state=42)
arbol.fit(X_train, y_train)

# Regresión logística con escalador
escalador = StandardScaler().fit(X_train)
X_train_esc = escalador.transform(X_train)
log_reg = LogisticRegression(max_iter=3000, class_weight='balanced', random_state=42)
log_reg.fit(X_train_esc, y_train)

print("8. Entrenando modelo de regresión lineal para rendimiento...")
dr = d[d['rendimiento'].notna() & (d['rendimiento'] > 0)].copy()
Xr = pd.concat([dr[['anio', 'log_area_sembrada']],
                pd.get_dummies(dr[['departamento', 'cultivo', 'temporada']], dtype=int)], axis=1)
yr = np.log1p(dr['rendimiento'])
Xr_columns = list(Xr.columns)

Xr_train, Xr_test, yr_train, yr_test = train_test_split(Xr, yr, test_size=0.20, random_state=42)
lin_reg = LinearRegression().fit(Xr_train, yr_train)

print("9. Guardando artefactos en 'modelo_agroriesgo.pkl'...")
os.makedirs('model_data', exist_ok=True)
bundle = {
    'arbol': arbol,
    'log_reg': log_reg,
    'escalador': escalador,
    'lin_reg': lin_reg,
    'X_columns': X_columns,
    'Xr_columns': Xr_columns,
    'PERDIDA_MEDIA': PERDIDA_MEDIA,
    'depto_mun': depto_mun,
    'cultivo_info': cultivo_info,
    'historial_dict': historial_dict,
    'recomendaciones': {
        'ALTO': [
            'Priorizar visita técnica de la UMATA / ICA antes de la cosecha.',
            'Revisar drenajes y reservorios de agua (exceso o falta de lluvia son causas frecuentes).',
            'Consultar el seguro agropecuario (FINAGRO) para proteger la inversión y capital de trabajo.',
            'Escalonar la siembra o diversificar con otro cultivo para no concentrar el riesgo.'
        ],
        'MEDIO': [
            'Monitorear el cultivo semanalmente y reportar oportunamente cualquier anomalía o plaga.',
            'Usar semilla certificada y variedades adaptadas a las condiciones climáticas de la zona.',
            'Implementar monitoreo fitosanitario preventivo y manejo adecuado de suelos.'
        ],
        'BAJO': [
            'Mantener las buenas prácticas agrícolas actuales (BPA) y registrar la cosecha para enriquecer el historial.',
            'Continuar con los planes de fertilización y manejo integrado programados.'
        ]
    }
}

with open('model_data/modelo_agroriesgo.pkl', 'wb') as f:
    pickle.dump(bundle, f, protocol=pickle.HIGHEST_PROTOCOL)

print(f"Completado exitosamente en {time.time() - t0:.2f} segundos!")
