import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Calculadora PAU - Arquitectura UPM",
    page_icon="🏛️",
    layout="centered"
)

# Título y descripción
st.title("Calculadora de Nota PAU")
st.subheader("Arquitectura - Universidad Politécnica de Madrid")
st.write("Esta calculadora te ayuda a simular tu nota de acceso para Arquitectura en la UPM.")

# Configuración de la barra lateral
with st.sidebar:
    st.markdown("### Fase General")
    nota_bachillerato = st.number_input(
        "Nota media de Bachillerato",
        min_value=5.0,
        max_value=10.0,
        value=9.75,
        step=0.01,
        help="Introduce tu nota media de Bachillerato (entre 5 y 10)"
    )

    st.markdown("#### Asignaturas Obligatorias")
    nota_lengua = st.number_input(
        "Lengua Castellana y Literatura",
        min_value=0.0,
        max_value=10.0,
        value=8.0,
        step=0.01
    )
    nota_historia = st.number_input(
        "Historia de la Filosofía",
        min_value=0.0,
        max_value=10.0,
        value=8.0,
        step=0.01
    )
    nota_ingles = st.number_input(
        "Inglés",
        min_value=0.0,
        max_value=10.0,
        value=8.0,
        step=0.01
    )
    nota_matematicas = st.number_input(
        "Matemáticas II",
        min_value=0.0,
        max_value=10.0,
        value=8.0,
        step=0.01
    )

    st.markdown("### Fase Específica")
    nota_fisica = st.number_input(
        "Física",
        min_value=0.0,
        max_value=10.0,
        value=8.0,
        step=0.01
    )
    nota_dibujo = st.number_input(
        "Dibujo Técnico II",
        min_value=0.0,
        max_value=10.0,
        value=8.0,
        step=0.01
    )

# Información adicional en el área principal
st.markdown("### ℹ️ Información sobre el cálculo")
st.info(
    "La nota de acceso se calcula: 60% Nota Media Bachillerato + 40% Fase General\n\n"
    "La nota final incluye la suma de las dos mejores ponderaciones (0.2) de las asignaturas específicas"
)

# Botón de cálculo en la barra lateral
with st.sidebar:
    st.markdown("---")
    st.button("Recalcular Nota", use_container_width=True)

# Área de resultados en el frame principal
# Nota de la fase general (60% NMB + 40% CFG)
nota_fase_general = (nota_lengua + nota_historia + nota_ingles + nota_matematicas) / 4
nota_acceso = (0.6 * nota_bachillerato) + (0.4 * nota_fase_general)

# Nota de la fase específica
notas_originales = {
    "Matemáticas II": nota_matematicas,
    "Física": nota_fisica,
    "Dibujo Técnico II": nota_dibujo
}
notas_ponderadas = {
    "Matemáticas II": nota_matematicas * 0.2,
    "Física": nota_fisica * 0.2,
    "Dibujo Técnico II": nota_dibujo * 0.2
}

notas_ordenadas = sorted(notas_ponderadas.items(), key=lambda x: x[1], reverse=True)
nota_especifica = notas_ordenadas[0][1] + notas_ordenadas[1][1]

nota_final = nota_acceso + nota_especifica

# Mostrar resultados en el área principal
st.markdown("### 📊 Resultados")
col1, col2 = st.columns(2)

with col1:
    st.metric("Nota de Acceso (hasta 10)", f"{nota_acceso:.3f}")

with col2:
    st.metric("Nota Final (hasta 14)", f"{nota_final:.3f}", border="True")

# Mostrar notas específicas con las dos mejores en rojo
st.markdown("#### 📝 Desglose de Notas Específicas")
for asignatura, nota_ponderada in notas_ordenadas:
    nota_original = notas_originales[asignatura]
    if notas_ordenadas.index((asignatura, nota_ponderada)) < 2:
        st.markdown(f"**:red[{asignatura}]**: :red[{nota_original:.2f}] (Ponderada: :red[{nota_ponderada:.3f}])")
    else:
        st.markdown(f"**{asignatura}**: {nota_original:.2f} (Ponderada: {nota_ponderada:.3f})")

st.info(
    "Las asignaturas marcadas en rojo son las que se utilizan para el cálculo de la nota final"
)
