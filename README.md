# AsistenteVirtualGuardia
# 🏥 AsisTriaje — Asistente Virtual de Triage para Guardia de Emergencias

> Trabajo Integrador Final · Modelado de Sistemas de IA Aplicada ·
> Tecnicatura Universitaria en Ciencia de Datos e IA Aplicada · UPATecO · Salta · 2026  
> Formador: Lic. Walter Gabriel Ramírez

---

## ¿Qué es el Asistente Virtual?

**Asistente Virtual** es un asistente conversacional diseñado para apoyar el proceso de triage en la guardia de emergencias.

El paciente o la enfermera describe los síntomas en lenguaje libre. El sistema interpreta esa descripción, la cruza con una base de reglas de derivación clínica y devuelve al profesional de guardia:

- 🔴 **Nivel de urgencia** (escala 1 al 3 — Protocolo de Triage )
- 🏥 **Especialista sugerido** para la derivación
- 🔬 **Estudios preliminares recomendados**
- 📋 **Resumen del caso** para el profesional

---

## Problema que resuelve

En guardias con alta demanda, el proceso de triage manual puede generar demoras en derivaciones y retrasos en estudios urgentes. Este asistente no reemplaza al profesional: **lo asiste** para que tome decisiones más rápidas y con información organizada.

---

## Ciclo técnico

**Ciclo 2 — LLM + API de lenguaje (Asistente conversacional)**

```
Descripción libre del paciente
        ↓
LLM interpreta síntomas y extrae información clínica
        ↓
Consulta base de reglas de derivación (JSON)
        ↓
Respuesta estructurada → Streamlit (app local)
```

---

## Stack tecnológico

| Herramienta | Uso |
|---|---|
| Python | Lenguaje base |
| Gemini API / OpenAI API | Motor LLM para interpretación de lenguaje natural |
| Streamlit | Interfaz de la aplicación local |
| Google Colab | Desarrollo y exploración |
| GitHub | Control de versiones y entrega |
| SHAP (Avance 4) | Explicabilidad del sistema |

---

## Estructura del repositorio

```
asis-triaje/
├── data/
│   ├── protocolos/         # PDFs: Triage Manchester, guías clínicas Ministerio Salud
│   ├── reglas/             # Base de reglas de derivación en formato JSON
│   └── casos/              # Casos simulados para pruebas (mínimo 200 registros)
├── notebooks/
│   └── exploracion.ipynb   # Exploración del contexto clínico y pruebas de prompt
├── app/
│   └── main.py             # Aplicación Streamlit
├── docs/
│   ├── ficha_avance1.docx  # Ficha de inicio
│   └── informe_APA.docx    # Informe final en formato APA
└── README.md
```

---

## Estado del proyecto

| Avance | Fecha | Estado |
|---|---|---|
| Avance 1 — Problema, solución y plan | 24/04/2026 | ✅Listo |
| Avance 2 — Núcleo técnico funcionando | 08/05/2026 | ✅Listo|
| Avance 3 — Aplicación local funcionando | 29/05/2026 | 🚑 En curso |
| Avance 4 — Evaluación completa | 12/06/2026 | ⏳ Pendiente |
| Presentación final | 23-30/06/2026 | ⏳ Pendiente |

---

## Tablero de gestión


---

## Cómo ejecutar la app (instrucciones de instalación)

>

```bash
# 1. Clonar el repositorio
git clone https://github.com/[usuario]/asis-triaje.git
cd asis-triaje

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar la API key


# 4. Ejecutar la app
streamlit run app/main.py
```

---
POSIBLE ARQUITECTURA
<img width="729" height="283" alt="image" src="https://github.com/user-attachments/assets/e513920c-d68e-46ee-ab55-b9755eb1d81a" />
----
FLUJO DEL SISTEMA
<img width="596" height="275" alt="image" src="https://github.com/user-attachments/assets/64b3a315-7b22-42b3-adaf-de483002f382" />


## Integrantes

| # | Nombre y apellido |
|---|---|
| 1 | QUISPE ALEJANDRA|
| 2 |OVANDO ROBERTO |
| 3 | SAUCEDO NOELIA |

---

## Nota importante

Este sistema es un **asistente de apoyo** al personal de salud. No reemplaza el criterio clínico del profesional. Las sugerencias de derivación y estudios son orientativas y deben ser validadas por el médico o enfermero a cargo.

---


