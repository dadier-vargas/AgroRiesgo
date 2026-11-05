document.addEventListener('DOMContentLoaded', function () {
    const selectDepto = document.getElementById('selectDepartamento');
    const selectMun = document.getElementById('selectMunicipio');
    const selectCult = document.getElementById('selectCultivo');
    const selectTemp = document.getElementById('selectTemporada');
    const inputArea = document.getElementById('inputArea');
    const inputAnio = document.getElementById('inputAnio');
    const formSiembra = document.getElementById('formSiembra');

    const btnPredecir = document.getElementById('btnPredecir');
    const btnSpinner = document.getElementById('btnSpinner');
    const btnIcon = document.getElementById('btnIcon');
    const btnLimpiar = document.getElementById('btnLimpiar');

    const placeholderResultados = document.getElementById('placeholderResultados');
    const panelResultados = document.getElementById('panelResultados');
    const cardSemaforo = document.getElementById('cardSemaforo');

    // Elementos de Resultados
    const resNivelTitulo = document.getElementById('resNivelTitulo');
    const resBadgeNivel = document.getElementById('resBadgeNivel');
    const resTextoBadge = document.getElementById('resTextoBadge');
    const resIconoNivel = document.getElementById('resIconoNivel');
    const resUbicacion = document.getElementById('resUbicacion');
    const resCultivoDetalle = document.getElementById('resCultivoDetalle');
    const resTemporadaDetalle = document.getElementById('resTemporadaDetalle');
    const resAreaDetalle = document.getElementById('resAreaDetalle');

    const resProbArbol = document.getElementById('resProbArbol');
    const progressBarArbol = document.getElementById('progressBarArbol');
    const resProbLog = document.getElementById('resProbLog');
    const progressBarLog = document.getElementById('progressBarLog');

    const resRendimiento = document.getElementById('resRendimiento');
    const resProduccionTotal = document.getElementById('resProduccionTotal');

    const resHistTemporadas = document.getElementById('resHistTemporadas');
    const resHistMedia = document.getElementById('resHistMedia');
    const resHistAnterior = document.getElementById('resHistAnterior');
    const resHistNacional = document.getElementById('resHistNacional');

    const listaReglasArbol = document.getElementById('listaReglasArbol');
    const listaRecomendaciones = document.getElementById('listaRecomendaciones');
    const recomIconCircle = document.getElementById('recomIconCircle');

    // Elementos del Panel del Extensionista
    const selectDeptoPanel = document.getElementById('selectDeptoPanel');
    const tbodyExtensionista = document.getElementById('tbodyExtensionista');
    const tabExtensionista = document.getElementById('tab-extensionista');

    // 1. Cargar Municipios al cambiar Departamento
    selectDepto.addEventListener('change', async function () {
        const depto = this.value;
        if (!depto) return;
        await cargarMunicipios(depto);
    });

    async function cargarMunicipios(depto, municipioSeleccionado = null) {
        selectMun.disabled = true;
        selectMun.innerHTML = '<option value="" disabled selected>Cargando municipios...</option>';

        try {
            const resp = await fetch(`/api/municipios/${encodeURIComponent(depto)}`);
            const data = await resp.json();

            selectMun.innerHTML = '<option value="" disabled selected>Seleccione un municipio...</option>';
            data.municipios.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m;
                opt.textContent = m;
                if (municipioSeleccionado && m === municipioSeleccionado) {
                    opt.selected = true;
                }
                selectMun.appendChild(opt);
            });
            selectMun.disabled = false;
        } catch (err) {
            console.error('Error al cargar municipios:', err);
            selectMun.innerHTML = '<option value="" disabled>Error al cargar municipios</option>';
        }
    }

    // 2. Manejo de Botones de Demostración (Casos Reales del Estudio)
    document.querySelectorAll('.demo-btn').forEach(btn => {
        btn.addEventListener('click', async function () {
            // Asegurar que la pestaña de agricultor esté activa
            const tabBtnAgricultor = document.getElementById('tab-agricultor');
            if (tabBtnAgricultor) {
                const bsTab = bootstrap.Tab.getOrCreateInstance(tabBtnAgricultor);
                bsTab.show();
            }

            const casoKey = this.dataset.caso;
            try {
                const resp = await fetch('/api/demo-cases');
                const demos = await resp.json();
                const caso = demos[casoKey];
                if (!caso) return;

                selectDepto.value = caso.departamento;
                await cargarMunicipios(caso.departamento, caso.municipio);

                selectCult.value = caso.cultivo;
                selectTemp.value = caso.temporada;
                inputArea.value = caso.area_sembrada;
                inputAnio.value = caso.anio;

                // Enviar automáticamente para visualizar el resultado de inmediato
                ejecutarPrediccion();
            } catch (err) {
                console.error('Error cargando caso demo:', err);
            }
        });
    });

    // 3. Envío del Formulario
    formSiembra.addEventListener('submit', function (e) {
        e.preventDefault();
        ejecutarPrediccion();
    });

    async function ejecutarPrediccion() {
        const depto = selectDepto.value;
        const mun = selectMun.value;
        const cult = selectCult.value;
        const temp = selectTemp.value;
        const area = parseFloat(inputArea.value);
        const anio = parseInt(inputAnio.value);

        if (!depto || !mun || !cult || isNaN(area) || area <= 0) {
            alert('Por favor complete todos los campos requeridos (Departamento, Municipio, Cultivo y un Área válida mayor a 0).');
            return;
        }

        // Estado visual de carga
        btnSpinner.classList.remove('d-none');
        btnIcon.classList.add('d-none');
        btnPredecir.disabled = true;

        try {
            const resp = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    departamento: depto,
                    municipio: mun,
                    cultivo: cult,
                    temporada: temp,
                    area_sembrada: area,
                    anio: anio
                })
            });

            const data = await resp.json();

            if (!resp.ok || data.error) {
                alert(`Error en la consulta: ${data.error || 'Respuesta inválida'}`);
                return;
            }

            renderizarResultados(data);

        } catch (err) {
            console.error('Error al solicitar predicción:', err);
            alert('Ocurrió un error al comunicarse con el modelo de IA.');
        } finally {
            btnSpinner.classList.add('d-none');
            btnIcon.classList.remove('d-none');
            btnPredecir.disabled = false;
        }
    }

    function renderizarResultados(data) {
        // Mostrar panel de resultados y ocultar placeholder
        placeholderResultados.classList.add('d-none');
        panelResultados.classList.remove('d-none');

        const diag = data.diagnostico;
        const cons = data.consulta;
        const hist = data.historial_municipal;
        const est = data.estimacion_agronomica;

        // Limpiar clases anteriores del semáforo
        cardSemaforo.classList.remove('risk-state-alto', 'risk-state-medio', 'risk-state-bajo');

        if (diag.nivel === 'ALTO') {
            cardSemaforo.classList.add('risk-state-alto');
            resNivelTitulo.textContent = 'ALERTA: ALTO RIESGO DE PÉRDIDA';
            resTextoBadge.textContent = 'ALTO (≥ 70%)';
            resIconoNivel.className = 'fa-solid fa-triangle-exclamation me-1';
            recomIconCircle.className = 'icon-circle bg-danger-subtle text-danger';
        } else if (diag.nivel === 'MEDIO') {
            cardSemaforo.classList.add('risk-state-medio');
            resNivelTitulo.textContent = 'PRECAUCIÓN: RIESGO MODERADO';
            resTextoBadge.textContent = 'MEDIO (50% - 70%)';
            resIconoNivel.className = 'fa-solid fa-circle-exclamation me-1';
            recomIconCircle.className = 'icon-circle bg-warning-subtle text-warning-emphasis';
        } else {
            cardSemaforo.classList.add('risk-state-bajo');
            resNivelTitulo.textContent = 'FAVORABLE: BAJO RIESGO DE PÉRDIDA';
            resTextoBadge.textContent = 'BAJO (< 50%)';
            resIconoNivel.className = 'fa-solid fa-circle-check me-1';
            recomIconCircle.className = 'icon-circle bg-success-subtle text-success';
        }

        // Datos del caso
        resUbicacion.textContent = `${cons.municipio} (${cons.departamento})`;
        resCultivoDetalle.textContent = `${cons.cultivo} · ${cons.grupo}`;
        resTemporadaDetalle.textContent = `${cons.anio}-${cons.temporada} (${cons.ciclo})`;
        resAreaDetalle.textContent = `${cons.area_sembrada.toLocaleString()} ha`;

        // Probabilidades de modelos
        resProbArbol.textContent = `${diag.prob_arbol}%`;
        progressBarArbol.style.width = `${diag.prob_arbol}%`;

        resProbLog.textContent = `${diag.prob_logistica}%`;
        progressBarLog.style.width = `${diag.prob_logistica}%`;

        // Rendimiento y producción
        resRendimiento.innerHTML = `${est.rendimiento_t_ha.toFixed(2)} <span class="fs-5 text-muted fw-normal">t/ha</span>`;
        resProduccionTotal.textContent = `${est.produccion_total_toneladas.toLocaleString()} toneladas`;

        // Historial municipal
        resHistTemporadas.textContent = hist.sin_historial ? 'Sin registros previos' : `${hist.temporadas_previas} temporadas`;
        resHistMedia.textContent = `${hist.perdida_historica_pct}%`;
        resHistAnterior.textContent = `${hist.perdida_anterior_pct}%`;
        resHistNacional.textContent = `${hist.perdida_media_nacional_pct}%`;

        // Explicabilidad: Reglas del camino de decisión del Árbol
        listaReglasArbol.innerHTML = '';
        if (data.explicabilidad_reglas && data.explicabilidad_reglas.length > 0) {
            data.explicabilidad_reglas.forEach((regla) => {
                const item = document.createElement('div');
                item.className = 'tree-rule-item';
                item.innerHTML = `
                    <div class="tree-rule-icon"><i class="fa-solid fa-code-fork"></i></div>
                    <div>
                        <div class="fw-semibold text-dark">${regla.texto}</div>
                        <small class="text-muted">Bifurcación del árbol evaluada en el registro de siembra</small>
                    </div>
                `;
                listaReglasArbol.appendChild(item);
            });
        } else {
            listaReglasArbol.innerHTML = '<div class="text-muted small">No se requirieron bifurcaciones profundas para este caso.</div>';
        }

        // Recomendaciones
        listaRecomendaciones.innerHTML = '';
        const claseRecom = diag.nivel === 'ALTO' ? '' : (diag.nivel === 'MEDIO' ? 'recom-medio' : 'recom-bajo');
        const iconRecom = diag.nivel === 'ALTO' ? 'fa-solid fa-triangle-exclamation' : (diag.nivel === 'MEDIO' ? 'fa-solid fa-eye' : 'fa-solid fa-check-double');

        (data.recomendaciones || []).forEach(r => {
            const li = document.createElement('li');
            li.className = `recom-item ${claseRecom}`;
            li.innerHTML = `
                <i class="${iconRecom} recom-icon"></i>
                <div>${r}</div>
            `;
            listaRecomendaciones.appendChild(li);
        });

        // Scroll suave al diagnóstico en pantallas pequeñas
        if (window.innerWidth < 992) {
            panelResultados.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Botón limpiar formulario
    btnLimpiar.addEventListener('click', function () {
        formSiembra.reset();
        selectMun.innerHTML = '<option value="" disabled selected>Primero elija un departamento...</option>';
        selectMun.disabled = true;
        panelResultados.classList.add('d-none');
        placeholderResultados.classList.remove('d-none');
    });

    // 4. Lógica del Panel del Extensionista
    async function cargarPanelExtensionista(depto) {
        if (!depto) return;
        tbodyExtensionista.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-4 text-muted">
                    <div class="spinner-border spinner-border-sm text-success me-2"></div>
                    Cargando priorización para ${depto}...
                </td>
            </tr>
        `;

        try {
            const resp = await fetch(`/api/panel-extensionista/${encodeURIComponent(depto)}`);
            const data = await resp.json();
            const items = data.items || [];

            if (items.length === 0) {
                tbodyExtensionista.innerHTML = `
                    <tr>
                        <td colspan="8" class="text-center py-4 text-muted">
                            No se encontraron registros de siembra para este departamento.
                        </td>
                    </tr>
                `;
                return;
            }

            tbodyExtensionista.innerHTML = '';
            items.forEach((item, idx) => {
                const badgeCls = item.nivel === 'ALTO' ? 'bg-danger' : (item.nivel === 'MEDIO' ? 'bg-warning text-dark' : 'bg-success');
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="fw-bold">${idx + 1}</td>
                    <td><strong>${item.municipio}</strong></td>
                    <td>${item.cultivo}</td>
                    <td><span class="badge bg-light text-dark border">${item.temporada}</span></td>
                    <td>${item.area_sembrada.toLocaleString()} ha</td>
                    <td class="fw-bold text-${item.nivel === 'ALTO' ? 'danger' : (item.nivel === 'MEDIO' ? 'warning' : 'success')}">${item.riesgo_pct}%</td>
                    <td><span class="badge ${badgeCls}">${item.nivel}</span></td>
                    <td><span class="badge bg-light text-secondary border">${item.perdida_real_pct}%</span></td>
                `;
                tbodyExtensionista.appendChild(tr);
            });

        } catch (err) {
            console.error('Error al cargar panel de extensionista:', err);
            tbodyExtensionista.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center py-4 text-danger">
                        Ocurrió un error al cargar la lista del panel.
                    </td>
                </tr>
            `;
        }
    }

    if (selectDeptoPanel) {
        selectDeptoPanel.addEventListener('change', function () {
            cargarPanelExtensionista(this.value);
        });
    }

    if (tabExtensionista) {
        tabExtensionista.addEventListener('shown.bs.tab', function () {
            if (selectDeptoPanel && selectDeptoPanel.value) {
                cargarPanelExtensionista(selectDeptoPanel.value);
            }
        });
    }

});
