# Manual de Usuario y Guía de Conceptos — AgroRiesgo IA

**Sistema Inteligente para la Anticipación del Riesgo de Pérdida de Cultivos en la Agricultura Colombiana**

> **Proyecto:** AgroRiesgo IA — Asignatura: Inteligencia Artificial  
> **Integrantes:** Verona Andrés, Vargas Dadier, Ballesteros Carlos, Miranda Deiver  
> **ODS Impactados:** ODS 2 (Hambre Cero) · ODS 12 (Producción y Consumo Responsables) · ODS 1 (Fin de la Pobreza)  
> **Fuente de Datos:** Evaluaciones Agropecuarias Municipales (EVA) — Ministerio de Agricultura y Desarrollo Rural de Colombia

---

## 1. Glosario de Términos Agronómicos y Métricas Clave

Para que cualquier usuario, agricultor, técnico o evaluador comprenda a cabalidad las cifras de la plataforma, a continuación se definen los conceptos fundamentales:

### 1.1. ¿Qué es una Hectárea (`ha`)?
* **Definición técnica:** La **hectárea** (símbolo: `ha`) es una unidad de superficie agraria equivalente a **10.000 metros cuadrados ($10.000\text{ m}^2$)**, es decir, un cuadrado de 100 metros de ancho por 100 metros de largo ($100\text{ m} \times 100\text{ m}$).
* **Referencia visual práctica:** En el campo o en la ciudad, una hectárea equivale aproximadamente al tamaño de una **cancha de fútbol profesional reglamentaria** (incluyendo sus zonas de banda y áreas técnicas).
* **En el contexto colombiano:** 
  * Una siembra de **1 a 5 ha** suele corresponder a un **pequeño productor campesino** (agricultura familiar).
  * Una siembra de **5 a 20 ha** corresponde a un **mediano productor**.
  * Siembras mayores a **50 o 100 ha** corresponden a **productores comerciales o agroindustriales** (ej. arroz tecnificado, maíz mecanizado).

---

### 1.2. ¿Qué es el Rendimiento en Toneladas por Hectárea (`t/ha`)?
* **Definición:** Es la medida estándar de **productividad de la tierra**. Indica cuántas toneladas métricas ($1\text{ t} = 1.000\text{ kilogramos}$) de alimento o producto cosechable se obtienen en promedio por cada hectárea sembrada.
* **Fórmula:**
  $$\text{Rendimiento (t/ha)} = \frac{\text{Producción Total Obtenida (toneladas)}}{\text{Área Cosechada (hectáreas)}}$$
* **Ejemplos reales en Colombia:**
  * **Papa:** Tiene rendimientos altos en peso (entre $10\text{ y }25\text{ t/ha}$), ya que los tubérculos son densos en agua.
  * **Maíz Tradicional:** Suele rendir entre $1.0\text{ y }2.5\text{ t/ha}$ en condiciones de ladera o secano.
  * **Fríjol Arbustivo:** Suele rendir entre $0.8\text{ y }1.5\text{ t/ha}$.

---

### 1.3. ¿Qué es la Producción Total Proyectada (`t`)?
* Es la cantidad global de alimento que se espera recoger al final de la temporada en todo el predio.
* **Cálculo:**
  $$\text{Producción Total (t)} = \text{Área Sembrada (ha)} \times \text{Rendimiento Estimado (t/ha)}$$
* Si un agricultor siembra $5\text{ ha}$ de papa y el modelo estima un rendimiento de $11.9\text{ t/ha}$, la producción total proyectada es:
  $$5 \times 11.9 = 59.5\text{ toneladas}$$

---

### 1.4. ¿Qué son las Temporadas Agrícolas en Colombia?
A diferencia de los países con cuatro estaciones térmicas (primavera, verano, otoño, invierno), Colombia se rige por **regímenes pluviométricos (lluvias y temporadas secas)** regulados por el IDEAM y el Ministerio de Agricultura:
* **Semestre A:** Comprende las siembras del **primer semestre del año** (usualmente entre marzo/abril y julio/agosto). Aprovecha la primera temporada de lluvias del año.
* **Semestre B:** Comprende las siembras del **segundo semestre del año** (usualmente entre agosto/septiembre y diciembre/enero). Aprovecha la segunda temporada de lluvias.
* **Ciclo Anual:** Se refiere a cultivos cuyo periodo vegetativo toma entre 9 y 12 meses o más para cosecharse (por ejemplo: yuca, ñame, arracacha, caña panelera).

---

### 1.5. ¿Qué es la "Pérdida Alta" de Cultivo?
* En el estudio oficial y en los datos del Ministerio de Agricultura (EVA), la **Tasa de Pérdida** se define como la proporción del terreno sembrado que **nunca se pudo cosechar**:
  $$\text{Tasa de Pérdida} = \frac{\text{Área Sembrada} - \text{Área Cosechada}}{\text{Área Sembrada}}$$
* **Definición de Pérdida Alta ($\ge 20\%$):** Si de 10 hectáreas sembradas se pierden 2 o más (por sequías, inundaciones, plagas, enfermedades o falta de mano de obra), se clasifica como una **Pérdida Alta**. Perder una quinta parte o más de la siembra destruye el margen de ganancia del campesino y pone en riesgo su seguridad alimentaria y capacidad de pago de créditos.

---

### 1.6. Entidades del Sector Agropecuario Citadas en las Recomendaciones
* **UMATA (Unidad Municipal de Asistencia Técnica Agropecuaria):** Oficina municipal de apoyo que brinda agrónomos y técnicos de campo gratuitos a los pequeños agricultores.
* **ICA (Instituto Colombiano Agropecuario):** Autoridad sanitaria nacional encargada de la prevención y control de plagas y enfermedades agropecuarias.
* **FINAGRO (Fondo para el Financiamiento del Sector Agropecuario):** Entidad estatal que administra líneas de crédito de fomento y subsidia hasta el $80\%$ de la póliza del **Seguro Agropecuario** contra riesgos climáticos.

---

## 2. Recorrido Sección por Sección de la Página Web

La aplicación web está diseñada para ser intuitiva, ágil y explicable. Cuenta con dos vistas principales accesibles desde las pestañas superiores:

```
[ Pestaña 1: Consulta del Agricultor ]    [ Pestaña 2: Panel del Extensionista ]
```

---

### 2.1. Encabezado y Casos de Demostración Rápida
En la parte superior de la página, el usuario encuentra:
* **Identificación del Proyecto:** Título, mención a los Objetivos de Desarrollo Sostenible (ODS 2 Hambre Cero, ODS 12 Producción Responsable) y métricas de desempeño del modelo (77.4% exactitud, 63.8% sensibilidad, 0.77 AUC-ROC).
* **Botones de Carga Rápida (Casos Reales del Estudio):**
  * 🔴 **Caso Alto Riesgo:** Carga automáticamente *Maíz Tradicional en Ariguaní (Magdalena)* con 1.000 ha en Temporada B.
  * 🟡 **Caso Medio:** Carga *Fríjol Arbustivo en Medellín (Antioquia)* con 10 ha en Temporada A.
  * 🟢 **Caso Bajo Riesgo:** Carga *Papa en Soatá (Boyacá)* con 5 ha en Temporada B.
  * *Utilidad:* Permite a cualquier evaluador o profesor probar la plataforma en 1 segundo sin necesidad de teclear datos manualmente.

---

### 2.2. Tarjeta 1: Formulario de Registro de Siembra (Columna Izquierda)
Es el módulo donde el agricultor o extensionista ingresa los 5 datos básicos de su parcela:

| Campo | Descripción | ¿Por qué es importante? |
| :--- | :--- | :--- |
| **1. Departamento** | Lista desplegable con los 32 departamentos de Colombia. | Define la región geográfica y sus condiciones climáticas y agroecológicas macro. |
| **2. Municipio** | Menú dinámico que se carga automáticamente según el departamento seleccionado. | Permite vincular el historial municipal específico de pérdidas de ese territorio. |
| **3. Cultivo** | Desplegable con 116 cultivos transitorios y anuales (Papa, Maíz Tradicional, Fríjol, Arroz, Ahuyama, Hortalizas, etc.). | Cada cultivo tiene diferente resistencia a plagas, requerimientos hídricos y ciclos vegetativos. |
| **4. Temporada** | Selección entre Semestre A, Semestre B o Anual. | Modela la estacionalidad de lluvias y sequías del semestre de siembra. |
| **5. Área Sembrada (`ha`)** | Número de hectáreas que se planea o se acaba de sembrar. | El tamaño de la siembra influye en la capacidad de manejo técnico y en la vulnerabilidad ante eventos adversos. |
| **Año de Referencia** | Campo opcional (por defecto año actual o 2024). | Permite al modelo acumular la experiencia histórica hasta esa fecha. |

* **Botón "Evaluar Riesgo de la Siembra":** Envía los datos por AJAX al backend de Flask. La predicción se realiza en menos de 10 milisegundos.
* **Botón "Limpiar":** Restablece el formulario a su estado inicial.

---

### 2.3. Tarjeta 2: Semáforo y Diagnóstico de Riesgo (Columna Derecha)
Una vez presionado el botón de evaluación, aparece el diagnóstico con un código de colores tipo semáforo:

#### Niveles del Semáforo:
* 🔴 **ALERTA: ALTO RIESGO DE PÉRDIDA ($\ge 70\%$):**  
  Indica que las condiciones históricas del municipio, el tipo de cultivo y el área sembrada configuran una alta probabilidad de perder el 20% o más de la siembra. Exige intervención técnica inmediata.
* 🟡 **PRECAUCIÓN: RIESGO MODERADO ($50\% - 70\%$):**  
  Indica que existe probabilidad significativa de pérdida que amerita monitoreo semanal preventivo y uso de variedades certificadas.
* 🟢 **FAVORABLE: BAJO RIESGO DE PÉRDIDA ($< 50\%$):**  
  Indica condiciones favorables y bajo riesgo histórico de siniestros severos en la zona.

#### Comparación de Modelos de Inteligencia Artificial:
* **Árbol de Decisión (Modelo Principal):** Muestra el porcentaje de probabilidad estimado por el árbol de profundidad 8. Es el modelo que define las alertas porque sus decisiones son transparentes y verificables.
* **Regresión Logística (Segunda Opinión):** Muestra la probabilidad calculada por un clasificador lineal regularizado sobre variables estandarizadas, actuando como contraste estadístico independiente.

---

### 2.4. Tarjeta 3: Estimación de Rendimiento y Cosecha
Módulo de **Regresión Lineal Múltiple** enfocado en la productividad económica del productor:
* **Rendimiento Esperado ($t/ha$):** Estima cuántas toneladas por hectárea rendirá el cultivo si llega a cosecha, aprendiendo de los rendimientos registrados en la base oficial EVA.
* **Producción Total Estimada ($t$):** Multiplica automáticamente el rendimiento estimado por las hectáreas declaradas en el formulario para entregarle al agricultor la proyección de su volumen cosechable.

---

### 2.5. Tarjeta 4: Historial Agronómico Municipal
Muestra el contexto territorial que el algoritmo recuperó automáticamente sin que el agricultor tuviera que buscarlo en bases de datos:
* **Temporadas previas registradas:** Cuántas veces se ha registrado oficialmente ese cultivo en ese municipio.
* **Pérdida media histórica municipal:** Porcentaje promedio de hectáreas perdidas históricamente en ese municipio para ese cultivo.
* **Pérdida en la temporada anterior:** Cómo le fue a la siembra inmediatamente anterior en ese mismo municipio.
* **Pérdida media nacional de referencia:** Promedio del país ($8.4\%$) para comparar si la zona tiene un riesgo superior o inferior al promedio nacional.

---

### 2.6. Tarjeta 5: Explicabilidad del Árbol de Decisión (¿Por qué el modelo tomó esta decisión?)
Esta sección responde a una de las exigencias más importantes de la Inteligencia Artificial moderna: **la explicabilidad (XAI - Explainable AI)**.  
En lugar de ser una "caja negra" incomprensible, el sistema desglosa los pasos y condiciones que siguió el Árbol de Decisión para clasificar el cultivo:
* *Ejemplo:* `perdida_anterior: 38.0% > 19.0%` (La siembra previa en el municipio tuvo pérdidas severas).
* *Ejemplo:* `perdida_historica: 16.9% > 13.0%` (El promedio histórico del municipio supera el umbral de alerta).
* *Ejemplo:* `Área sembrada: 1000.0 ha > 3.5 ha` (Es una siembra de gran escala con mayor exposición).

---

### 2.7. Tarjeta 6: Recomendaciones de Acción Preventiva
Según el nivel de riesgo arrojado por el semáforo, la página despliega recomendaciones técnicas aplicables en el campo colombiano:
* **Para Riesgo Alto:**
  1. Priorizar visita técnica urgente de la UMATA / ICA antes de la floración y cosecha.
  2. Revisar drenajes, zanjas de desagüe y reservorios de agua (el exceso o déficit hídrico es la principal causa de pérdida).
  3. Consultar y contratar el Seguro Agropecuario de FINAGRO para proteger la inversión.
  4. Escalonar las fechas de siembra o sembrar cultivos alternativos para no concentrar el riesgo financiero en un solo lote.
* **Para Riesgo Medio:**
  1. Monitoreo fitosanitario semanal para detección temprana de plagas.
  2. Utilizar únicamente semilla certificada y variedades adaptadas a la zona agroecológica.
* **Para Riesgo Bajo:**
  1. Mantener Buenas Prácticas Agrícolas (BPA) y registrar el rendimiento final para enriquecer la base de datos municipal.

---

### 2.8. Pestaña 2: Panel de Priorización para el Extensionista (UMATA / ICA)
Al cambiar a la segunda pestaña de la aplicación web:
* **Problema que resuelve:** Las oficinas municipales de asistencia técnica (UMATA y Secretarías de Agricultura) cuentan con pocos técnicos y agrónomos para recorrer cientos de veredas. No pueden visitar todas las fincas al mismo tiempo.
* **Funcionalidad:**
  * El usuario selecciona un **Departamento** (por ejemplo: Boyacá, Cundinamarca, Magdalena, Antioquia).
  * La plataforma despliega una **tabla ordenada por nivel de riesgo descendente** con las siembras más críticas.
  * Muestra: orden de prioridad ($1, 2, 3...$), municipio, cultivo, temporada, hectáreas sembradas, riesgo predicho y la pérdida real histórica.
  * **Beneficio directo:** Permite enfocar las visitas presenciales y los recursos públicos de asistencia primero a donde existe mayor probabilidad de que la cosecha se pierda.

---

## 3. Resumen de Fórmulas y Relaciones Matemáticas

$$\begin{aligned}
1\text{ ha} &= 10.000\text{ m}^2 \\
1\text{ t} &= 1.000\text{ kg} \\
\text{Tasa de Pérdida} &= \frac{\text{Área Sembrada} - \text{Área Cosechada}}{\text{Área Sembrada}} \\
\text{Pérdida Alta} &= \begin{cases} 1 & \text{si Tasa de Pérdida } \ge 0.20 \\ 0 & \text{si Tasa de Pérdida } < 0.20 \end{cases} \\
\text{Semáforo} &= \begin{cases} \text{ALTO} & \text{si Probabilidad } \ge 70\% \\ \text{MEDIO} & \text{si } 50\% \le \text{Probabilidad} < 70\% \\ \text{BAJO} & \text{si Probabilidad } < 50\% \end{cases} \\
\text{Producción Total (t)} &= \text{Área Sembrada (ha)} \times \text{Rendimiento (t/ha)}
\end{aligned}$$
