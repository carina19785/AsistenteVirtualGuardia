# 🏥 Asistente Virtual — Sistema Híbrido de Triage para Guardia de Emergencias

> Trabajo Integrador Final · Modelado de Sistemas de IA Aplicada 
> Profe: Lic. Walter Gabriel Ramírez

---

## ¿Qué es un Asistente Virtual?

**Asistente Virtual** es un sistema **híbrido** de triage para la guardia de emergencias del Hospital San Bernardo de Salta. Que combina tres enfoques de IA para asistir al personal de enfermería en la clasificación y derivación de pacientes.
---

## 🤖 Arquitectura del sistema híbrido

```
CAPA 1 — Enfoque Simbólico
  Reglas clínicas explícitas en reglas.json
  "Si corte en miembro → Traumatología"
  Basadas en el Protocolo de Triage Manchester
          ↓
CAPA 2 — ML Clásico (scikit-learn)
  RandomForest entrenado con signos vitales
  Presión + Temperatura + Saturación + FC + Edad → Urgencia (1-5)
  Métricas: Precisión, Recall, F1-score, AUC-ROC
          ↓
CAPA 3 — Conexionista (Gemini LLM)
  Interpreta el texto libre del paciente
  "me duele el pecho" → Cardiología, Nivel 1
          ↓
DECISIÓN FINAL HÍBRIDA
  Toma la urgencia más alta entre ML y LLM
  Muestra especialista + estudios + indicaciones
          ↓
APP LOCAL — Streamlit
  Interfaz visual para el personal de guardia
```

---

## 📁 Estructura del repositorio

```
asis-triaje/
├── data/
│   ├── reglas/
│   │   └── reglas.json                      ← Base de reglas de derivación (14 categorías)
│   └── casos/
│       └── datos_triage.csv                 ← Dataset simulado (400 registros)
├── notebooks/
│   └── asis_triaje_avance2_hibrido.ipynb    ← Notebook Avance 2 (ML + LLM + métricas)
├── app/
│   ├── app_avance3.py                       ← App Streamlit Avance 3
│   └── modelo_urgencia.pkl                  ← Modelo RandomForest entrenado
├── docs/
│   ├── AsisTriaje_Ficha_Avance1.docx
│   ├── AsisTriaje_FichaTemplate_Completada.docx
│   └── AsisTriaje_Justificacion_Tecnica_Avance2.docx
└── README.md
```

---

## ⚙️ Instrucciones de instalación

### Requisitos previos
- Python 3.9 o superior instalado
- Una API Key gratuita de Gemini 

### Paso 1 — Clonar el repositorio

```bash
git clone https://github.com/carina19785/AsistenteVirtualGuardia.git
cd AsistenteVirtualGuardia
```

### Paso 2 — Instalar dependencias

```bash
pip install streamlit google-generativeai scikit-learn pandas numpy matplotlib seaborn python-dotenv
```

O con el archivo de requerimientos:

```bash
pip install -r requirements.txt
```

### Paso 3 — Obtener la API Key de Gemini (gratuita)

1. Entrá a **https://aistudio.google.com/app/apikey**
2. Iniciá sesión con tu cuenta de Google
3. Hacé click en **"Create API Key"**
4. Copiá la clave que empieza con `AIza...`

### Paso 4 — Configurar la API Key

Creá un archivo `.env` en la carpeta `app/`:

```
GEMINI_API_KEY=AIzaSy...tu_clave_aqui
```

### Paso 5 — Generar el modelo ML (solo primera vez)

Abrí el notebook `notebooks/asis_triaje_avance2_hibrido.ipynb` en VS Code o Google Colab y ejecutá todas las celdas. Esto genera el archivo `modelo_urgencia.pkl`.

Copiá el archivo generado a la carpeta `app/`:

```bash
cp modelo_urgencia.pkl app/
```

### Paso 6 — Ejecutar la app

```bash
cd app
streamlit run app_avance3.py
```

La app se abre automáticamente en el navegador en `http://localhost:8501`

---

## 🖥️ Cómo usar la app

1. **Ingresá la API Key** de Gemini en el panel izquierdo
2. **Describí los síntomas** del paciente en lenguaje libre en el campo de texto
3. **Completá los signos vitales** (opcional pero recomendado para activar el análisis ML)
4. **Presioná "Evaluar paciente"**
5. El sistema muestra: nivel de urgencia, especialista sugerido, estudios y indicaciones

---

## 📊 Estado del proyecto

| Avance | Fecha | Estado |
|---|---|---|
| Avance 1 — Problema, solución y plan  | ✅ Entregado |
| Avance 2 — Núcleo técnico funcionando | | ✅ Completado |
| Avance 3 — Aplicación local funcionando |  | ✅ Completado |
| Avance 4 — Evaluación completa | 12/06/2026 | ⏳ Pendiente |
| Presentación final | 23-30/06/2026 | ⏳ Pendiente |
---

## 👥 Integrantes

| # | Nombre y apellido |
|---|---|
| 1 | QUISPE ALEJANDRA CARINA |
| 2 | SAUCEDO NOELIA |

---

## ⚠️ Nota importante

Aistente Virtual es un **asistente de apoyo** al personal de salud. No reemplaza el criterio médico ni está certificado como dispositivo médico. Las sugerencias de derivación y estudios son orientativas y deben ser validadas por el profesional a cargo.



