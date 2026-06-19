"""
Asistente virtual — 
Sistema Híbrido de Triage: Simbólico + ML Clásico + LLM
"""

import streamlit as st
import google.generativeai as genai
import json, os, pickle
import numpy as np
from datetime import datetime

# ══════════════════════════════════════════════════════
#  CONFIGURACIÓN
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="Asistente Virtual — Hospital San Bernardo",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.hospital-header {
    background: linear-gradient(135deg, #1C2B4A 0%, #2E4070 100%);
    color: white; padding: 20px 28px;
    border-radius: 12px; margin-bottom: 20px;
}
.result-card {
    border-radius: 10px; padding: 16px 20px;
    margin: 8px 0; border-left: 6px solid;
}
.urgencia-1 { background:#FDEDEC; border-color:#E74C3C; }
.urgencia-2 { background:#FEF9E7; border-color:#F39C12; }
.urgencia-3 { background:#FFFDE7; border-color:#F1C40F; }
.urgencia-4 { background:#EBF5FB; border-color:#3498DB; }
.urgencia-5 { background:#EAFAF1; border-color:#2ECC71; }
.aviso { background:#FEF9E7; border:1px solid #F39C12;
         border-radius:8px; padding:10px 14px;
         font-size:13px; color:#7D6608; margin-top:12px; }
.capa-badge {
    display:inline-block; padding:3px 10px;
    border-radius:12px; font-size:12px;
    font-weight:bold; color:white; margin:2px;
}
.simbolico  { background:#8E44AD; }
.ml-clasico { background:#2980B9; }
.llm        { background:#27AE60; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  CONSTANTES
# ══════════════════════════════════════════════════════
URGENCIA_CFG = {
    1: {"emoji":"🔴","label":"CODIGO ROJO",    "bg":"#FDEDEC","color":"#E74C3C"},
    2: {"emoji":"🟠","label":"URGENTE",       "bg":"#FEF9E7","color":"#E67E22"},
    3: {"emoji":"🟡","label":"URGENCIA MENOR","bg":"#FFFDE7","color":"#D4AC0D"},
    4: {"emoji":"🔵","label":"POCO URGENTE",  "bg":"#EBF5FB","color":"#2980B9"},
    5: {"emoji":"🟢","label":"NO URGENTE",    "bg":"#EAFAF1","color":"#27AE60"},
}
LABELS = {1:"Codigo rojo",2:"Urgente",3:"Urgencia menor",4:"Poco urgente",5:"No urgente"}

REGLAS = {
    "corte_herida_miembro":    {"especialista":"Traumatología / Cirugía General","urgencia":2,"urgencia_label":"Urgente","estudios":["Radiografía zona afectada","Hemograma","Coagulograma si sangrado importante"],"indicaciones":"Limpiar y cubrir la herida. Evaluar profundidad y necesidad de sutura."},
    "traumatismo_craneal":     {"especialista":"Neurocirugía / Guardia Neurológica","urgencia":1,"urgencia_label":"Emergencia","estudios":["TAC de cráneo sin contraste","Evaluación neurológica inmediata","Hemograma","Glucemia"],"indicaciones":"Inmovilizar. Monitoreo de conciencia y pupilas."},
    "dolor_toracico":          {"especialista":"Cardiología / Guardia de Emergencias","urgencia":1,"urgencia_label":"Emergencia","estudios":["ECG de 12 derivaciones INMEDIATO","Troponinas I y T","Rx de tórax","Saturación O2"],"indicaciones":"Acceso venoso inmediato. Reposo absoluto. Monitoreo cardíaco."},
    "fiebre_sin_herida":       {"especialista":"Clínica Médica","urgencia":3,"urgencia_label":"Urgencia menor","estudios":["Hemograma diferencial","PCR","Orina completa","Hemocultivo x2 si T>38.5"],"indicaciones":"Hidratación. Antitérmico si T°>38.5°C."},
    "dificultad_respiratoria": {"especialista":"Neumonología / Guardia de Emergencias","urgencia":1,"urgencia_label":"Emergencia","estudios":["Saturometría inmediata","Rx tórax","Gasometría arterial"],"indicaciones":"O2 si saturación <94%. Posición semi-sentada."},
    "dolor_abdominal":         {"especialista":"Cirugía General / Guardia Quirúrgica","urgencia":2,"urgencia_label":"Urgente","estudios":["Ecografía abdominal","Hemograma","Amilasa y lipasa","Orina completa"],"indicaciones":"Sin analgésicos hasta evaluación médica. Hidratación IV."},
    "fractura_sospecha":       {"especialista":"Traumatología y Ortopedia","urgencia":2,"urgencia_label":"Urgente","estudios":["Radiografía 2 proyecciones","Hemograma si fractura expuesta"],"indicaciones":"Inmovilizar. Sin reducción sin especialista."},
    "perdida_consciencia":     {"especialista":"Neurología / Guardia de Emergencias","urgencia":1,"urgencia_label":"Emergencia","estudios":["Glucemia capilar INMEDIATA","ECG","TAC cráneo","Hemograma","Ionograma"],"indicaciones":"Posición lateral. Vía aérea permeable. Acceso venoso."},
    "problema_ocular":         {"especialista":"Oftalmología","urgencia":2,"urgencia_label":"Urgente","estudios":["Agudeza visual","Lavado ocular si químico"],"indicaciones":"No frotar. Lavado con suero fisiológico."},
    "problema_psiquiatrico":   {"especialista":"Psiquiatría / Guardia de Salud Mental","urgencia":2,"urgencia_label":"Urgente","estudios":["Evaluación psiquiátrica","Glucemia","Toxicológico en orina"],"indicaciones":"Ambiente tranquilo. No dejar solo."},
    "dolor_cabeza":            {"especialista":"Neurología","urgencia":3,"urgencia_label":"Urgencia menor","estudios":["Evaluación neurológica","Tensión arterial","TAC si cefalea súbita"],"indicaciones":"Reposo en ambiente oscuro. Escalar a urgencia 1 si cefalea súbita intensa."},
    "resfrio_gripal":          {"especialista":"Clínica Médica","urgencia":4,"urgencia_label":"Poco urgente","estudios":["Evaluación clínica","Hisopado si sospecha influenza"],"indicaciones":"Hidratación oral. Reposo. Antitérmico si fiebre."},
    "sincope":                 {"especialista":"Neurología","urgencia":2,"urgencia_label":"Urgente","estudios":["Glucemia capilar","ECG","TA ambos brazos"],"indicaciones":"Acostar. Elevar miembros. Descartar causa cardíaca."},
    "corte_tronco_cara":       {"especialista":"Cirugía General","urgencia":2,"urgencia_label":"Urgente","estudios":["Hemograma","Coagulograma","Rx o TAC según zona"],"indicaciones":"Compresión directa. No retirar objetos incrustados."},
}

# ══════════════════════════════════════════════════════
#  CARGAR MODELO ML
# ══════════════════════════════════════════════════════
@st.cache_resource
def cargar_modelo():
    """Carga el modelo RandomForest entrenado."""
    if os.path.exists('modelo_urgencia.pkl'):
        with open('modelo_urgencia.pkl', 'rb') as f:
            return pickle.load(f)
    return None

modelo_rf = cargar_modelo()

# ══════════════════════════════════════════════════════
#  FUNCIONES PRINCIPALES
# ══════════════════════════════════════════════════════
def predecir_urgencia_ml(signos):
    """Capa 2: ML Clásico — predice urgencia desde signos vitales."""
    if modelo_rf is None:
        return None, None
    try:
        features = np.array([[
            signos.get('presion_sistolica', 120),
            signos.get('presion_diastolica', 80),
            signos.get('temperatura', 37.0),
            signos.get('saturacion_o2', 98),
            signos.get('frecuencia_cardiaca', 75),
            signos.get('edad', 40)
        ]])
        urgencia = int(modelo_rf.predict(features)[0])
        confianza = float(modelo_rf.predict_proba(features).max())
        return urgencia, confianza
    except:
        return None, None


def get_system_prompt():
    return f"""Sos un Asistente Virtual, para la guardia de emergencias del Hospital San Bernardo de Salta, Argentina.

REGLAS DE DERIVACIÓN:
{json.dumps(REGLAS, ensure_ascii=False, indent=2)}

INSTRUCCIONES:
1. Analizá la descripción del paciente.
2. Identificá la categoría que mejor corresponde.
3. Si coincide con varias, priorizá la de MAYOR urgencia (número más bajo).
4. Respondé ÚNICAMENTE con JSON válido, sin texto adicional.

FORMATO:
{{
  "categoria_detectada": "nombre",
  "especialista": "especialista sugerido",
  "nivel_urgencia": número 1-5,
  "urgencia_label": "label",
  "estudios_sugeridos": ["estudio 1"],
  "indicaciones_iniciales": "texto",
  "confianza": "Alta / Media / Baja",
  "advertencia": "texto o vacío"
}}

RESTRICCIONES: No diagnosticás. No reemplazás al médico. Síntomas vagos = confianza Baja."""


def evaluar_llm(descripcion, api_key):
    """Capa 3: LLM — interpreta texto libre con Gemini."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-lite',
            system_instruction=get_system_prompt()
        )
        response = model.generate_content(
            f'DESCRIPCIÓN DEL PACIENTE:\n{descripcion}',
            generation_config=genai.GenerationConfig(temperature=0.1, max_output_tokens=800)
        )
        texto = response.text.strip()
        if texto.startswith('```'):
            texto = texto.split('```')[1]
            if texto.startswith('json'):
                texto = texto[4:]
        return {'ok': True, 'data': json.loads(texto.strip())}
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def triage_hibrido(descripcion, signos, api_key):
    """Sistema híbrido completo: Simbólico + ML + LLM."""
    # Capa 2: ML
    ml_urgencia, ml_confianza = predecir_urgencia_ml(signos)

    # Capa 3: LLM
    llm_resp = evaluar_llm(descripcion, api_key)
    llm_data = llm_resp.get('data') if llm_resp['ok'] else None
    llm_urgencia = llm_data.get('nivel_urgencia') if llm_data else None

    # Decisión final: urgencia más alta (número más bajo)
    urgencias = [u for u in [ml_urgencia, llm_urgencia] if u is not None]
    urgencia_final = min(urgencias) if urgencias else 3

    fuente = "Híbrida (ML + LLM)" if ml_urgencia and llm_urgencia else ("Solo ML" if ml_urgencia else "Solo LLM")

    return {
        'urgencia_final': urgencia_final,
        'fuente': fuente,
        'ml': {'urgencia': ml_urgencia, 'confianza': ml_confianza},
        'llm': llm_data,
        'llm_error': llm_resp.get('error') if not llm_resp['ok'] else None
    }

# ══════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🔑 Configuración")
    api_key = st.text_input("API Key de Gemini", type="password",
                             help="Obtené tu clave gratuita en aistudio.google.com",
                             placeholder="AIza...")

    st.markdown("---")
    st.markdown("### 🤖 Sistema Híbrido")
    st.markdown("""
    <span class='capa-badge simbolico'>Simbólico</span> Reglas JSON clínicas<br><br>
    <span class='capa-badge ml-clasico'>ML Clásico</span> RandomForest — signos vitales<br><br>
    <span class='capa-badge llm'>LLM</span> Gemini — texto libre
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 Escala de Urgencias")
    for n, cfg in URGENCIA_CFG.items():
        st.markdown(
            f"<div style='padding:3px 10px;margin:3px 0;border-radius:6px;"
            f"background:{cfg['bg']};border-left:4px solid {cfg['color']};font-size:13px;'>"
            f"{cfg['emoji']} <b>Nivel {n}</b> — {cfg['label']}</div>",
            unsafe_allow_html=True
        )

    if modelo_rf:
        st.success("✅ Modelo ML cargado")
    else:
        st.warning("⚠️ modelo_urgencia.pkl no encontrado.\nEjecutá el notebook primero.")

    st.markdown("---")
    st.caption("Asistente Virtual — Hospital San Bernardo")
    st.caption("Grupo 3: Quispe Alejandra Carina, Saucedo Noelia")

# ══════════════════════════════════════════════════════
#  ENCABEZADO
# ══════════════════════════════════════════════════════
st.markdown("""
<div class="hospital-header">
    <h2 style="margin:0;color:white;">🏥 Asistente Virtual — Sistema Híbrido de Triage</h2>
    <p style="margin:4px 0 0 0;color:#AED6F1;font-size:14px;">
        Guardia de Emergencias · Hospital San Bernardo <br>
        <span style="font-size:12px;">
            <b>GRUPO 3: </b> 
            <b>Quispe Alejandra Carina</b>
            <b>Saucedo Noelia</b> 
        </span>
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="aviso">
⚕️ <b>Aviso:</b> Este sistema es un <b>asistente de apoyo</b>.
Las sugerencias son <b>orientativas</b>. El criterio clínico del profesional <b>prevalece siempre</b>.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  FORMULARIO
# ══════════════════════════════════════════════════════
col_form, col_hist = st.columns([3, 2], gap="large")

with col_form:
    st.markdown("### 📝 Ingreso del paciente")

    descripcion = st.text_area(
        "Describí los síntomas en lenguaje libre",
        placeholder="Ej: 'El paciente llegó caminando, dice que tiene dolor fuerte en el pecho y le duele el brazo izquierdo desde hace 20 minutos...'",
        height=130,
        help="Escribí como hablarías normalmente. El sistema entiende lenguaje coloquial."
    )

    st.markdown("**Signos vitales** *(completar para activar el análisis ML)*")
    c1, c2, c3 = st.columns(3)
    with c1:
        ps  = st.number_input("Presión sistólica", 60, 250, value=None, step=1, placeholder="Ej: 120")
        pd_ = st.number_input("Presión diastólica", 30, 150, value=None, step=1, placeholder="Ej: 80")
    with c2:
        temp = st.number_input("Temperatura (°C)", 34.0, 43.0, value=None, step=0.1, format="%.1f", placeholder="Ej: 37.5")
        sat  = st.number_input("Saturación O₂ (%)", 50, 100, value=None, step=1, placeholder="Ej: 97")
    with c3:
        fc   = st.number_input("Frecuencia cardíaca", 20, 250, value=None, step=1, placeholder="Ej: 88")
        edad = st.number_input("Edad del paciente", 0, 120, value=None, step=1, placeholder="Ej: 45")

    evaluar_btn = st.button("🔍 Evaluar paciente", type="primary", use_container_width=True)

with col_hist:
    st.markdown("### 🕒 Historial de la sesión")
    if "historial" not in st.session_state:
        st.session_state.historial = []
    if st.session_state.historial:
        for item in reversed(st.session_state.historial[-6:]):
            cfg = URGENCIA_CFG.get(item['urgencia'], URGENCIA_CFG[3])
            st.markdown(
                f"<div style='padding:7px 10px;margin:3px 0;border-radius:7px;"
                f"background:{cfg['bg']};border-left:4px solid {cfg['color']};font-size:12px;'>"
                f"{cfg['emoji']} <b>{item['hora']}</b> — Nivel {item['urgencia']}<br>"
                f"→ {item['especialista']}<br>"
                f"<span style='color:#666;'>{item['desc'][:55]}...</span></div>",
                unsafe_allow_html=True
            )
        if st.button("🗑️ Limpiar historial", use_container_width=True):
            st.session_state.historial = []
            st.rerun()
    else:
        st.info("Los casos evaluados aparecerán aquí.")

# ══════════════════════════════════════════════════════
#  RESULTADO
# ══════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### 📊 Resultado del triage")

if evaluar_btn:
    if not api_key:
        st.error("⚠️ Ingresá tu API Key de Gemini en el panel izquierdo.")
    elif not descripcion.strip():
        st.warning("⚠️ Describí los síntomas antes de evaluar.")
    else:
        signos = {}
        if ps:   signos['presion_sistolica']   = int(ps)
        if pd_:  signos['presion_diastolica']  = int(pd_)
        if temp: signos['temperatura']         = float(temp)
        if sat:  signos['saturacion_o2']       = int(sat)
        if fc:   signos['frecuencia_cardiaca'] = int(fc)
        if edad: signos['edad']                = int(edad)

        with st.spinner("🤖 Analizando con sistema híbrido..."):
            res = triage_hibrido(descripcion, signos, api_key)

        urg_final = res.get('urgencia_final', 3)
        cfg = URGENCIA_CFG.get(urg_final, URGENCIA_CFG[3])
        llm = res.get('llm') or {}
        ml  = res.get('ml') or {}

        # Guardar historial
        st.session_state.historial.append({
            'hora': datetime.now().strftime("%H:%M:%S"),
            'urgencia': urg_final,
            'especialista': llm.get('especialista', '—'),
            'desc': descripcion
        })

        # ── RESULTADO PRINCIPAL ──
        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(
                f"<div style='text-align:center;padding:18px;border-radius:12px;"
                f"background:{cfg['bg']};border:2px solid {cfg['color']};'>"
                f"<div style='font-size:40px'>{cfg['emoji']}</div>"
                f"<div style='font-size:26px;font-weight:bold;color:{cfg['color']};'>NIVEL {urg_final}</div>"
                f"<div style='font-size:14px;font-weight:bold;color:{cfg['color']};'>{cfg['label']}</div>"
                f"<div style='font-size:11px;color:#666;margin-top:6px;'>{res.get('fuente','')}</div>"
                f"</div>", unsafe_allow_html=True
            )
        with r2:
            st.markdown(
                f"<div style='padding:18px;border-radius:12px;background:#F8F9FA;border:1px solid #D5D8DC;'>"
                f"<div style='font-size:11px;color:#666;text-transform:uppercase;'>ESPECIALISTA SUGERIDO</div>"
                f"<div style='font-size:17px;font-weight:bold;color:#1C2B4A;margin-top:6px;'>"
                f"🏥 {llm.get('especialista','—')}</div>"
                f"<div style='font-size:11px;color:#666;margin-top:10px;'>CONFIANZA LLM</div>"
                f"<div style='font-size:15px;font-weight:bold;margin-top:4px;'>"
                f"{'🟢' if llm.get('confianza')=='Alta' else '🟡' if llm.get('confianza')=='Media' else '🔴'} "
                f"{llm.get('confianza','—')}</div>"
                f"</div>", unsafe_allow_html=True
            )
        with r3:
            ml_txt = f"Nivel {ml.get('urgencia','—')} ({ml.get('confianza', 0)*100:.0f}% conf.)" if ml.get('urgencia') else "Sin datos de signos vitales"
            st.markdown(
                f"<div style='padding:18px;border-radius:12px;background:#F8F9FA;border:1px solid #D5D8DC;'>"
                f"<div style='font-size:11px;color:#666;text-transform:uppercase;'>ML — SIGNOS VITALES</div>"
                f"<div style='font-size:15px;font-weight:bold;color:#2874A6;margin-top:6px;'>🤖 {ml_txt}</div>"
                f"<div style='font-size:11px;color:#666;margin-top:10px;'>CATEGORÍA DETECTADA</div>"
                f"<div style='font-size:13px;color:#333;margin-top:4px;'>📋 {llm.get('categoria_detectada','—')}</div>"
                f"</div>", unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── ESTUDIOS E INDICACIONES ──
        e_col, i_col = st.columns(2)
        with e_col:
            st.markdown("#### 🔬 Estudios preliminares sugeridos")
            for estudio in llm.get('estudios_sugeridos', []):
                st.markdown(
                    f"<div style='background:white;border:1px solid #D5D8DC;border-radius:6px;"
                    f"padding:6px 12px;margin:3px 0;font-size:14px;'>🧪 {estudio}</div>",
                    unsafe_allow_html=True
                )
        with i_col:
            st.markdown("#### 📋 Indicaciones iniciales para guardia")
            st.markdown(
                f"<div style='background:#F0F8FF;border-radius:8px;padding:14px;"
                f"border-left:4px solid #2980B9;font-size:14px;line-height:1.6;'>"
                f"{llm.get('indicaciones_iniciales','—')}</div>",
                unsafe_allow_html=True
            )

        if llm.get('advertencia'):
            st.warning(f"⚠️ {llm.get('advertencia')}")

        if res.get('llm_error'):
            st.error(f"❌ Error LLM: {res.get('llm_error')}")

        st.markdown("""
        <div class="aviso">
        ⚕️ <b>Recordatorio:</b> Esta evaluación es <b>orientativa</b>.
        El profesional de guardia debe validar clínicamente el caso antes de proceder.
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown(
        "<div style='text-align:center;padding:40px;color:#AAB7B8;font-size:15px;'>"
        "🏥 Completá los datos del paciente y presioná <b>Evaluar paciente</b>."
        "</div>", unsafe_allow_html=True
    )
